import asyncio
import io

import pytest
from docx import Document as DocxDocument
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base, CompanyProfile
from app.schemas.company_profile import CompanyProfileUpdate
from app.services.company_profile import company_profile_service, get_company_profile_context
from app.storage.local import local_storage


@pytest.fixture(autouse=True)
def isolate_storage(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(local_storage, "base_dir", tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)


def _payload(**overrides):
    payload = {
        "full_name": "Kabel Tech Energy LLC",
        "short_name": "Kabel Tech Energy",
        "legal_address": "Tashkent, Legal street 1",
        "actual_address": "Tashkent, Factory street 7",
        "tax_id": "123456789",
        "oked": "27320",
        "bank_name": "National Bank",
        "bank_mfo": "01001",
        "bank_account": "20208000123456789012",
        "director_name": "Director Name",
        "chief_accountant_name": "Chief Accountant",
        "legal_responsible_name": "Legal Responsible",
        "phone": "+998 90 123 45 67",
        "email": "legal@kte.uz",
        "website": "https://kte.uz",
        "is_active": True,
        "notes": "Stage 8-A foundation",
    }
    payload.update(overrides)
    return payload


def test_get_company_profile_returns_404_when_missing(client) -> None:
    response = client.get("/api/company-profile")

    assert response.status_code == 404
    assert response.json()["detail"] == "Company profile not found"


def test_put_company_profile_creates_and_get_returns_profile(client) -> None:
    created = client.put("/api/company-profile", json=_payload())

    assert created.status_code == 200
    assert created.json()["full_name"] == "Kabel Tech Energy LLC"

    fetched = client.get("/api/company-profile")

    assert fetched.status_code == 200
    assert fetched.json()["short_name"] == "Kabel Tech Energy"
    assert fetched.json()["email"] == "legal@kte.uz"


def test_put_company_profile_updates_existing_singleton_record(client) -> None:
    first = client.put("/api/company-profile", json=_payload())
    updated = client.put(
        "/api/company-profile",
        json=_payload(short_name="KTE", website="https://company.example", notes="Updated profile"),
    )

    assert first.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["id"] == first.json()["id"]
    assert updated.json()["short_name"] == "KTE"
    assert updated.json()["website"] == "https://company.example"
    assert updated.json()["notes"] == "Updated profile"


def test_company_profile_validation_rejects_blank_required_fields_and_bad_email(client) -> None:
    response = client.put(
        "/api/company-profile",
        json=_payload(full_name="   ", short_name=" ", email="not-an-email"),
    )

    assert response.status_code == 422


def test_stamp_and_signature_upload_endpoints_are_not_available_in_stage8a(client) -> None:
    stamp = client.post("/api/company-profile/stamp")
    signature = client.post("/api/company-profile/signature")

    assert stamp.status_code == 404
    assert signature.status_code == 404


def test_upload_logo_allowed_type_updates_storage_key(client) -> None:
    client.put("/api/company-profile", json=_payload())

    response = client.post("/api/company-profile/logo", files={"file": ("logo.png", b"png-bytes", "image/png")})

    assert response.status_code == 200
    payload = response.json()
    assert payload["logo_storage_key"].endswith(".png")
    assert list(local_storage.base_dir.iterdir())


def test_upload_letterhead_docx_pdf_and_legacy_doc_are_allowed(client) -> None:
    client.put("/api/company-profile", json=_payload())

    docx_response = client.post(
        "/api/company-profile/letterhead",
        files={"file": ("letterhead.docx", _docx_bytes("Blank letterhead"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    pdf_response = client.post(
        "/api/company-profile/letterhead",
        files={"file": ("letterhead.pdf", _minimal_pdf(), "application/pdf")},
    )
    doc_response = client.post(
        "/api/company-profile/letterhead",
        files={"file": ("letterhead.doc", b"\xD0\xCF\x11\xE0\xa1\xb1\x1a\xe1legacy", "application/msword")},
    )

    assert docx_response.status_code == 200
    assert pdf_response.status_code == 200
    assert doc_response.status_code == 200
    assert doc_response.json()["letterhead_storage_key"].endswith(".doc")


def test_upload_rejects_unsupported_type_and_empty_file(client) -> None:
    client.put("/api/company-profile", json=_payload())

    unsupported = client.post("/api/company-profile/logo", files={"file": ("logo.svg", b"<svg/>", "image/svg+xml")})
    empty = client.post("/api/company-profile/letterhead", files={"file": ("empty.docx", b"", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})

    assert unsupported.status_code == 400
    assert empty.status_code == 400


def test_delete_logo_and_letterhead_clear_storage_keys(client) -> None:
    client.put("/api/company-profile", json=_payload())
    client.post("/api/company-profile/logo", files={"file": ("logo.jpg", b"jpg-bytes", "image/jpeg")})
    client.post("/api/company-profile/letterhead", files={"file": ("letterhead.pdf", _minimal_pdf(), "application/pdf")})

    deleted_logo = client.delete("/api/company-profile/logo")
    deleted_letterhead = client.delete("/api/company-profile/letterhead")

    assert deleted_logo.status_code == 200
    assert deleted_letterhead.status_code == 200
    assert deleted_logo.json()["logo_storage_key"] is None
    assert deleted_letterhead.json()["letterhead_storage_key"] is None


def test_company_profile_context_includes_asset_keys_and_excludes_stamp_signature(client) -> None:
    client.put("/api/company-profile", json=_payload())
    client.post("/api/company-profile/logo", files={"file": ("logo.webp", b"webp-bytes", "image/webp")})
    client.post("/api/company-profile/letterhead", files={"file": ("letterhead.docx", _docx_bytes("Template"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})

    async def scenario() -> None:
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        try:
            async with session_factory() as session:
                session.add(
                    CompanyProfile(
                        full_name="Kabel Tech Energy LLC",
                        short_name="Kabel Tech Energy",
                        logo_storage_key="logo.webp",
                        letterhead_storage_key="letterhead.docx",
                        is_active=True,
                    )
                )
                await session.commit()
                context = await get_company_profile_context(session)
                assert context is not None
                data = context.model_dump()
                assert data["logo_storage_key"] == "logo.webp"
                assert data["letterhead_storage_key"] == "letterhead.docx"
                assert "stamp" not in data
                assert "signature" not in data
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def test_company_profile_service_keeps_single_active_profile_and_context() -> None:
    async def scenario() -> None:
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        try:
            async with session_factory() as session:
                session.add(
                    CompanyProfile(
                        full_name="Legacy Company",
                        short_name="Legacy",
                        is_active=True,
                    )
                )
                session.add(
                    CompanyProfile(
                        full_name="Dormant Company",
                        short_name="Dormant",
                        is_active=True,
                    )
                )
                await session.commit()

                await company_profile_service.upsert_profile(
                    session,
                    payload=CompanyProfileUpdate(**_payload()),
                )
                await session.commit()

                result = await session.execute(select(CompanyProfile).order_by(CompanyProfile.id))
                profiles = result.scalars().all()
                active_profiles = [profile for profile in profiles if profile.is_active]
                context = await get_company_profile_context(session)

                assert len(active_profiles) == 1
                assert active_profiles[0].full_name == "Kabel Tech Energy LLC"
                assert context is not None
                assert context.short_name == "Kabel Tech Energy"
        finally:
            await engine.dispose()

    asyncio.run(scenario())


def _docx_bytes(text: str) -> bytes:
    doc = DocxDocument()
    doc.add_paragraph(text)
    stream = io.BytesIO()
    doc.save(stream)
    return stream.getvalue()


def _minimal_pdf() -> bytes:
    return (
        b"%PDF-1.4\n"
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R >> endobj\n"
        b"4 0 obj << /Length 44 >> stream\nBT /F1 12 Tf 20 100 Td (Hello PDF) Tj ET\nendstream endobj\n"
        b"xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \n"
        b"trailer << /Root 1 0 R /Size 5 >>\nstartxref\n298\n%%EOF"
    )
