from pathlib import Path
from uuid import uuid4
from typing import Any

import emails
from datetime import datetime
from emails.template import JinjaTemplate
from pydantic import EmailStr

from .config import get_email_config
from .crud import create_email
from .model import EmailDb
from app.core.db import service as db_service


async def process_email(
    username: str,
    to_email: EmailStr,
    subject: str,
    html_template: str,
    template_data: Any,
):
    await save_email(
        username=username,
        to_email=to_email,
        subject=subject,
        html_template=html_template,
        template_data=template_data,
    )

    return await send_email(
        to_email=to_email,
        subject=subject,
        html_template=html_template,
        template_data=template_data,
    )


async def save_email(
    username: str,
    to_email: EmailStr,
    subject: str,
    html_template: str,
    template_data: Any,
):
    email_config = get_email_config()
    email_db = EmailDb(
        email_id=str(uuid4()),
        username=username,
        from_email=email_config.from_email,
        to_email=to_email,
        subject=subject,
        html_template=html_template,
        template_data=template_data,
        date_created=datetime.now(),
    )
    db_context = db_service.get_db_context()
    return await create_email(db_context=db_context, email_db=email_db)


async def send_email(
    to_email: EmailStr, subject="", html_template=None, template_data={}
):
    email_config = get_email_config()

    if not email_config.email_enabled:
        return

    html = ""
    if html_template:
        with open(Path(email_config.email_templates_dir) / html_template) as f:
            html = f.read()

    message = emails.Message(
        subject=JinjaTemplate(subject),
        html=JinjaTemplate(html),
        mail_from=(email_config.from_name, email_config.from_email),
    )

    smtp_options = {"host": email_config.smtp_host, "port": email_config.smtp_port}
    if email_config.smtp_tls:
        smtp_options["tls"] = True
    if email_config.smtp_user:
        smtp_options["user"] = email_config.smtp_user
    if email_config.smtp_password:
        smtp_options["password"] = email_config.smtp_password

    return message.send(to=to_email, render=template_data, smtp=smtp_options)
