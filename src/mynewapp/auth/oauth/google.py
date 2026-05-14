from __future__ import annotations

import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import requests

_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
_PORT = 8482
_REDIRECT_URI = f"http://localhost:{_PORT}"

_SUCCESS_HTML = b"""<!DOCTYPE html><html><body style="font-family:sans-serif;text-align:center;padding:60px;background:#0d1117;color:#e6edf3;">
<h2>&#10003; Connexion Google r&#233;ussie</h2>
<p style="color:#8b949e;">Vous pouvez fermer cet onglet et revenir sur MyNewApp.</p>
</body></html>"""


class GoogleOAuth:
    def has_credentials(self) -> bool:
        return bool(_CLIENT_ID and _CLIENT_SECRET)

    def authenticate(self) -> dict[str, str]:
        params = {
            "client_id": _CLIENT_ID,
            "redirect_uri": _REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account",
        }
        auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

        code_holder: list[str] = []
        error_holder: list[str] = []

        class _Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                qs = parse_qs(urlparse(self.path).query)
                if "code" in qs:
                    code_holder.append(qs["code"][0])
                elif "error" in qs:
                    error_holder.append(qs["error"][0])
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
            raise RuntimeError(f"Google auth error: {error_holder[0]}")
        if not code_holder:
            raise TimeoutError("Google OAuth timed out waiting for response.")

        token_resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code_holder[0],
                "client_id": _CLIENT_ID,
                "client_secret": _CLIENT_SECRET,
                "redirect_uri": _REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=15,
        )
        token_resp.raise_for_status()
        access_token: str = token_resp.json()["access_token"]

        user_resp = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )
        user_resp.raise_for_status()
        data: dict[str, str] = user_resp.json()
        return {
            "id": str(data.get("id", "")),
            "email": str(data.get("email", "")),
            "name": str(data.get("name", "")),
            "picture": str(data.get("picture", "")),
            "access_token": access_token,
        }
