[toc]

# 项目背景

- 在开发这个工具之初，面临的核心需求是：不仅要能简单替换文字，还要能处理复杂的正则逻辑，且必须绝对安全
- 基于此，确立了三个核心开发原则:
  - 非破坏性：永远不要直接修改源文件。采用“读取 -> 计算新名 -> 复制到 Output”的流程
  - 规则与执行分离 ：解析规则（Parser）和执行重命名（Executor）必须分开
  - 管道化处理：一个文件名可能经过多次处理，代码结构必须支持这种流式操作

# 运作流程图示例

```bash
[用户]
  |
  +--- 1. 选择模式 (main.py)
  |
  v
[规则加载器 (Loader)] <---- 读取 .txt 配置文件
  |
  +--- 2. 生成规则对象 (Rule Objects)
  |
  +--- 3. (如果是交互式规则) 拦截下来，询问用户参数 (Configurator)
  |
  v
[重命名引擎 (FileRenamer)]
  |
  +--- 4. 拿到文件名 "photo.jpg"
  |
  +--- 5. 循环应用所有规则 (Rule 1 -> Rule 2 -> Rule 3...)
  |
  v
[文件系统 (os/shutil)] ----> 输出 "2023-11-26.jpg"
```

# main.py

- 程序的入口,只负责组装

## FileRenamer 类

- apply_rules(filename)
  - 接收一个文件名，然后像流水线一样，让它依次经过 self.rules 列表中的每一个规则
  - 规则按顺序执行，第一个规则改完的名字，会传给第二个规则继续改
- get_unique_filename(...)
  - 保存文件前，检查“目标文件是否存在”。如果存在，它会自动在后面加 `_1`, `_2`，防止把原有的文件覆盖掉
- process_files(...)
  - 遍历文件夹，把每个文件扔给 apply_rules 处理，最后调用 shutil.copy2 进行物理复制

# 提取数字并补零

```bash
[ 阶段一：(Loader) ]
      |
      +--- 1. 读取文本: ".*(\d+).* ==> {number}"
      |
      +--- 2. regex_loader 识别出 "{number}"
      |       -> 设定 rule_type = "extract_number"
      |       -> 设定 metadata = {}  <--- 注意：这里是空的！
      |
      v
[ 产出 Rule ] --------------------------------+
                                                  |
[ 阶段二：Configurator ]                  |
      |                                           |
      +--- 3. main.py 发现列表里有Rule对象，呼叫 Configurator
      |                                           |
      +--- 4. Configurator 看到 "extract_number"     |
      |       -> 暂停程序，问用户: "要几位补零？"        |
      |       -> 用户输入: "3"                        |
      |       -> 写入 rule.metadata["digits"] = 3     |
      |                                           |
      v                                           |
[ 产出 Rule ] <----------------------------------+
      |
      v
[ 阶段三：Renamer ]
      |
      +--- 5. Renamer 拿到文件名 "photo_1.jpg"
      |
      +--- 6. 匹配成功，准备执行 "extract_number" 逻辑
      |
      +--- 7. 查看 metadata["digits"]
      |       -> 发现是 3
      |       -> 执行 str(1).zfill(3)
      |
      +--- 8. 输出: "001.jpg"
```

## 制造 Rule 对象

- 当 RegexRuleLoader 读取 regex_rules.txt 时，它会进行“模式识别”
- txt: ... ==> {number}

```python
if replacement == "{number}":
    rule_type = "extract_number"  # <--- “特殊标记”
    metadata = {}                 # <--- 创建一个空字典
```

- 这是一个半成品 Rule 对象
- type: "extract_number"
- metadata: {} (空的是因为加载器只读文本，不知道用户想要几位补零)

## 拦截与补全

- main.py 拿到这个“半成品”列表后，会立刻调用 InteractiveConfigurator.configure(rules)

```python
# 遍历所有规则，检查rule_type
elif rule.rule_type == "extract_number":
    # 调用专属配置方法
    InteractiveConfigurator._configure_extract_number(i, rule)
```
