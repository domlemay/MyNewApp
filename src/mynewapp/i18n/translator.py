from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal

from mynewapp.i18n.locales import en, fr

_LOCALES: dict[str, dict[str, str]] = {"en": en.T, "fr": fr.T}


class Translator(QObject):
    language_changed = pyqtSignal(str)

    _instance: Translator | None = None

    def __new__(cls) -> Translator:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if "_initialized" in self.__dict__:
            return
        super().__init__()
        self._lang = "fr"
        self._initialized = True

    @property
    def lang(self) -> str:
        return self._lang

    def set_language(self, lang: str) -> None:
        if lang in _LOCALES and lang != self._lang:
            self._lang = lang
            self.language_changed.emit(lang)

    def tr(self, key: str, **kwargs: object) -> str:
        text = _LOCALES.get(self._lang, {}).get(key) or _LOCALES["en"].get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, IndexError):
                return text
        return text


_translator = Translator()


def tr(key: str, **kwargs: object) -> str:
    return _translator.tr(key, **kwargs)


def set_language(lang: str) -> None:
    _translator.set_language(lang)


def get_language() -> str:
    return _translator.lang


def get_translator() -> Translator:
    return _translator
