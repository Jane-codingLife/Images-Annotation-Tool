""" Controller API ★ 「如果今天換成 HTTP 呼叫，這個 function 還能用嗎？」 ★
    01.不 import UI 相關套件
    02.不讀取使用者互動
    03.僅負責「資料流」
        - 接收參數
        - 呼叫 repo/db
        - 回傳資料
        - raise Exception
    04.所有 public method 都可以被 API 呼叫
        ☐ 參數能用 JSON 表示？
        ☐ 回傳值能序列化？ 推薦：str/int/float/bool/list[str]/dict
        ☐ 不依賴 Python 物件狀態？
    05.Exception 設計：只 raise，不處理錯誤顯示
        - ValueError
        - FileNotFoundError
        - RuntimeError
        - 自訂 Exception（進階）
    06.方法命名：動詞 + 名詞
    07.狀態與 index 管理
        - index 由 View 管理
        - Controller 是「純服務」 => 不知道使用者目前狀態，只有當 View 傳遞時才知道傳遞值
    08.index 規則明確（0-based or 1-based）
    09.型別提示 < ex. def get_images(self, get_index: int) -> list[str]: >
    10.Logging 設計：只記錄「系統事件」
        - 開始處理
        - 成功
        - 失敗（exception）
    11.Web-ready：不依賴檔案系統位置
        - 路徑由外部傳入、不檢查路徑，只接受資源
        - 不寫死專案結構
    12.回傳格式能直接轉 JSON
"""

import logging
from models import ImageRepository, AnnotationDB

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
            raise

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
            raise

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
            raise


if __name__ == "__main__":
    pass
