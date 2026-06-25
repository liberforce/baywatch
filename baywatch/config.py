import dataclasses
import logging
import os
import sys
import typing

import dotenv

import baywatch.notify.email
from baywatch.adapters.normalizers.base import BaseNormalizer
from baywatch.adapters.repositories.pages import PageRepository
from baywatch.domain.interfaces.normalizer import NormalizerInterface
from baywatch.domain.models.page import Page

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class Config:
    smtp: baywatch.notify.email.Smtp
    email: baywatch.notify.email.Email
    url: str
    logfile: typing.Optional[str]
    polling_period_in_sec: int = 60
    update_ref_at_startup: bool = False
    ref_page: Page = Page("")
    output_page_repository: PageRepository = PageRepository()
    normalizer: NormalizerInterface = BaseNormalizer()


class EnvConfigLoader:
    def load(self) -> Config:
        dotenv.load_dotenv()
        smtp = baywatch.notify.email.Smtp(
            user=baywatch.notify.email.Smtp.User(
                name=os.environ["SMTP_USERNAME"],
                password=os.environ["SMTP_PASSWORD"],
            )
        )
        recipients = [r.strip() for r in os.environ["SMTP_RECIPIENTS"].split(";")]
        email_config = baywatch.notify.email.Email(
            sender=os.environ["SMTP_SENDER"],
            recipients=recipients,
            subject=os.environ["BAYWATCH_EMAIL_SUBJECT"],
        )
        try:
            polling_period_in_sec = int(os.environ["BAYWATCH_POLLING_PERIOD_IN_SEC"])
        except ValueError:
            val = os.environ["BAYWATCH_POLLING_PERIOD_IN_SEC"]
            LOGGER.error(f"Invalid polling period: {val}")
            sys.exit(f"Error: Invalid polling period: {val}")

        logfile = os.environ.get("BAYWATCH_LOG_FILE")

        return Config(
            smtp=smtp,
            email=email_config,
            polling_period_in_sec=polling_period_in_sec,
            url=os.environ["BAYWATCH_WATCHED_URL"],
            logfile=logfile if logfile else None,
        )
