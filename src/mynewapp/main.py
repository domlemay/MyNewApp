from __future__ import annotations

import sys

from loguru import logger
from PyQt6.QtWidgets import QApplication

from mynewapp.auth.auth_service import AuthService
from mynewapp.auth.models import User
from mynewapp.ui.auth.login_window import LoginWindow
from mynewapp.ui.main_window import MainWindow


def main() -> None:
    logger.remove()
    logger.add(sys.stderr, level="INFO", colorize=True)
    logger.add("logs/mynewapp.log", rotation="10 MB", retention="7 days", level="DEBUG")

    app = QApplication(sys.argv)
    app.setApplicationName("MyNewApp")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("domlemay")

    auth = AuthService()

    login = LoginWindow(auth)
    current_user: User | None = None

    def on_login(user: object) -> None:
        nonlocal current_user
        if isinstance(user, User):
            current_user = user
        login.accept()

    login.login_success.connect(on_login)
    if login.exec() != LoginWindow.DialogCode.Accepted or current_user is None:
        sys.exit(0)

    window = MainWindow(auth, current_user)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
