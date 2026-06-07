#! /bin/env python
import typing
import dataclasses
import difflib
import hashlib
import logging
import os
import pathlib
import re
import time

import dotenv
import requests

import baywatch.notify.email

LOGGER = logging.getLogger(__name__)
REF_PAGE_PATH = "ref.html"


def download_page(url: str) -> str:
    LOGGER.info("Downloading watched page")
    response = requests.get(url)
    return response.text


@dataclasses.dataclass
class Config:
    smtp: baywatch.notify.email.Smtp
    email: baywatch.notify.email.Email
    url: str
    polling_period_in_sec: int = 60
    update_ref_at_startup: bool = False
    ref_digest: str = ""
    ref_data: str = ""


def tag(data: str) -> typing.Tuple[str, str]:
    LOGGER.info("Updating reference page")
    save_page(data, REF_PAGE_PATH)
    return (data, get_digest(data))


def save_page(data: str, filepath: str):
    path = pathlib.Path(filepath)

    with path.open("wt") as file:
        file.write(data)


def load_page(filepath: str) -> str:
    path = pathlib.Path(filepath)

    with path.open("r") as file:
        contents = file.read()

    return contents


def get_digest(contents: str) -> str:
    hasher = hashlib.md5()
    hasher.update(contents.encode("utf-8"))
    return hasher.hexdigest()


def normalize_content_field(data: str) -> str:
    result = re.sub(
        r' content=".*" ',
        "",
        data,
        flags=re.MULTILINE,
    )
    return result


def has_changed(ref_data: str, new_data: str, method=None) -> bool:
    preprocessing_method = method if method else lambda x: x
    changed = preprocessing_method(new_data) != preprocessing_method(ref_data)

    if changed:
        LOGGER.info("Page was updated")
    else:
        LOGGER.info("Page didn't change")

    return changed


def load_config() -> Config:
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


def init(config: Config) -> None:
    logging.basicConfig(
        # filename="baywatch.log",
        format="%(asctime)s\t%(levelname)s\t%(message)s",
        level=logging.DEBUG,
    )

    LOGGER.info("Initializing...")

    if not pathlib.Path(REF_PAGE_PATH).exists():
        config.update_ref_at_startup = True

    if config.update_ref_at_startup:
        ref_data = download_page(config.url)
        ref_data, ref_digest = tag(ref_data)
    else:
        ref_data = load_page(REF_PAGE_PATH)
        ref_digest = get_digest(ref_data)

    config.ref_data = ref_data
    config.ref_digest = ref_digest


def compute_html_diff(old_page: str, new_page: str) -> str:
    differ = difflib.HtmlDiff()
    table = differ.make_table(old_page, new_page)
    return table


def watch(config: Config) -> None:
    LOGGER.info(f"Start polling (period={config.polling_period_in_sec}s)...")

    while 1:
        str_new_data = download_page(config.url)

        if has_changed(config.ref_data, str_new_data, normalize_content_field):
            config.ref_data = str_new_data
            _, config.ref_digest = tag(str_new_data)
            config.email.body = str_new_data
            config.smtp.send_email(config.email)

        time.sleep(config.polling_period_in_sec)


def main() -> None:
    config = load_config()
    init(config)
    watch(config)


if __name__ == "__main__":
    main()
