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
        - 路徑由外部傳入
        - 不寫死專案結構
    12.回傳格式能直接轉 JSON
"""

import logging
from pathlib import Path
from models import ImageRepository, AnnotationDB

logger = logging.getLogger(__name__)


class ImageAnnotationController:
    def __init__(self, repo_path: str, db_path: str):
        try:
            repo_path = Path(repo_path)
            db_path = Path(db_path)
        except Exception:
            logger.error(f"ValueError: str is not path.")
            raise
        if not repo_path.exists():
            logger.error("FileNotFoundError: repo_path is not exists.")
            raise
        elif not repo_path.is_dir():
            logger.error("FileNotFoundError: repo_path is not dir.")
            raise
        self.img_repo = ImageRepository(repo_path)

        if not db_path.exists():
            logger.error("FileNotFoundError: db_path is not exists.")
            raise
        elif not db_path.is_file() and (not (db_path.suffix in [".db"])):
            logger.error("FileNotFoundError: db_path is not db file.")
            raise
        self.db = AnnotationDB(db_path)

        self.current_index = 0
        self.total_index = len(self.img_repo)

        logger.info(f"Controller initialized: 總計圖頁={self.total_index}")

    # ========= 資料讀取 =========
    def get_current_image(self):
        # 取得目前圖檔
        return self.img_repo.get(self.current_index)

    def get_image_data(self):
        image_path = self.get_current_image()
        return self.db.get_or_create(image_path)

    def get_current_annotation(self):
        # 取得目前圖檔的註解
        return self.get_image_data()["note"]

    def get_status(self):
        # 取得狀態 => 當前頁數(給 UI 需要+1)、總頁數
        return self.current_index + 1, self.total_index

    def get_images(self):
        return self.img_repo.images

    def has_annotation(self, img_path: str):
        # 是否已有註解
        note_flag = False
        if self.db.get_annotation(img_path):
            note_flag = True

        return note_flag

    # ========= 操　　作 =========
    def next_image(self):
        # 下一頁
        if (self.current_index + 1) < self.total_index:
            self.current_index += 1
            logger.debug(f"Move to next image, current Index: {self.current_index}")
        return self.get_current_image()

    def prev_image(self):
        # 上一頁
        if self.current_index > 0:
            self.current_index -= 1
            logger.debug(f"Move to previous image, current Index: {self.current_index}")
        return self.get_current_image()

    def jump_to(self, index_ui_current: int):
        # 跳頁    【 參數: 型態 => 型別提示（type hint） 】
        # 傳入 UI 的跳頁頁碼，與程式 index 需 -1
        index = index_ui_current - 1
        if not 0 <= index < self.total_index:
            logger.error(f"Input {index}: Index out of range")
            raise IndexError(f"Input {index}: Index out of range")
        self.current_index = index
        logger.info(f"Jump to image, current Index: {self.current_index}")
        return self.get_current_image()

    # ========= 資料寫入 =========
    def save_annotation(self, note: str):
        # 儲存註解
        image_data = self.get_image_data()
        image_id = image_data["id"]
        self.db.update_note(image_id, note)
        logger.info(f"{image_id}:{image_data['image_path']} Annotation Update 成功！")


if __name__ == "__main__":
    from models import ImageRepository, AnnotationDB
    repo = ImageRepository(r"../comic/Devil's Candy")
    db = AnnotationDB(r"../data/annotation.db")
    iac = ImageAnnotationController(repo, db)
    # print(iac.get_images())
    # print(iac.has_annotation(r"D:\Python\ImagesCV\comic\Devil's Candy\DVC_ch01_p011.png"))