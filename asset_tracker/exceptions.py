class AssetTrackerError(Exception):
    pass


class DatabaseRecordError(IOError, AssetTrackerError):
    pass


class DataValidationError(ValueError, AssetTrackerError):
    pass
