""" Logging 日誌的初始設置
 - logging_config 負責「全域規則與輸出管道」
 - 各模組只負責用 logger 寫訊息，不管它最後寫去哪裡
"""

import logging
from pathlib import Path

# 檔案位置設定
BASE_PATH = Path(__file__).resolve().parent.parent
LOG_PATH = BASE_PATH / "log"
LOG_PATH.mkdir(exist_ok=True)

# 日誌基礎設定  :>  demo 快速版本
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s [%(levelname)s] %(name)s:- %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     filename=log_file,
#     encoding="utf-8"
# )

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s:- %(message)s"
)

# handler
# 1: 全部
app_handler = logging.FileHandler(
    filename=LOG_PATH / "appLog.log",
    encoding="utf-8"
)
app_handler.setFormatter(formatter)
# app_handler.setLevel(logging.DEBUG)

# 2: DB
db_handler = logging.FileHandler(
    filename=LOG_PATH / "dbLog.log",
    encoding="utf-8"
)
db_handler.setFormatter(formatter)
# db_handler.setLevel(logging.INFO)

# 3: Controller
con_handler = logging.FileHandler(
    filename=LOG_PATH / "controllerLog.log",
    encoding="utf-8"
)
con_handler.setFormatter(formatter)

# logger 指定
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
if not root_logger.handlers:
    root_logger.addHandler(app_handler)

db_logger = logging.getLogger("models.annotation_db")
db_logger.setLevel(logging.INFO)
if not db_logger.handlers:
    db_logger.addHandler(db_handler)
db_logger.propagate = False

con_logger = logging.getLogger("controllers.image_controller")
con_logger.setLevel(logging.INFO)
if not con_logger.handlers:
    con_logger.addHandler(con_handler)
con_logger.propagate = False
