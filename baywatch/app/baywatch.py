import re
import copy
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

    def do(self, action: str, page: Page) -> None:
        if action == "tag":
            tag(
                page,
                self.config.output_page_repository,
            )
        elif action == "send_email":
            self.config.email.body = page.data
            self.config.smtp.send_email(self.config.email)
        elif action == "watch_child":
            match = re.search(
                r'[^"]*accepted_restrictions_for[^"]*',
                page.data,
                flags=re.MULTILINE,
            )
            if not match:
                LOGGER.warning("Resource not found in page search")
            else:
                resource = match[0]
                tmp_config = copy.deepcopy(self.config)
                tmp_config.url = f"https://rdv.anct.gouv.fr/{resource}"
                tmp_config.polling_period_in_sec = 10
                Bay(tmp_config).watch(n_times=2, actions=["send_email"])

    def watch(
        self,
        n_times: int = -1,
        actions: typing.Optional[list[str]] = None,
    ) -> None:
        LOGGER.info(f"Start polling (period={self.config.polling_period_in_sec}s)...")
        if n_times < 0:
            while 1:
                self._watch(actions)
        else:
            for n in range(n_times):
                self._watch(actions)

    def _watch(self, actions: typing.Optional[list[str]] = None) -> None:
        new_page = Page(DataExtractor().extract(self.config.url))

        if self.has_changed(
            self.config.ref_page,
            new_page,
            self.config.normalizer,
        ):
            if actions is not None:
                for action in actions:
                    self.do(action, new_page)

            self.config.ref_page = new_page

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
        process = normalizer.normalize if normalizer else lambda x: x
        changed = process(new_page) != process(ref_page)

        if changed:
            LOGGER.info("Page was updated")
        else:
            LOGGER.info("Page didn't change")

        return changed


def main() -> None:
    config_loader = EnvConfigLoader()
    config = config_loader.load()
    bay = Bay(config)
    actions = ["tag", "send_email", "watch_child"]
    bay.watch(actions=actions)


if __name__ == "__main__":
    main()
