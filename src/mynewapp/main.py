from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from loguru import logger

from mynewapp.ui.main_window import MainWindow


def main() -> None:
    logger.remove()
    logger.add(sys.stderr, level="INFO", colorize=True)
    logger.add("logs/mynewapp.log", rotation="10 MB", retention="7 days", level="DEBUG")

    app = QApplication(sys.argv)
    app.setApplicationName("MyNewApp")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("domlemay")
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
