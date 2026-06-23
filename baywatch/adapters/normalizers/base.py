from baywatch.domain.interfaces.normalizer import NormalizerInterface
from baywatch.domain.models.page import Page


class BaseNormalizer(NormalizerInterface):
    def normalize(self, page: Page) -> str:
        return page.data
