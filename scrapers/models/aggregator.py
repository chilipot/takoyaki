from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from scrapers.models.common import MangaSource


@dataclass()
class Chapter:
    name: str  # This is the chapter title ex: V2. Ch. 321
    num: int  # This is the ordered place in the chapter list
    rel_link: str  # Relative URI to chapter view with page images
    source: MangaSource

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'num': self.num,
            'reLink': self.rel_link,
            'source': self.source.name,
        }


@dataclass()
class Page:
    link: str = field(compare=False, hash=True)
    num: int

    def to_dict(self) -> dict:
        return {
            'link': self.link,
            'num': self.num
        }


@dataclass()
class SearchResult:
    id: str  # IDK the use for this yet but seems important
    source: MangaSource
    title: str
    poster_image: str
    latest_chapter: str  # chapter number is weird so just keep that weird format as a string
    details_link: str  # scrape the anchor href
