class AppError(Exception):
    """ Base class for all application-level errors. """
    user_msg = "發生未知錯誤"
    
    def __init__(self, msg=None):
        super().__init__(msg or self.user_msg)


class DBError(AppError):
    user_msg = "註解儲存失敗"


class ImageError(AppError):
    user_msg = "無法取得圖源"


class ResourceNotLoadedError(AppError):
    user_msg = "尚未載入圖片資源"


class PathError(AppError):
    user_msg = "檔案路徑錯誤"

