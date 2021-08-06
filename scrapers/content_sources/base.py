from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Generator, Optional, List

from scrapers.models.aggregator import SearchResult, Chapter
from scrapers.models.common import MangaSource


class ScanlatorSource(ABC):
    SOURCE = MangaSource

    @abstractmethod
    def chapter_image_links(self, chapter: Chapter) -> List[Chapter]:
        pass

    @abstractmethod
    def all_chapters(self, source: str, since: date = None) -> List[Chapter]:
        """
        Scrapes chapter data - links, ordering, names, etc.
        Does not open links and scrape page data.
        """
        pass

    @abstractmethod
    def search(self, *names) -> list[SearchResult]:
        pass