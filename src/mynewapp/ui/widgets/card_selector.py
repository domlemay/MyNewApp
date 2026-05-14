from __future__ import annotations

from PyQt6.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt6.QtGui import QCursor, QFont
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget


class CardOption:
    def __init__(
        self,
        key: str,
        label: str,
        description: str = "",
        icon: str = "",
        detail_key: str = "",
    ) -> None:
        self.key = key
        self.label = label
        self.description = description
        self.icon = icon
        self.detail_key = detail_key or key


class CardSelector(QWidget):
    """Grid of selectable cards — single or multi-select. Emits hovered_key on hover."""

    selection_changed = pyqtSignal(list)
    hovered = pyqtSignal(str)   # detail_key of hovered card (or "" on leave)

    def __init__(
        self,
        options: list[CardOption],
        multi: bool = False,
        columns: int = 3,
        compact: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._options = options
        self._multi = multi
        self._columns = columns
        self._compact = compact
        self._selected: set[str] = set()
        self._cards: dict[str, QFrame] = {}
        self._disabled: set[str] = set()
        self._build()

    def _build(self) -> None:
        # Clear existing
        existing = self.layout()
        if existing is not None:
            while existing.count():
                item = existing.takeAt(0)
                if item is not None and item.widget() is not None:
                    item.widget().deleteLater()  # type: ignore[union-attr]
            QWidget().setLayout(existing)

        grid = QGridLayout(self)
        grid.setSpacing(8)
        grid.setContentsMargins(0, 0, 0, 0)
        self._cards.clear()

        for i, opt in enumerate(self._options):
            card = self._make_card(opt)
            self._cards[opt.key] = card
            grid.addWidget(card, i // self._columns, i % self._columns)

    def _make_card(self, opt: CardOption) -> QFrame:
        h = 72 if self._compact else 88
        w = 170 if self._compact else 190

        card = QFrame()
        card.setObjectName("card")
        card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        card.setFixedSize(w, h)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(2)

        if opt.icon:
            icon_lbl = QLabel(opt.icon)
            icon_lbl.setFont(QFont("Segoe UI Emoji", 16 if not self._compact else 14))
            layout.addWidget(icon_lbl)

        title = QLabel(opt.label)
        title.setFont(QFont("Segoe UI", 11 if not self._compact else 10, QFont.Weight.Bold))
        title.setObjectName("cardTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        if opt.description and not self._compact:
            desc = QLabel(opt.description)
            desc.setFont(QFont("Segoe UI", 9))
            desc.setObjectName("cardDesc")
            desc.setWordWrap(True)
            layout.addWidget(desc)

        # Hover and click via event filter
        card.installEventFilter(self)
        card._opt_key = opt.key  # type: ignore[attr-defined]
        card._detail_key = opt.detail_key  # type: ignore[attr-defined]
        self._apply_card_style(card, False, False)
        return card

    def eventFilter(self, obj: QObject | None, event: QEvent | None) -> bool:  # noqa: N802
        if isinstance(obj, QFrame) and hasattr(obj, "_opt_key") and event is not None:
            key = obj._opt_key
            detail = obj._detail_key  # type: ignore[attr-defined]
            if event.type() == QEvent.Type.Enter:
                if key not in self._disabled:
                    self._apply_card_style(obj, key in self._selected, True)
                self.hovered.emit(detail)
            elif event.type() == QEvent.Type.Leave:
                self._apply_card_style(obj, key in self._selected, False)
            elif event.type() == QEvent.Type.MouseButtonPress:
                if key not in self._disabled:
                    self._toggle(key)
                return True
        return super().eventFilter(obj, event)

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
            self._apply_card_style(card, key in self._selected, False)

    def _apply_card_style(self, card: QFrame, selected: bool, hovered: bool) -> None:
        key = getattr(card, "_opt_key", "")
        disabled = key in self._disabled
        if disabled:
            card.setStyleSheet(
                "QFrame { background: #0d1117; border: 1px solid #21262d; border-radius: 8px; opacity: 0.5; }"
                "QLabel#cardTitle { color: #484f58; }"
                "QLabel#cardDesc { color: #30363d; }"
            )
        elif selected:
            card.setStyleSheet(
                "QFrame { background: #0d419d; border: 2px solid #58a6ff; border-radius: 8px; }"
                "QLabel#cardTitle { color: #e6edf3; }"
                "QLabel#cardDesc { color: #a5c8ff; }"
            )
        elif hovered:
            card.setStyleSheet(
                "QFrame { background: #1c2128; border: 1px solid #58a6ff; border-radius: 8px; }"
                "QLabel#cardTitle { color: #e6edf3; }"
                "QLabel#cardDesc { color: #8b949e; }"
            )
        else:
            card.setStyleSheet(
                "QFrame { background: #161b22; border: 1px solid #30363d; border-radius: 8px; }"
                "QLabel#cardTitle { color: #c9d1d9; }"
                "QLabel#cardDesc { color: #8b949e; }"
            )

    def set_disabled_keys(self, keys: set[str]) -> None:
        self._disabled = keys
        self._refresh_styles()

    def get_selected(self) -> list[str]:
        return list(self._selected)

    def set_selected(self, keys: list[str]) -> None:
        self._selected = set(keys)
        self._refresh_styles()

    def set_options(self, options: list[CardOption]) -> None:
        self._options = options
        self._build()
