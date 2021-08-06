from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from scrapers.models.common import MangaSource


@dataclass()
class Chapter:
    name: str  # This is the chapter title ex: V2. Ch. 321
    num: int  # This is the ordered place in the chapter list
    rel_link: str  # Relative URI to chapter view with page images
    updated_at: Optional[date]
    source: MangaSource
    additional_props: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'num': self.num,
            'reLink': self.rel_link,
            'updatedAt': self.updated_at.isoformat(),
            'source': self.source.name,
            'additionalProps': self.additional_props,
        }


@dataclass()
class Page:
    chapter: Chapter # backref, not sure if necessary
    link: str = field(compare=False, hash=True)
    num: int

    def to_dict(self) -> dict:
        return {
            'link': self.link,
            'num': self.num
        }


@dataclass
class SearchResult:
    id: int  # IDK the use for this yet but seems important
    source: MangaSource
    title: str
    poster_image: str
    latest_chapter: str  # chapter number is weird so just keep that weird format as a string
    details_link: str  # scrape the anchor href
