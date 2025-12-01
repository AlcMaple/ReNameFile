import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from .home import HomePage
from .diff import DiffPage
from .example import ExamplePage


class WindowManager(ttk.Window):
    def __init__(self):
        super().__init__(title="ReNameFile", themename="cosmo", size=(800, 600))

        # 共享数据上下文 Context，用于页面间共享数据
        self.context = {"target_dir": None, "file_mapping": []}

        # 页面容器
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # 初始化所有页面
        self.pages = {}
        for PageClass, name in [
            (HomePage, "home"),
            (DiffPage, "diff"),
            (ExamplePage, "example"),
        ]:
            page = PageClass(self.container, self)
            self.pages[name] = page
            # 使用 gird 布局使得页面重叠在同一个位置
            page.grid(row=0, column=0, sticky="nsew")

        # 配置 Grid 权重
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # 显示首页
        self.switch_to("home")

    def switch_to(self, page_name, **kwargs):
        """切换页面，传递参数"""
        page = self.pages[page_name]
        # 显示
        page.tkraise()
        # 传递参数
        page.on_show(**kwargs)
