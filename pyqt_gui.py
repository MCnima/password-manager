import csv
import os
import secrets
import string
import sys

from cryptography.fernet import InvalidToken
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFormLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import project


class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add password")
        self.setMinimumWidth(420)

        layout = QFormLayout(self)
        self.site_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.description_input = QLineEdit()

        layout.addRow("Website / service", self.site_input)
        layout.addRow("Username", self.username_input)
        layout.addRow("Password", self.password_input)
        layout.addRow("Description", self.description_input)

        button_row = QHBoxLayout()
        generate_button = QPushButton("Generate")
        generate_button.clicked.connect(self.generate_password)
        save_button = QPushButton("Save")
        save_button.setDefault(True)
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(generate_button)
        button_row.addStretch()
        button_row.addWidget(cancel_button)
        button_row.addWidget(save_button)
        layout.addRow(button_row)

    def generate_password(self):
        alphabet = string.ascii_letters + string.digits + "@#$&_-=!"
        self.password_input.setText("".join(secrets.choice(alphabet) for _ in range(20)))

    def values(self):
        return (
            self.site_input.text().strip(),
            self.username_input.text().strip(),
            self.password_input.text(),
            self.description_input.text().strip() or "None",
        )


class PasswordManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vault - Password Manager")
        self.resize(980, 620)
        self.current_user = None
        self.current_password = None
        self._create_data_file()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.login_page = self._build_login_page()
        self.signup_page = self._build_signup_page()
        self.vault_page = self._build_vault_page()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.signup_page)
        self.stack.addWidget(self.vault_page)
        self.stack.setCurrentWidget(self.login_page)

        self.statusBar().showMessage("Ready")

    @staticmethod
    def _create_data_file():
        if not os.path.exists("data.csv"):
            open("data.csv", "a", encoding="utf-8").close()

    def _build_login_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(180, 100, 180, 100)

        title = QLabel("Password Manager")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        form = QFormLayout()
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Username")
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Username", self.login_username)
        form.addRow("Password", self.login_password)
        layout.addLayout(form)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        signup_button = QPushButton("Create account")
        signup_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.signup_page))
        layout.addWidget(signup_button)
        return page

    def _build_signup_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(180, 100, 180, 100)

        title = QLabel("Create Account")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        form = QFormLayout()
        self.signup_username = QLineEdit()
        self.signup_password = QLineEdit()
        self.signup_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_confirm = QLineEdit()
        self.signup_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Username", self.signup_username)
        form.addRow("Password", self.signup_password)
        form.addRow("Confirm password", self.signup_confirm)
        layout.addLayout(form)

        create_button = QPushButton("Create account")
        create_button.clicked.connect(self.signup)
        layout.addWidget(create_button)

        back_button = QPushButton("Back to login")
        back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.login_page))
        layout.addWidget(back_button)
        return page

    def _build_vault_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        header = QHBoxLayout()
        self.user_label = QLabel("My Vault")
        self.user_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.addWidget(self.user_label)
        header.addStretch()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search vault")
        self.search_input.setMaximumWidth(240)
        self.search_input.textChanged.connect(self.filter_table)
        header.addWidget(self.search_input)

        add_button = QPushButton("Add password")
        add_button.clicked.connect(self.add_password)
        header.addWidget(add_button)

        copy_button = QPushButton("Copy password")
        copy_button.clicked.connect(self.copy_selected_password)
        header.addWidget(copy_button)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_selected)
        header.addWidget(delete_button)

        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout)
        header.addWidget(logout_button)
        layout.addLayout(header)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Website / Service", "Username", "Password", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        return page

    def login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()
        if not username or not password:
            QMessageBox.warning(self, "Missing information", "Enter both username and password.")
            return
        if not project.manage_login_pass(username, password):
            QMessageBox.warning(self, "Login failed", "Incorrect username or password.")
            return

        vault_path = f"{username}.csv"
        if not os.path.exists(vault_path):
            QMessageBox.warning(self, "Vault missing", "This account's vault file could not be found.")
            return

        try:
            project.decryptt(username, password)
        except InvalidToken:
            QMessageBox.critical(self, "Vault error", "The vault could not be decrypted.")
            return

        self.current_user = username
        self.current_password = password
        self.login_password.clear()
        self.user_label.setText(f"{username}'s Vault")
        self.refresh_table()
        self.stack.setCurrentWidget(self.vault_page)
        self.statusBar().showMessage("Vault unlocked")

    def signup(self):
        username = self.signup_username.text().strip()
        password = self.signup_password.text()
        confirmation = self.signup_confirm.text()
        if not username or not password:
            QMessageBox.warning(self, "Missing information", "Enter a username and password.")
            return
        if password != confirmation:
            QMessageBox.warning(self, "Password mismatch", "The passwords do not match.")
            return
        if len(username) > 128 or any(character in username for character in r'\/:*?"<>|'):
            QMessageBox.warning(self, "Invalid username", "Use a username without file-name special characters.")
            return
        with open("data.csv", "r", newline="", encoding="utf-8") as data_file:
            if any(row and row[0] == username for row in csv.reader(data_file)):
                QMessageBox.warning(self, "Username taken", "Choose a different username.")
                return
        with open("data.csv", "a", newline="", encoding="utf-8") as data_file:
            csv.writer(data_file).writerow([username, project.hash(password, username)])
        open(f"{username}.csv", "a", encoding="utf-8").close()
        project.encrypt_file(username, password)

        self.signup_username.clear()
        self.signup_password.clear()
        self.signup_confirm.clear()
        QMessageBox.information(self, "Account created", "Account created successfully.")
        self.login_username.setText(username)
        self.stack.setCurrentWidget(self.login_page)

    def refresh_table(self):
        self.table.setRowCount(0)
        if not self.current_user:
            return
        with open(f"{self.current_user}.csv", "r", newline="", encoding="utf-8") as data_file:
            for row in csv.reader(data_file):
                if len(row) not in (3, 4):
                    continue
                row_number = self.table.rowCount()
                self.table.insertRow(row_number)
                display_row = row if len(row) == 4 else ["Legacy", row[0], row[1], row[2]]
                for column, value in enumerate(display_row):
                    self.table.setItem(row_number, column, QTableWidgetItem(value))
        self.filter_table()

    def filter_table(self):
        query = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            values = [
                self.table.item(row, column).text().lower()
                if self.table.item(row, column)
                else ""
                for column in range(self.table.columnCount())
            ]
            self.table.setRowHidden(row, query not in " ".join(values))

    def add_password(self):
        dialog = PasswordDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        service, username, password, description = dialog.values()
        if not service or not username or not password:
            QMessageBox.warning(self, "Missing information", "Service, username, and password are required.")
            return
        project.add_to_file(
            self.current_user,
            username,
            password,
            description,
            service=service,
        )
        self.refresh_table()
        self.statusBar().showMessage("Password saved")

    def copy_selected_password(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "No selection", "Select a password to copy.")
            return
        password_item = self.table.item(row, 2)
        if password_item:
            QApplication.clipboard().setText(password_item.text())
            self.statusBar().showMessage("Password copied")

    def delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "No selection", "Select a vault entry to delete.")
            return
        result = QMessageBox.question(
            self,
            "Delete entry",
            "Delete the selected password?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            return
        rows = []
        with open(f"{self.current_user}.csv", "r", newline="", encoding="utf-8") as data_file:
            rows = list(csv.reader(data_file))
        del rows[row]
        with open(f"{self.current_user}.csv", "w", newline="", encoding="utf-8") as data_file:
            csv.writer(data_file).writerows(rows)
        self.refresh_table()
        self.statusBar().showMessage("Entry deleted")

    def encrypt_active_vault(self):
        if self.current_user and self.current_password:
            project.encrypt_file(self.current_user, self.current_password)

    def logout(self):
        try:
            self.encrypt_active_vault()
        except Exception as error:
            QMessageBox.critical(self, "Encryption failed", str(error))
            return
        self.current_user = None
        self.current_password = None
        self.table.setRowCount(0)
        self.search_input.clear()
        self.login_username.clear()
        self.statusBar().showMessage("Vault locked")
        self.stack.setCurrentWidget(self.login_page)

    def closeEvent(self, event):
        if self.current_user:
            try:
                self.encrypt_active_vault()
            except Exception as error:
                QMessageBox.critical(self, "Encryption failed", str(error))
                event.ignore()
                return
        event.accept()


def launch():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PasswordManagerWindow()
    window.show()
    sys.exit(app.exec())
