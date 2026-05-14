from __future__ import annotations

import os
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import jwt
import requests

_CLIENT_ID = os.getenv("APPLE_SERVICE_ID", "")        # e.g. com.yourapp.signin
_TEAM_ID = os.getenv("APPLE_TEAM_ID", "")              # e.g. ABCD123456
_KEY_ID = os.getenv("APPLE_KEY_ID", "")                # Key ID from developer.apple.com
_PRIVATE_KEY = os.getenv("APPLE_PRIVATE_KEY", "")      # PEM content of the .p8 key file
_PORT = 8483
_REDIRECT_URI = f"http://localhost:{_PORT}"

_SUCCESS_HTML = b"""<!DOCTYPE html><html><body style="font-family:sans-serif;text-align:center;padding:60px;background:#0d1117;color:#e6edf3;">
<h2>&#10003; Connexion Apple r&#233;ussie</h2>
<p style="color:#8b949e;">Vous pouvez fermer cet onglet et revenir sur MyNewApp.</p>
</body></html>"""


def _make_client_secret() -> str:
    now = int(time.time())
    payload = {
        "iss": _TEAM_ID,
        "iat": now,
        "exp": now + 180,
        "aud": "https://appleid.apple.com",
        "sub": _CLIENT_ID,
    }
    return jwt.encode(payload, _PRIVATE_KEY, algorithm="ES256", headers={"kid": _KEY_ID})


class AppleSignIn:
    def has_credentials(self) -> bool:
        return bool(_CLIENT_ID and _TEAM_ID and _KEY_ID and _PRIVATE_KEY)

    def authenticate(self) -> dict[str, str]:
        params = {
            "client_id": _CLIENT_ID,
            "redirect_uri": _REDIRECT_URI,
            "response_type": "code",
            "scope": "name email",
            "response_mode": "form_post",
        }
        auth_url = "https://appleid.apple.com/auth/authorize?" + urlencode(params)

        code_holder: list[str] = []
        error_holder: list[str] = []

        class _Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode()
                qs = parse_qs(body)
                if "code" in qs:
                    code_holder.append(qs["code"][0])
                elif "error" in qs:
                    error_holder.append(qs["error"][0])
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(_SUCCESS_HTML)

            def do_GET(self) -> None:  # noqa: N802
                # Handle edge case where Apple sends GET
                qs = parse_qs(urlparse(self.path).query)
                if "code" in qs:
                    code_holder.append(qs["code"][0])
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(_SUCCESS_HTML)

            def log_message(self, *_args: object) -> None:
                pass

        server = HTTPServer(("localhost", _PORT), _Handler)
        thread = threading.Thread(target=lambda: server.handle_request(), daemon=True)
        thread.start()

        webbrowser.open(auth_url)
        thread.join(timeout=180)
        server.server_close()

        if error_holder:
            raise RuntimeError(f"Apple auth error: {error_holder[0]}")
        if not code_holder:
            raise TimeoutError("Apple Sign In timed out waiting for response.")

        client_secret = _make_client_secret()
        token_resp = requests.post(
            "https://appleid.apple.com/auth/token",
            data={
                "client_id": _CLIENT_ID,
                "client_secret": client_secret,
                "code": code_holder[0],
                "grant_type": "authorization_code",
                "redirect_uri": _REDIRECT_URI,
            },
            timeout=15,
        )
        token_resp.raise_for_status()
        token_data: dict[str, str] = token_resp.json()

        id_token = token_data.get("id_token", "")
        claims: dict[str, object] = jwt.decode(id_token, options={"verify_signature": False})

        return {
            "id": str(claims.get("sub", "")),
            "email": str(claims.get("email", "")),
            "name": str(claims.get("name", "")),
            "picture": "",
            "access_token": token_data.get("access_token", ""),
        }
