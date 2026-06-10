from functools import lru_cache
import os
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class Settings:
    def __init__(self) -> None:
        _load_dotenv()
        self.app_name = os.getenv("APP_NAME", "Legal Factory AI")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
