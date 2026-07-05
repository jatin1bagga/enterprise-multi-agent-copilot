import mimetypes
import smtplib
from email.message import EmailMessage
from pathlib import Path

from app.core.config import Settings


def send_email(
    settings: Settings,
    to_address: str,
    subject: str,
    body: str,
    attachment_paths: list[str],
) -> None:
    if not settings.smtp_configured:
        raise RuntimeError(
            "Email is not configured. Set SMTP_HOST and SMTP_FROM_ADDRESS in the backend .env to enable the Mail Agent."
        )

    message = EmailMessage()
    message["From"] = settings.smtp_from_address
    message["To"] = to_address
    message["Subject"] = subject
    message.set_content(body)

    for path_str in attachment_paths:
        path = Path(path_str)
        if not path.exists():
            continue
        mime_type, _ = mimetypes.guess_type(path.name)
        maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)
        message.add_attachment(
            path.read_bytes(), maintype=maintype, subtype=subtype, filename=path.name
        )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username and settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)
