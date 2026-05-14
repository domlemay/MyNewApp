from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QTextEdit, QTabWidget, QWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from mynewapp.i18n import tr


class DetailPanel(QFrame):
    """Right-side panel showing details for the hovered/selected card."""

    def __init__(self, width: int = 260, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("detailPanel")
        self.setFixedWidth(width)
        self._build()
        self._apply_style()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self._icon = QLabel("")
        self._icon.setFont(QFont("Segoe UI Emoji", 28))
        self._icon.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self._icon)

        self._title = QLabel("")
        self._title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._title.setObjectName("detailTitle")
        self._title.setWordWrap(True)
        layout.addWidget(self._title)

        self._desc = QLabel("")
        self._desc.setObjectName("detailDesc")
        self._desc.setWordWrap(True)
        self._desc.setFont(QFont("Segoe UI", 11))
        layout.addWidget(self._desc)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #30363d;")
        layout.addWidget(sep)

        self._tree_label = QLabel(tr("arch_file_tree"))
        self._tree_label.setObjectName("detailSub")
        layout.addWidget(self._tree_label)

        self._tree = QTextEdit()
        self._tree.setReadOnly(True)
        self._tree.setFont(QFont("Cascadia Code", 9))
        self._tree.setObjectName("detailTree")
        self._tree.setMaximumHeight(160)
        layout.addWidget(self._tree)

        self._examples_label = QLabel("")
        self._examples_label.setObjectName("detailSub")
        layout.addWidget(self._examples_label)

        layout.addStretch()

    def show_empty(self) -> None:
        hint = QLabel("← Hover a card to see details")
        self._title.setText("")
        self._icon.setText("")
        self._desc.setText("Hover over a card to see details here.")
        self._tree.clear()
        self._examples_label.setText("")
        self._tree_label.setVisible(False)

    def update(  # type: ignore[override]
        self,
        icon: str = "",
        title: str = "",
        description: str = "",
        file_tree: str = "",
        examples: str = "",
        tree_label: str = "",
    ) -> None:
        self._icon.setText(icon)
        self._title.setText(title)
        self._desc.setText(description)
        self._tree.setPlainText(file_tree)
        self._tree_label.setText(tree_label or tr("arch_file_tree"))
        self._tree_label.setVisible(bool(file_tree))
        self._tree.setVisible(bool(file_tree))
        if examples:
            self._examples_label.setText(f"✦ {examples}")
            self._examples_label.setVisible(True)
        else:
            self._examples_label.setVisible(False)

    def _apply_style(self) -> None:
        self.setStyleSheet("""
            #detailPanel {
                background: #161b22;
                border-left: 1px solid #30363d;
                border-radius: 0px;
            }
            #detailTitle { color: #e6edf3; }
            #detailDesc { color: #8b949e; }
            #detailSub { color: #58a6ff; font-size: 10px; font-weight: 700; text-transform: uppercase; }
            #detailTree {
                background: #0d1117;
                color: #c9d1d9;
                border: 1px solid #21262d;
                border-radius: 4px;
            }
            QLabel#examples { color: #3fb950; font-size: 11px; }
        """)
