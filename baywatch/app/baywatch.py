import logging
import random
import time
import pathlib
import typing

from baywatch.adapters.normalizers import make_normalizer
from baywatch.config import Config, EnvConfigLoader
from baywatch.adapters.repositories.pages import PageRepository
from baywatch.domain.models.page import Page
from baywatch.adapters.http import DataExtractor

REF_PAGE_PATH = "ref.html"

LOGGER = logging.getLogger(__name__)


def tag(page: Page, page_repo: PageRepository) -> typing.Tuple[str, str]:
    LOGGER.info("Updating reference page")
    page_repo.save(page, REF_PAGE_PATH)
    return (page.data, page.digest)


class Bay:
    def __init__(self, config: Config) -> None:
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
        self.config = config

    def watch(self) -> None:
        LOGGER.info(f"Start polling (period={self.config.polling_period_in_sec}s)...")

        while 1:
            new_page = Page(DataExtractor().extract(self.config.url))

            if self.has_changed(
                self.config.ref_page,
                new_page,
                self.config.normalizer,
            ):
                tag(
                    new_page,
                    self.config.output_page_repository,
                )
                self.config.ref_page = new_page
                self.config.email.body = new_page.data
                self.config.smtp.send_email(self.config.email)

            # Add some jitter to try to not be flagged as a bot
            jitter_upper_bound = self.config.polling_period_in_sec // 10
            jitter_lower_bound = -jitter_upper_bound
            jitter = random.randrange(jitter_lower_bound, jitter_upper_bound)
            nice_polling_period = self.config.polling_period_in_sec + jitter
            LOGGER.info(f"Trying again in {nice_polling_period}s...")
            time.sleep(nice_polling_period)

    def has_changed(
        self,
        ref_page: Page,
        new_page: Page,
        normalizer=None,
    ) -> bool:
        preprocessing_method = normalizer.normalize if normalizer else lambda x: x
        changed = preprocessing_method(new_page) != preprocessing_method(ref_page)

        if changed:
            LOGGER.info("Page was updated")
        else:
            LOGGER.info("Page didn't change")

        return changed


def main() -> None:
    config_loader = EnvConfigLoader()
    config = config_loader.load()
    bay = Bay(config)
    bay.watch()


if __name__ == "__main__":
    main()
