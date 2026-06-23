import abc

from baywatch.domain.models.page import Page


class NormalizerInterface(abc.ABC):
    @abc.abstractmethod
    def normalize(self, page: Page) -> str: ...
