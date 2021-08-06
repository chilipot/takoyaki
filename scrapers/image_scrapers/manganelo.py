import logging
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import asdict
from datetime import datetime, date
from typing import Optional, Generator
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from ..constants import Source
from ..errors import InvalidSourceError
from ..models import Chapter, Page

logger = logging.getLogger("manual_scrapers:manganelo")


class ManganeloScraper:
    """
    TODO: Fix Image links retrieval from Manganelo, since they're protected by Cloudflare,
          maybe we proxy these via pypuppeteer by visiting the chapter site itself first and then opening the image
    """
    SOURCE = Source.MANGANELO

    def _parse_updated_at(self, date_str: str) -> date:
        try:
            return datetime.strptime(date_str, '%b %d,%y').date()
        except ValueError:
            return datetime.now().date()  # use current date as sensible default

    def _search(self, name) -> Optional[str]:
        """
        Runs a search on the site for given manga name and returns the URI of the manga page.
        :param name: the name of a manga
        :return: the URI of the manga on the site or None if could not be found
        """
        resp = requests.post(f"{self.SOURCE.base_url}/getstorysearchjson", data={"searchword": name.lower()})
        maybe_link = next((f"/manga/{result['id_encode']}"
                           for result in resp.json()
                           if BeautifulSoup(result["name"], "lxml").text.lower() == name.lower()), None)
        return maybe_link

    def chapter_image_links(self, chapter: Chapter) -> Chapter:
        """
        Returns chapter with pages given chapter
        :param chapter: Chapter
        :return: chapter with pages
        """
        if chapter.source != self.SOURCE:
            raise InvalidSourceError()
        resp = requests.get(urljoin(self.SOURCE.base_url, chapter.rel_link))
        soup = BeautifulSoup(resp.text, "lxml")
        page_images = soup.find(class_="container-chapter-reader").findChildren("img")
        pages = [Page(img.attrs.get("src")) for img in page_images if img]
        chapter_with_pages = Chapter(**{**asdict(chapter), "pages": pages})
        return chapter_with_pages

    def all_chapters(self, source: str, since: date = None, with_pages: bool = False) -> Generator[Chapter, None, None]:
        """
        TODO: instead of source as a link, pass in a Manga object
        Generator for every chapter for a given manga source link (optionally since a certain upload date)
        Silently ignores errors if possible.
        :param source: relative URI of manga on site
        :param since: filter for upload dates later than given value
        :param with_pages: whether to include chapter pages with chapter
        :return: generator for every chapter for a given manga source link (optionally since a certain upload date)
        """
        resp = requests.get(urljoin(self.SOURCE.base_url, source))
        soup = BeautifulSoup(resp.text, "lxml")
        chapter_rows = soup.find(class_="row-content-chapter").findChildren("li", class_="a-h")

        chapter_list = []
        for ind, raw_chapter in enumerate(chapter_rows):
            num = len(chapter_rows) - ind - 1
            name_elem = raw_chapter.findChild("a", class_="chapter-name")
            name = name_elem.text
            link = name_elem.attrs.get("href")
            upload_date = raw_chapter.findChild(class_="chapter-time").text
            chapter = Chapter(name, num, link.removeprefix(self.SOURCE.base_url),
                              self._parse_updated_at(upload_date), self.SOURCE)
            if since is None or chapter.updated_at >= since:
                chapter_list.append(chapter)

        if with_pages:
            def add_pages(i):
                chapter_list[i] = self.chapter_image_links(chapter_list[i])

            with ThreadPoolExecutor() as executor:
                executor.map(add_pages, list(range(len(chapter_list))))

        for chapter in chapter_list:
            yield chapter

    def search(self, *names) -> Optional[str]:
        """
        Search the source site for a manga that matches any of the given names
        :param names: a collection of potential names for the manga
        :return: the URI to the manga page of the first matching result or None if none could be found
        """
        with ThreadPoolExecutor() as executor:
            for result in executor.map(self._search, names):
                if result is not None:
                    return result
