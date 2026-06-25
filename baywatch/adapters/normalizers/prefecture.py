import re

from baywatch.domain.models.page import Page

from .base import NormalizerInterface


class PrefectureNormalizer(NormalizerInterface):
    def normalize(self, page: Page) -> str:
        result = page.data
        result = re.sub(
            r' content=".*" ',
            "",
            result,
            flags=re.MULTILINE,
        )
        result = re.sub(
            r'"prendre_rdv',
            r'"https://rdv.anct.gouv.fr/prendre_rdv',
            result,
            flags=re.MULTILINE,
        )
        result = re.sub(
            r'"/assets/[^"]*"',
            r'"/assets/"',
            result,
            flags=re.MULTILINE,
        )
        return result
