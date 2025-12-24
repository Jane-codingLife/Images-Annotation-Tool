""" Controller = 專案的大腦  =>  <控制圖檔和資料庫註解 的 連結與處理>
 - 管 index、串資料、提供 UI 好用的 API
 --- 給 UI 讀資料
    - 目前圖檔位置
    - 目前註解(與圖對應的)
    - 目前狀態 => 當前頁數、總頁數
 --- 給 UI 觸發動作
    - 載入檔案位置(圖片放置資料夾)  =>  放到 UI 介面設計，包含呼叫副程式(依賴)再提供給 Controller
    - 下一頁
    - 前一頁
    - 跳頁
    - 儲存註解
"""

import logging

logger = logging.getLogger(__name__)


class ImageAnnotationController:
    def __init__(self, repo, db):
        self.img_repo = repo
        self.db = db
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