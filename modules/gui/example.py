import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from main import BaseFrame


class ExamplePage(BaseFrame):
    def create_widgets(self):
        self.label = ttk.Label(self, text="Example Page")
        self.label.pack(pady=10)
        self.dir_info = ttk.Label(self, text="Directory: ", bootstyle="secondary")
        self.dir_info.pack(pady=5)

        # 数据区域
        table_area = ttk.Labelframe(
            self, text="Data Area", bootstyle="info", padding=20
        )
        table_area.pack(expand=True, fill=BOTH, pady=20)
        ttk.Label(table_area, text="Data").pack()

        # 按钮区域
        btn_bar = ttk.Frame(self)
        btn_bar.pack(pady=10, fill=X)
        ttk.Button(
            btn_bar, text="开始智能分析", bootstyle="success", command=self.go_next
        ).pack(side=RIGHT)

    def on_show(self, directory=None, **kwargs):
        """接收首页传来的目录"""
        if directory:
            self.dir_info.config(text=f"Directory: {directory}")
            # TODO:扫描该目录下所有的文件

    def go_next(self):
        # TODO:AI分析过程
        self.manager.switch_to("diff", results="")
