import logging
from pathlib import Path

import emails
from emails.template import JinjaTemplate
from pydantic import EmailStr

from app.core.config import core_config
from app.core.models.user import User
from app.core.security.security import (
    generate_password_reset_token,
    generate_verify_token,
)

from .config import email_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_email(
    email_to: EmailStr, subject_template="", html_template="", environment={}
):
    logger.debug("send_email()")
    if not email_config.email_enabled:
        logger.info("emails disabled, skipping email send")
        return
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(email_config.from_name, email_config.from_email),
    )
    smtp_options = {"host": email_config.smtp_host, "port": email_config.smtp_port}
    if email_config.smtp_tls:
        smtp_options["tls"] = True
    if email_config.smtp_user:
        smtp_options["user"] = email_config.smtp_user
    if email_config.smtp_password:
        smtp_options["password"] = email_config.smtp_password
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    return response


def send_welcome_email(user: User):
    logger.debug("send_welcome_email()")
    logger.debug(f"sending welcome email to: {user.email}")
    subject = f"{core_config.project_name} - Verify account for user {user.username}"
    with open(Path(email_config.email_templates_dir) / "welcome_email.html") as f:
        template_str = f.read()
    token = generate_verify_token(
        user=user, exp_min=core_config.verify_token_expire_min
    )
    base_url = (
        f"{core_config.base_url}{core_config.get_current_api()}{core_config.users_path}"
    )
    link = f"{base_url}{core_config.verify_path}?token={token.access_token}"
    send_email(
        email_to=user.email,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": core_config.project_name,
            "username": user.username,
            "link": link,
        },
    )


async def send_reset_email(user: User):
    logger.debug("send_reset_email()")
    logger.debug(f"sending reset email to: {user.email}")
    subject = f"{core_config.project_name} - Password recovery for user {user.username}"
    with open(Path(email_config.email_templates_dir) / "reset_password.html") as f:
        template_str = f.read()
    token = generate_password_reset_token(
        user=user, exp_min=email_config.email_reset_token_expire_min
    )
    base_url = (
        f"{core_config.base_url}{core_config.get_current_api()}{core_config.login_path}"
    )
    link = f"{base_url}{core_config.reset_path}?token={token.access_token}"
    send_email(
        email_to=user.email,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": core_config.project_name,
            "username": user.username,
            "email": user.email,
            "valid_min": email_config.email_reset_token_expire_min,
            "link": link,
        },
    )
