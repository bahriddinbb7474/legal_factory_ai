import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base, CompanyProfile
from app.schemas.company_profile import CompanyProfileUpdate
from app.services.company_profile import company_profile_service, get_company_profile_context


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
