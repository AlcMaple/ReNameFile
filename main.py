import os
import re

# 文件/目录高级操作库
import shutil


def rename_files(directory_path):
    # 读取替换规则
    replacement_rules = {}
    # 获取项目文件夹绝对路径
    '''
        os.path.abspath(path)：返回path规范化的绝对路径。    /home/user/code/script.py
        os.path.dirname(path)：返回path中去掉文件名后的路径。    若路径是 /home/user/code/script.py，则返回 /home/user/code
        __file__：表示当前脚本文件的路径     /home/user/code/script.py
    '''
    path = os.path.dirname(os.path.abspath(__file__))
    try:
        # 只读方式打开文件
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
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取指定目录下的所有文件
    files = [
        f
        for f in os.listdir(directory_path)
        if os.path.isfile(os.path.join(directory_path, f))
    ]

    for file in files:

        filename, extension = os.path.splitext(file)

        # 将_A_转换为_
        new_filename = filename.replace("_A_", "_")

        # 应用替换规则
        for source, target in replacement_rules.items():
            # 不区分大小写替换
            pattern = re.compile(re.escape(source), re.IGNORECASE)
            new_filename = pattern.sub(target, new_filename)

        new_file = new_filename + extension

        # 复制文件到输出目录，如果需要重命名则用新名字
        source_path = os.path.join(directory_path, file)
        dest_path = os.path.join(output_dir, new_file)

        try:
            shutil.copy2(source_path, dest_path)
            if new_file != file:
                print(f"{file} -> {new_file}")
            else:
                print(f"复制: {file}")
        except Exception as e:
            print(f"处理 {file} 时出错: {e}")


if __name__ == "__main__":
    directory_path = input("请输入需要重命名文件的目录的绝对路径: ")
    rename_files(directory_path)
    print("处理完成，文件已保存到output目录")
