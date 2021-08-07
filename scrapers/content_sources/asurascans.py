from typing import List, Union

import aiohttp
from bs4 import BeautifulSoup, Tag

from scrapers.content_sources.base import ScanlatorScraper
from scrapers.models.aggregator import SearchResult, Chapter
from scrapers.models.common import MangaSource
from scrapers.models.kitsu import Manga, MangaShort

HEADERS = {
    'user-agent': ' Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}


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

    @classmethod
    def _map_chapter(cls, item: Tag) -> Chapter:
        anchor = item.find('a')
        return Chapter(
            name=item.get('data-num'),
            num=int(item.get('data-num')),
            rel_link=anchor.get('href'),
            source=cls.SOURCE,
        )

    async def get_chapter_pages(self, chapter: Chapter) -> List[Chapter]:
        pass

    async def get_manga_chapters(self, link: str) -> List[Chapter]:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(link) as resp:
                soup = BeautifulSoup(await resp.text())
                if "Bot Verification" in soup.title.string:
                    return list()
                print(await resp.text())
                chapter_list_items = soup.find('div', id="chapterlist").find_all("li")
                print(f"Found {len(chapter_list_items)} chapters")
                return [self._map_chapter(i) for i in chapter_list_items]

    async def search(self, manga: Union[Manga, MangaShort]) -> list[SearchResult]:
        async with aiohttp.ClientSession() as session:
            query = {'action': 'ts_ac_do_search',
                     'ts_ac_query': manga.canonical_title}
            async with session.post(url=self._SEARCH_URL, data=query) as resp:
                json_data = await resp.json(content_type=None)  # disable content-type check since it will never match
                results = json_data['series'][0]['all']
                print(f"Found {len(results)} results")
                return [self._map_search_result(r) for r in results]
