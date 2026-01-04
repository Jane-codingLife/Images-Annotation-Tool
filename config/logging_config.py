""" Logging 日誌的初始設置
 - logging_config 負責「全域規則與輸出管道」
 - 各模組只負責用 logger 寫訊息，不管它最後寫去哪裡
"""

import logging
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

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
# 1: 全部(大小)
# app_handler = logging.FileHandler(
#     filename=LOG_PATH / "appLog.log",
#     encoding="utf-8"
# )
app_handler = RotatingFileHandler(
    filename=LOG_PATH / "appLog.log",
    maxBytes=2 * 1024 * 1024,
    backupCount=10,
    encoding="utf-8"
)
app_handler.setFormatter(formatter)
app_handler.setLevel(logging.INFO)

# 2: DB(每日)
mod_handler = logging.FileHandler(
    filename=LOG_PATH / "modelLog.log",
    encoding="utf-8"
)
# mod_handler = TimedRotatingFileHandler(
#     filename=LOG_PATH / "modelLog.log",
#     when="midnight",
#     interval=1,
#     backupCount=30,
#     encoding="utf-8"
# )
# mod_handler.suffix = "%Y-%m-%d"
mod_handler.setFormatter(formatter)
mod_handler.setLevel(logging.INFO)

# 3: Controller(每周)
con_handler = logging.FileHandler(
    filename=LOG_PATH / "controllerLog.log",
    encoding="utf-8"
)
# con_handler = TimedRotatingFileHandler(
#     filename=LOG_PATH / "controllerLog.log",
#     when="W0",             # W0 = 週一
#     interval=1,
#     backupCount=8,         # 保留 8 週
#     encoding="utf-8"
# )
# con_handler.suffix = "%Y-W%W"
con_handler.setFormatter(formatter)
con_handler.setLevel(logging.INFO)

# logger 指定
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
if not root_logger.handlers:
    root_logger.addHandler(app_handler)

mod_logger = logging.getLogger("models")
mod_logger.setLevel(logging.INFO)
if not mod_logger.handlers:
    mod_logger.addHandler(mod_handler)
mod_logger.propagate = False

con_logger = logging.getLogger("controllers")
con_logger.setLevel(logging.INFO)
if not con_logger.handlers:
    con_logger.addHandler(con_handler)
con_logger.propagate = False
