# import json
# import logging
# from dataclasses import asdict
# from datetime import datetime, date
# from pprint import pprint
# from typing import Optional, Generator, Dict
# from urllib.parse import urljoin
#
# import cloudscraper
#
# from ..constants import Source
# from ..errors import InvalidSourceError
# from ..models import Chapter, Page
#
# logger = logging.getLogger("scrapers:mangahub")
#
#
# class MangahubScraper:
#     SOURCE = Source.MANGAHUB
#
#     GRAPHQL_QUERY_URL: str = "https://api.mghubcdn.com/graphql"
#
#     IMAGE_BASE_URL: str = "https://img.mghubcdn.com/file/imghub"
#
#     QUERIES: Dict[str, str] = {
#         "search": "{alias}:search(q:\"{query}\",limit:10){{rows{{id,title,slug,rank,latestChapter,updatedDate}}}}",
#         "manga": "{alias}:manga(slug:\"{manga_slug}\"){{id,rank,title,updatedDate,chapters{{id,number,title,date,slug}}}}",
#         "chapter": "{alias}:chapter(slug:\"{manga_slug}\",number:{chapter_num}){{number,title,pages}}"
#     }
#
#     def _clean_query_kwargs(self, kwargs):
#         defaults = {"alias": "alias"}
#         defaults.update(kwargs)
#         kwargs = {k: v.replace('"', '\\"') for k, v in defaults.items()}
#         return kwargs
#
#     def _build_query(self, query_key: str, **kwargs) -> Dict[str, str]:
#         kwargs = self._clean_query_kwargs(kwargs)
#         return {"query": f"{{{self.QUERIES[query_key].format(**kwargs)}}}"}
#
#     def _build_multi_query(self, *queries) -> Dict[str, str]:
#         built_queries = [self.QUERIES[query_key].format(**self._clean_query_kwargs(kwargs))
#                          for query_key, kwargs in queries]
#         multi_query_str = ",".join(built_queries)
#         return {"query": f"{{{multi_query_str}}}"}
#
#     def chapter_image_links(self, chapter: Chapter) -> Chapter:
#         """
#         Returns chapter with pages given chapter
#         :param chapter: Chapter
#         :return: chapter with pages
#         """
#         if chapter.source != self.SOURCE:
#             raise InvalidSourceError()
#         if "source_num" not in chapter.additional_props:
#             raise ValueError("Missing \"source_name\" in \"additional_props\"")
#         if "manga_slug" not in chapter.additional_props:
#             raise ValueError("Missing \"manga_slug\" in \"additional_props\"")
#
#         with cloudscraper.create_scraper() as sess:
#             alias = "chapter"
#             query = self._build_query("chapter", alias=alias,
#                                       manga_slug=chapter.additional_props["manga_slug"],
#                                       chapter_num=str(chapter.additional_props["source_num"]))
#             resp = sess.post(self.GRAPHQL_QUERY_URL, json=query)
#             raw_pages_str = resp.json()["data"][alias]["pages"]
#
#         raw_pages_index_lookup = json.loads(raw_pages_str)
#         pages = [Page(urljoin(self.IMAGE_BASE_URL, v))
#                  for k, v in sorted(raw_pages_index_lookup.items(), key=lambda x: int(x[0]))]
#         chapter_with_pages = Chapter(**{**asdict(chapter), "pages": pages})
#         return chapter_with_pages
#
#     def all_chapters(self, source: str, since: date = None, with_pages: bool = False) -> Generator[Chapter, None, None]:
#         """
#         TODO: instead of source as a link, pass in a Manga object
#         Generator for every chapter for a given manga source link (optionally since a certain upload date)
#         Silently ignores errors if possible.
#         :param source: slug of manga (Mangahub
#         :param since: filter for upload dates later than given value
#         :param with_pages: whether to include chapter pages with chapter
#         :return: generator for every chapter for a given manga source link (optionally since a certain upload date)
#         """
#         with cloudscraper.create_scraper() as sess:
#             alias = "manga"
#             resp = sess.post(self.GRAPHQL_QUERY_URL, json=self._build_query("manga", alias=alias, manga_slug=source))
#             raw_chapters = resp.json()["data"][alias]["chapters"]
#
#             chapter_list = []
#             for ind, raw_chapter in enumerate(raw_chapters):
#                 num = len(raw_chapters) - ind - 1
#                 name = f"Chapter {raw_chapter['number']}"  # Custom name for better cleanliness
#                 upload_date = datetime.fromisoformat(raw_chapter["date"].removesuffix("Z")).date()
#                 link = urljoin(self.SOURCE.base_url, f"/chapter/{source}/{raw_chapter['slug']}") # Dummy
#                 chapter = Chapter(name, num, link, upload_date, self.SOURCE,
#                                   additional_props={"source_num": raw_chapter["number"], "manga_slug": source})
#                 if since is None or chapter.updated_at >= since:
#                     chapter_list.append(chapter)
#
#             if with_pages:
#                 query = self._build_multi_query(*[("chapter",
#                                                    dict(alias=f"chapter{ind}",
#                                                         manga_slug=chapter.additional_props["manga_slug"],
#                                                         chapter_num=str(chapter.additional_props["source_num"])))
#                                                   for ind, chapter in enumerate(chapter_list)])
#                 resp = sess.post(self.GRAPHQL_QUERY_URL, json=query)
#
#                 for ind, chapter in enumerate(chapter_list):
#                     raw_pages_str = resp.json()["data"][f"chapter{ind}"]["pages"]
#                     raw_pages_index_lookup = json.loads(raw_pages_str)
#                     pages = [Page(urljoin(self.IMAGE_BASE_URL + "/", v))
#                              for k, v in sorted(raw_pages_index_lookup.items(), key=lambda x: int(x[0]))]
#                     chapter_list[ind] = Chapter(**{**asdict(chapter), "pages": pages})
#
#         for chapter in chapter_list:
#             yield chapter
#
#     def search(self, *names) -> Optional[str]:
#         """
#         Search the source site for a manga that matches any of the given names
#         :param names: a collection of potential names for the manga
#         :return: the slug of the manga of the first matching result or None if none could be found
#         """
#         search_query = self._build_multi_query(*[("search", {"query": name, "alias": f"search{ind}"})
#                                                  for ind, name in enumerate(names)])
#
#         with cloudscraper.create_scraper() as sess:
#             resp = sess.post(self.GRAPHQL_QUERY_URL, json=search_query)
#             resp_data = resp.json()
#
#         maybe_link = next((next((result["slug"]
#                                  for result in resp_data["data"][f"search{ind}"]["rows"]
#                                  if result["title"].lower() == name.lower()), None)
#                            for ind, name in enumerate(names)), None)
#         return maybe_link