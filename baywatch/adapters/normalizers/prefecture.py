import re

from baywatch.domain.models.page import Page

from .base import NormalizerInterface


class PrefectureNormalizer(NormalizerInterface):
    def normalize(self, page: Page) -> str:
        result = re.sub(
            r' content=".*" ',
            "",
            page.data,
            flags=re.MULTILINE,
        )
        return result
