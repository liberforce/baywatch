#!/usr/bin/env python3

import dataclasses
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class SmtpConfig:
    password: str
    username: str


@dataclasses.dataclass
class Email:
    sender: str
    recipient: str
    subject: str
    body: str = ""


def send_email(
    smtp: SmtpConfig,
    email: Email,
):
    LOGGER.info(
        "Sending notification email from %s to %s",
        email.sender,
        email.recipient,
    )
    msg = MIMEMultipart()
    msg["From"] = email.sender
    msg["To"] = email.recipient
    msg["Subject"] = email.subject
    message = email.body
    # msg.attach(MIMEText(message, "plain"))
    msg.attach(MIMEText(message, "html"))
    mailserver = smtplib.SMTP("mail-eu.smtp2go.com", 587)
    mailserver.ehlo()
    mailserver.starttls()
    mailserver.ehlo()
    mailserver.login(smtp.username, smtp.password)
    mailserver.sendmail(
        email.sender,
        email.recipient,
        msg.as_string(),
    )
    mailserver.quit()
