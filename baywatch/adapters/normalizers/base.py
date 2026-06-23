from baywatch.domain.models.page import Page
from baywatch.domain.interfaces.normalizer import NormalizerInterface


class BaseNormalizer(NormalizerInterface):
    def normalize(self, page: Page) -> str:
        return page.data
