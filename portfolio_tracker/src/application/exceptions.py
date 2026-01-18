class ApplicationError(Exception):
    pass


class UseCaseError(ApplicationError):
    pass


class HistoricalPriceError(ApplicationError):
    pass


class CurrentPriceNotExist(ApplicationError):
    pass


class TotalValueUnableToCalculate(ApplicationError):
    pass


class AnalyticsDataIsEmpty(ApplicationError):
    pass


class AssetNotExist(ApplicationError):
    pass


class AssetUpdatingError(ApplicationError):
    pass
