from abc import ABC, abstractmethod
from datetime import date
from typing import List, Union

from scrapers.models.aggregator import SearchResult, Chapter
from scrapers.models.common import MangaSource
from scrapers.models.kitsu import Manga, MangaShort


class ScanlatorScraper(ABC):
    SOURCE: MangaSource = None

    @abstractmethod
    async def get_chapter_pages(self, chapter: Chapter) -> List[Chapter]:
        pass

    @abstractmethod
    async def get_manga_chapters(self, source: str, since: date = None) -> List[Chapter]:
        """
        Scrapes chapter data - links, ordering, names, etc.
        Does not open links and scrape page data.
        """
        pass

    @abstractmethod
    async def search(self, manga: Union[Manga, MangaShort]) -> list[SearchResult]:
        pass
