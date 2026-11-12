import unittest
from unittest.mock import patch

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


if __name__ == "__main__":
    unittest.main()
