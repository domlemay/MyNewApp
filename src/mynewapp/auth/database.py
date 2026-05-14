from __future__ import annotations

import base64
import os
from pathlib import Path

import keyring
from cryptography.fernet import Fernet
from platformdirs import user_data_dir
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from mynewapp.auth.models import Base

_APP = "mynewapp"
_KEY_NAME = "db_encryption_key"


def _get_or_create_key() -> bytes:
    stored = keyring.get_password(_APP, _KEY_NAME)
    if stored:
        return base64.urlsafe_b64decode(stored.encode())
    key = Fernet.generate_key()
    keyring.set_password(_APP, _KEY_NAME, base64.urlsafe_b64encode(key).decode())
    return key


class Database:
    _instance: "Database | None" = None

    def __new__(cls) -> "Database":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return
        data_dir = Path(user_data_dir(_APP, appauthor=False))
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = data_dir / "mynewapp.db"
        self._engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self._engine)
        self._SessionLocal = sessionmaker(bind=self._engine)
        self._fernet = Fernet(_get_or_create_key())
        self._initialized = True

    def session(self) -> Session:
        return self._SessionLocal()

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, token: str) -> str:
        return self._fernet.decrypt(token.encode()).decode()
