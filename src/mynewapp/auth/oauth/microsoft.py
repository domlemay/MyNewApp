from __future__ import annotations

import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import msal
from loguru import logger

_CLIENT_ID = os.getenv("MICROSOFT_OAUTH_CLIENT_ID", "")
_AUTHORITY = "https://login.microsoftonline.com/common"
_SCOPES = ["User.Read", "openid", "profile", "email"]
_REDIRECT_PORT = 5175
_REDIRECT_URI = f"http://localhost:{_REDIRECT_PORT}"


class MicrosoftOAuth:
    """Microsoft OAuth via MSAL with local redirect server."""

    def __init__(self, client_id: str = "") -> None:
        self._client_id = client_id or _CLIENT_ID
        self._token: str | None = None
        self._error: str | None = None
        self._code: str | None = None

    def has_client_id(self) -> bool:
        return bool(self._client_id)

    def authenticate(self) -> dict:
        if not self._client_id:
            raise RuntimeError(
                "Microsoft OAuth client_id not configured. "
                "Set MICROSOFT_OAUTH_CLIENT_ID in your .env file."
            )
        app = msal.PublicClientApplication(self._client_id, authority=_AUTHORITY)
        flow = app.initiate_auth_code_flow(_SCOPES, redirect_uri=_REDIRECT_URI)
        webbrowser.open(flow["auth_uri"])

        code = self._wait_for_code()
        if not code:
            raise RuntimeError(self._error or "Microsoft OAuth failed")

        result = app.acquire_token_by_auth_code_flow(flow, {"code": code})
        if "error" in result:
            raise RuntimeError(result.get("error_description", result["error"]))

        account = result.get("id_token_claims", {})
        return {
            "access_token": result.get("access_token", ""),
            "email": account.get("preferred_username", account.get("email", "")),
            "name": account.get("name", ""),
            "id": account.get("oid", ""),
        }

    def _wait_for_code(self, timeout: int = 120) -> str | None:
        self._code = None
        self._error = None
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                params = parse_qs(urlparse(self.path).query)
                if "code" in params:
                    outer._code = params["code"][0]
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b"<h2>Authenticated! You can close this tab.</h2>")
                else:
                    outer._error = params.get("error_description", ["Unknown error"])[0]
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"<h2>Authentication failed. Please retry.</h2>")

            def log_message(self, *args: object) -> None:
                pass

        server = HTTPServer(("localhost", _REDIRECT_PORT), Handler)
        server.timeout = timeout
        server.handle_request()
        server.server_close()
        return self._code
