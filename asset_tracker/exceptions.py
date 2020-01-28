class AssetTrackerError(Exception):
    pass


class DatabaseRecordError(IOError, AssetTrackerError):
    pass
