from __future__ import annotations

from pathlib import Path

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)

from mynewapp.core import StateManager

from ._base import BaseStep


class StepProjectInfo(BaseStep):
    def __init__(self, state: StateManager) -> None:
        super().__init__(state, "Project Information", "Name your project and choose where to save it.")

    def _build_content(self) -> None:
        # Project Name
        self._add_field_label("Project Name")
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("my-awesome-project")
        self._name_input.setObjectName("fieldInput")
        self._content.addWidget(self._name_input)

        # Description
        self._add_field_label("Description (optional)")
        self._desc_input = QLineEdit()
        self._desc_input.setPlaceholderText("A short description of your project")
        self._desc_input.setObjectName("fieldInput")
        self._content.addWidget(self._desc_input)

        # Output directory
        self._add_field_label("Output Directory")
        dir_row = QHBoxLayout()
        self._dir_input = QLineEdit(str(Path.home() / "Projects"))
        self._dir_input.setObjectName("fieldInput")
        browse_btn = QPushButton("Browse...")
        browse_btn.setObjectName("secondaryBtn")
        browse_btn.setFixedWidth(90)
        browse_btn.clicked.connect(self._browse)
        dir_row.addWidget(self._dir_input)
        dir_row.addWidget(browse_btn)
        self._content.addLayout(dir_row)

        self._content.addStretch()

        # Connect
        self._name_input.textChanged.connect(
            lambda t: self._state.update_config(name=t)
        )
        self._desc_input.textChanged.connect(
            lambda t: self._state.update_config(description=t)
        )
        self._dir_input.textChanged.connect(
            lambda t: self._state.update_config(output_dir=Path(t))
        )

    def _browse(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if d:
            self._dir_input.setText(d)

    def _add_field_label(self, text: str) -> None:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        lbl.setObjectName("fieldLabel")
        self._content.addWidget(lbl)
        self._content.addSpacing(4)
