#!/usr/bin/env python3

import dataclasses
import logging
import smtplib
from email.message import EmailMessage

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
        msg = EmailMessage()
        msg["From"] = email.sender
        msg["To"] = ",".join(email.recipients)
        msg["Subject"] = email.subject
        msg.add_alternative(email.body, subtype="html")
        msg.add_attachment(
            email.body,
            subtype="html",
            filename="page.html",
        )

        with smtplib.SMTP("mail-eu.smtp2go.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(
                self.user.name,
                self.user.password,
            )
            smtp.send_message(msg)
