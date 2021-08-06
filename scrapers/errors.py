class InvalidSourceError(Exception):
    pass


class ScrapingFailure(Exception):
    pass


class AccessBlocked(ScrapingFailure):
    "stupid bot protection"
    pass
