"""UI components for the Git module."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from yast3.core.i18n import _
from yast3.core.modules.git import (
    get_git_config,
    is_git_installed,
    set_git_config,
)


class GitWindow(QMainWindow):
    closed = Signal()

    def __init__(self):
        super().__init__()
        self.resize(600, 500)
        self.setWindowTitle(_("Git Configuration — YaST3"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        if not is_git_installed():
            layout.addWidget(QLabel(_("Git is not installed on this system.")))
            return

        self.config = get_git_config()

        # Tab widget
        self.tab_widget = QTabWidget()

        # User tab
        self.user_tab = QWidget()
        self._setup_user_tab()
        self.tab_widget.addTab(self.user_tab, _("User"))

        # Core tab
        self.core_tab = QWidget()
        self._setup_core_tab()
        self.tab_widget.addTab(self.core_tab, _("Core"))

        # Commit tab
        self.commit_tab = QWidget()
        self._setup_commit_tab()
        self.tab_widget.addTab(self.commit_tab, _("Commit"))

        # Merge tab
        self.merge_tab = QWidget()
        self._setup_merge_tab()
        self.tab_widget.addTab(self.merge_tab, _("Merge"))

        # Other tab
        self.other_tab = QWidget()
        self._setup_other_tab()
        self.tab_widget.addTab(self.other_tab, _("Other"))

        layout.addWidget(self.tab_widget)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_btn = QPushButton(_("Save"))
        self.save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(self.save_btn)

        self.reset_btn = QPushButton(_("Reset"))
        self.reset_btn.clicked.connect(self.reset_config)
        button_layout.addWidget(self.reset_btn)

        layout.addLayout(button_layout)

    def _setup_user_tab(self):
        """Setup User settings tab."""
        layout = QVBoxLayout(self.user_tab)
        layout.setSpacing(12)

        # User Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel(_("User Name")))
        self.name_edit = QLineEdit(self.config.user_name)
        self.name_edit.setPlaceholderText(_("Enter your Git user name"))
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # User Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel(_("Email Address")))
        self.email_edit = QLineEdit(self.config.user_email)
        self.email_edit.setPlaceholderText(_("Enter your Git email address"))
        email_layout.addWidget(self.email_edit)
        layout.addLayout(email_layout)

        # Signing Key
        signingkey_layout = QHBoxLayout()
        signingkey_layout.addWidget(QLabel(_("GPG Signing Key")))
        self.signingkey_edit = QLineEdit(self.config.user_signingkey)
        self.signingkey_edit.setPlaceholderText(_("Enter GPG key ID"))
        signingkey_layout.addWidget(self.signingkey_edit)
        layout.addLayout(signingkey_layout)

        layout.addStretch()

    def _setup_core_tab(self):
        """Setup Core settings tab."""
        layout = QVBoxLayout(self.core_tab)
        layout.setSpacing(12)

        # Editor
        editor_layout = QHBoxLayout()
        editor_layout.addWidget(QLabel(_("Default Editor")))
        self.editor_edit = QLineEdit(self.config.core_editor)
        self.editor_edit.setPlaceholderText(_("e.g., vim, nano, code"))
        editor_layout.addWidget(self.editor_edit)
        layout.addLayout(editor_layout)

        # Auto CRLF
        autocrlf_layout = QHBoxLayout()
        autocrlf_layout.addWidget(QLabel(_("Auto CRLF")))
        self.autocrlf_combo = QComboBox()
        self.autocrlf_combo.addItems(["", "true", "false", "input"])
        self.autocrlf_combo.setCurrentText(self.config.core_autocrlf)
        autocrlf_layout.addWidget(self.autocrlf_combo)
        layout.addLayout(autocrlf_layout)

        # Safe CRLF
        safecrlf_layout = QHBoxLayout()
        safecrlf_layout.addWidget(QLabel(_("Safe CRLF")))
        self.safecrlf_combo = QComboBox()
        self.safecrlf_combo.addItems(["", "true", "false", "warn"])
        self.safecrlf_combo.setCurrentText(self.config.core_safecrlf)
        safecrlf_layout.addWidget(self.safecrlf_combo)
        layout.addLayout(safecrlf_layout)

        layout.addStretch()

    def _setup_commit_tab(self):
        """Setup Commit settings tab."""
        layout = QVBoxLayout(self.commit_tab)
        layout.setSpacing(12)

        # Commit Template
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel(_("Commit Template")))
        self.template_edit = QLineEdit(self.config.commit_template)
        template_layout.addWidget(self.template_edit)
        self.template_btn = QPushButton(_("Browse"))
        self.template_btn.clicked.connect(self._browse_template)
        template_layout.addWidget(self.template_btn)
        layout.addLayout(template_layout)

        # GPG Sign
        self.gpgsign_check = QCheckBox(_("Sign commits with GPG"))
        self.gpgsign_check.setChecked(self.config.commit_gpgsign)
        layout.addWidget(self.gpgsign_check)

        layout.addStretch()

    def _setup_merge_tab(self):
        """Setup Merge settings tab."""
        layout = QVBoxLayout(self.merge_tab)
        layout.setSpacing(12)

        # Conflict Style
        conflictstyle_layout = QHBoxLayout()
        conflictstyle_layout.addWidget(QLabel(_("Conflict Style")))
        self.conflictstyle_combo = QComboBox()
        self.conflictstyle_combo.addItems(["", "merge", "diff3"])
        self.conflictstyle_combo.setCurrentText(self.config.merge_conflictstyle)
        conflictstyle_layout.addWidget(self.conflictstyle_combo)
        layout.addLayout(conflictstyle_layout)

        # Pull Rebase
        rebase_layout = QHBoxLayout()
        rebase_layout.addWidget(QLabel(_("Pull Rebase")))
        self.rebase_combo = QComboBox()
        self.rebase_combo.addItems(["", "true", "false", "interactive", "preserve"])
        self.rebase_combo.setCurrentText(self.config.pull_rebase)
        rebase_layout.addWidget(self.rebase_combo)
        layout.addLayout(rebase_layout)

        layout.addStretch()

    def _setup_other_tab(self):
        """Setup Other settings tab."""
        layout = QVBoxLayout(self.other_tab)
        layout.setSpacing(12)

        # Color UI
        self.color_ui_check = QCheckBox(_("Enable color output"))
        self.color_ui_check.setChecked(self.config.color_ui)
        layout.addWidget(self.color_ui_check)

        # Default Branch
        defaultbranch_layout = QHBoxLayout()
        defaultbranch_layout.addWidget(QLabel(_("Default Branch Name")))
        self.defaultbranch_edit = QLineEdit(self.config.init_defaultbranch)
        self.defaultbranch_edit.setPlaceholderText(_("e.g., main, master"))
        defaultbranch_layout.addWidget(self.defaultbranch_edit)
        layout.addLayout(defaultbranch_layout)

        # Credential Helper
        credential_layout = QHBoxLayout()
        credential_layout.addWidget(QLabel(_("Credential Helper")))
        self.credential_combo = QComboBox()
        self.credential_combo.addItems(
            ["", "cache", "store", "gnome-keyring", "kwallet"]
        )
        self.credential_combo.setCurrentText(self.config.credential_helper)
        credential_layout.addWidget(self.credential_combo)
        layout.addLayout(credential_layout)

        layout.addStretch()

    def _browse_template(self):
        """Browse for commit template file."""
        path, _filter = QFileDialog.getOpenFileName(
            self, _("Select Commit Template"), "", _("All Files (*)")
        )
        if path:
            self.template_edit.setText(path)

    def closeEvent(self, event) -> None:
        self.closed.emit()
        self.deleteLater()

    def save_config(self) -> None:
        user_name = self.name_edit.text().strip()
        user_email = self.email_edit.text().strip()

        if not user_name or not user_email:
            QMessageBox.warning(
                self, _("Error"), _("User name and email are required.")
            )
            return

        # Update config object
        self.config.user_name = user_name
        self.config.user_email = user_email
        self.config.user_signingkey = self.signingkey_edit.text().strip()
        self.config.core_editor = self.editor_edit.text().strip()
        self.config.core_autocrlf = self.autocrlf_combo.currentText()
        self.config.core_safecrlf = self.safecrlf_combo.currentText()
        self.config.commit_template = self.template_edit.text().strip()
        self.config.commit_gpgsign = self.gpgsign_check.isChecked()
        self.config.merge_conflictstyle = self.conflictstyle_combo.currentText()
        self.config.pull_rebase = self.rebase_combo.currentText()
        self.config.color_ui = self.color_ui_check.isChecked()
        self.config.init_defaultbranch = self.defaultbranch_edit.text().strip()
        self.config.credential_helper = self.credential_combo.currentText()

        if set_git_config(self.config):
            QMessageBox.information(
                self, _("Success"), _("Git configuration saved successfully.")
            )
            self.statusBar().showMessage(_("Saved successfully"), 3000)
        else:
            QMessageBox.critical(
                self, _("Error"), _("Failed to save Git configuration.")
            )

    def reset_config(self) -> None:
        """Reset all fields to original values."""
        # User tab
        self.name_edit.setText(self.config.user_name)
        self.email_edit.setText(self.config.user_email)
        self.signingkey_edit.setText(self.config.user_signingkey)

        # Core tab
        self.editor_edit.setText(self.config.core_editor)
        self.autocrlf_combo.setCurrentText(self.config.core_autocrlf)
        self.safecrlf_combo.setCurrentText(self.config.core_safecrlf)

        # Commit tab
        self.template_edit.setText(self.config.commit_template)
        self.gpgsign_check.setChecked(self.config.commit_gpgsign)

        # Merge tab
        self.conflictstyle_combo.setCurrentText(self.config.merge_conflictstyle)
        self.rebase_combo.setCurrentText(self.config.pull_rebase)

        # Other tab
        self.color_ui_check.setChecked(self.config.color_ui)
        self.defaultbranch_edit.setText(self.config.init_defaultbranch)
        self.credential_combo.setCurrentText(self.config.credential_helper)

        self.statusBar().showMessage(_("Reset to original values"), 2000)