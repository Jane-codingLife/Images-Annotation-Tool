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
from config.errors import PathError, DBError

logger = logging.getLogger(__name__)


class AnnotationDB:
    def __init__(self, db_path):
        # 初始化
        try:
            db_path = Path(db_path)
        except Exception:
            logger.exception(f"轉換 Path 失敗: {db_path}")
            raise PathError()
        if not db_path.is_file():
            logger.exception(f"路徑非檔案格式: {db_path}")
            raise PathError(f"{db_path} 非檔案格式。")
        elif db_path.suffix not in [".db"]:
            logger.exception(f"路徑非資料庫檔案: {db_path}")
            raise PathError(f"{db_path} 非資料庫檔案。(目前僅用 SQLite 的 .db 格式)")

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
            raise DBError()

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
            raise DBError()

    def get_by_index(self, index):
        # 取得一筆資料
        # 這是 debug / admin 用 API
        try:
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

        except Exception:
            logger.exception("index 取得圖片資料失敗")
            raise DBError()

    # ========== Controller 對接 ==========
    def get_annotation(self, img_path):
        # 依圖片路徑取得註解
        try:
            img_path = str(img_path)

            with self._connect() as conn:
                sql = """
                SELECT note
                FROM image_data
                WHERE image_path = ?
                """
                row = conn.execute(sql, (img_path, )).fetchone()
                return row[0] if row else row

        except Exception:
            logger.exception("註解取得失敗")
            raise DBError()

    def update_note(self, img_path, note):
        # 更新註解
        try:
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

        except Exception:
            logger.exception("更新 note 失敗")
            raise DBError()
