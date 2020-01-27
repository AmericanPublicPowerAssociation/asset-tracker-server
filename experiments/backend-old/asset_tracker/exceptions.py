class AssetTrackerError(Exception):
    pass


class DatabaseRecordError(IOError, AssetTrackerError):
    pass


class FileUploadError(IOError, AssetTrackerError):
    pass
