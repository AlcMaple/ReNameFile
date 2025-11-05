import os
import re
import shutil


def rename_files(directory_path, keep_structure):
    # 读取替换规则
    replacement_rules = {}
    path = os.path.dirname(os.path.abspath(__file__))

    try:
        with open(os.path.join(path, "words.txt"), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if "：" in line:
                    source, target = line.split("：", 1)
                    replacement_rules[source.lower()] = target
    except FileNotFoundError:
        print(f"找不到words.txt文件: {path}")
        return

    # 创建输出目录
    output_dir = os.path.join(path, "output")
    if os.path.exists(output_dir):
        print(f"警告: output目录已存在，将覆盖其中的文件")
    else:
        os.makedirs(output_dir)

    # 统计信息
    total_files = 0
    renamed_files = 0
    copied_files = 0

    # 遍历目录树
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            total_files += 1
            source_path = os.path.join(root, file)

            # 分离文件名和扩展名
            filename, extension = os.path.splitext(file)

            # 应用替换规则
            original_filename = filename
            for source, target in replacement_rules.items():
                pattern = re.compile(re.escape(source), re.IGNORECASE)
                filename = pattern.sub(target, filename)

            new_file = filename + extension

            # 目标路径
            if keep_structure:
                # 保持原目录结构
                relative_path = os.path.relpath(root, directory_path)
                dest_dir = os.path.join(output_dir, relative_path)
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, new_file)
            else:
                # 所有文件放在output根目录
                dest_path = os.path.join(output_dir, new_file)

                # 处理文件名冲突
                counter = 1
                base_dest_path = dest_path
                while os.path.exists(dest_path):
                    filename_no_ext = os.path.splitext(new_file)[0]
                    dest_path = os.path.join(
                        output_dir, f"{filename_no_ext}_{counter}{extension}"
                    )
                    counter += 1

            # 复制文件
            try:
                shutil.copy2(source_path, dest_path)

                if new_file != file:
                    renamed_files += 1
                    relative_source = os.path.relpath(source_path, directory_path)
                    print(f"重命名: {relative_source} -> {os.path.basename(dest_path)}")
                else:
                    copied_files += 1
                    relative_source = os.path.relpath(source_path, directory_path)
                    print(f"复制: {relative_source}")

            except Exception as e:
                print(f"处理 {source_path} 时出错: {e}")

    # 打印统计信息
    print("\n" + "=" * 50)
    print(f"处理完成！")
    print(f"总文件数: {total_files}")
    print(f"重命名文件数: {renamed_files}")
    print(f"仅复制文件数: {copied_files}")
    print(f"文件已保存到: {output_dir}")
    print("=" * 50)


if __name__ == "__main__":
    print("=" * 50)
    print("文件批量重命名工具")
    print("=" * 50)

    directory_path = input("请输入需要处理的目录的绝对路径: ").strip()

    # 验证目录是否存在
    if not os.path.exists(directory_path):
        print(f"错误: 目录不存在 - {directory_path}")
        exit(1)

    if not os.path.isdir(directory_path):
        print(f"错误: 路径不是一个目录 - {directory_path}")
        exit(1)

    # 是否保持目录结构
    while True:
        choice = input("是否保持原文件夹结构？(y/n): ").strip().lower()
        if choice in ["y", "n", "yes", "no"]:
            keep_structure = choice in ["y", "yes"]
            break
        else:
            print("请输入 y 或 n")

    print("\n开始处理...\n")
    rename_files(directory_path, keep_structure)
