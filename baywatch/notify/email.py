#!/usr/bin/env python3

import dataclasses
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class Email:
    sender: str
    recipients: list[str]
    subject: str
    body: str = ""


class Smtp:
    @dataclasses.dataclass
    class User:
        name: str
        password: str

    def __init__(self, user: User):
        self.user = user

    def send_email(
        self,
        email: Email,
    ) -> None:
        LOGGER.info(
            "Sending notification email from %s to %s",
            email.sender,
            ";".join(email.recipients),
        )
        msg = MIMEMultipart()
        msg["From"] = email.sender
        msg["To"] = ",".join(email.recipients)
        msg["Subject"] = email.subject
        message = email.body
        # msg.attach(MIMEText(message, "plain"))
        msg.attach(MIMEText(message, "html"))
        mailserver = smtplib.SMTP("mail-eu.smtp2go.com", 587)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.ehlo()
        mailserver.login(self.user.name, self.user.password)
        mailserver.sendmail(
            email.sender,
            email.recipients,
            msg.as_string(),
        )
        mailserver.quit()
