#! /bin/env python
import dataclasses
import difflib
import hashlib
import logging
import os
import pathlib
import re
import subprocess
import time

import dotenv

import baywatch.notify.email

LOGGER = logging.getLogger(__name__)
REF_PAGE_PATH = "ref.html"
NEW_PAGE_PATH = "page.html"


def download_page(url: str, cookie: str = "") -> str:
    LOGGER.info("Downloading watched page")
    cmd = f"""/usr/bin/curl '{url}' \
      --silent \
      --compressed \
      -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0' \
      -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
      -H 'Accept-Language: fr-FR,fr;q=0.8,en-US;q=0.5,en;q=0.3' \
      -H 'Accept-Encoding: gzip, deflate, br, zstd' \
      -H 'DNT: 1' \
      -H 'Connection: keep-alive' \
      -H 'Cookie: _rdv_sp_session={cookie}' \
      -H 'Upgrade-Insecure-Requests: 1' \
      -H 'Sec-Fetch-Dest: document' \
      -H 'Sec-Fetch-Mode: navigate' \
      -H 'Sec-Fetch-Site: same-origin' \
      -H 'Sec-Fetch-User: ?1' \
      -H 'If-None-Match: W/"17033ffc47c121edbba3be1c8006fc97"' \
      -H 'Priority: u=0, i' \
      -H 'TE: trailers'
"""

    output = subprocess.check_output(
        cmd,
        shell=True,
    )
    return output.decode("utf-8")


@dataclasses.dataclass
class Config:
    sender: str
    recipient: str
    password: str
    username: str
    url: str
    curl_escaped_cookie: str
    polling_period_in_sec: int = 60
    update_ref_at_startup: bool = False
    ref_digest: str = ""
    ref_data: str = ""


def tag(data: str) -> tuple[str, str]:
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


def has_changed(ref_data: str, new_data: str) -> bool:
    changed = new_data != ref_data

    if changed:
        LOGGER.info("Page was updated")
    else:
        LOGGER.info("Page didn't change")

    return changed


def load_config() -> Config:
    dotenv.load_dotenv()
    return Config(
        username=os.environ["SMTP_USERNAME"],
        sender=os.environ["SMTP_SENDER"],
        recipient=os.environ["SMTP_RECIPIENT"],
        password=os.environ["SMTP_PASSWORD"],
        curl_escaped_cookie=os.environ["CURL_ESCAPED_COOKIE"],
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

    if config.update_ref_at_startup:
        ref_data = download_page(config.url, config.curl_escaped_cookie)
        ref_data, ref_digest = tag(ref_data)
        config.ref_data = normalize(ref_data)
        config.ref_digest = ref_digest
    else:
        ref_data = load_page(REF_PAGE_PATH)
        config.ref_data = ref_data
        config.ref_digest = get_digest(ref_data)


def compute_html_diff(old_page: str, new_page: str) -> str:
    differ = difflib.HtmlDiff()
    table = differ.make_table(old_page, new_page)
    return table


def normalize(data: str) -> str:
    result = re.sub(
        r' content=".*" ',
        "",
        data,
        flags=re.MULTILINE,
    )
    return result


def watch(config: Config) -> None:
    LOGGER.info(f"Start polling (period={config.polling_period_in_sec}s)...")

    while 1:
        str_new_data = download_page(config.url, config.curl_escaped_cookie)
        str_new_data = normalize(str_new_data)

        if has_changed(config.ref_data, str_new_data):
            config.ref_data = str_new_data
            _, config.ref_digest = tag(str_new_data)
            baywatch.notify.email.send_email(
                config.username,
                config.password,
                config.sender,
                config.recipient,
                subject="La page surveillée a été modifiée!",
                contents=str_new_data,
            )

        time.sleep(config.polling_period_in_sec)


def main() -> None:
    config = load_config()
    init(config)
    watch(config)


if __name__ == "__main__":
    main()
