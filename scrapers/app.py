import json

import socketio
from aiohttp import web

from scrapers.content_sources.asurascans import AsuraScansScraper
from scrapers.content_sources.base import ScanlatorScraper
from scrapers.models.aggregator import SearchResult, Chapter
from scrapers.models.common import MangaSource
from scrapers.models.kitsu import MangaShort
from scrapers.schemas import MangaShortSchema, SearchResultSchema, ChapterSchema, PageSchema

sio = socketio.AsyncServer()

app = web.Application()

sio.attach(app)


async def index(request):
    # with open('index.html') as f:
    #     return web.Response(text=f.read(), content_type='text/html')
    return web.Response(text="hello world")


async def manga_sources(request):
    available_sources = json.dumps({s.name: s.value for s in MangaSource})
    return web.Response(text=available_sources, content_type="application/json")


content_sources: dict[MangaSource, ScanlatorScraper] = {
    MangaSource.ASURASCANS: AsuraScansScraper()
}

app.router.add_get('/', index)
app.router.add_get('/manga-sources', manga_sources)

"""
WebSocket endpoints
"""


@sio.on('search_event')
async def search_event_handler(sid, data):
    name = data['name']
    print(f"User {sid} requested {name}")
    # call kitsu api


@sio.on('retrieve_manga_results')
async def pull_manga_results_from_scrapers(sid, data):
    manga_short_schema = MangaShortSchema()
    selected_manga: MangaShort = manga_short_schema.load(data['selected'])
    source: MangaSource = MangaSource[data['source'].upper()]

    scraper = content_sources[source]
    search_results = await scraper.search(selected_manga)
    search_result_schema = SearchResultSchema(many=True)
    await sio.emit('retrieve_manga_results', {'data': search_result_schema.dump(search_results)}, to=sid)


@sio.on('retrieve_manga_chapters')
async def scrape_available_chapters(sid, data):
    search_result_schema = SearchResultSchema()
    selected_result: SearchResult = search_result_schema.load(data['selected'])
    source = selected_result.source

    scraper = content_sources[source]
    chapters = await scraper.get_manga_chapters(selected_result.details_link)
    chapter_schema = ChapterSchema(many=True)
    await sio.emit('retrieve_manga_chapters', {'data': chapter_schema.dump(chapters)}, to=sid)


@sio.on('retrieve_chapter_pages')
async def scrape_chapter_pages(sid, data):
    chapter_schema = ChapterSchema()
    selected_chapter: Chapter = chapter_schema.load(data['selected'])
    source = selected_chapter.source

    scraper = content_sources[source]
    pages = await scraper.get_chapter_pages(selected_chapter)
    page_schema = PageSchema(many=True)
    await sio.emit('retrieve_chapter_pages', {'data': page_schema.dump(pages)}, to=sid)


if __name__ == '__main__':
    web.run_app(app)
