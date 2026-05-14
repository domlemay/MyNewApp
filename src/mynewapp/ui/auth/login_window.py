from __future__ import annotations

from PyQt6.QtCore import QSettings, QSize, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from mynewapp.auth.auth_service import AuthService
from mynewapp.auth.oauth.github_device import GitHubDeviceFlow
from mynewapp.auth.oauth.microsoft import MicrosoftOAuth
from mynewapp.i18n import tr


class _DeviceFlowWorker(QThread):
    code_ready = pyqtSignal(str, str)  # user_code, verification_uri
    token_ready = pyqtSignal(str)      # access_token
    error = pyqtSignal(str)

    def __init__(self, flow: GitHubDeviceFlow) -> None:
        super().__init__()
        self._flow = flow

    def run(self) -> None:
        try:
            data = self._flow.start()
            self.code_ready.emit(data["user_code"], data["verification_uri"])
            token = self._flow.poll(str(data["device_code"]), interval=int(str(data.get("interval", 5))))
            self.token_ready.emit(token)
        except Exception as e:
            self.error.emit(str(e))


class _MicrosoftWorker(QThread):
    done = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, oauth: MicrosoftOAuth) -> None:
        super().__init__()
        self._oauth = oauth

    def run(self) -> None:
        try:
            info = self._oauth.authenticate()
            self.done.emit(info)
        except Exception as e:
            self.error.emit(str(e))


_STYLE = """
QDialog { background: #0d1117; }
QFrame#card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
}
QLabel#title { color: #e6edf3; }
QLabel#subtitle { color: #8b949e; }
QLabel#fieldLabel { color: #8b949e; font-size: 11px; margin-top: 4px; }
QLabel#errorLabel { color: #f85149; font-size: 11px; }
QLabel#linkLabel { color: #58a6ff; font-size: 11px; }
QLineEdit#field {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    color: #e6edf3;
    padding: 9px 12px;
    font-size: 13px;
}
QLineEdit#field:focus { border-color: #58a6ff; }
QPushButton#primary {
    background: #238636;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px;
    font-size: 13px;
    font-weight: 700;
}
QPushButton#primary:hover { background: #2ea043; }
QPushButton#secondary {
    background: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 10px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#secondary:hover { background: #30363d; }
QPushButton#oauth {
    background: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 9px;
    font-size: 12px;
}
QPushButton#oauth:hover { background: #30363d; }
QPushButton#link {
    background: transparent;
    color: #58a6ff;
    border: none;
    font-size: 11px;
    text-decoration: underline;
}
QPushButton#skip {
    background: transparent;
    color: #484f58;
    border: none;
    font-size: 11px;
}
QPushButton#skip:hover { color: #8b949e; }
QLabel#codeBox {
    background: #0d1117;
    border: 2px solid #58a6ff;
    border-radius: 8px;
    color: #58a6ff;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 8px;
    padding: 12px 24px;
}
"""


class LoginWindow(QDialog):
    login_success = pyqtSignal(object)  # User

    def __init__(self, auth: AuthService) -> None:
        super().__init__()
        self._auth = auth
        self._gh_flow = GitHubDeviceFlow()
        self._ms_oauth = MicrosoftOAuth()
        self._worker: QThread | None = None
        self._mode = "login"
        self._settings = QSettings("MyNewApp", "mynewapp")
        self.setWindowTitle("MyNewApp")
        self.setFixedSize(QSize(440, 580))
        self.setModal(True)
        self.setStyleSheet(_STYLE)
        self._build()

    def _build(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(10)

        # Logo / title
        title = QLabel(tr("login_title"))
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        sub = QLabel(tr("login_subtitle"))
        sub.setObjectName("subtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(sub)

        card_layout.addSpacing(8)

        # OAuth buttons
        gh_btn = QPushButton(f"  {tr('github_login')}")
        gh_btn.setObjectName("oauth")
        gh_btn.clicked.connect(self._on_github)
        card_layout.addWidget(gh_btn)

        ms_btn = QPushButton(f"  {tr('microsoft_login')}")
        ms_btn.setObjectName("oauth")
        ms_btn.clicked.connect(self._on_microsoft)
        card_layout.addWidget(ms_btn)

        sep = QLabel(tr("or_continue_with"))
        sep.setObjectName("subtitle")
        sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(sep)

        # Stacked: login / register / device flow
        self._stack = QStackedWidget()
        self._stack.addWidget(self._build_login_form())
        self._stack.addWidget(self._build_register_form())
        self._stack.addWidget(self._build_device_flow_panel())
        card_layout.addWidget(self._stack, stretch=1)

        # Switch link
        switch_row = QHBoxLayout()
        self._switch_label = QLabel(tr("no_account"))
        self._switch_label.setObjectName("subtitle")
        self._switch_btn = QPushButton(tr("sign_up"))
        self._switch_btn.setObjectName("link")
        self._switch_btn.clicked.connect(self._toggle_mode)
        switch_row.addStretch()
        switch_row.addWidget(self._switch_label)
        switch_row.addWidget(self._switch_btn)
        switch_row.addStretch()
        card_layout.addLayout(switch_row)

        # Skip
        skip_btn = QPushButton(tr("skip_login"))
        skip_btn.setObjectName("skip")
        skip_btn.clicked.connect(self._on_skip)
        card_layout.addWidget(skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        outer.addWidget(card)

    def _build_login_form(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        layout.addWidget(self._field_label(tr("email")))
        self._email = QLineEdit()
        self._email.setObjectName("field")
        self._email.setPlaceholderText(tr("email_ph"))
        saved_email = str(self._settings.value("login/last_email", ""))
        if saved_email:
            self._email.setText(saved_email)
        layout.addWidget(self._email)

        layout.addWidget(self._field_label(tr("password")))
        self._password = QLineEdit()
        self._password.setObjectName("field")
        self._password.setPlaceholderText(tr("password_ph"))
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.returnPressed.connect(self._on_login)
        layout.addWidget(self._password)

        self._login_error = QLabel("")
        self._login_error.setObjectName("errorLabel")
        layout.addWidget(self._login_error)

        login_btn = QPushButton(tr("login_btn"))
        login_btn.setObjectName("primary")
        login_btn.clicked.connect(self._on_login)
        layout.addWidget(login_btn)
        return w

    def _build_register_form(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        layout.addWidget(self._field_label(tr("email")))
        self._reg_email = QLineEdit()
        self._reg_email.setObjectName("field")
        self._reg_email.setPlaceholderText(tr("email_ph"))
        layout.addWidget(self._reg_email)

        layout.addWidget(self._field_label(tr("password")))
        self._reg_password = QLineEdit()
        self._reg_password.setObjectName("field")
        self._reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._reg_password.setPlaceholderText(tr("password_ph"))
        layout.addWidget(self._reg_password)

        layout.addWidget(self._field_label(tr("confirm_password")))
        self._reg_confirm = QLineEdit()
        self._reg_confirm.setObjectName("field")
        self._reg_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self._reg_confirm.setPlaceholderText(tr("password_ph"))
        self._reg_confirm.returnPressed.connect(self._on_register)
        layout.addWidget(self._reg_confirm)

        self._reg_error = QLabel("")
        self._reg_error.setObjectName("errorLabel")
        layout.addWidget(self._reg_error)

        reg_btn = QPushButton(tr("register_btn"))
        reg_btn.setObjectName("primary")
        reg_btn.clicked.connect(self._on_register)
        layout.addWidget(reg_btn)
        return w

    def _build_device_flow_panel(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._df_status = QLabel("")
        self._df_status.setObjectName("subtitle")
        self._df_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._df_status.setWordWrap(True)
        layout.addWidget(self._df_status)

        self._df_code = QLabel("")
        self._df_code.setObjectName("codeBox")
        self._df_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._df_code.setVisible(False)
        layout.addWidget(self._df_code, alignment=Qt.AlignmentFlag.AlignCenter)

        back_btn = QPushButton(tr("back"))
        back_btn.setObjectName("secondary")
        back_btn.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        layout.addWidget(back_btn)
        return w

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("fieldLabel")
        return lbl

    def _toggle_mode(self) -> None:
        if self._mode == "login":
            self._mode = "register"
            self._stack.setCurrentIndex(1)
            self._switch_label.setText(tr("have_account"))
            self._switch_btn.setText(tr("sign_in"))
        else:
            self._mode = "login"
            self._stack.setCurrentIndex(0)
            self._switch_label.setText(tr("no_account"))
            self._switch_btn.setText(tr("sign_up"))

    def _on_login(self) -> None:
        email = self._email.text().strip()
        pwd = self._password.text()
        user = self._auth.login(email, pwd)
        if user:
            self._settings.setValue("login/last_email", email)
            self.login_success.emit(user)
            self.accept()
        else:
            self._login_error.setText(tr("login_error"))

    def _on_register(self) -> None:
        email = self._reg_email.text().strip()
        pwd = self._reg_password.text()
        confirm = self._reg_confirm.text()
        if pwd != confirm:
            self._reg_error.setText(tr("register_error_match"))
            return
        if len(pwd) < 8:
            self._reg_error.setText(tr("register_error_weak"))
            return
        try:
            user = self._auth.register(email, pwd)
            self._settings.setValue("login/last_email", email)
            self.login_success.emit(user)
            self.accept()
        except Exception as e:
            self._reg_error.setText(str(e))

    def _on_github(self) -> None:
        if not self._gh_flow.has_client_id():
            QMessageBox.information(
                self,
                "GitHub OAuth",
                "GitHub OAuth App client_id is not configured.\n\n"
                "Set GITHUB_OAUTH_CLIENT_ID in your .env file.\n"
                "Create an OAuth App at: github.com/settings/developers",
            )
            return
        self._stack.setCurrentIndex(2)
        self._df_status.setText(tr("device_flow_open"))
        self._df_code.setVisible(False)
        self._worker = _DeviceFlowWorker(self._gh_flow)
        self._worker.code_ready.connect(self._on_code_ready)
        self._worker.token_ready.connect(self._on_gh_token)
        self._worker.error.connect(self._on_worker_error)
        self._worker.start()

    def _on_code_ready(self, user_code: str, uri: str) -> None:
        self._df_status.setText(tr("device_flow_enter"))
        self._df_code.setText(user_code)
        self._df_code.setVisible(True)

    def _on_gh_token(self, token: str) -> None:
        try:
            info = self._gh_flow.get_user_info(token)
            user = self._auth.login_or_create_oauth(
                provider="github",
                provider_id=info["id"],
                email=info["email"] or f"{info['login']}@github.local",
                display_name=info["name"],
                avatar_url=info["avatar_url"],
                access_token=token,
            )
            self.login_success.emit(user)
            self.accept()
        except Exception as e:
            self._on_worker_error(str(e))

    def _on_microsoft(self) -> None:
        if not self._ms_oauth.has_client_id():
            QMessageBox.information(
                self,
                "Microsoft OAuth",
                "Microsoft OAuth client_id is not configured.\n\n"
                "Set MICROSOFT_OAUTH_CLIENT_ID in your .env file.",
            )
            return
        self._stack.setCurrentIndex(2)
        self._df_status.setText("Opening Microsoft login in your browser…")
        self._worker = _MicrosoftWorker(self._ms_oauth)
        self._worker.done.connect(self._on_ms_done)
        self._worker.error.connect(self._on_worker_error)
        self._worker.start()

    def _on_ms_done(self, info: dict[str, str]) -> None:
        user = self._auth.login_or_create_oauth(
            provider="microsoft",
            provider_id=info["id"],
            email=info["email"],
            display_name=info["name"],
            access_token=info.get("access_token", ""),
        )
        self.login_success.emit(user)
        self.accept()

    def _on_worker_error(self, msg: str) -> None:
        self._df_status.setText(f"Error: {msg}")
        self._df_code.setVisible(False)

    def _on_skip(self) -> None:
        self._auth.guest_login()
        self.accept()
