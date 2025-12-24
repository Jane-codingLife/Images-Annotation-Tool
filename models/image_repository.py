""" 圖片儲存庫 【.jpg/.png/.jpeg】
 - where images
 - which images
 - get images
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageRepository:
    def __init__(self, folder_path):
        # 初始化
        self.folder = Path(folder_path)
        self.images = self._load_images()

        logger.info(f"ImageRepository initialized，圖片數量={len(self.images)}")

    def _load_images(self):
        # 載入資料夾中的所有圖片
        try:
            # assert 開發測試，問題直接報錯結束程式。
            # .exist()s => 路徑   .is_dir() => 資料夾    .is_file() => 檔案
            assert self.folder.exists(), "資料夾不存在"
            assert self.folder.is_dir(), "路徑不是資料夾"

            # .iterdir() => 列出資料夾內容
            # .suffix => 副檔名    .name => 檔名(含副檔名)   .stem => 純檔名
            images = sorted([
                p for p in self.folder.iterdir()
                if p.suffix.lower() in (".jpg", ".png", ".jpeg")
            ])

            assert len(images) > 0, "資料夾內沒有圖片"

            return images

        except AssertionError:
            # 接收並記錄 assert 的錯誤點
            logger.exception("AssertionError：圖片來源假設不成立")
            raise

        except Exception:
            # 其他錯誤情況
            logger.error("載入圖片失敗", exc_info=True)
            raise

    def __len__(self):
        # 實作 Python 的內建協定。
        return len(self.images)

    def get(self, index):
        # 取得單張圖片
        try:
            assert isinstance(index, int), "index 必須是整數"
            assert 0 <= index < len(self.images), "index 超出範圍"

            path = self.images[index]
            logger.debug(f"取得圖片索引偏移量={index}, 圖片位置={path}")
            return path

        except AssertionError:
            logger.exception("AssertionError：圖片 index 假設不成立")
            raise


if __name__ == "__main__":
    repo = ImageRepository(r"../comic/Devil's Candy")
    print("圖片總數:", len(repo))
    print(repo.images)
    print(repo.images[3])
    print(repo.get(5))
