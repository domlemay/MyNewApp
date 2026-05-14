from __future__ import annotations

import os
import time
import webbrowser
from collections.abc import Callable

import httpx
from loguru import logger

# Set GITHUB_OAUTH_CLIENT_ID in your .env to your GitHub OAuth App's client_id
# Create one at: github.com/settings/developers → OAuth Apps → New OAuth App
# Enable "Device Flow" on the app settings
_CLIENT_ID = os.getenv("GITHUB_OAUTH_CLIENT_ID", "")

_DEVICE_URL = "https://github.com/login/device/code"
_TOKEN_URL = "https://github.com/login/oauth/access_token"
_SCOPE = "repo workflow read:user user:email"


class GitHubDeviceFlow:
    """
    Implements GitHub's Device Flow for desktop apps.
    Docs: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#device-flow
    """

    def __init__(self, client_id: str = "") -> None:
        self._client_id = client_id or _CLIENT_ID

    def has_client_id(self) -> bool:
        return bool(self._client_id)

    def start(self) -> dict:
        """Step 1: request device code. Returns {device_code, user_code, verification_uri, interval}."""
        if not self._client_id:
            raise RuntimeError(
                "GitHub OAuth client_id not configured. "
                "Set GITHUB_OAUTH_CLIENT_ID in your .env file."
            )
        resp = httpx.post(
            _DEVICE_URL,
            data={"client_id": self._client_id, "scope": _SCOPE},
            headers={"Accept": "application/json"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        webbrowser.open(data["verification_uri"])
        return data

    def poll(
        self,
        device_code: str,
        interval: int = 5,
        on_waiting: Callable[[str], None] | None = None,
        timeout: int = 300,
    ) -> str:
        """Step 2: poll until token is granted. Returns access_token."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(interval)
            resp = httpx.post(
                _TOKEN_URL,
                data={
                    "client_id": self._client_id,
                    "device_code": device_code,
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                },
                headers={"Accept": "application/json"},
                timeout=15,
            )
            data = resp.json()
            error = data.get("error", "")
            if error == "authorization_pending":
                if on_waiting:
                    on_waiting("Waiting for authorization…")
                continue
            if error == "slow_down":
                interval += 5
                continue
            if error == "expired_token":
                raise RuntimeError("Device code expired. Please try again.")
            if error == "access_denied":
                raise RuntimeError("Access denied by user.")
            if "access_token" in data:
                logger.info("GitHub Device Flow: token obtained")
                return data["access_token"]
        raise TimeoutError("GitHub Device Flow timed out.")

    def get_user_info(self, token: str) -> dict:
        resp = httpx.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        user = resp.json()
        emails_resp = httpx.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        primary_email = user.get("email", "")
        if emails_resp.status_code == 200:
            for e in emails_resp.json():
                if e.get("primary"):
                    primary_email = e["email"]
                    break
        return {
            "login": user.get("login", ""),
            "email": primary_email,
            "name": user.get("name") or user.get("login", ""),
            "avatar_url": user.get("avatar_url", ""),
            "id": str(user.get("id", "")),
        }
