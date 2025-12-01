import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class BaseFrame(ttk.Frame):
    def __init__(self, master, manager):
        super().__init__(master, padding=20)
        self.manager = manager  # 管理器引用，用于跳转
        self.create_widgets()

    def create_widgets(self):
        """绘制界面"""
        pass

    def on_show(self, **kwargs):
        """接收页面传来的数据"""
        pass


if __name__ == "__main__":
    from modules.gui.manager import WindowManager

    app = WindowManager()
    app.mainloop()
