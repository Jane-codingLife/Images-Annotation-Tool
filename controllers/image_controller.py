import logging
from models import ImageRepository, AnnotationDB
from config.errors import ResourceNotLoadedError

logger = logging.getLogger(__name__)


class ImageAnnotationController:
    def __init__(self, repo: ImageRepository, db: AnnotationDB):
        self.img_repo = repo
        self.db = db

        logger.info(f"Controller initialized: ImageRepository and SQLiteDB succeed.")

    # ========= 資料處理(V+N) =========
    def get_total_count(self) -> dict:
        return {
            "success": True,
            "total_count": len(self.img_repo)
        }

    def get_all_images(self) -> dict:
        # 取得所有的圖檔路徑
        imgs = [str(img) for img in self.img_repo.images]
        return {
            "success": True,
            "images_list": imgs or ""
        }

    def get_index_image(self, index_1_based: int) -> dict:
        # 以索引取得圖片路徑
        try:
            index_0_based = index_1_based - 1
            img = str(self.img_repo.get(index_0_based))
            return {
                "success": True,
                "index_0_based": index_0_based or 0,
                "image_path": img or ""
            }
        except Exception:
            logger.exception("Image Path Getting Error.")
            raise ResourceNotLoadedError()

    def get_annotation(self, img_path: str) -> dict:
        # 取得圖片對應的註解
        try:
            note = self.db.get_annotation(img_path)
            return {
                "success": True,
                "image_path": img_path or "",
                "annotation": note or ""
            }
        except Exception:
            logger.exception("Annotation Getting Error.")
            raise ResourceNotLoadedError()

    def update_db_annotation(self, img_path: str, note: str) -> dict:
        # 更新註解
        try:
            self.db.update_note(img_path, note)
            logger.info(f"{img_path} Annotation Update 成功！")
            return {
                "success": True,
                "img_path": img_path or ""
            }
        except Exception:
            logger.exception(f"Annotation Update Error: img_path/{img_path}")
            raise ResourceNotLoadedError()
