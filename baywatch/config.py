import dataclasses
import dotenv
import logging
import os
import sys

import baywatch.notify.email
from baywatch.adapters.repositories.pages import PageRepository
from baywatch.adapters.normalizers.base import BaseNormalizer
from baywatch.domain.models.page import Page
from baywatch.domain.interfaces.normalizer import NormalizerInterface

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class Config:
    smtp: baywatch.notify.email.Smtp
    email: baywatch.notify.email.Email
    url: str
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
        email_config = baywatch.notify.email.Email(
            sender=os.environ["SMTP_SENDER"],
            recipient=os.environ["SMTP_RECIPIENT"],
            subject=os.environ["BAYWATCH_EMAIL_SUBJECT"],
        )
        try:
            polling_period_in_sec = int(os.environ["BAYWATCH_POLLING_PERIOD_IN_SEC"])
        except ValueError:
            val = os.environ["BAYWATCH_POLLING_PERIOD_IN_SEC"]
            LOGGER.error(f"Invalid polling period: {val}")
            sys.exit(f"Error: Invalid polling period: {val}")

        return Config(
            smtp=smtp,
            email=email_config,
            polling_period_in_sec=polling_period_in_sec,
            url=os.environ["BAYWATCH_WATCHED_URL"],
        )
