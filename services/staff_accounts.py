import re
import sqlite3

from werkzeug.security import generate_password_hash

from db import get_db_connection
from services.email_service import EmailDeliveryError, send_staff_credentials_email


class StaffAccountError(Exception):
    """Raised when a staff account cannot be created."""


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_staff_details(username, email, temporary_password, confirm_password, connection):
    if not username:
        raise StaffAccountError("Username is required.")
    if not email or not EMAIL_PATTERN.fullmatch(email):
        raise StaffAccountError("Enter a valid email address.")
    if len(temporary_password) < 8:
        raise StaffAccountError("Temporary password must be at least 8 characters.")
    if temporary_password != confirm_password:
        raise StaffAccountError("Temporary password and confirmation do not match.")

    if connection.execute(
        "SELECT 1 FROM users WHERE username = ?", (username,)
    ).fetchone():
        raise StaffAccountError("Username already exists.")
    if connection.execute(
        "SELECT 1 FROM users WHERE email = ? COLLATE NOCASE", (email,)
    ).fetchone():
        raise StaffAccountError("Email address already exists.")


def create_staff_account(username, email, temporary_password, confirm_password, smtp_config):
    """Create an approved staff account only after its credentials are emailed."""
    username = username.strip()
    email = email.strip()
    connection = get_db_connection()

    try:
        connection.execute("BEGIN")
        _validate_staff_details(
            username,
            email,
            temporary_password,
            confirm_password,
            connection,
        )
        connection.execute(
            """
            INSERT INTO users (username, password, email, role, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                username,
                generate_password_hash(temporary_password),
                email,
                "Staff",
                "Approved",
            ),
        )
        send_staff_credentials_email(
            email,
            username,
            temporary_password,
            smtp_config,
        )
        connection.commit()
    except EmailDeliveryError as error:
        connection.rollback()
        raise StaffAccountError(str(error)) from error
    except sqlite3.IntegrityError as error:
        connection.rollback()
        raise StaffAccountError("An account with that username or email already exists.") from error
    except StaffAccountError:
        connection.rollback()
        raise
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
