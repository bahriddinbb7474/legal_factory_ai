from abc import ABC, abstractmethod
from pathlib import Path


class StorageProvider(ABC):
    @abstractmethod
    async def save(self, content: bytes, suffix: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def save_text(self, content: str, suffix: str = ".txt") -> str:
        raise NotImplementedError

    @abstractmethod
    async def read(self, key: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def read_text(self, key: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_path(self, key: str) -> Path:
        raise NotImplementedError
