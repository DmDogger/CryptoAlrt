class ApplicationError(Exception):
    pass


class UseCaseError(ApplicationError):
    pass


class HistoricalPriceError(ApplicationError):
    pass


class CurrentPriceNotExist(ApplicationError):
    pass
