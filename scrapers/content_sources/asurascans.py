from datetime import date
from typing import List, Union

import aiohttp

from scrapers.content_sources.base import ScanlatorScraper
from scrapers.models.aggregator import SearchResult, Chapter
from scrapers.models.common import MangaSource
from scrapers.models.kitsu import Manga, MangaShort


class AsuraScansScraper(ScanlatorScraper):
    SOURCE = MangaSource.ASURASCANS
    _SEARCH_URL = "https://www.asurascans.com/wp-admin/admin-ajax.php"

    @classmethod
    def _map_search_result(cls, raw) -> SearchResult:
        return SearchResult(
            id=raw['ID'],
            source=cls.SOURCE,
            title=raw['post_title'],
            poster_image=raw['post_image'],
            latest_chapter=raw['post_latest'],
            details_link=raw['post_link']
        )

    async def get_chapter_pages(self, chapter: Chapter) -> List[Chapter]:
        pass

    async def get_manga_chapters(self, source: str, since: date = None) -> List[Chapter]:
        pass

    async def search(self, manga: Union[Manga, MangaShort]) -> list[SearchResult]:
        async with aiohttp.ClientSession() as session:
            query = {'action': 'ts_ac_do_search',
                     'ts_ac_query': manga.canonical_title}
            async with session.post(url=self._SEARCH_URL, data=query) as resp:
                json_data = await resp.json(content_type=None)  # disable content-type check since it will never match
                results = json_data['series'][0]['all']
                print(f"Found {len(results)} results")
                return [self._map_search_result(r) for r in results]
