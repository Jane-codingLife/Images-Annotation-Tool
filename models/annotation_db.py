""" 圖文註解資料庫  =>  id、image_path、note
 - 資料庫初始化資料表建立 create
 - 資料表總筆數取得 select
 - 取得 image 資料 select、insert
 - 更新 image 資料 update
 - assert、try/except、logging 預防性錯誤、系統日誌
"""

import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AnnotationDB:
    def __init__(self, db_path):
        # 初始化
        try:
            db_path = Path(db_path)
        except Exception:
            logger.exception(f"轉換 Path 失敗: {db_path}")
            raise FileExistsError(f"{db_path} 路徑不存在。")
        if not db_path.is_file():
            logger.exception(f"路徑非檔案格式: {db_path}")
            raise FileNotFoundError(f"{db_path} 非檔案格式。")
        elif db_path.suffix not in [".db"]:
            logger.exception(f"路徑非資料庫檔案: {db_path}")
            raise FileNotFoundError(f"{db_path} 非資料庫檔案。(目前僅用 SQLite 的 .db 格式)")

        self.db_path = db_path
        self._init_db()

    def _connect(self):
        # DB 連線
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        # DB 初始化
        # ☆ 初始化的嚴謹設定中，雖然可以判斷是否存在，但仍舊必要執行，確保初始化的完整性！
        try:
            with self._connect() as conn:
                sql = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='image_data'
                """
                exists = conn.execute(sql).fetchone() is not None

                sql = """
                CREATE TABLE IF NOT EXISTS image_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT NOT NULL UNIQUE,
                    note TEXT
                )
                """
                conn.execute(sql)

            if exists:
                logger.info("資料表 image_data 已存在")
            else:
                logger.info("資料表 image_data 已建立")

        except Exception:
            logger.exception("資料庫初始化/資料表建立失敗")
            raise

    def get_total_count(self):
        # 取得目前資料表總數
        try:
            with self._connect() as conn:
                sql = """
                SELECT COUNT(*)
                FROM image_data
                """
                (count, ) = conn.execute(sql).fetchone()

            return count

        except Exception:
            logger.exception("取得總筆數失敗")
            raise

    def get_by_index(self, index):
        # 取得一筆資料
        # 這是 debug / admin 用 API
        try:
            assert isinstance(index, int), "index 必須是整數"
            assert index >= 0, "index 不可為負數"

            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                sql = """
                SELECT id, image_path, note
                FROM image_data
                ORDER BY id
                LIMIT 1 OFFSET ?
                """
                row = conn.execute(sql, (index,)).fetchone()

            return row

        except AssertionError:
            logger.exception("AssertionError：圖片 index 假設不成立")
            raise

        except Exception:
            logger.exception("index 取得圖片資料失敗")
            raise

    # ========== Controller 對接 ==========
    # def get_or_create(self, image_path):
    #     # 取得或新建圖片資料
    #     # ★ 主要對接 image_repository 的資料取得
    #     try:
    #         image_path = str(image_path)
    #
    #         with self._connect() as conn:
    #             conn.row_factory = sqlite3.Row
    #             sql = """
    #             SELECT id, image_path, note
    #             FROM image_data
    #             WHERE image_path = ?
    #             """
    #             row = conn.execute(sql, (image_path, )).fetchone()
    #
    #             # 如果資料不是 None
    #             if row:
    #                 return row
    #
    #             sql = """
    #             INSERT INTO image_data (image_path, note)
    #                 VALUES (?, ?)
    #             """
    #             conn.execute(sql, (image_path, ""))
    #             conn.commit()
    #             logger.info(f"[image_data] {image_path} 新增一筆成功")
    #
    #             # 重新呼叫
    #             return self.get_or_create(image_path)
    #
    #     except Exception:
    #         logger.exception("圖片資料取得/建立失敗")
    #         raise

    def get_annotation(self, image_path):
        # 依圖片路徑取得註解
        try:
            image_path = str(image_path)

            with self._connect() as conn:
                sql = """
                SELECT note
                FROM image_data
                WHERE image_path = ?
                """
                row = conn.execute(sql, (image_path, )).fetchone()
                return row[0] if row else row

        except Exception:
            logger.exception("註解取得失敗")
            raise

    def update_note(self, img_path, note):
        # 更新註解
        try:
            assert isinstance(img_path, str), "img_path 必須是字串"

            with self._connect() as conn:
                sql = """
                SELECT *
                FROM image_data
                WHERE image_path = ?
                """
                row = conn.execute(sql, (img_path, )).fetchone()
                if not row:
                    sql = """
                    INSERT INTO image_data (image_path, note)
                        VALUES (?, ?)
                    """
                    conn.execute(sql, (img_path, ""))
                    conn.commit()
                    logger.info(f"[image_data] {img_path} 新增一筆成功")

                sql = """
                UPDATE image_data
                SET note = ?
                WHERE image_path = ?
                """
                conn.execute(sql, (note, img_path))
                conn.commit()
                logger.info(f"[image_data] {img_path} 更新一筆成功")

        except AssertionError:
            logger.exception("AssertionError：假設不成立")
            raise

        except Exception:
            logger.exception("更新 note 失敗")
            raise


if __name__ == "__main__":
    BASE_PATH = Path(__file__).resolve().parent.parent
    DB_PATH = BASE_PATH / "data"
    DB_PATH.mkdir(exist_ok=True)
    db = AnnotationDB(DB_PATH / "annotation.db")
    # from image_repository import ImageRepository
    # repo = ImageRepository(r"comic\Devil's Candy")
    # test = db.get_or_create(repo.images[1])
    # print(test)
    # print(db.get_by_index(0))
    # print(db.get_by_index(1))
    # print(db.get_by_index(2))
    # print(db.get_by_index(3))
    # print(db.get_by_index(4))
    # print(db.get_by_index(5))

    # print(db.get_annotation(r"D:\Python\ImagesCV\comic\Devil's Candy\DVC_ch01_p007"))

    # GC = [
    #     db.get_or_create("test1.jpg"),
    #     db.get_or_create("test2.png"),
    #     db.get_or_create("test3.jpeg"),
    # ]
    # print("image_data 資料表中目前的總數:", db.get_total_count())
    # print(GC[0])
    # db.update_note(1, "abc\ndef")
    # print(db.get_by_index(0))



