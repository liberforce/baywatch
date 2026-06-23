#! /bin/env python
import difflib
import logging
import pathlib
import random
import time
import typing


from baywatch.domain.models.page import Page
from baywatch.adapters.http import DataExtractor
from baywatch.adapters.normalizers import make_normalizer
from baywatch.adapters.repositories.pages import PageRepository
from baywatch.config import Config, EnvConfigLoader

LOGGER = logging.getLogger(__name__)
REF_PAGE_PATH = "ref.html"


def tag(page: Page, page_repo: PageRepository) -> typing.Tuple[str, str]:
    LOGGER.info("Updating reference page")
    page_repo.save(page, REF_PAGE_PATH)
    return (page.data, page.digest)


def has_changed(ref_page: Page, new_page: Page, normalizer=None) -> bool:
    preprocessing_method = normalizer.normalize if normalizer else lambda x: x
    changed = preprocessing_method(new_page) != preprocessing_method(ref_page)

    if changed:
        LOGGER.info("Page was updated")
    else:
        LOGGER.info("Page didn't change")

    return changed


def init(config: Config) -> None:
    logging.basicConfig(
        # filename="baywatch.log",
        format="%(asctime)s\t%(levelname)s\t%(message)s",
        level=logging.DEBUG,
    )

    LOGGER.info("Initializing...")
    page_repo = PageRepository()

    if not pathlib.Path(REF_PAGE_PATH).exists():
        config.update_ref_at_startup = True

    if config.update_ref_at_startup:
        ref_page = Page(DataExtractor().extract(config.url))
        tag(ref_page, page_repo)
    else:
        ref_page = page_repo.load(REF_PAGE_PATH)

    config.ref_page = ref_page
    config.normalizer = make_normalizer("prefecture")


def compute_html_diff(old_page: str, new_page: str) -> str:
    differ = difflib.HtmlDiff()
    table = differ.make_table(old_page, new_page)
    return table


def watch(config: Config) -> None:
    LOGGER.info(f"Start polling (period={config.polling_period_in_sec}s)...")

    while 1:
        new_page = Page(DataExtractor().extract(config.url))

        if has_changed(
            config.ref_page,
            new_page,
            config.normalizer,
        ):
            tag(
                new_page,
                config.output_page_repository,
            )
            config.ref_page = new_page
            config.email.body = new_page.data
            config.smtp.send_email(config.email)

        # Add some jitter to try to not be flagged as a bot
        jitter_upper_bound = config.polling_period_in_sec // 10
        jitter_lower_bound = -jitter_upper_bound
        jitter = random.randrange(jitter_lower_bound, jitter_upper_bound)
        nice_polling_period = config.polling_period_in_sec + jitter
        LOGGER.info(f"Trying again in {nice_polling_period}s...")
        time.sleep(nice_polling_period)


def main() -> None:
    config_loader = EnvConfigLoader()
    config = config_loader.load()
    init(config)
    watch(config)


if __name__ == "__main__":
    main()
