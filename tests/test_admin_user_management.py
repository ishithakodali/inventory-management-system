import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from werkzeug.security import check_password_hash


_test_db_handle, TEST_DB_PATH = tempfile.mkstemp(suffix=".db")
os.close(_test_db_handle)
Path(TEST_DB_PATH).unlink(missing_ok=True)
os.environ["INVENTORY_DB_PATH"] = TEST_DB_PATH

from app import app
from db import get_db_connection
from models.users import create_admin
from services.email_service import EmailDeliveryError, send_staff_credentials_email


class AdminUserManagementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(
            TESTING=True,
            SMTP_HOST="smtp.example.test",
            SMTP_PORT=587,
            SMTP_USERNAME="smtp-user",
            SMTP_PASSWORD="smtp-password",
            SMTP_FROM_EMAIL="inventory@example.test",
            SMTP_USE_TLS=True,
        )

    @classmethod
    def tearDownClass(cls):
        Path(TEST_DB_PATH).unlink(missing_ok=True)

    def setUp(self):
        self.client = app.test_client()
        connection = get_db_connection()
        connection.execute("DELETE FROM users")
        connection.execute("DELETE FROM products")
        connection.commit()
        connection.close()
        create_admin()

    def _login_as(self, username, role):
        with self.client.session_transaction() as session:
            session["username"] = username
            session["role"] = role

    def _get_user(self, username):
        connection = get_db_connection()
        user = connection.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        connection.close()
        return user

    def test_admin_can_create_hashed_staff_account(self):
        self._login_as("admin", "Admin")
        form = {
            "username": "new.staff",
            "email": "new.staff@example.test",
            "temporary_password": "temporary-pass",
            "confirm_password": "temporary-pass",
        }

        with patch("services.staff_accounts.send_staff_credentials_email") as send_email:
            response = self.client.post("/manage-users", data=form, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Staff account created and login credentials emailed.", response.data)
        user = self._get_user("new.staff")
        self.assertEqual(user["email"], "new.staff@example.test")
        self.assertEqual(user["role"], "Staff")
        self.assertEqual(user["status"], "Approved")
        self.assertNotEqual(user["password"], form["temporary_password"])
        self.assertTrue(check_password_hash(user["password"], form["temporary_password"]))
        send_email.assert_called_once_with(
            "new.staff@example.test",
            "new.staff",
            "temporary-pass",
            app.config,
        )

    def test_duplicate_username_and_case_insensitive_email_are_rejected(self):
        self._login_as("admin", "Admin")
        with patch("services.staff_accounts.send_staff_credentials_email"):
            self.client.post("/manage-users", data={
                "username": "staff-one",
                "email": "staff@example.test",
                "temporary_password": "temporary-pass",
                "confirm_password": "temporary-pass",
            })
            duplicate_username = self.client.post("/manage-users", data={
                "username": "staff-one",
                "email": "other@example.test",
                "temporary_password": "temporary-pass",
                "confirm_password": "temporary-pass",
            })
            duplicate_email = self.client.post("/manage-users", data={
                "username": "staff-two",
                "email": "STAFF@example.test",
                "temporary_password": "temporary-pass",
                "confirm_password": "temporary-pass",
            })

        self.assertIn(b"Username already exists.", duplicate_username.data)
        self.assertIn(b"Email address already exists.", duplicate_email.data)
        self.assertIsNone(self._get_user("staff-two"))

    def test_invalid_staff_form_is_rejected(self):
        self._login_as("admin", "Admin")
        response = self.client.post("/manage-users", data={
            "username": "",
            "email": "invalid-email",
            "temporary_password": "short",
            "confirm_password": "different",
        })

        self.assertIn(b"Username is required.", response.data)
        self.assertIsNone(self._get_user(""))

    def test_email_failure_rolls_back_account_creation(self):
        self._login_as("admin", "Admin")
        with patch(
            "services.staff_accounts.send_staff_credentials_email",
            side_effect=EmailDeliveryError("Credential delivery failed."),
        ):
            response = self.client.post("/manage-users", data={
                "username": "mail-failure",
                "email": "mail-failure@example.test",
                "temporary_password": "temporary-pass",
                "confirm_password": "temporary-pass",
            })

        self.assertIn(b"Credential delivery failed.", response.data)
        self.assertIsNone(self._get_user("mail-failure"))

    def test_manage_users_requires_admin(self):
        guest_response = self.client.get("/manage-users")
        self.assertEqual(guest_response.status_code, 302)
        self.assertIn("/login", guest_response.headers["Location"])

        self._login_as("staff", "Staff")
        staff_response = self.client.get("/manage-users")
        self.assertEqual(staff_response.status_code, 403)

    def test_login_has_no_registration_option_and_register_redirects(self):
        login_response = self.client.get("/login")
        self.assertNotIn(b"Register Here", login_response.data)
        self.assertNotIn(b"Create Account", login_response.data)
        self.assertNotIn(b"Sign Up", login_response.data)

        register_response = self.client.get("/register")
        self.assertEqual(register_response.status_code, 302)
        self.assertIn("/login", register_response.headers["Location"])

    def test_legacy_password_is_upgraded_after_successful_login(self):
        connection = get_db_connection()
        connection.execute(
            "INSERT INTO users (username, password, role, status) VALUES (?, ?, ?, ?)",
            ("legacy-staff", "legacy-password", "Staff", "Approved"),
        )
        connection.commit()
        connection.close()

        response = self.client.post("/login", data={
            "username": "legacy-staff",
            "password": "legacy-password",
        })

        self.assertEqual(response.status_code, 302)
        user = self._get_user("legacy-staff")
        self.assertNotEqual(user["password"], "legacy-password")
        self.assertTrue(check_password_hash(user["password"], "legacy-password"))

    def test_authenticated_inventory_products_page_still_loads(self):
        self._login_as("admin", "Admin")
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, 200)

    @patch("services.email_service.smtplib.SMTP")
    def test_credential_email_content_and_smtp_delivery(self, smtp_constructor):
        smtp = smtp_constructor.return_value.__enter__.return_value
        smtp_config = {
            "SMTP_HOST": "smtp.example.test",
            "SMTP_PORT": 587,
            "SMTP_USERNAME": "smtp-user",
            "SMTP_PASSWORD": "smtp-password",
            "SMTP_FROM_EMAIL": "inventory@example.test",
            "SMTP_USE_TLS": True,
        }

        send_staff_credentials_email(
            "staff@example.test",
            "staff-user",
            "temporary-pass",
            smtp_config,
        )

        message = smtp.send_message.call_args.args[0]
        self.assertEqual(message["Subject"], "Your Inventory Management System Account")
        self.assertEqual(message["To"], "staff@example.test")
        self.assertEqual(
            message.get_content(),
            "Hello,\n\n"
            "An administrator has created your account.\n\n"
            "Username:\nstaff-user\n\n"
            "Temporary Password:\ntemporary-pass\n\n"
            "Please log in using these credentials.\n\n"
            "Regards,\n"
            "Inventory Management System\n",
        )
        smtp.starttls.assert_called_once()
        smtp.login.assert_called_once_with("smtp-user", "smtp-password")


if __name__ == "__main__":
    unittest.main()
