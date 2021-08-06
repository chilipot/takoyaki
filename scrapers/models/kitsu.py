from dataclasses import dataclass
from typing import ClassVar, Tuple

from jsonapi_client.resourceobject import ResourceObject

from scrapers.models.common import MangaType, MangaStatus


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

    field_names: ClassVar[tuple[str]] = 'title', 'description', 'slug', 'image'

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
    titles: dict[str, str]
    titles_array: list[str]
    abbreviated_titles: list[str]
    average_rating: str
    manga_type: MangaType
    subtype: MangaType
    status: MangaStatus
    poster_image: dict[str, str]
    categories: list[Categories]
    genres: list[Genres]

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
            'mangaType': self.manga_type.value(),
            'subtype': self.subtype.value(),
            'status': self.status.value(),
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
            'mangaType': MangaType[resource.mangaType.upper()],
            'subtype': MangaType[resource.subtype.upper],
            'status': MangaStatus[resource.status.upper],
            'posterImage': {size: link for size, link in resource.posterImage.items() if
                            size != 'meta'} if resource.posterImage else None,
            'categories': [Categories.resource_to_dict(category) for category in
                           resource.categories.resources] if resource.relationships.categories else [],
            'genres': [Genres.resource_to_dict(genre) for genre in
                       resource.genres.resources] if resource.relationships.genres else []
        }
