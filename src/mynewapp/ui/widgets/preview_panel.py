from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from mynewapp.models import ProjectConfig


class PreviewPanel(QFrame):
    """Live preview of the project structure."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("previewPanel")
        self.setFixedWidth(280)
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Preview")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        title.setObjectName("previewTitle")
        layout.addWidget(title)

        self._tree = QTextEdit()
        self._tree.setReadOnly(True)
        self._tree.setObjectName("previewTree")
        self._tree.setFont(QFont("Cascadia Code", 10))
        layout.addWidget(self._tree, stretch=1)

        self.setStyleSheet("""
            #previewPanel {
                background: #161b22;
                border-left: 1px solid #30363d;
            }
            #previewTitle { color: #8b949e; }
            #previewTree {
                background: #0d1117;
                color: #c9d1d9;
                border: none;
            }
        """)

    def update_preview(self, config: ProjectConfig) -> None:
        name = config.name or "my-project"
        lines = [
            f"{name}/",
            "├── src/",
            f"│   └── {name.replace('-','_')}/",
            "│       ├── __init__.py",
            "│       └── main.py",
            "├── tests/",
            "│   ├── unit/",
            "│   └── integration/",
            "├── docs/",
            "├── .github/",
            "│   └── workflows/",
            "│       └── ci.yml",
            "├── .env.example",
            "├── .gitignore",
            "├── pyproject.toml",
            "├── README.md",
            "└── CONTRIBUTING.md",
        ]
        self._tree.setPlainText("\n".join(lines))
