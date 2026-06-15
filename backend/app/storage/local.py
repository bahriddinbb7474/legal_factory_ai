import asyncio
import uuid
from pathlib import Path

from app.core.config import ROOT_DIR
from app.storage.base import StorageProvider


class StoragePathError(ValueError):
    pass


class LocalStorageProvider(StorageProvider):
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = (base_dir or ROOT_DIR / "data" / "uploads").resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, content: bytes, suffix: str) -> str:
        key = self._new_key(suffix)
        path = self.get_path(key)
        await asyncio.to_thread(path.write_bytes, content)
        return key

    async def save_text(self, content: str, suffix: str = ".txt") -> str:
        key = self._new_key(suffix)
        path = self.get_path(key)
        await asyncio.to_thread(path.write_text, content, "utf-8")
        return key

    async def read(self, key: str) -> bytes:
        path = self.get_path(key)
        return await asyncio.to_thread(path.read_bytes)

    async def read_text(self, key: str) -> str:
        path = self.get_path(key)
        return await asyncio.to_thread(path.read_text, "utf-8")

    async def delete(self, key: str) -> None:
        path = self.get_path(key)
        if path.exists():
            await asyncio.to_thread(path.unlink)

    async def exists(self, key: str) -> bool:
        return self.get_path(key).exists()

    def get_path(self, key: str) -> Path:
        if "\\" in key or ".." in Path(key).parts or Path(key).is_absolute():
            raise StoragePathError("Invalid storage key")
        path = (self.base_dir / key).resolve()
        if self.base_dir not in path.parents and path != self.base_dir:
            raise StoragePathError("Invalid storage key")
        return path

    def _new_key(self, suffix: str) -> str:
        normalized_suffix = suffix.lower()
        if not normalized_suffix.startswith("."):
            normalized_suffix = f".{normalized_suffix}"
        return f"{uuid.uuid4().hex}{normalized_suffix}"


local_storage = LocalStorageProvider()
