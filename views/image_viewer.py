""" 圖片檢視窗
 - 另開視窗檢視圖片
 - 縮放(Zoom)圖片大小: 滾輪縮放
 - 移動(Pan)圖片位置: 拖曳平移
"""

import logging
import tkinter as tk
from PIL import Image, ImageTk


class ImageViewer(tk.Toplevel):
    def __init__(self, parent, image_path):
        super().__init__(parent)
        self.transient(parent)

        self.title("圖片檢視器")
        self.geometry("600x800+50+80")

        # UI Layout
        self.canvas = tk.Canvas(self, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Set
        self.original_image = Image.open(image_path)
        self.scale = 1.0
        self._photo_image = None
        self._canvas_img_id = None
        self._pan_x = 0
        self._pan_y = 0
        # 影像左上角在 Canvas 上的位置
        self.offset_x = 0
        self.offset_y = 0

        # event
        self._render_image()

        # bind
        self.bind("<Escape>", lambda e: parent.destroy())
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<ButtonPress-1>", self.on_pan_start)
        self.canvas.bind("<B1-Motion>", self.on_pan_move)
        self.canvas.bind("<Double-Button-1>", self.on_reset)

    # ====== Event Handler ======
    def _render_image(self):
        w, h = self.original_image.size
        new_size = (int(w * self.scale), int(h * self.scale))

        resized = self.original_image.resize(new_size, Image.Resampling.LANCZOS)

        self._photo_image = ImageTk.PhotoImage(resized)

        self.canvas.delete("all")
        self._canvas_img_id = self.canvas.create_image(
            # self.canvas.winfo_width() // 2,
            # self.canvas.winfo_height() // 2,
            self.offset_x,
            self.offset_y,
            image=self._photo_image,
            anchor="nw"
        )

    # ====== Bind Handler ======
    def on_zoom(self, event):
        old_scale = self.scale

        # event.delta 滾輪的方向與強度: 向上+ 向下-
        if event.delta > 0:
            self.scale *= 1.1
        else:
            self.scale /= 1.1

        self.scale = max(0.2, min(self.scale, 5.0))

        # 滑鼠在 Canvas 上的位置
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)

        # 計算縮放後 offset 調整
        self.offset_x = cx - (cx - self.offset_x) * (self.scale / old_scale)
        self.offset_y = cy - (cy - self.offset_y) * (self.scale / old_scale)

        self._render_image()

    def on_pan_start(self, event):
        self._pan_x = event.x
        self._pan_y = event.y

    def on_pan_move(self, event):
        # 移動量參數，以 Button-1 點擊點為中心
        dx = event.x - self._pan_x
        dy = event.y - self._pan_y

        # self.canvas.move(self._canvas_img_id, dx, dy)
        self.offset_x += dx
        self.offset_y += dy

        # 每次移動修正點擊的當下定位
        self._pan_x = event.x
        self._pan_y = event.y

        self._render_image()

    def on_reset(self, event):
        self.scale = 1.0

        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        iw, ih = self.original_image.size

        self.offset_x = (cw - iw) // 2
        self.offset_y = (ch - ih) // 2

        self._render_image()


