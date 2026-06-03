#!/usr/bin/env python3

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

LOGGER = logging.getLogger(__name__)


def send_email(
    username: str,
    password: str,
    mail_from: str,
    mail_to: str,
    subject: str,
    contents: str = "",
):
    LOGGER.info("Sending notification email from %s to %s", mail_from, mail_to)
    msg = MIMEMultipart()
    msg["From"] = mail_from
    msg["To"] = mail_to
    msg["Subject"] = subject
    message = contents
    # msg.attach(MIMEText(message, "plain"))
    msg.attach(MIMEText(message, "html"))
    mailserver = smtplib.SMTP("mail-eu.smtp2go.com", 587)
    mailserver.ehlo()
    mailserver.starttls()
    mailserver.ehlo()
    mailserver.login(username, password)
    mailserver.sendmail(mail_from, mail_to, msg.as_string())
    mailserver.quit()
