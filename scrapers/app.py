import socketio
from aiohttp import web

from scrapers.content_sources.asurascans import AsuraScansScraper
from scrapers.content_sources.base import ScanlatorScraper
from scrapers.models.common import MangaSource
from scrapers.models.kitsu import Manga
from scrapers.schemas import load_data

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
    selected_manga: Manga = load_data(data['selected'], 'Manga')
    source: MangaSource = MangaSource[data['source'].upper()]

    scraper = content_sources[source]
    search_results = await scraper.search(selected_manga)
    return {'data': search_results}

if __name__ == '__main__':
    web.run_app(app)