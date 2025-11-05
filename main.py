import os
import re
import shutil


class FileRenamer:
    def __init__(self, script_dir):
        self.script_dir = script_dir
        self.rules = []
        self.stats = {"total": 0, "renamed": 0, "copied": 0, "errors": 0}

    def load_replacement_rules(self):
        """加载替换规则（words.txt）"""
        rules_file = os.path.join(self.script_dir, "words.txt")
        try:
            with open(rules_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "：" in line:
                        source, target = line.split("：", 1)
                        # 不区分大小写
                        pattern = re.compile(re.escape(source), re.IGNORECASE)
                        self.rules.append(("simple", pattern, target, None))
            print(f" 加载了 {len(self.rules)} 条替换规则")
            return True
        except FileNotFoundError:
            print(f" 找不到 words.txt 文件")
            return False

    def load_regex_rules(self):
        """加载正则表达式规则（regex_rules.txt）"""
        rules_file = os.path.join(self.script_dir, "regex_rules.txt")
        try:
            with open(rules_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # 交互式规则
                    if "==>" in line:
                        pattern_str, replacement = line.split("==>", 1)
                        pattern_str = pattern_str.strip()
                        replacement = replacement.strip()

                        try:
                            # 原始字符串
                            pattern = re.compile(pattern_str)

                            # 特殊规则类型
                            rule_type = "regex"
                            metadata = None

                            # "提取数字"规则
                            if replacement == "{number}":
                                rule_type = "extract_number"
                                metadata = {}
                            # "提取文本"规则
                            elif replacement == "{text}":
                                rule_type = "extract_text"
                                metadata = {}
                            # "自定义格式"规则
                            elif "{" in replacement and "}" in replacement:
                                rule_type = "custom_format"
                                metadata = {"format_str": replacement}

                            self.rules.append(
                                (rule_type, pattern, replacement, metadata)
                            )

                        except re.error as e:
                            print(f" 第 {line_num} 行正则表达式错误: {e}")

            print(f" 加载了 {len(self.rules)} 条正则表达式规则")
            return len(self.rules) > 0
        except FileNotFoundError:
            print(f" 找不到 regex_rules.txt 文件")
            return False

    def configure_interactive_rules(self):
        """配置交互式规则的参数"""
        for i, (rule_type, pattern, replacement, metadata) in enumerate(self.rules):
            if rule_type == "extract_number":
                print(f"\n检测到规则 #{i+1}: 提取数字规则")
                print(f"  模式: {pattern.pattern}")
                while True:
                    try:
                        digits = input(
                            "  你想把数字格式化成几位数？(输入数字，如 2 表示两位数): "
                        ).strip()
                        digits = int(digits)
                        if digits > 0:
                            metadata["digits"] = digits
                            print(f"   已设置为 {digits} 位数")
                            break
                        else:
                            print("  请输入大于0的数字")
                    except ValueError:
                        print("  请输入有效的数字")

            elif rule_type == "extract_text":
                print(f"\n检测到规则 #{i+1}: 提取文本规则")
                print(f"  模式: {pattern.pattern}")
                choice = input("  是否转换为大写？(y/n): ").strip().lower()
                metadata["uppercase"] = choice in ["y", "yes"]
                choice = input("  是否转换为小写？(y/n): ").strip().lower()
                metadata["lowercase"] = choice in ["y", "yes"]
                print(f"   已配置文本提取规则")

            elif rule_type == "custom_format":
                print(f"\n检测到规则 #{i+1}: 自定义格式规则")
                print(f"  模式: {pattern.pattern}")
                print(f"  格式: {replacement}")

                # 提取所有占位符
                placeholders = re.findall(r"\{(\w+)(?::(\d+))?\}", replacement)
                for placeholder, width in placeholders:
                    if placeholder == "number" and not width:
                        while True:
                            try:
                                digits = input(
                                    f"  占位符 {{{placeholder}}} 要格式化成几位数？: "
                                ).strip()
                                digits = int(digits)
                                if digits > 0:
                                    if "format_params" not in metadata:
                                        metadata["format_params"] = {}
                                    metadata["format_params"][placeholder] = digits
                                    break
                                else:
                                    print("  请输入大于0的数字")
                            except ValueError:
                                print("  请输入有效的数字")

                print(f"   已配置自定义格式规则")

    def apply_rules(self, filename):
        """应用所有规则到文件名"""
        new_filename = filename

        for rule_type, pattern, replacement, metadata in self.rules:
            match = pattern.search(new_filename)

            if rule_type == "simple":
                new_filename = pattern.sub(replacement, new_filename)

            elif rule_type == "regex":
                converted_replacement = replacement
                converted_replacement = re.sub(
                    r"\$(\d+)", r"\\\1", converted_replacement
                )
                new_filename = pattern.sub(converted_replacement, new_filename)

            elif rule_type == "extract_number" and match:
                # 提取数字并格式化
                if match.groups():
                    number_str = match.group(1)
                    try:
                        number = int(number_str)
                        digits = metadata.get("digits", 1)
                        formatted_number = str(number).zfill(digits)
                        new_filename = formatted_number
                    except ValueError:
                        pass

            elif rule_type == "extract_text" and match:
                # 提取文本
                if match.groups():
                    text = match.group(1)
                    if metadata.get("uppercase"):
                        text = text.upper()
                    elif metadata.get("lowercase"):
                        text = text.lower()
                    new_filename = text

            elif rule_type == "custom_format" and match:
                # 自定义格式
                format_str = metadata["format_str"]
                format_params = metadata.get("format_params", {})

                # 替换占位符
                result = format_str
                for i, group in enumerate(match.groups(), 1):
                    # 处理 \1, \2 等
                    result = result.replace(f"\\{i}", group if group else "")

                # 处理 {number}, {text} 等占位符
                if "{number}" in result and match.groups():
                    try:
                        number = int(match.group(1))
                        digits = format_params.get("number", 1)
                        formatted_number = str(number).zfill(digits)
                        result = result.replace("{number}", formatted_number)
                    except (ValueError, IndexError):
                        pass

                if "{text}" in result and match.groups():
                    try:
                        text = match.group(1)
                        result = result.replace("{text}", text)
                    except IndexError:
                        pass

                new_filename = result

        return new_filename

    def get_unique_filename(self, dest_dir, filename):
        """处理文件名冲突"""
        dest_path = os.path.join(dest_dir, filename)

        if not os.path.exists(dest_path):
            return dest_path

        name, ext = os.path.splitext(filename)
        counter = 1

        while os.path.exists(dest_path):
            new_filename = f"{name}_{counter}{ext}"
            dest_path = os.path.join(dest_dir, new_filename)
            counter += 1

        return dest_path

    def process_files(self, directory_path, keep_structure, output_dir):
        """处理所有文件"""
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                self.stats["total"] += 1
                source_path = os.path.join(root, file)

                # 分离文件名和扩展名
                filename, extension = os.path.splitext(file)

                # 应用重命名规则
                new_filename = self.apply_rules(filename)
                new_file = new_filename + extension

                # 目标路径
                if keep_structure:
                    relative_path = os.path.relpath(root, directory_path)
                    dest_dir = os.path.join(output_dir, relative_path)
                    os.makedirs(dest_dir, exist_ok=True)
                    dest_path = os.path.join(dest_dir, new_file)
                else:
                    dest_path = self.get_unique_filename(output_dir, new_file)

                # 复制文件
                try:
                    shutil.copy2(source_path, dest_path)

                    relative_source = os.path.relpath(source_path, directory_path)
                    if new_file != file:
                        self.stats["renamed"] += 1
                        print(f" 重命名: {relative_source}")
                        print(f"  {file} -> {os.path.basename(dest_path)}")
                    else:
                        self.stats["copied"] += 1
                        print(f"  复制: {relative_source}")

                except Exception as e:
                    self.stats["errors"] += 1
                    print(f" 处理 {source_path} 时出错: {e}")

    def print_stats(self, output_dir):
        """打印统计信息"""
        print("\n" + "=" * 60)
        print("处理完成！")
        print(f"总文件数:     {self.stats['total']}")
        print(f"重命名文件数: {self.stats['renamed']}")
        print(f"仅复制文件数: {self.stats['copied']}")
        print(f"错误数:       {self.stats['errors']}")
        print(f"输出目录:     {output_dir}")
        print("=" * 60)


def create_sample_files(script_dir):
    """创建示例配置文件"""

    # 替换规则示例
    words_content = """# 文本替换规则（不区分大小写）
# 格式: 原文本：替换文本
# 以 # 开头的行为注释

old：new
test：测试
document：文档
photo：照片
"""

    # 正则表达式规则示例
    regex_content = r"""# 正则表达式替换规则
# 格式: 正则模式 ==> 替换内容
# 以 # 开头的行为注释
# 注意：在txt文件中直接写 \d \w 等，不需要双反斜杠

# ============ 交互式规则（运行时会询问参数）============

# 提取数字规则（运行时会询问格式化位数）
# 示例: "File - 1.txt" 提取数字 1，如果设置2位数 -> "01.txt"
.*\s*-\s*(\d+).* ==> {number}

# 提取文本规则（运行时会询问是否转换大小写）
# 示例: "Prefix-MyFile-Suffix.txt" 提取 MyFile
.*-([^-]+)-.* ==> {text}

# 自定义格式规则（运行时会询问占位符参数）
# 示例: "IMG_20231201_001.jpg" -> "2023-12-01_001.jpg"
# 注意：使用 $1 $2 $3 来引用捕获组，而不是 \1 \2 \3
# IMG_(\d{4})(\d{2})(\d{2})_(\d+).* ==> $1-$2-$3_{number}


# ============ 普通正则表达式规则（直接替换）============

# 将日期格式从 YYYY-MM-DD 改为 YYYYMMDD
# 使用 $1 $2 $3 来引用捕获组
# (\d{4})-(\d{2})-(\d{2}) ==> $1$2$3

# 删除文件名中的所有数字
# \d+ ==> 

# 将下划线改为连字符
# _ ==> -

# 删除文件名中的空格
# \s+ ==> 

# 删除版本号 (如 _v1, _v2)
# _v\d+ ==> 

# 添加前缀（$1 代表整个原文件名）
# ^(.+) ==> prefix_$1

# 添加后缀
# ^(.+) ==> $1_suffix

# 提取括号内容
# .*\(([^)]+)\).* ==> $1
"""

    # 写入示例文件
    samples = {
        "words.txt": words_content,
        "regex_rules.txt": regex_content,
    }

    for filename, content in samples.items():
        filepath = os.path.join(script_dir, filename)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f" 创建示例文件: {filename}")


def display_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("文件批量重命名工具")
    print("=" * 60)
    print("请选择重命名模式:")
    print("1. 简单替换模式 (words.txt)")
    print("2. 正则表达式模式 (regex_rules.txt)")
    print("0. 创建示例配置文件并退出")
    print("=" * 60)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    display_menu()

    mode = input("请选择模式 (0-2): ").strip()

    if mode == "0":
        create_sample_files(script_dir)
        print("\n示例文件已创建，请编辑配置文件后重新运行程序。")
        return

    # 创建重命名器实例
    renamer = FileRenamer(script_dir)

    # 根据模式加载规则
    print("\n加载规则...")
    if mode == "1":
        if not renamer.load_replacement_rules():
            return
    elif mode == "2":
        if not renamer.load_regex_rules():
            return
        # 配置交互式规则
        renamer.configure_interactive_rules()
    else:
        print(" 无效的选择")
        return

    # 获取输入目录
    print()
    directory_path = input("请输入需要处理的目录的绝对路径: ").strip()

    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        print(f" 错误: 无效的目录路径")
        return

    # 询问是否保持目录结构
    while True:
        choice = input("是否保持原文件夹结构？(y/n): ").strip().lower()
        if choice in ["y", "n", "yes", "no"]:
            keep_structure = choice in ["y", "yes"]
            break
        else:
            print("请输入 y 或 n")

    # 创建输出目录
    output_dir = os.path.join(script_dir, "output")
    if os.path.exists(output_dir):
        choice = input(f"\noutput目录已存在，是否清空？(y/n): ").strip().lower()
        if choice in ["y", "yes"]:
            shutil.rmtree(output_dir)
            os.makedirs(output_dir)
    else:
        os.makedirs(output_dir)

    # 开始处理
    print("\n开始处理文件...\n")
    renamer.process_files(directory_path, keep_structure, output_dir)

    # 显示统计
    renamer.print_stats(output_dir)


if __name__ == "__main__":
    main()
