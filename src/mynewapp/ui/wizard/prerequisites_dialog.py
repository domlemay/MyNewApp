from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mynewapp.models import ProjectConfig
from mynewapp.services.prerequisites_service import PrerequisitesService, ToolStatus


class PrerequisitesDialog(QDialog):
    """Show tool installation status before project generation."""

    def __init__(self, config: ProjectConfig, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = PrerequisitesService()
        self._config = config
        self._statuses: list[ToolStatus] = []
        self.setWindowTitle("Vérification des prérequis")
        self.setMinimumWidth(600)
        self.setMinimumHeight(380)
        self.setStyleSheet("""
            QDialog { background: #0f1117; }
            QLabel { color: #c9d1d9; background: transparent; }
        """)
        self._build_ui()
        self._run_check()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(14)

        title = QLabel("🔍  Vérification des prérequis")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #e6edf3;")
        layout.addWidget(title)

        subtitle = QLabel(
            "Ces outils CLI sont nécessaires pour générer et installer les dépendances de votre projet."
        )
        subtitle.setFont(QFont("Segoe UI", 10))
        subtitle.setStyleSheet("color: #8b949e;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #21262d;")
        layout.addWidget(sep)

        # Column headers
        layout.addWidget(self._make_header_row())

        # Scrollable rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(260)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 6px; background: #161b22; }
            QScrollBar::handle:vertical { background: #30363d; border-radius: 3px; }
        """)
        self._rows_widget = QWidget()
        self._rows_widget.setStyleSheet("background: transparent;")
        self._rows_layout = QVBoxLayout(self._rows_widget)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(4)
        self._rows_layout.addStretch()
        scroll.setWidget(self._rows_widget)
        layout.addWidget(scroll)

        # Warning
        self._warn_lbl = QLabel("")
        self._warn_lbl.setStyleSheet(
            "color: #f0a500; background: #1a140a; border: 1px solid #6e4000; "
            "border-radius: 6px; padding: 10px;"
        )
        self._warn_lbl.setWordWrap(True)
        self._warn_lbl.setFont(QFont("Segoe UI", 10))
        self._warn_lbl.setVisible(False)
        layout.addWidget(self._warn_lbl)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._refresh_btn = QPushButton("↻  Revérifier")
        self._refresh_btn.setStyleSheet(self._secondary_style())
        self._refresh_btn.setFixedWidth(120)
        self._refresh_btn.clicked.connect(self._run_check)
        btn_row.addWidget(self._refresh_btn)

        btn_row.addStretch()

        self._cancel_btn = QPushButton("Annuler")
        self._cancel_btn.setStyleSheet(self._secondary_style())
        self._cancel_btn.setFixedWidth(100)
        self._cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self._cancel_btn)

        self._anyway_btn = QPushButton("⚠  Générer quand même")
        self._anyway_btn.setStyleSheet("""
            QPushButton {
                background: #2d1b00; color: #f0a500;
                border: 1px solid #6e4000; border-radius: 6px;
                padding: 8px 18px; font-size: 12px; font-weight: 700;
            }
            QPushButton:hover { background: #3d2500; }
        """)
        self._anyway_btn.setVisible(False)
        self._anyway_btn.clicked.connect(self.accept)
        btn_row.addWidget(self._anyway_btn)

        self._ok_btn = QPushButton("Générer le projet  →")
        self._ok_btn.setStyleSheet("""
            QPushButton {
                background: #238636; color: white;
                border: 1px solid #2ea043; border-radius: 6px;
                padding: 8px 20px; font-size: 12px; font-weight: 700;
            }
            QPushButton:hover { background: #2ea043; }
        """)
        self._ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(self._ok_btn)

        layout.addLayout(btn_row)

    def _run_check(self) -> None:
        self._statuses = self._service.check_for_config(self._config)
        self._rebuild_rows()
        has_critical = self._service.has_critical_missing(self._statuses)
        has_any_missing = any(not s.installed for s in self._statuses)

        if has_critical:
            self._warn_lbl.setText(
                "⚠  Des outils requis sont manquants. La génération des fichiers fonctionnera, "
                "mais l'installation automatique des dépendances échouera."
            )
            self._warn_lbl.setVisible(True)
            self._ok_btn.setVisible(False)
            self._anyway_btn.setVisible(True)
        elif has_any_missing:
            self._warn_lbl.setText(
                "ℹ  Des outils optionnels sont manquants. La génération fonctionnera normalement."
            )
            self._warn_lbl.setStyleSheet(
                "color: #8b949e; background: #161b22; border: 1px solid #30363d; "
                "border-radius: 6px; padding: 10px;"
            )
            self._warn_lbl.setVisible(True)
            self._ok_btn.setVisible(True)
            self._anyway_btn.setVisible(False)
        else:
            self._warn_lbl.setVisible(False)
            self._ok_btn.setVisible(True)
            self._anyway_btn.setVisible(False)

    def _rebuild_rows(self) -> None:
        while self._rows_layout.count() > 1:
            item = self._rows_layout.takeAt(0)
            w = item.widget() if item else None
            if w is not None:
                w.hide()
                w.deleteLater()

        for i, status in enumerate(self._statuses):
            row = self._make_tool_row(status)
            self._rows_layout.insertWidget(i, row)

    def _make_header_row(self) -> QWidget:
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 0, 12, 4)
        layout.setSpacing(0)

        for text, width in [("Outil", 240), ("Statut", 130), ("Version / Lien", 0)]:
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            lbl.setStyleSheet("color: #484f58;")
            if width:
                lbl.setFixedWidth(width)
            layout.addWidget(lbl)
        layout.addStretch()
        return row

    def _make_tool_row(self, status: ToolStatus) -> QWidget:
        row = QWidget()
        row.setStyleSheet(
            "background: #161b22; border: 1px solid #21262d; border-radius: 6px;"
        )
        layout = QHBoxLayout(row)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(0)

        badge = "●" if status.critical else "○"
        badge_color = "#f85149" if status.critical else "#6e7681"
        badge_lbl = QLabel(badge)
        badge_lbl.setStyleSheet(f"color: {badge_color}; font-size: 10px;")
        badge_lbl.setFixedWidth(18)
        layout.addWidget(badge_lbl)

        name_col = QWidget()
        name_col.setStyleSheet("background: transparent;")
        name_layout = QVBoxLayout(name_col)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(0)
        name_lbl = QLabel(status.label)
        name_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        name_lbl.setStyleSheet("color: #c9d1d9;")
        kind_lbl = QLabel("requis" if status.critical else "optionnel")
        kind_lbl.setFont(QFont("Segoe UI", 8))
        kind_lbl.setStyleSheet("color: #484f58;")
        name_layout.addWidget(name_lbl)
        name_layout.addWidget(kind_lbl)
        name_col.setFixedWidth(222)
        layout.addWidget(name_col)

        status_lbl = QLabel("✅  Installé" if status.installed else "❌  Manquant")
        status_lbl.setFont(QFont("Segoe UI", 10))
        status_lbl.setStyleSheet(
            "color: #3fb950;" if status.installed else "color: #f85149;"
        )
        status_lbl.setFixedWidth(130)
        layout.addWidget(status_lbl)

        if status.installed and status.version:
            ver_lbl = QLabel(status.version[:60])
            ver_lbl.setFont(QFont("Cascadia Code", 9))
            ver_lbl.setStyleSheet("color: #6e7681;")
            layout.addWidget(ver_lbl)
        elif not status.installed and status.install_url:
            link_lbl = QLabel(
                f'<a href="{status.install_url}" style="color: #58a6ff;">↗ Installer</a>'
            )
            link_lbl.setFont(QFont("Segoe UI", 10))
            link_lbl.setOpenExternalLinks(True)
            link_lbl.setTextFormat(Qt.TextFormat.RichText)
            layout.addWidget(link_lbl)

        layout.addStretch()
        return row

    @staticmethod
    def _secondary_style() -> str:
        return """
            QPushButton {
                background: #21262d; color: #c9d1d9;
                border: 1px solid #30363d; border-radius: 6px;
                padding: 8px 14px; font-size: 12px;
            }
            QPushButton:hover { background: #30363d; }
        """
