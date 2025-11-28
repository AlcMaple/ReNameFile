"""
GUI界面 - 文件批量重命名工具
使用 ttkbootstrap 实现现代化界面
"""

import os
import sys
import shutil
import threading
import queue
from tkinter import filedialog, messagebox, simpledialog, StringVar, IntVar, BooleanVar
from typing import Optional

try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
except ImportError:
    print("错误: 需要安装 ttkbootstrap 库")
    print("请运行: pip install ttkbootstrap")
    sys.exit(1)

from modules.loader import RuleLoader
from modules.configurator import InteractiveConfigurator
from main import FileRenamer


class ReNameFileGUI:
    """GUI主窗口类"""

    def __init__(self, root):
        self.root = root
        self.root.title("ReNameFile Tool")
        self.root.geometry("800x600")

        # 获取脚本目录
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

        # 变量
        self.target_dir = StringVar()
        self.mode = IntVar(value=1)  # 默认简单模式
        self.keep_structure = BooleanVar(value=True)
        self.clear_output = BooleanVar(value=False)

        # 任务相关
        self.is_running = False
        self.log_queue = queue.Queue()
        self.input_queue = queue.Queue()  # 用于GUI输入的队列
        self.input_response_queue = queue.Queue()  # 用于输入响应的队列

        # 创建界面
        self._create_widgets()

        # 启动日志更新
        self._update_log()

    def _create_widgets(self):
        """创建界面组件"""
        # 区域1: 输入源
        input_frame = ttk.Labelframe(
            self.root, text="目标目录", padding=10, bootstyle="primary"
        )
        input_frame.pack(fill=X, padx=10, pady=5)

        dir_frame = ttk.Frame(input_frame)
        dir_frame.pack(fill=X)

        ttk.Entry(
            dir_frame, textvariable=self.target_dir, width=60
        ).pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        ttk.Button(
            dir_frame, text="浏览...", command=self._browse_directory, bootstyle="info"
        ).pack(side=LEFT)

        ttk.Label(
            input_frame, text="(支持直接拖拽文件夹到此处)", font=("", 9)
        ).pack(pady=(5, 0))

        # 区域2: 控制台
        control_frame = ttk.Labelframe(
            self.root, text="控制台", padding=10, bootstyle="primary"
        )
        control_frame.pack(fill=X, padx=10, pady=5)

        # 模式选择
        mode_label = ttk.Label(control_frame, text="模式选择:", font=("", 10, "bold"))
        mode_label.pack(anchor=W, pady=(0, 5))

        mode_frame1 = ttk.Frame(control_frame)
        mode_frame1.pack(fill=X, pady=2)

        ttk.Radiobutton(
            mode_frame1,
            text="简单替换模式 (words.txt)",
            variable=self.mode,
            value=1,
            bootstyle="primary",
        ).pack(side=LEFT)

        ttk.Button(
            mode_frame1,
            text="编辑规则",
            command=lambda: self._edit_rules("words.txt"),
            bootstyle="secondary-outline",
            width=10,
        ).pack(side=LEFT, padx=10)

        mode_frame2 = ttk.Frame(control_frame)
        mode_frame2.pack(fill=X, pady=2)

        ttk.Radiobutton(
            mode_frame2,
            text="正则模式 (regex_rules.txt)",
            variable=self.mode,
            value=2,
            bootstyle="primary",
        ).pack(side=LEFT)

        ttk.Button(
            mode_frame2,
            text="编辑规则",
            command=lambda: self._edit_rules("regex_rules.txt"),
            bootstyle="secondary-outline",
            width=10,
        ).pack(side=LEFT, padx=10)

        # 选项
        options_label = ttk.Label(control_frame, text="选项:", font=("", 10, "bold"))
        options_label.pack(anchor=W, pady=(10, 5))

        ttk.Checkbutton(
            control_frame,
            text="保持原有目录结构 (Keep Structure)",
            variable=self.keep_structure,
            bootstyle="primary-round-toggle",
        ).pack(anchor=W, pady=2)

        ttk.Checkbutton(
            control_frame,
            text="清空旧的 Output 目录",
            variable=self.clear_output,
            bootstyle="primary-round-toggle",
        ).pack(anchor=W, pady=2)

        # 区域3: 执行与反馈
        exec_frame = ttk.Labelframe(
            self.root, text="执行与反馈", padding=10, bootstyle="primary"
        )
        exec_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # 开始按钮
        self.start_button = ttk.Button(
            exec_frame,
            text="▶ 开始重命名 (Start)",
            command=self._start_rename,
            bootstyle="success",
            width=30,
        )
        self.start_button.pack(pady=(0, 10))

        # 日志输出
        log_label = ttk.Label(exec_frame, text="日志输出:", font=("", 10, "bold"))
        log_label.pack(anchor=W, pady=(0, 5))

        # 创建带滚动条的文本框
        log_container = ttk.Frame(exec_frame)
        log_container.pack(fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(log_container)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.log_text = ttk.Text(
            log_container,
            height=15,
            yscrollcommand=scrollbar.set,
            wrap=WORD,
            font=("Consolas", 9),
        )
        self.log_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)

        # 初始日志
        self._log("[INFO] 就绪，请选择目标目录并点击开始")

    def _browse_directory(self):
        """浏览选择目录"""
        directory = filedialog.askdirectory(title="选择目标目录")
        if directory:
            self.target_dir.set(directory)

    def _edit_rules(self, filename):
        """编辑规则文件"""
        filepath = os.path.join(self.script_dir, filename)
        if not os.path.exists(filepath):
            create = messagebox.askyesno(
                "文件不存在",
                f"{filename} 不存在，是否创建示例文件？"
            )
            if create:
                from main import create_sample_files
                create_sample_files(self.script_dir)
                self._log(f"[INFO] 已创建示例文件: {filename}")

        if os.path.exists(filepath):
            # 使用系统默认编辑器打开
            if sys.platform == "win32":
                os.startfile(filepath)
            elif sys.platform == "darwin":
                os.system(f'open "{filepath}"')
            else:
                os.system(f'xdg-open "{filepath}"')

    def _log(self, message):
        """添加日志到队列"""
        self.log_queue.put(message)

    def _update_log(self):
        """从队列更新日志显示"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.insert(END, message + "\n")
                self.log_text.see(END)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._update_log)

    def _validate_inputs(self) -> bool:
        """验证输入参数"""
        # 检查目标目录
        target = self.target_dir.get().strip()
        if not target:
            messagebox.showerror("错误", "请选择目标目录")
            return False

        if not os.path.exists(target) or not os.path.isdir(target):
            messagebox.showerror("错误", "目标目录不存在或无效")
            return False

        # 检查规则文件
        mode = self.mode.get()
        if mode == 1:
            rules_file = "words.txt"
        else:
            rules_file = "regex_rules.txt"

        rules_path = os.path.join(self.script_dir, rules_file)
        if not os.path.exists(rules_path):
            messagebox.showerror(
                "错误",
                f"规则文件 {rules_file} 不存在\n请点击'编辑规则'创建或编辑规则文件"
            )
            return False

        return True

    def _gui_input(self, prompt: str) -> str:
        """GUI输入函数 - 在主线程弹出对话框"""
        # 将输入请求发送到队列
        self.input_queue.put(prompt)

        # 等待响应
        response = self.input_response_queue.get()
        return response

    def _check_input_queue(self):
        """检查是否有输入请求"""
        try:
            prompt = self.input_queue.get_nowait()
            # 弹出输入对话框
            result = simpledialog.askstring("输入", prompt, parent=self.root)
            if result is None:
                result = ""
            self.input_response_queue.put(result)
        except queue.Empty:
            pass
        finally:
            if self.is_running:
                self.root.after(100, self._check_input_queue)

    def _gui_output(self, message: str):
        """GUI输出函数"""
        self._log(message)

    def _start_rename(self):
        """开始重命名任务"""
        if self.is_running:
            return

        # 验证输入
        if not self._validate_inputs():
            return

        # 禁用按钮
        self.start_button.config(state=DISABLED)
        self.is_running = True

        # 清空日志
        self.log_text.delete(1.0, END)
        self._log("[INFO] 任务开始...")

        # 启动输入检查
        self.root.after(100, self._check_input_queue)

        # 在子线程中执行
        thread = threading.Thread(target=self._rename_worker, daemon=True)
        thread.start()

    def _rename_worker(self):
        """重命名工作线程"""
        try:
            target_dir = self.target_dir.get().strip()
            mode = self.mode.get()
            keep_structure = self.keep_structure.get()
            clear_output = self.clear_output.get()

            # 创建输出目录
            output_dir = os.path.join(self.script_dir, "output")

            if os.path.exists(output_dir) and clear_output:
                self._log("[INFO] 清空旧的 output 目录...")
                shutil.rmtree(output_dir)

            os.makedirs(output_dir, exist_ok=True)

            # 创建配置器（使用GUI的输入输出函数）
            configurator = InteractiveConfigurator(
                input_func=self._gui_input,
                output_func=self._gui_output
            )

            # 创建规则加载器
            rule_loader = RuleLoader(self.script_dir, configurator)

            # 加载规则
            self._log(f"[INFO] 加载规则...")
            rules = []

            if mode == 1:
                rules = rule_loader.load_simple_rules()
                self._log(f"[INFO] 加载规则 words.txt... 成功 ({len(rules)}条)")
            else:
                rules = rule_loader.load_regex_rules(interactive=True)
                self._log(f"[INFO] 加载规则 regex_rules.txt... 成功 ({len(rules)}条)")

            if not rules:
                self._log("[ERROR] 没有加载到任何规则")
                return

            # 创建重命名器
            renamer = FileRenamer()
            renamer.set_rules(rules)

            # 重定向输出
            original_print = print

            def gui_print(*args, **kwargs):
                message = " ".join(str(arg) for arg in args)
                self._log(message)

            # 临时替换print
            import builtins
            builtins.print = gui_print

            # 处理文件
            self._log(f"[INFO] 开始处理文件...")
            renamer.process_files(target_dir, keep_structure, output_dir)

            # 恢复print
            builtins.print = original_print

            # 显示统计
            stats = renamer.stats
            self._log("\n" + "=" * 60)
            self._log(f"[SUCCESS] 处理完成！")
            self._log(f"总文件数:     {stats['total']}")
            self._log(f"重命名文件数: {stats['renamed']}")
            self._log(f"仅复制文件数: {stats['copied']}")
            self._log(f"错误数:       {stats['errors']}")
            self._log(f"输出目录:     {output_dir}")
            self._log("=" * 60)

            # 弹出完成提示
            self.root.after(0, lambda: messagebox.showinfo("完成", "文件处理完毕！"))

        except Exception as e:
            self._log(f"[ERROR] 发生错误: {str(e)}")
            import traceback
            self._log(traceback.format_exc())
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理失败:\n{str(e)}"))

        finally:
            # 恢复按钮
            self.is_running = False
            self.root.after(0, lambda: self.start_button.config(state=NORMAL))


def main():
    """主入口"""
    # 创建主题窗口
    root = ttk.Window(themename="cosmo")
    app = ReNameFileGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
