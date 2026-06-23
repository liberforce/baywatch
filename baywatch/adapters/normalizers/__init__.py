from baywatch.domain.interfaces.normalizer import NormalizerInterface

from .base import BaseNormalizer
from .prefecture import PrefectureNormalizer


def make_normalizer(kind: str) -> NormalizerInterface:
    if kind == "prefecture":
        return PrefectureNormalizer()

    return BaseNormalizer()


__all_ = [
    BaseNormalizer,
    PrefectureNormalizer,
]
