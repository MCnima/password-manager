import unittest
import csv
import os
import tempfile
from unittest.mock import patch
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLineEdit
import pyqt_gui
import project


class EncryptionExitTests(unittest.TestCase):
    def test_invalid_menu_input_reencrypts_before_exit(self):
        responses = iter(["login", "create", "site", "12", "invalid"])

        with patch("project.os.path.exists", return_value=True), \
                patch("project.login", return_value=("alice", "secret")), \
                patch("project.decryptt") as decrypt_file, \
                patch("project.encrypt_file") as encrypt_file, \
                patch("builtins.input", side_effect=lambda *args: next(responses)):
            with self.assertRaises(SystemExit):
                project.main()

        decrypt_file.assert_called_once_with("alice", "secret")
        encrypt_file.assert_called_once_with("alice", "secret")

    def test_keyboard_interrupt_reencrypts_before_propagating(self):
        with patch("project.os.path.exists", return_value=True), \
                patch("project.login", return_value=("alice", "secret")), \
                patch("project.decryptt") as decrypt_file, \
                patch("project.encrypt_file") as encrypt_file, \
                patch("builtins.input", side_effect=["login", KeyboardInterrupt]):
            with self.assertRaises(KeyboardInterrupt):
                project.main()

        decrypt_file.assert_called_once_with("alice", "secret")
        encrypt_file.assert_called_once_with("alice", "secret")

    def test_decryption_failure_does_not_overwrite_file(self):
        decryption_error = ValueError("invalid token")

        with patch("project.os.path.exists", return_value=True), \
                patch("builtins.input", return_value="login"), \
                patch("project.login", return_value=("alice", "secret")), \
                patch("project.decryptt", side_effect=decryption_error), \
                patch("project.encrypt_file") as encrypt_file:
            with self.assertRaises(SystemExit):
                project.main()

        encrypt_file.assert_not_called()


class GuiCrashTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def test_add_password_field_is_visible_but_login_is_masked(self):
        dialog = pyqt_gui.PasswordDialog()
        with patch.object(pyqt_gui.PasswordManagerWindow, "_create_data_file"):
            window = pyqt_gui.PasswordManagerWindow()
        self.assertEqual(dialog.password_input.echoMode(), QLineEdit.EchoMode.Normal)
        self.assertEqual(window.login_password.echoMode(), QLineEdit.EchoMode.Password)
        self.assertFalse(window.windowIcon().isNull())
        dialog.close()
        window.close()

    def test_password_is_masked_with_user_role_secret(self):
        with tempfile.TemporaryDirectory() as directory:
            old_cwd = os.getcwd()
            os.chdir(directory)
            try:
                with patch.object(pyqt_gui.PasswordManagerWindow, "_create_data_file"):
                    window = pyqt_gui.PasswordManagerWindow()
                window.current_user = "sample"
                window.current_password = "secret"
                with open("sample.csv", "w", newline="", encoding="utf-8") as vault:
                    csv.writer(vault).writerows([
                        ["first-service", "first-user", "first-secret", "old"],
                        ["second-service", "second-user", "second-secret", "new"],
                    ])
                window.refresh_table()
                first = window.table.item(0, 2)
                second = window.table.item(1, 2)
                self.assertEqual(first.data(Qt.ItemDataRole.UserRole), "first-secret")
                self.assertEqual(first.text(), "\u2022" * 12)
                self.assertEqual(second.data(Qt.ItemDataRole.UserRole + 1), 1)
            finally:
                os.chdir(old_cwd)

    def test_malformed_data_csv_does_not_raise(self):
        with tempfile.TemporaryDirectory() as directory:
            old_cwd = os.getcwd()
            os.chdir(directory)
            try:
                with open("data.csv", "w", newline="", encoding="utf-8") as data:
                    data.write("broken,row,with,extra,columns\n")
                self.assertFalse(project.manage_login_pass("missing", "wrong"))
            finally:
                os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
