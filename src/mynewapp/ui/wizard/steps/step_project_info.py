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
from mynewapp.i18n import get_translator, tr

from ._base import BaseStep


class StepProjectInfo(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._name_lbl: QLabel | None = None
        self._desc_lbl: QLabel | None = None
        self._dir_lbl: QLabel | None = None
        self._browse_btn: QPushButton | None = None
        super().__init__(state, "step_project_info", "sub_project_info")
        get_translator().language_changed.connect(self._on_language_changed)

    def _build_content(self) -> None:
        # Project Name
        self._name_lbl = self._add_field_label(tr("project_name"))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText(tr("project_name_ph"))
        self._name_input.setObjectName("fieldInput")
        self._content.addWidget(self._name_input)
        self._content.addSpacing(8)

        # Description
        self._desc_lbl = self._add_field_label(tr("description"))
        self._desc_input = QLineEdit()
        self._desc_input.setPlaceholderText(tr("description_ph"))
        self._desc_input.setObjectName("fieldInput")
        self._content.addWidget(self._desc_input)
        self._content.addSpacing(8)

        # Output directory
        self._dir_lbl = self._add_field_label(tr("output_directory"))
        dir_row = QHBoxLayout()
        self._dir_input = QLineEdit(str(self._state.config.output_dir))
        self._dir_input.setObjectName("fieldInput")
        self._browse_btn = QPushButton(tr("browse"))
        self._browse_btn.setObjectName("secondaryBtn")
        self._browse_btn.setFixedWidth(100)
        self._browse_btn.clicked.connect(self._browse)
        dir_row.addWidget(self._dir_input)
        dir_row.addWidget(self._browse_btn)
        self._content.addLayout(dir_row)

        self._content.addStretch()

        self._name_input.textChanged.connect(
            lambda t: self._state.update_config(name=t)
        )
        self._desc_input.textChanged.connect(
            lambda t: self._state.update_config(description=t)
        )
        self._dir_input.textChanged.connect(
            lambda t: self._state.update_config(output_dir=Path(t))
        )
        self._state.config_changed.connect(self._on_config_changed)

    def _browse(self) -> None:
        d = QFileDialog.getExistingDirectory(self, tr("output_directory"))
        if d:
            self._dir_input.setText(d)

    def _on_config_changed(self, config: object) -> None:
        new_dir = str(getattr(config, "output_dir", ""))
        if new_dir and new_dir != self._dir_input.text():
            self._dir_input.blockSignals(True)
            self._dir_input.setText(new_dir)
            self._dir_input.blockSignals(False)

    def _add_field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        lbl.setObjectName("fieldLabel")
        self._content.addWidget(lbl)
        self._content.addSpacing(4)
        return lbl

    def _on_language_changed(self, _lang: str) -> None:
        if self._name_lbl:
            self._name_lbl.setText(tr("project_name"))
        if self._desc_lbl:
            self._desc_lbl.setText(tr("description"))
        if self._dir_lbl:
            self._dir_lbl.setText(tr("output_directory"))
        if self._browse_btn:
            self._browse_btn.setText(tr("browse"))
        if self._name_input:
            self._name_input.setPlaceholderText(tr("project_name_ph"))
        if self._desc_input:
            self._desc_input.setPlaceholderText(tr("description_ph"))
