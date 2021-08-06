from datetime import date
from typing import Generator, Optional, List

from manga_scraper.constants import Source
from manga_scraper.models import Chapter


class ImageScraper:
    SOURCE = Source

    def chapter_image_links(self, chapter: Chapter) -> Chapter:
        pass

    def all_chapters(self, source:str, since: date = None, with_pages: bool = False) -> List[Chapter]:
        pass

    def search(self, *names) -> Optional[str]:
        pass