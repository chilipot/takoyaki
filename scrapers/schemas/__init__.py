from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField

from scrapers.models.aggregator import SearchResult, Chapter
from scrapers.models.common import MangaSource, MangaStatus, MangaType
from scrapers.models.kitsu import Genre, Category, Manga, MangaShort


class SearchResultSchema(Schema):
    id = fields.Str()
    source = EnumField(MangaSource)
    title = fields.Str()
    poster_image = fields.Str()
    latest_chapter = fields.Str()
    details_link = fields.Str()

    @post_load
    def make_search_result(self, data, **kwargs):
        return SearchResult(**data)


class GenreSchema(Schema):
    name = fields.Str()
    slug = fields.Str()
    description = fields.Str()

    @post_load
    def make_genre(self, data, **kwargs):
        return Genre(**data)


class CategorySchema(Schema):
    title = fields.Str()
    description = fields.Str()
    slug = fields.Str()
    image = fields.Str()

    @post_load
    def make_category(self, data, **kwargs):
        return Category(**data)


class MangaSchema(Schema):
    id = fields.Str()
    slug = fields.Str()
    synopsis = fields.Str()
    canonical_title = fields.Str()
    titles = fields.Dict(keys=fields.Str(), values=fields.Str())
    titles_array = fields.List(fields.Str())
    abbreviated_titles = fields.List(fields.Str())
    average_rating = fields.Str()
    manga_type = EnumField(MangaType)
    subtype = EnumField(MangaType)
    status = EnumField(MangaStatus)
    poster_image = fields.Dict(keys=fields.Str(), values=fields.Str())
    categories = fields.List(fields.Nested(CategorySchema))
    genres = fields.List(fields.Nested(GenreSchema))

    @post_load
    def make_manga(self, data, **kwargs):
        return Manga(**data)


class MangaShortSchema(Schema):
    id = fields.Str()
    slug = fields.Str()
    canonical_title = fields.Str()

    @post_load
    def make_manga_short(self, data, **kwargs):
        return MangaShort(**data)


class ChapterSchema(Schema):
    name = fields.Str()
    num = fields.Int()
    rel_link = fields.Str()
    source = EnumField(MangaSource)

    @post_load
    def make_chapter(self, data, **kwargs):
        return Chapter(**data)
