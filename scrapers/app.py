import socketio
from aiohttp import web

from scrapers.content_sources.asurascans import AsuraScansScraper
from scrapers.content_sources.base import ScanlatorScraper
from scrapers.models.common import MangaSource
from scrapers.models.kitsu import Manga, MangaShort
from scrapers.schemas import MangaSchema, MangaShortSchema, SearchResultSchema

sio = socketio.AsyncServer()

app = web.Application()

sio.attach(app)


async def index(request):
    # with open('index.html') as f:
    #     return web.Response(text=f.read(), content_type='text/html')
    return web.Response(text="hello world")


content_sources: dict[MangaSource, ScanlatorScraper] = {
    MangaSource.ASURASCANS: AsuraScansScraper()
}

app.router.add_get('/', index)

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

if __name__ == '__main__':
    web.run_app(app)