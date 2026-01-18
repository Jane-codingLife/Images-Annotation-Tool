"""
 >> View 只關心「顯示什麼、怎麼互動」
 >> View 永遠不應該知道「資料是檔案 / DB / API」
 >> Controller 決定「資料從哪來、怎麼算、怎麼存」
檢查點
 □ View 檔案中沒有 os / Path
 □ View 不知道資料夾結構
 □ 所有錯誤顯示只在 View 一個地方
 □ Controller 換成 Fake，UI 仍可跑
"""

import logging
import tkinter as tk
import tkinter.font as tkFont
from pathlib import Path
from tkinter import filedialog, messagebox
from models import ImageRepository, AnnotationDB
from controllers import ImageAnnotationController
from views.image_viewer import ImageViewer
from config.errors import AppError
# 安裝 pillow
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)


# ---------- Error Handlers ----------
# def error_handler(exc: Exception):
#     # 1. 給工程師完整 trace（已經寫進 log 了，這行是保險）
#     logger.exception(f"UI caught Error: {str(exc)}")
#     # 2. 給使用者看的訊息（整理過）
#     messagebox.showerror("錯誤", str(exc))


def safe_call(func, args=None):
    try:
        if args:
            func(**args)
        else:
            func()
    except AppError as e:
        logger.exception("Handled application error")
        messagebox.showerror("錯誤", e.user_msg)
    except Exception:
        logger.exception("Unhandled error")
        messagebox.showerror("錯誤", "系統發生異常，請查看 log")


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("圖文翻譯工具: 翻譯與瀏覽")
        self.geometry("1300x800+130+50")
        default_font = tkFont.Font(family="標楷體", size=15)
        self.option_add("*Font", default_font)

        # Controller 之後才會建立
        self.controller = None
        # Canvas 圖資源避免被 GC
        self._photo_image = None
        # Auto Save flag => Annotation Update
        self._dirty = False
        self._dirty_img_path = None
        # Image List Visible flag
        self.list_visible = None
        self.current_index_1_based = 1
        self.total_index = 0
        self.img_path = None
        self.db_path = None

        safe_call(self._build_layout)
        safe_call(self._bind_events)

        # set event bind
        self.bind("<Control-Left>", self.on_key_prev)
        self.bind("<Control-Right>", self.on_key_next)
        self.bind("<Control-s>", self.on_key_save)
        self.bind("<Escape>", self.off_show_list)

        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Double-Button-1>", self.on_open_image_viewer)

        self.txt_annotation.bind("<Key>", self.on_text_modified)
        self.listbox.bind("<<ListboxSelect>>", self.on_list_select)

    # ---------- UI Layout ----------
    def _build_layout(self):
        # ===== Top =====
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill=tk.X, padx=10, pady=5)

        self.btn_image_list = tk.Button(self.top_frame, text="圖片清單")
        # self.btn_image_list.pack(side=tk.LEFT, padx=10)

        self.btn_select = tk.Button(self.top_frame, text="選擇資料夾")
        # self.btn_select.pack(side=tk.LEFT)

        self.lbl_folderName = tk.Label(self.top_frame, text="...")
        # self.lbl_folderName.pack(side=tk.LEFT)

        self.btn_db_select = tk.Button(self.top_frame, text="資料庫選定")
        self.btn_db_select.pack(side=tk.LEFT)

        self.lbl_status = tk.Label(self.top_frame, text="尚未載入資料")
        self.lbl_status.pack(side=tk.RIGHT)

        # ===== Content =====
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ListImage - 圖片清單列表(預設隱藏，點擊 btn_image_list 才開啟)
        self.list_frame = tk.Frame(self.content_frame, width=200)
        self.list_visible = False

        self.listbox = tk.Listbox(self.list_frame, activestyle="none")
        self.scroll_list = tk.Scrollbar(self.list_frame, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scroll_list.set)
        self.scroll_list.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Left - Image區塊
        self.left_frame = tk.Frame(self.content_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.left_frame, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 測試用: 標示預留圖片空間
        # self.lbl_image = tk.Label(self.left_frame, text="Image Area")
        # self.lbl_image.pack(expand=True)

        # Right - Annotation區塊
        self.right_frame = tk.Frame(self.content_frame, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH,  expand=True)
        self.right_frame.pack_propagate(False)

        # spacing1 => 行間距   spacing2 => 自動斷行間距(垂直)   spacing3 => 額外間距
        self.txt_annotation = tk.Text(self.right_frame, wrap="word", spacing1=10, spacing2=4)
        self.scroll_annotation = tk.Scrollbar(self.right_frame, command=self.txt_annotation.yview)
        self.txt_annotation.config(yscrollcommand=self.scroll_annotation.set)
        self.scroll_annotation.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_annotation.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ===== Bottom =====
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(fill=tk.X, padx=250, pady=5)

        self.btn_prev = tk.Button(self.bottom_frame, text="上一頁")
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        self.btn_next = tk.Button(self.bottom_frame, text="下一頁")
        self.btn_next.pack(side=tk.LEFT, padx=5)

        self.entry_jump = tk.Entry(self.bottom_frame, width=5, justify="center")
        self.entry_jump.pack(side=tk.LEFT, padx=5)

        self.btn_jump = tk.Button(self.bottom_frame, text="跳頁")
        self.btn_jump.pack(side=tk.LEFT)

        self.btn_save = tk.Button(self.bottom_frame, text="儲存")
        self.btn_save.pack(side=tk.RIGHT)

    # ---------- Event Binding ----------
    def _bind_events(self):
        self.btn_select.config(command=lambda fc=self.on_select_folder: safe_call(fc))
        self.btn_db_select.config(command=lambda fc=self.on_select_folder_db: safe_call(fc))
        self.btn_prev.config(command=lambda fc=self.on_prev: safe_call(fc))
        self.btn_next.config(command=lambda fc=self.on_next: safe_call(fc))
        self.btn_jump.config(command=lambda fc=self.on_jump: safe_call(fc))
        self.btn_save.config(command=lambda fc=self.on_save: safe_call(fc))
        self.btn_image_list.config(command=lambda fc=self.on_show_listbox: safe_call(fc))

    # ---------- Event Handlers ----------
    def on_select_folder_db(self):
        self.db_path = filedialog.askopenfilename()
        if not self.db_path:
            return

        self.btn_db_select.pack_forget()
        self.btn_image_list.pack(side=tk.LEFT, padx=10)
        self.btn_select.pack(side=tk.LEFT)
        self.lbl_folderName.pack(side=tk.LEFT)

    def on_select_folder(self):
        # 資料夾選擇：初始化所有資料來源
        images_path = filedialog.askdirectory()
        if not images_path and not self.db_path:
            return

        images_path = Path(images_path)
        self.lbl_folderName.config(text=f" {images_path.name}")
        logger.info(f"資料夾選擇: {images_path}")

        # 組裝(Composition)
        repo = ImageRepository(images_path)
        db = AnnotationDB(self.db_path)
        self.controller = ImageAnnotationController(repo, db)
        self.current_index_1_based = 1
        self.total_index = self.controller.get_total_count()["total_count"]
        safe_call(self.refresh_listbox)
        safe_call(self.update_view)

    def on_prev(self):
        # 上一頁
        if not self.controller:
            return

        self._dirty_img_path = self.img_path
        safe_call(self.save_flag)
        if self.current_index_1_based == 1:
            messagebox.showinfo("資訊", "已經是第一頁。")
            return
        self.current_index_1_based -= 1
        safe_call(self.refresh_listbox)
        safe_call(self.update_view)

    def on_next(self):
        # 下一頁
        if not self.controller:
            return

        self._dirty_img_path = self.img_path
        safe_call(self.save_flag)
        if self.current_index_1_based == self.total_index:
            messagebox.showinfo("資訊", "已經是第一頁。")
            return
        self.current_index_1_based += 1
        safe_call(self.refresh_listbox)
        safe_call(self.update_view)

    def on_jump(self):
        if not self.controller:
            return

        self._dirty_img_path = self.img_path
        safe_call(self.save_flag)
        try:
            page = int(self.entry_jump.get())
        except Exception:
            raise AppError()
        if page < 1 or page > self.total_index:
            messagebox.showinfo("資訊", "超過頁數。")
            return
        self.current_index_1_based = page
        safe_call(self.refresh_listbox)
        safe_call(self.update_view)

    def on_save(self):
        self._dirty_img_path = self.img_path
        safe_call(self.save_flag, {"force": True})
        safe_call(self.refresh_listbox)
        messagebox.showinfo("存檔完成", "已儲存")

    def save_flag(self, *, force=False):
        """
        Use case:
            - 將目前正在編輯的圖片註解寫入 DB
            - force=True 表示忽略 dirty
        """
        if not self._dirty_img_path:
            return False

        if not self._dirty and not force:
            return False

        text = self.txt_annotation.get("1.0", tk.END).strip()
        result = self.controller.update_db_annotation(self._dirty_img_path, text)

        if result["success"]:
            self._dirty = False
            self._dirty_img_path = None
            return True

        return False

    def on_show_listbox(self):
        if self.list_visible:
            self.list_frame.pack_forget()
            self.listbox.selection_clear(0, tk.END)
        else:
            self.listbox.selection_set(self.current_index_1_based - 1)
            self.list_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.list_visible = not self.list_visible

    def refresh_listbox(self):
        if not self.controller:
            return
        yview = self.listbox.yview()
        self.listbox.delete(0, tk.END)

        result = self.controller.get_all_images()
        for img in result["images_list"]:
            img = Path(img)
            self.listbox.insert(tk.END, img.stem)
            idx = self.listbox.index("end") - 1
            note = self.controller.get_annotation(img)["annotation"]
            if note:
                self.listbox.itemconfig(idx, bg="gray")

        self.listbox.selection_set(self.current_index_1_based - 1)
        self.listbox.yview_moveto(yview[0])

    # ---------- View Update ----------
    def update_view(self):
        safe_call(self.update_status)
        safe_call(self.update_image)
        safe_call(self.update_annotation)

    def update_status(self):
        # 狀態處理
        self.lbl_status.config(text=f"{self.current_index_1_based} / {self.total_index}")

    def update_annotation(self):
        # 註解處理
        if not self.controller:
            return
        self.txt_annotation.delete("1.0", tk.END)
        text = self.controller.get_annotation(self.img_path)["annotation"]
        if text:
            self.txt_annotation.insert("1.0", text)

    def update_image(self):
        # 圖片顯示處理 Canvas
        if not self.controller:
            return

        self.img_path = self.controller.get_index_image(self.current_index_1_based)["image_path"]
        if not self.img_path:
            return

        # 1.開圖
        img = Image.open(self.img_path)

        # 2.取得 Canvas 大小
        self.canvas.update_idletasks()
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        if canvas_w <= 1 or canvas_h <= 1:
            return  # 尚未初始化完成

        # 3. 等比例縮放
        img_ratio = img.width / img.height
        canvas_ratio = canvas_w / canvas_h

        if img_ratio > canvas_ratio:
            # 原圖 > 視窗尺寸  =>  依視窗寬、調高
            new_w = canvas_w
            new_h = int(canvas_w / img_ratio)
        else:
            # 原圖 < 視窗尺寸  =>  調寬、依視窗高
            new_h = canvas_h
            new_w = int(canvas_h * img_ratio)

        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # 4. 轉成 Tk Image
        self._photo_image = ImageTk.PhotoImage(img)

        # 5. 清空並顯示
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_w // 2,
            canvas_h // 2,
            image=self._photo_image,
            anchor="center"
        )

    # ---------- Canvas event(bind) Handler ----------
    def on_canvas_resize(self, event):
        safe_call(self.update_image)

    def on_open_image_viewer(self, event):
        if self.img_path:
            ImageViewer(self, self.img_path)

    # Windows bind
    def on_key_prev(self, event):
        safe_call(self.on_prev)

    def on_key_next(self, event):
        safe_call(self.on_next)

    def on_key_save(self, event):
        safe_call(self.on_save)

    def off_show_list(self, event):
        self.list_visible = True
        safe_call(self.on_show_listbox)

    # Widget bind
    def on_text_modified(self, event):
        if event.char:
            self._dirty = True

    def on_list_select(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return

        self._dirty_img_path = self.img_path
        safe_call(self.save_flag)
        self.current_index_1_based = selection[0] + 1
        safe_call(self.update_view)
        safe_call(self.refresh_listbox)


if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()
