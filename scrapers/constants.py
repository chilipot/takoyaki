import functools
from enum import Enum
from urllib.parse import urljoin

# replacing this with the AggregatorSource enum in base.py
# Move the base_urls to the aggregator scraping class itself, no reason for it to be public.
class Source(Enum):
    MANGADEX = "MANGADEX"
    MANGAKAKALOT = "MANGAKAKALOT"
    MANGANELO = "MANGANELO"
    BATOTO = "BATOTO"
    MANGAUPDATES = "MANGAUPDATES"
    MANGAHUB = "MANGAHUB"

    @property
    def base_url(self):
        return {
            self.MANGAKAKALOT: "https://mangakakalot.com",
            self.MANGANELO: "https://manganelo.com",
            self.MANGADEX: "https://mangadex.tv",
            self.BATOTO: "https://bato.to",
            self.MANGAUPDATES: 'https://mangaupdates.com',
            self.MANGAHUB: "https://mangahub.io"
        }[self]

    def path(self, *paths: str):
        paths = [(path.removeprefix("/").removesuffix("/") + "/")
                 if ind < len(paths) - 1 else path.removeprefix("/")
                 for ind, path in enumerate(paths)]
        return functools.reduce(urljoin, paths, self.base_url)
