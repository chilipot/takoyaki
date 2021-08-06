from dataclasses import dataclass, field
from datetime import date
from typing import Optional, List, Dict, ClassVar, Tuple

from jsonapi_client.resourceobject import ResourceObject

from manga_scraper.constants import Source

"""
Aggregator dataclasses
"""


@dataclass()
class Page:
    link: str = field(compare=False, hash=True)
    num: int

    def to_dict(self) -> dict:
        return {
            'link': self.link,
            'num': self.num
        }


@dataclass()
class Chapter:
    name: str
    num: int  # This is the ordered place in the chapter list
    rel_link: str  # Relative URI to chapter view with page images
    updated_at: Optional[date]
    source: Source
    additional_props: Dict = field(default_factory=dict)
    pages: Optional[List[Page]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'num': self.num,
            'reLink': self.rel_link,
            'updatedAt': self.updated_at.isoformat(),
            'source': self.source.name,
            'additionalProps': self.additional_props,
            'pages': [page.to_dict() for page in self.pages]
        }


"""
METADATA dataclasses
"""


@dataclass()
class Genres:
    name: str
    slug: str
    description: str

    field_names: ClassVar[Tuple[str]] = 'name', 'slug', 'description'

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'slug': self.slug,
            'description': self.description
        }

    @staticmethod
    def resource_to_dict(resource: ResourceObject) -> dict:
        return {
            'name': resource.name,
            'slug': resource.slug,
            'description': resource.description
        }


@dataclass()
class Categories:
    title: str
    description: str
    slug: str
    image: str

    field_names: ClassVar[Tuple[str]] = 'title', 'description', 'slug', 'image'

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'image': self.image
        }

    @staticmethod
    def resource_to_dict(resource: ResourceObject) -> dict:
        return {
            'title': resource.title,
            'slug': resource.slug,
            'description': resource.description,
            'image': resource.image
        }


@dataclass()
class Manga:
    """
    Python class wrapper of required Kitsu Manga fields.
    """
    id: str
    slug: str
    synopsis: str
    canonical_title: str
    titles: Dict[str, str]
    titles_array: List[str]
    abbreviated_titles: List[str]
    average_rating: str
    manga_type: str
    subtype: str
    status: str
    poster_image: Dict[str, str]
    categories: List[Categories]
    genres: List[Genres]

    field_names: ClassVar[Tuple[str]] = 'id', 'slug', 'synopsis', 'canonicalTitle', 'titles', 'abbreviatedTitles', \
                                        'averageRating', 'mangaType', 'subtype', 'status', 'posterImage', 'categories', \
                                        'genres'

    def to_dict(self) -> dict:
        """
        Avoid having to recursively building the dataclass.
        Keys are in camelCase for easier use on the frontend.
        """
        return {
            'id': self.id,
            'slug': self.slug,
            'synopsis': self.synopsis,
            'canonicalTitle': self.canonical_title,
            'titles': self.titles,
            'titles_array': list(self.titles.values()),
            'abbreviatedTitles': self.abbreviated_titles,
            'averageRating': self.average_rating,
            'mangaType': self.manga_type,
            'subtype': self.subtype,
            'status': self.status,
            'posterImage': self.poster_image,
            'categories': [category.to_dict() for category in self.categories],
            'genres': [genre.to_dict() for genre in self.genres]
        }

    @staticmethod
    def resource_to_dict(resource: ResourceObject) -> dict:
        """
        Takes in the JSON:API Resource object directly instead of wasting time instantiating this model
        """
        return {
            'id': resource.id,
            'slug': resource.slug,
            'synopsis': resource.synopsis,
            'canonicalTitle': resource.canonicalTitle,
            'titles': resource.titles,
            'titles_array': list(resource.titles.values()),
            'abbreviatedTitles': resource.abbreviatedTitles,
            'averageRating': resource.averageRating,
            'mangaType': resource.mangaType,
            'subtype': resource.subtype,
            'status': resource.status,
            'posterImage': {size: link for size, link in resource.posterImage.items() if
                            size != 'meta'} if resource.posterImage else None,
            'categories': [Categories.resource_to_dict(category) for category in
                           resource.categories.resources] if resource.relationships.categories else [],
            'genres': [Genres.resource_to_dict(genre) for genre in
                       resource.genres.resources] if resource.relationships.genres else []
        }
