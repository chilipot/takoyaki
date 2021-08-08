# import logging
# import re
# from concurrent.futures.thread import ThreadPoolExecutor
# from dataclasses import asdict
# from datetime import datetime, date, timedelta
# from functools import partial
# from typing import Optional, Generator
# from urllib.parse import urljoin
#
# import nest_asyncio
# import requests
# from bs4 import BeautifulSoup, SoupStrainer
#
# from .. import dynamic_requests_session
# from ..constants import Source
# from ..errors import InvalidSourceError
# from ..models import Chapter, Page
#
# logger = logging.getLogger("scrapers:batoto")
#
# nest_asyncio.apply()
#
#
# class BatotoScraper:
#     SOURCE = Source.BATOTO
#
#     CHAPTER_NUM_REGEX = r"Ch\.(\d+(?:\.\d+)?)"
#
#     PAGE_GRAB_CHUNK_SIZE = 150
#
#     def _parse_updated_at(self, date_str: str) -> date:
#         try:
#             days_ago = int(date_str.split(" days ago", 1)[0])
#             return datetime.now().date() - timedelta(days=days_ago)
#         except ValueError:
#             return datetime.now().date()  # use current date as sensible default
#
#     def _parse_chapter_count(self, chapter_count_elem) -> Optional[float]:
#         if chapter_count_elem is None:
#             return None
#         # Remove trailing last upload date and extra whitespace
#         raw_chapter_count = chapter_count_elem.text.strip().split("\n", 1)[0].strip()
#
#         # Parse chapter number (could be integer or float)
#         match = re.search(self.CHAPTER_NUM_REGEX, raw_chapter_count)
#         return match and float(match.groups()[0])
#
#     def _search(self, name) -> Optional[str]:
#         """
#         Runs a search on the site for given manga name and returns the URI of the manga page.
#         :param name: the name of a manga
#         :return: the URI of the manga on the site or None if could not be found
#         """
#         resp = requests.get(f"{self.SOURCE.base_url}/search", params={"word": name})
#         soup = BeautifulSoup(resp.text, "lxml", parse_only=SoupStrainer(id="series-list"))
#
#         # Find the result with the highest chapter count that matches the searched name and return its link
#         best_english_result = None
#         max_chapter_count = -1
#         for result in soup.find_all(class_="no-flag"):
#             title_elem = result.find(class_="item-title")
#             if title_elem is None:
#                 continue
#             title = title_elem.text
#             link = title_elem.attrs.get("href")
#             chapter_count = self._parse_chapter_count(result.find(class_="item-volch"))
#             if title.lower() == name.lower() and link is not None \
#                     and chapter_count is not None and chapter_count > max_chapter_count:
#                 max_chapter_count = chapter_count
#                 best_english_result = link
#         return best_english_result
#
#     def _parse_chapter_image_links(self, chapter, resp):
#         soup = BeautifulSoup(resp.html.html, "lxml", parse_only=SoupStrainer(id="viewer"))
#         page_images = soup.find_all("img")
#         pages = [Page(img.attrs.get("src")) for img in page_images]
#         chapter_with_pages = Chapter(**{**asdict(chapter), 'pages': pages})
#         return chapter_with_pages
#
#     def chapter_image_links(self, chapter: Chapter) -> Chapter:
#         """
#         Returns chapter with pages given chapter
#         :param chapter: Chapter
#         :return: chapter with pages
#         """
#         if chapter.source != self.SOURCE:
#             raise InvalidSourceError()
#
#         with dynamic_requests_session() as session:
#             resp = session.get(urljoin(self.SOURCE.base_url, chapter.rel_link))
#             resp.html.render()
#         return self._parse_chapter_image_links(chapter, resp)
#
#     def all_chapters(self, source: str, since: date = None, with_pages: bool = False) -> Generator[Chapter, None, None]:
#         """
#         TODO: instead of source as a link, pass in a Manga object
#         Generator for every chapter for a given manga source link (optionally since a certain upload date)
#         Silently ignores errors if possible.
#         :param source: relative URI of manga on site
#         :param since: filter for upload dates later than given value
#         :param with_pages: whether to include chapter pages with chapter
#         :return: generator for every chapter for a given manga source link (optionally since a certain upload date)
#         """
#         resp = requests.get(urljoin(self.SOURCE.base_url, source))
#         soup = BeautifulSoup(resp.text, "lxml", parse_only=SoupStrainer(class_="main"))
#         chapter_rows = soup.find_all(class_="chapt")
#         chapter_list = []
#         for ind, raw_chapter in enumerate(chapter_rows):
#             num = len(chapter_rows) - ind - 1
#             name = raw_chapter.text.strip()
#             link = raw_chapter.attrs.get("href")
#             raw_upload_date = raw_chapter.find_next_sibling(class_="extra").findChild("i").text.strip()
#             chapter = Chapter(name, num, link, self._parse_updated_at(raw_upload_date), self.SOURCE)
#             if since is None or chapter.updated_at >= since:
#                 chapter_list.append(chapter)
#
#         if with_pages:
#             async def get_rendered_page(i, rel_link):
#                 res = await session.get(urljoin(self.SOURCE.base_url, rel_link))
#                 await res.html.arender(timeout=1000)  # Arbitrarily long number cuz why not
#                 chap_with_pages = self._parse_chapter_image_links(chapter_list[i], res)
#                 return i, chap_with_pages
#
#             with dynamic_requests_session(async_session=True) as session:
#                 results = []
#                 for ind in range(0, len(chapter_list), self.PAGE_GRAB_CHUNK_SIZE):
#                     coroutines = [partial(get_rendered_page, i, chap.rel_link)
#                                   for i, chap in enumerate(chapter_list[ind:ind+self.PAGE_GRAB_CHUNK_SIZE])]
#                     if coroutines:
#                         results.extend(session.run(*coroutines))
#
#                 for i, chapter_with_pages in results:
#                     chapter_list[i] = chapter_with_pages
#
#         for chapter in chapter_list:
#             yield chapter
#
#     def search(self, *names) -> Optional[str]:
#         """
#         Search the source site for a manga that matches any of the given names
#         :param names: a collection of potential names for the manga
#         :return: the URI to the manga page of the first matching result or None if none could be found
#         """
#         with ThreadPoolExecutor() as executor:
#             for result in executor.map(self._search, names):
#                 if result is not None:
#                     return result
