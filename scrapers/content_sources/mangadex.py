# import logging
# from concurrent.futures.thread import ThreadPoolExecutor
# from dataclasses import asdict
# from datetime import datetime, date
# from pprint import pprint
# from typing import Optional, Generator
# from urllib.parse import urljoin
#
# import requests
# from bs4 import BeautifulSoup
#
# from manga_scraper.constants import Source
# from manga_scraper.errors import InvalidSourceError
# from manga_scraper.image_scrapers.base import ImageScraper
# from manga_scraper.models import Chapter, Page
#
# logger = logging.getLogger("manual_scrapers:mangadex")
#
#
# class MangadexScraper(ImageScraper):
#     SOURCE = Source.MANGADEX
#
#     def _parse_updated_at(self, date_str: str) -> Optional[date]:
#         try:
#             return datetime.strptime(date_str, '%b %d,%y').date()
#         except ValueError:
#             return None
#
#     def _search(self, name) -> Optional[str]:
#         """
#         Runs a search on the site for given manga name and returns the URI of the manga page.
#         :param name: the name of a manga
#         :return: the URI of the manga on the site or None if could not be found
#         """
#         resp = requests.get(f"{self.SOURCE.base_url}/search", params={"type": "titles", "title": name.lower()})
#         soup = BeautifulSoup(resp.text, "lxml")
#         maybe_link = next((x.attrs.get("href")
#                            for x in soup.find_all(class_="manga_title")
#                            if x.text.lower() == name.lower()), None)
#         return maybe_link
#
#     def chapter_image_links(self, chapter: Chapter) -> Chapter:
#         """
#         Returns chapter with pages given chapter
#         :param chapter: Chapter
#         :return: chapter with pages
#         """
#         if chapter.source != self.SOURCE:
#             raise InvalidSourceError()
#         resp = requests.get(urljoin(self.SOURCE.base_url, chapter.rel_link))
#         soup = BeautifulSoup(resp.text, "lxml")
#         page_images = [(wrapper.attrs.get('data-page'),wrapper.findChild("img")) for wrapper in soup.find_all(class_="reader-image-wrapper")]
#         pages = [Page(img.attrs.get("src") or img.attrs.get("data-src"), num) for num, img in page_images if img]
#         chapter_with_pages = Chapter(**{**asdict(chapter), "pages": pages})
#         return chapter_with_pages
#
#     def all_chapters(self, source: str, since: date = None, with_pages: bool = False) -> list[Chapter]:
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
#         soup = BeautifulSoup(resp.text, "lxml")
#         chapter_rows = soup.find_all(class_="chapter-row")[1:]
#
#         chapter_list = []
#         for ind, raw_chapter in enumerate(chapter_rows):
#             num = len(chapter_rows) - ind - 1
#             link = raw_chapter.findChild("a")
#             elements = [x.text.strip() for x in raw_chapter.findChildren("div") if x.text.strip()]
#             if len(elements) != 3 or not link.attrs.get("href"):
#                 logger.warning(f"Unknown chapter elements found while scraping chapter: {num}")
#                 continue
#             name, upload_date, view_count = elements
#             chapter = Chapter(name, num, link.attrs.get("href"), self._parse_updated_at(upload_date), self.SOURCE)
#             if since is None or chapter.updated_at >= since:
#                 chapter_list.append(chapter)
#
#         if with_pages:
#             def add_pages(i):
#                 chapter_list[i] = self.chapter_image_links(chapter_list[i])
#
#             with ThreadPoolExecutor() as executor:
#                 executor.map(add_pages, list(range(len(chapter_list))))
#
#         return chapter_list
#
#     def search(self, *names) -> Optional[str]:
#         """
#         Search the source site for a manga that matches any of the given names
#         :param names: a collection of potential names for the manga
#         :return: the URI to the manga page of the first matching result or None if none could be found
#         """
#         for result in map(self._search, names):
#             if result is not None:
#                 return result
#
# if __name__ == '__main__':
#     m = MangadexScraper()
#     s = m.search("Solo Leveling")
#     pprint([p for p in m.all_chapters(s, with_pages=True)])