import enum


class MangaSource(enum.Enum):
    BATOTO = "Bato.to"
    MANGADEX = "Mangadex"
    MANGAHUB = "Mangahub"
    MANGANELO = "Manganelo"
    ASURASCANS = "AsuraScans"


class MangaType(enum.Enum):
    DOUJIN = "Doujin"
    MANGA = "Manga"
    MANHUA = "Manhua"
    MANHWA = "Manhwa"
    NOVEL = "Novel"
    OEL = "OEL"
    ONESHOT = "One-shot"


class MangaStatus(enum.Enum):
    CURRENT = "Current"
    FINISHED = "Finished"
    TBA = "TBA"
    UNRELEASED = "Unreleased"
    UPCOMING = "Upcoming"
    CANCELLED = "Cancelled"
