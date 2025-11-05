# 目录

- [项目介绍](#项目介绍)
- [温馨提示](#温馨提示)
- [使用](#使用)
- [项目扩展](#项目扩展)

# 项目介绍

- 项目名称：ReNameFile
- 项目描述：一个批量重命名文件工具，可以批量重命名指定目录下的所有文件

# 温馨提示

- 在使用前，防止出问题，请备份好需要重命名的文件夹（用副本去执行脚本）
- 在使用后，请仔细检查重命名后的文件是否正确，如有问题，请联系作者
- 安全性兼容，请保留源文件夹（重命名前的文件夹）一段时间，待你使用重命名后的文件夹一段时间没出问题后，再删除原文件夹（有能力的可以考虑不删源文件夹）

# 使用

- 准备需要替换文件名的内容，格式按照 words.txt 文件格式，每行一个需要替换的词语，格式为：原词语：新词语
  > 注意是中文冒号
- 准备需要重命名文件的文件夹绝对路径路径
- 运行 main.py 文件，输入需要替换的文件名的文件夹绝对路径

# 可视化教程

## 重命名前目录结构

```bash
C:\
├── ReNameFile
│   ├── rename_files.py
│   └── words.txt
│
└── MySourceFiles
    ├── report_A_daily.pdf
    ├── MEETING_NOTES_projectX.docx
    └── UNCHANGED_FILE.txt
```

## 准备 words.txt

```bash
report：报告
daily：日报
ProjectX：大型项目A
```

## 重命名后的结构

```bash
C:\
├── MyScript
│   ├── rename_files.py
│   ├── words.txt
│   └── output
│       ├── 报告_日报.pdf
│       ├── MEETING_NOTES_大型项目A.docx
│       └── UNCHANGED_FILE.txt
│
└── MySourceFiles
    ├── report_A_daily.pdf
    ├── MEETING_NOTES_projectX.docx
    └── UNCHANGED_FILE.txt
```

# 项目扩展

| 状态 | 任务                                       | 备注 |
| :--: | ------------------------------------------ | ---- |
|  ✅  | 支持重命名子目录下的文件                   |      |
|  ✅  | 新增输出平铺结构和原结构                   |      |
|  ✅  | 支持正则表达式                             |      |
|  ⬜  | WebGUI 界面                                |      |
|  ⬜  | 提供选择文件方式定位需要重命名的目录       |      |
|  ⬜  | 动态计算规则，根据给的案例计算出重命名公式 |      |
