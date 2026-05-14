from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mynewapp.core import StateManager
from mynewapp.i18n import tr

from ._base import BaseStep

# (field_name, title_key, desc_key, applicable_platforms)
# applicable_platforms = [] means shown for all platforms
_SEC_GROUPS: list[tuple[str, str, list[tuple[str, str, str, list[str]]]]] = [
    ("sec_group_web", "web", [
        ("cors",               "sec_cors",               "sec_cors_desc",               ["web_spa", "web_ssr", "web_api", "web_fullstack"]),
        ("security_headers",   "sec_security_headers",   "sec_security_headers_desc",   ["web_spa", "web_ssr", "web_api", "web_fullstack"]),
        ("rate_limiting",      "sec_rate_limiting",      "sec_rate_limiting_desc",      ["web_api", "web_fullstack"]),
        ("csrf_protection",    "sec_csrf_protection",    "sec_csrf_protection_desc",    ["web_spa", "web_ssr", "web_fullstack"]),
        ("xss_protection",     "sec_xss_protection",     "sec_xss_protection_desc",     ["web_spa", "web_ssr", "web_fullstack"]),
        ("jwt_secure",         "sec_jwt_secure",         "sec_jwt_secure_desc",         ["web_api", "web_fullstack"]),
    ]),
    ("sec_group_validation", "validation", [
        ("strict_validation",          "sec_strict_validation",          "sec_strict_validation_desc",          []),
        ("acid_transactions",          "sec_acid_transactions",          "sec_acid_transactions_desc",          []),
        ("sql_injection_protection",   "sec_sql_injection_protection",   "sec_sql_injection_protection_desc",   []),
        ("encrypt_sensitive_fields",   "sec_encrypt_sensitive_fields",   "sec_encrypt_sensitive_fields_desc",   []),
        ("sanitize_output",            "sec_sanitize_output",            "sec_sanitize_output_desc",            []),
    ]),
    ("sec_group_access", "access", [
        ("rbac",            "sec_rbac",            "sec_rbac_desc",            ["web_api", "web_fullstack"]),
        ("least_privilege", "sec_least_privilege", "sec_least_privilege_desc", []),
        ("token_rotation",  "sec_token_rotation",  "sec_token_rotation_desc",  ["web_api", "web_fullstack"]),
    ]),
    ("sec_group_infra", "infra", [
        ("env_secrets_only",     "sec_env_secrets_only",     "sec_env_secrets_only_desc",     []),
        ("audit_log",            "sec_audit_log",            "sec_audit_log_desc",            []),
        ("docker_non_root",      "sec_docker_non_root",      "sec_docker_non_root_desc",      ["web_spa", "web_ssr", "web_api", "web_fullstack"]),
        ("dependency_scanning",  "sec_dependency_scanning",  "sec_dependency_scanning_desc",  []),
        ("https_enforced",       "sec_https_enforced",       "sec_https_enforced_desc",       ["web_spa", "web_ssr", "web_api", "web_fullstack"]),
    ]),
    ("sec_group_mobile", "mobile", [
        ("certificate_pinning", "sec_certificate_pinning", "sec_certificate_pinning_desc", ["mobile_crossplatform", "mobile_native"]),
        ("secure_storage",      "sec_secure_storage",      "sec_secure_storage_desc",      ["mobile_crossplatform", "mobile_native"]),
        ("biometrics",          "sec_biometrics",          "sec_biometrics_desc",          ["mobile_crossplatform", "mobile_native"]),
    ]),
]

# Fields that are ON by default
_DEFAULTS_ON: set[str] = {"strict_validation", "sql_injection_protection", "env_secrets_only"}


def _is_applicable(platforms: list[str], item_platforms: list[str]) -> bool:
    if not item_platforms:
        return True
    return any(p in item_platforms for p in platforms)


class StepSecurity(BaseStep):
    def __init__(self, state: StateManager) -> None:
        self._checkboxes: dict[str, QCheckBox] = {}
        self._group_boxes: dict[str, QGroupBox] = {}
        super().__init__(state, "step_security", "sub_security")
        state.config_changed.connect(self._on_config_changed)

    def _build_content(self) -> None:
        main = QHBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(16)

        # Left: scrollable checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 6px; background: #161b22; }
            QScrollBar::handle:vertical { background: #30363d; border-radius: 3px; }
        """)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        col = QVBoxLayout(container)
        col.setContentsMargins(0, 0, 8, 0)
        col.setSpacing(10)

        for group_key, _gid, items in _SEC_GROUPS:
            box = QGroupBox(tr(group_key))
            box.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            box.setStyleSheet("""
                QGroupBox {
                    color: #8b949e;
                    border: 1px solid #21262d;
                    border-radius: 8px;
                    margin-top: 8px;
                    padding: 8px 12px 8px 12px;
                    background: #0d1117;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 6px;
                    color: #8b949e;
                }
            """)
            box_layout = QVBoxLayout(box)
            box_layout.setSpacing(4)

            for field, title_key, _desc_key, _platforms in items:
                cb = QCheckBox(tr(title_key))
                cb.setFont(QFont("Segoe UI", 10))
                is_default = field in _DEFAULTS_ON
                cb.setChecked(is_default)
                if is_default:
                    cb.setStyleSheet("color: #3fb950; font-weight: 600;")
                else:
                    cb.setStyleSheet("color: #c9d1d9;")
                cb.stateChanged.connect(self._make_toggle(field, cb))
                self._checkboxes[field] = cb
                box_layout.addWidget(cb)

            self._group_boxes[group_key] = box
            col.addWidget(box)

        col.addStretch()
        scroll.setWidget(container)
        main.addWidget(scroll, stretch=1)

        # Right: hint panel
        main.addWidget(self._build_hint_panel(), stretch=0)

        container_w = QWidget()
        container_w.setLayout(main)
        self._content.addWidget(container_w, stretch=1)

        # Apply initial defaults to state
        self._sync_to_state()

    def _build_hint_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(260)
        panel.setStyleSheet("""
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel(tr("sec_hint_title"))
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title.setStyleSheet("color: #e6edf3; background: transparent; border: none;")
        layout.addWidget(title)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #30363d; border: none;")
        layout.addWidget(sep)

        body = QLabel(tr("sec_hint_body"))
        body.setFont(QFont("Segoe UI", 9))
        body.setStyleSheet("color: #8b949e; background: transparent; border: none;")
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(body)

        layout.addStretch()

        # Legend
        legend_on = QLabel("● " + tr("sec_on_by_default"))
        legend_on.setFont(QFont("Segoe UI", 9))
        legend_on.setStyleSheet("color: #3fb950; background: transparent; border: none;")
        legend_on.setWordWrap(True)
        layout.addWidget(legend_on)

        return panel

    def _make_toggle(self, field: str, cb: QCheckBox) -> Callable[[int], None]:
        def handler(_state: int) -> None:
            if cb.isChecked():
                if field in _DEFAULTS_ON:
                    cb.setStyleSheet("color: #3fb950; font-weight: 600;")
                else:
                    cb.setStyleSheet("color: #58a6ff; font-weight: 600;")
            else:
                cb.setStyleSheet("color: #6e7681;")
            self._sync_to_state()
        return handler

    def _sync_to_state(self) -> None:
        security_data = {field: cb.isChecked() for field, cb in self._checkboxes.items()}
        self._state.update_config(security=security_data)

    def _on_config_changed(self, config: object) -> None:
        platforms: list[str] = list(getattr(config, "platforms", []) or [])
        # Show/hide group boxes and items based on platform
        for group_key, _gid, items in _SEC_GROUPS:
            box = self._group_boxes.get(group_key)
            if box is None:
                continue
            any_visible = False
            for field, _tk, _dk, item_platforms in items:
                cb = self._checkboxes.get(field)
                if cb is None:
                    continue
                applicable = _is_applicable(platforms, item_platforms)
                cb.setVisible(applicable)
                if applicable:
                    any_visible = True
            box.setVisible(any_visible)
