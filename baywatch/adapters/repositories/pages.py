import pathlib


class PageRepository:
    def save(self, data: str, filepath: str):
        path = pathlib.Path(filepath)

        with path.open("wt") as file:
            file.write(data)

    def load(self, filepath: str) -> str:
        path = pathlib.Path(filepath)

        with path.open("r") as file:
            contents = file.read()

        return contents
