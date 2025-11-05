"""
正则表达式规则加载器
从 regex_rules.txt 文件加载正则表达式规则
"""

import os
import re
from typing import List
from .types import Rule


class RegexRuleLoader:
    """正则表达式规则加载器"""

    @staticmethod
    def load(script_dir: str) -> List[Rule]:
        """
        加载正则表达式规则（regex_rules.txt）

        Args:
            script_dir: 脚本所在目录

        Returns:
            规则列表
        """
        rules = []
        rules_file = os.path.join(script_dir, "regex_rules.txt")

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

                            rule = Rule(rule_type, pattern, replacement, metadata)
                            rules.append(rule)

                        except re.error as e:
                            print(f" 第 {line_num} 行正则表达式错误: {e}")

            print(f" 加载了 {len(rules)} 条正则表达式规则")
            return rules

        except FileNotFoundError:
            print(f" 找不到 regex_rules.txt 文件")
            return []
