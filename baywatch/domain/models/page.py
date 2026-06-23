import hashlib


class Page:
    def __init__(self, data: str):
        self.data = data

    @property
    def digest(self) -> str:
        hasher = hashlib.md5()
        hasher.update(self.data.encode("utf-8"))
        return hasher.hexdigest()
