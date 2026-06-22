import dataclasses
import dotenv
import os

import baywatch.notify.email


@dataclasses.dataclass
class Config:
    smtp: baywatch.notify.email.Smtp
    email: baywatch.notify.email.Email
    url: str
    polling_period_in_sec: int = 60
    update_ref_at_startup: bool = False
    ref_digest: str = ""
    ref_data: str = ""


class EnvConfigLoader:
    def load(self) -> Config:
        dotenv.load_dotenv()
        smtp = baywatch.notify.email.Smtp(
            config=baywatch.notify.email.Smtp.Config(
                username=os.environ["SMTP_USERNAME"],
                password=os.environ["SMTP_PASSWORD"],
            )
        )
        email_config = baywatch.notify.email.Email(
            sender=os.environ["SMTP_SENDER"],
            recipient=os.environ["SMTP_RECIPIENT"],
            subject=os.environ["BAYWATCH_EMAIL_SUBJECT"],
        )
        return Config(
            smtp=smtp,
            email=email_config,
            polling_period_in_sec=int(os.environ["BAYWATCH_POLLING_PERIOD_IN_SEC"]),
            url=os.environ["BAYWATCH_WATCHED_URL"],
        )
