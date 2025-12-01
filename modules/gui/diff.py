import tkinter as tk
from tkinter import ttk as tkttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from main import BaseFrame


class DiffPage(BaseFrame):
    def create_widgets(self):
        # 标题
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=X, pady=(0, 10))
        ttk.Label(
            title_frame,
            text="结果确认",
            font="-size 16 -weight bold",
            bootstyle="primary",
        ).pack(side=LEFT)
        ttk.Label(
            title_frame,
            text="请检查重命名结果。如果不满意，可直接修改或修改部分后重新分析",
            bootstyle="secondary",
        ).pack(side=LEFT, padx=10)

        # 表格区域
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=BOTH, expand=True, pady=10)

        # Treeview 表格
        columns = ("original", "new_name", "source")
        self.tree = tkttk.Treeview(
            table_frame, columns=columns, show="headings", height=15
        )

        # 列标题和宽度
        self.tree.heading("original", text="原文件名")
        self.tree.heading("new_name", text="新文件名")
        self.tree.heading("source", text="来源")

        self.tree.column("original", width=250, anchor=W)
        self.tree.column("new_name", width=250, anchor=W)
        self.tree.column("source", width=100, anchor=CENTER)

        # 滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        # 编辑
        self.tree.bind("<Double-1>", self.on_double_click)

        # 底部按钮栏
        btn_bar = ttk.Frame(self)
        btn_bar.pack(pady=10, fill=X, side=BOTTOM)

        # 是否保留目录结构复选框
        self.keep_structure = ttk.BooleanVar(value=True)
        ttk.Checkbutton(
            btn_bar,
            text="保留目录结构",
            variable=self.keep_structure,
            bootstyle="round-toggle",
        ).pack(side=LEFT)

        # 执行重命名按钮
        ttk.Button(
            btn_bar,
            text="执行重命名",
            bootstyle="danger",
            command=self.on_execute,
        ).pack(side=RIGHT, padx=5)

        # 重新分析按钮
        ttk.Button(
            btn_bar,
            text="重新分析",
            bootstyle="primary",
            command=self.on_reanalyze,
        ).pack(side=RIGHT)

    def on_double_click(self, event):
        """双击表格行进行编辑"""
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        # 只允许编辑"新文件名"列（第2列，#2）
        if column != "#2":
            return

        item = self.tree.identify_row(event.y)
        if not item:
            return

        # 获取当前值
        current_value = self.tree.item(item, "values")[1]

        # 创建编辑框
        x, y, width, height = self.tree.bbox(item, column)
        edit_entry = ttk.Entry(self.tree)
        edit_entry.place(x=x, y=y, width=width, height=height)
        edit_entry.insert(0, current_value)
        edit_entry.select_range(0, tk.END)
        edit_entry.focus()

        def save_edit(event=None):
            new_value = edit_entry.get()
            values = list(self.tree.item(item, "values"))
            values[1] = new_value
            # 修改后标记为用户锁定
            values[2] = "👤 用户"
            self.tree.item(item, values=values)
            edit_entry.destroy()

        def cancel_edit(event=None):
            edit_entry.destroy()

        edit_entry.bind("<Return>", save_edit)
        edit_entry.bind("<Escape>", cancel_edit)
        edit_entry.bind("<FocusOut>", save_edit)

    def on_execute(self):
        """执行重命名操作"""
        keep_structure = self.keep_structure.get()
        # TODO: 获取表格中的所有数据并执行重命名
        file_mappings = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            file_mappings.append(
                {"original": values[0], "new_name": values[1], "source": values[2]}
            )
        # TODO: 调用重命名引擎执行实际的文件复制/重命名操作
        pass

    def on_reanalyze(self):
        """重新分析"""
        # TODO: 收集当前表格中标记为"👤 用户"的条目作为示例
        examples = []
        targets = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            original = values[0]
            new_name = values[1]
            source = values[2]

            if "用户" in source:
                # 用户锁定的作为示例
                examples.append({"original": original, "new_name": new_name})
            else:
                # AI生成的作为待重新推理的目标
                targets.append(original)

        # TODO: 调用AI重新分析
        # 1. 将 examples 和 targets 发送给 LLM
        # 2. 获取AI的新推理结果
        # 3. 更新表格中AI生成的行
        pass

    def load_data(self, data):
        """加载数据到表格

        Args:
            data: 列表，每项包含 {"original": "原文件名", "new_name": "新文件名", "source": "👤 用户" or "🤖 AI"}
        """
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 插入新数据
        for row in data:
            self.tree.insert(
                "",
                END,
                values=(
                    row.get("original", ""),
                    row.get("new_name", ""),
                    row.get("source", "🤖 AI"),
                ),
            )

    def on_show(self, result=None, **kwargs):
        if result:
            self.result_info.configure(text=result)
