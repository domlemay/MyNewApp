from __future__ import annotations

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QFont, QCursor


class CardOption:
    def __init__(self, key: str, label: str, description: str = "", icon: str = "") -> None:
        self.key = key
        self.label = label
        self.description = description
        self.icon = icon


class CardSelector(QWidget):
    """Grid of selectable cards — single or multi-select."""

    selection_changed = pyqtSignal(list)

    def __init__(
        self,
        options: list[CardOption],
        multi: bool = False,
        columns: int = 3,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._options = options
        self._multi = multi
        self._columns = columns
        self._selected: set[str] = set()
        self._cards: dict[str, QFrame] = {}
        self._build()

    def _build(self) -> None:
        grid = QGridLayout(self)
        grid.setSpacing(12)
        grid.setContentsMargins(0, 0, 0, 0)

        for i, opt in enumerate(self._options):
            card = self._make_card(opt)
            self._cards[opt.key] = card
            grid.addWidget(card, i // self._columns, i % self._columns)

    def _make_card(self, opt: CardOption) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        card.setFixedSize(200, 90)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)

        if opt.icon:
            icon_lbl = QLabel(opt.icon)
            icon_lbl.setFont(QFont("Segoe UI Emoji", 18))
            layout.addWidget(icon_lbl)

        title = QLabel(opt.label)
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.SemiBold))
        title.setObjectName("cardTitle")
        layout.addWidget(title)

        if opt.description:
            desc = QLabel(opt.description)
            desc.setFont(QFont("Segoe UI", 10))
            desc.setObjectName("cardDesc")
            desc.setWordWrap(True)
            layout.addWidget(desc)

        card.mousePressEvent = lambda _e, k=opt.key: self._toggle(k)
        self._apply_card_style(card, False)
        return card

    def _toggle(self, key: str) -> None:
        if not self._multi:
            self._selected.clear()
        if key in self._selected:
            self._selected.discard(key)
        else:
            self._selected.add(key)
        self._refresh_styles()
        self.selection_changed.emit(list(self._selected))

    def _refresh_styles(self) -> None:
        for key, card in self._cards.items():
            self._apply_card_style(card, key in self._selected)

    def _apply_card_style(self, card: QFrame, selected: bool) -> None:
        if selected:
            card.setStyleSheet(
                "QFrame { background: #0d419d; border: 2px solid #58a6ff; border-radius: 8px; }"
                "QLabel#cardTitle { color: #e6edf3; }"
                "QLabel#cardDesc { color: #8b949e; }"
            )
        else:
            card.setStyleSheet(
                "QFrame { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }"
                "QFrame:hover { border-color: #58a6ff; }"
                "QLabel#cardTitle { color: #c9d1d9; }"
                "QLabel#cardDesc { color: #8b949e; }"
            )

    def get_selected(self) -> list[str]:
        return list(self._selected)

    def set_selected(self, keys: list[str]) -> None:
        self._selected = set(keys)
        self._refresh_styles()
