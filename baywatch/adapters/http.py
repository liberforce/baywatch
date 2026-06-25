import logging
import typing

import requests
import urllib3

LOGGER = logging.getLogger(__name__)


class DataExtractor:
    def extract(self, url: str) -> typing.Optional[str]:
        LOGGER.info("Downloading watched page")
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.8,en-US;q=0.5,en;q=0.3",
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except urllib3.HTTPSConnectionPool as exc:
            LOGGER.error(f"Connection failed: {exc}")
            return None
        else:
            return response.text
