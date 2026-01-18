""" 圖片儲存庫 【.jpg/.png/.jpeg】
 - where images
 - which images
 - get images
"""

import logging
from pathlib import Path
from config.errors import PathError, ImageError

logger = logging.getLogger(__name__)


class ImageRepository:
    def __init__(self, folder_path):
        # 初始化
        try:
            folder_path = Path(folder_path)
        except Exception:
            logger.exception(f"轉換 Path 失敗: {folder_path}")
            raise PathError()
        if not folder_path.is_dir():
            logger.exception(f"路徑非資料夾: {folder_path}")
            raise PathError(f"{folder_path} 非資料夾路徑。")

        self.folder = folder_path
        self.images = self._load_images()

        logger.info(f"ImageRepository initialized，圖片數量={len(self.images)}")

    def _load_images(self):
        # 載入資料夾中的所有圖片
        try:
            # .iterdir() => 列出資料夾內容
            # .suffix => 副檔名    .name => 檔名(含副檔名)   .stem => 純檔名
            images = sorted([
                p for p in self.folder.iterdir()
                if p.suffix.lower() in (".jpg", ".png", ".jpeg")
            ])
            return images

        except Exception:
            logger.error("載入圖片失敗", exc_info=True)
            raise ImageError()

    def __len__(self):
        # 實作 Python 的內建協定。
        return len(self.images)

    def get(self, index):
        # 取得單張圖片
        try:
            path = self.images[index]
            logger.debug(f"取得圖片索引偏移量={index}, 圖片位置={path}")
            return path

        except Exception:
            logger.exception("AssertionError：圖片 index 假設不成立")
            raise ImageError()
