""" UI 使用者介面
    - 顯示
    - 操作
"""

import logging
import tkinter as tk
import tkinter.font as tkFont
from pathlib import Path
from tkinter import filedialog, messagebox
from models import ImageRepository, AnnotationDB
from controllers import ImageAnnotationController
from views.image_viewer import ImageViewer
# 安裝 pillow
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)


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
        # Image List Visible flag
        self.list_visible = None

        self._build_layout()
        self._bind_events()

        # set event bind
        self.bind("<Control-Left>", self.on_key_prev)
        self.bind("<Control-Right>", self.on_key_next)
        self.bind("<Control-s>", self.on_key_save)
        self.bind("<Escape>", self.off_show_list)

        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Double-Button-1>", self.on_open_image_viewer)

        self.txt_annotation.bind("<KeyRelease>", self.on_text_modified)
        self.listbox.bind("<<ListboxSelect>>", self.on_list_select)

    # ---------- UI Layout ----------
    def _build_layout(self):
        # ===== Top =====
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill=tk.X, padx=10, pady=5)

        self.btn_image_list = tk.Button(self.top_frame, text="圖片清單")
        self.btn_image_list.pack(side=tk.LEFT, padx=10)

        self.btn_select = tk.Button(self.top_frame, text="選擇資料夾")
        self.btn_select.pack(side=tk.LEFT)

        self.lbl_folderName = tk.Label(self.top_frame, text="...")
        self.lbl_folderName.pack(side=tk.LEFT)

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
        self.btn_select.config(command=self.on_select_folder)
        self.btn_prev.config(command=self.on_prev)
        self.btn_next.config(command=self.on_next)
        self.btn_jump.config(command=self.on_jump)
        self.btn_save.config(command=self.on_save)
        self.btn_image_list.config(command=self.on_show_listbox)

    # ---------- Event Handlers ----------
    def on_select_folder(self):
        images_path = filedialog.askdirectory()
        if not images_path:
            return

        images_path = Path(images_path)
        db_path = Path(__file__).resolve().parent.parent / "data"
        db_path.mkdir(exist_ok=True)
        db_path = db_path / "annotation.db"

        self.lbl_folderName.config(text=f" {images_path.name}")
        logger.info(f"資料夾選擇: {images_path}")

        # ⚠ Day4-2 這裡才會建立 repo / db / controller
        # messagebox.showinfo("提示", "資料夾已選擇，Controller 尚未初始化")
        try:
            # repo = ImageRepository(images_path)
            # db = AnnotationDB(db_path)
            self.controller = ImageAnnotationController(str(images_path), str(db_path))
            self.update_view()
            self.refresh_listbox()
        except Exception as e:
            logger.error(f"UI Error: {e}")
            messagebox.showerror("取得失敗", str(e))

    def on_prev(self):
        if not self.controller:
            return
        try:
            self.save_flag()
            self.controller.prev_image()
            self.update_view()
        except Exception as e:
            logger.error(f"UI Error: {e}")
            messagebox.showerror("圖頁錯誤", str(e))

    def on_next(self):
        if not self.controller:
            return
        try:
            self.save_flag()
            self.controller.next_image()
            self.update_view()
        except Exception as e:
            logger.error(f"UI Error: {e}")
            messagebox.showerror("圖頁錯誤", str(e))

    def on_jump(self):
        if not self.controller:
            return
        try:
            self.save_flag()
            page = int(self.entry_jump.get())
            self.controller.jump_to(page)
            self.update_view()
        except Exception as e:
            logger.error(f"UI Error: {e}")
            messagebox.showerror("圖頁錯誤", str(e))

    def on_save(self):
        if not self.controller:
            return
        # text = self.txt_annotation.get("1.0", tk.END).strip()
        try:
            # self.controller.save_annotation(text)
            # self._dirty = False
            self.save_flag()
            messagebox.showinfo("存檔完成", "已儲存")
        except Exception as e:
            logger.error(f"UI Error: {e}")
            messagebox.showerror("存檔失敗", str(e))

    def save_flag(self):
        if not self._dirty:
            return
        text = self.txt_annotation.get("1.0", tk.END).strip()
        try:
            self.controller.save_annotation(text)
            self._dirty = False
        except Exception:
            logger.error(f"[UI] Save Error: save_flag")
            raise

        self.refresh_listbox()

    def on_show_listbox(self):
        # if self.listbox.size() == 0:
        #     self.refresh_listbox()
        if self.list_visible:
            self.list_frame.pack_forget()
            self.listbox.selection_clear(0, tk.END)
        else:
            if self.controller:
                idx = self.controller.current_index
                self.listbox.selection_set(idx)
            self.list_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.list_visible = not self.list_visible

    def refresh_listbox(self):
        if not self.controller:
            return
        self.listbox.delete(0, tk.END)

        for img in self.controller.get_images():
            self.listbox.insert(tk.END, img.stem)
            idx = self.listbox.index("end") - 1
            try:
                if self.controller.has_annotation(img):
                    self.listbox.itemconfig(idx, bg="gray")
            except Exception as e:
                logger.error(f"UI Error: {e}")
                messagebox.showerror("清單標註錯誤:", str(e))

    # ---------- View Update ----------
    def update_view(self):
        self.update_status()
        self.update_annotation()
        self.update_image()

    def update_status(self):
        # 狀態處理
        if not self.controller:
            return
        current, total = self.controller.get_status()
        self.lbl_status.config(text=f"{current} / {total}")

    def update_annotation(self):
        # 註解處理
        if not self.controller:
            return
        self.txt_annotation.delete("1.0", tk.END)
        text = self.controller.get_current_annotation()
        if text:
            self.txt_annotation.insert("1.0", text)

    def update_image(self):
        # 圖片顯示處理 Canvas
        if not self.controller:
            return

        image_path = self.controller.get_current_image()
        if not image_path:
            return

        try:
            # 1.開圖
            img = Image.open(image_path)

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

        except Exception as e:
            logger.error(f"UI Error: {e}")
            messagebox.showerror("圖片顯示錯誤", str(e))

    # ---------- Canvas event(bind) Handler ----------
    def on_canvas_resize(self, event):
        self.update_image()

    def on_open_image_viewer(self, event):
        image_path = self.controller.get_current_image()
        try:
            if image_path:
                ImageViewer(self, image_path)
        except Exception as e:
            logger.error(f"UI Error: {e}")
            messagebox.showerror("另開圖片視窗開啟失敗")

    # Windows bind
    def on_key_prev(self, event):
        self.on_prev()

    def on_key_next(self, event):
        self.on_next()

    def on_key_save(self, event):
        self.on_save()

    def off_show_list(self, event):
        self.list_visible = True
        self.on_show_listbox()

    # Widget bind
    def on_text_modified(self, event):
        self._dirty = True

    def on_list_select(self, event):
        selection = self.listbox.curselection()
        if not selection or not self.controller:
            return
        try:
            self.save_flag()
            page = selection[0] + 1  # 0-based
            self.controller.jump_to(page)
            self.update_view()
        except Exception as e:
            logger.error(f"UI Error: {e}")
            messagebox.showerror("清單顯示失敗", str(e))


if __name__ == "__main__":
    win = MainWindow()
    win.mainloop()
