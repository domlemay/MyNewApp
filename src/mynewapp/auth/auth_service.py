from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import bcrypt
from loguru import logger
from sqlalchemy import select

from mynewapp.auth.database import Database
from mynewapp.auth.models import User


class AuthService:
    def __init__(self) -> None:
        self._db = Database()
        self._current_user: User | None = None

    @property
    def current_user(self) -> User | None:
        return self._current_user

    @property
    def is_logged_in(self) -> bool:
        return self._current_user is not None

    # ─── Email / Password ────────────────────────────────────────────────────

    def register(self, email: str, password: str, display_name: str = "") -> User:
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User(
            email=email.lower().strip(),
            password_hash=hashed,
            display_name=display_name or email.split("@")[0],
            provider="email",
        )
        with self._db.session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"Registered user: {email}")
        self._current_user = user
        return user

    def login(self, email: str, password: str) -> User | None:
        with self._db.session() as session:
            stmt = select(User).where(User.email == email.lower().strip())
            user = session.scalar(stmt)
            if user is None or user.password_hash is None:
                return None
            if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
                return None
            user.last_login = datetime.utcnow()
            session.commit()
            session.refresh(user)
            self._current_user = user
            logger.info(f"Login: {email}")
            return user

    # ─── OAuth / GitHub ───────────────────────────────────────────────────────

    def login_or_create_oauth(
        self,
        provider: str,
        provider_id: str,
        email: str,
        display_name: str,
        avatar_url: str = "",
        access_token: str = "",
    ) -> User:
        with self._db.session() as session:
            stmt = select(User).where(User.provider == provider, User.provider_id == provider_id)
            user = session.scalar(stmt)
            if user is None:
                stmt2 = select(User).where(User.email == email.lower())
                user = session.scalar(stmt2)
            if user is None:
                user = User(
                    email=email.lower(),
                    provider=provider,
                    provider_id=provider_id,
                    display_name=display_name,
                    avatar_url=avatar_url,
                )
                session.add(user)
            else:
                user.provider = provider
                user.provider_id = provider_id
                user.display_name = display_name or user.display_name
                user.avatar_url = avatar_url or user.avatar_url

            if access_token and provider == "github":
                user.github_token_enc = self._db.encrypt(access_token)

            user.last_login = datetime.utcnow()
            session.commit()
            session.refresh(user)
            self._current_user = user
            return user

    def get_github_token(self) -> str | None:
        if not self._current_user or not self._current_user.github_token_enc:
            return None
        try:
            return self._db.decrypt(self._current_user.github_token_enc)
        except Exception:
            return None

    def save_github_token(self, token: str) -> None:
        if not self._current_user:
            return
        with self._db.session() as session:
            stmt = select(User).where(User.id == self._current_user.id)
            user = session.scalar(stmt)
            if user:
                user.github_token_enc = self._db.encrypt(token)
                session.commit()

    def logout(self) -> None:
        self._current_user = None

    def guest_login(self) -> None:
        self._current_user = User(
            email="guest@local",
            display_name="Guest",
            provider="guest",
        )

    # ─── User Preferences ────────────────────────────────────────────────────

    def get_user_pref(self, user: User, key: str, default: Any = None) -> Any:
        try:
            prefs: dict[str, Any] = json.loads(user.prefs or "{}")
        except (json.JSONDecodeError, TypeError):
            prefs = {}
        return prefs.get(key, default)

    def set_user_pref(self, user: User, key: str, value: Any) -> None:
        try:
            prefs: dict[str, Any] = json.loads(user.prefs or "{}")
        except (json.JSONDecodeError, TypeError):
            prefs = {}
        prefs[key] = value
        serialized = json.dumps(prefs)
        user.prefs = serialized
        if not getattr(user, "id", None):
            return
        with self._db.session() as session:
            db_user = session.scalar(select(User).where(User.id == user.id))
            if db_user:
                db_user.prefs = serialized
                session.commit()

    def change_password(self, user: User, new_password: str) -> None:
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        user.password_hash = hashed
        if not getattr(user, "id", None):
            return
        with self._db.session() as session:
            db_user = session.scalar(select(User).where(User.id == user.id))
            if db_user:
                db_user.password_hash = hashed
                session.commit()
        logger.info(f"Password changed for user: {user.email}")
