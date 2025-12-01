from main import BaseFrame

import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class HomePage(BaseFrame):
    def create_widgets(self):
        # 垂直居中布局
        container = ttk.Frame(self)
        container.pack(expand=True, fill=BOTH)

        # 标题
        title = ttk.Label(
            container,
            text="ReNameFile",
            font="-size 24 -weight bold",
            bootstyle="primary",
        )
        title.pack(pady=(0, 40))

        # 按钮
        btn = ttk.Button(
            container,
            text="📂 选择要处理的文件夹",
            command=self.select_folder,
            bootstyle="info-outline",
            width=25,
        )
        btn.pack(ipady=10)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.manager.switch_to("example", directory=folder_path)
