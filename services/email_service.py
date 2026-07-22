import smtplib
from email.message import EmailMessage


class EmailDeliveryError(Exception):
    """Raised when a staff credential email cannot be delivered."""


def send_staff_credentials_email(recipient_email, username, temporary_password, smtp_config):
    required_settings = (
        "SMTP_HOST",
        "SMTP_USERNAME",
        "SMTP_PASSWORD",
        "SMTP_FROM_EMAIL",
    )
    if any(not smtp_config.get(setting) for setting in required_settings):
        raise EmailDeliveryError(
            "SMTP is not configured. The staff account was not created."
        )

    message = EmailMessage()
    message["Subject"] = "Your Inventory Management System Account"
    message["From"] = smtp_config["SMTP_FROM_EMAIL"]
    message["To"] = recipient_email
    message.set_content(
        "Hello,\n\n"
        "An administrator has created your account.\n\n"
        f"Username:\n{username}\n\n"
        f"Temporary Password:\n{temporary_password}\n\n"
        "Please log in using these credentials.\n\n"
        "Regards,\n"
        "Inventory Management System\n"
    )

    try:
        with smtplib.SMTP(
            smtp_config["SMTP_HOST"],
            int(smtp_config["SMTP_PORT"]),
            timeout=10,
        ) as smtp:
            if smtp_config.get("SMTP_USE_TLS", True):
                smtp.starttls()
            smtp.login(smtp_config["SMTP_USERNAME"], smtp_config["SMTP_PASSWORD"])
            smtp.send_message(message)
    except (OSError, ValueError, smtplib.SMTPException) as error:
        raise EmailDeliveryError(
            "Credentials could not be emailed. The staff account was not created."
        ) from error
