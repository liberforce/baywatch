import pathlib

from baywatch.domain.interfaces.normalizer import NormalizerInterface
from baywatch.domain.models.page import Page


class PageRepository:
    def save(self, page: Page, filepath: str):
        path = pathlib.Path(filepath)

        with path.open("wt") as file:
            file.write(page.data)

    def load(self, filepath: str) -> Page:
        path = pathlib.Path(filepath)

        with path.open("r") as file:
            contents = file.read()

        return Page(contents)


class NormalizedPage(Page):
    def __init__(
        self,
        page: Page,
        normalizer: NormalizerInterface | None = None,
    ):
        self._page = page
        self._normalizer = normalizer

    @property
    def data(self):
        if self.normalizer is None:
            return self.page.data
        else:
            return self._normalizer.normalize(self._page.data)
