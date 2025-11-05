"""
替换规则加载器
从 words.txt 文件加载文本替换规则
"""

import os
import re
from typing import List
from .types import Rule


class SimpleRuleLoader:
    """替换规则加载器"""

    @staticmethod
    def load(script_dir: str) -> List[Rule]:
        """
        加载替换规则（words.txt）

        Args:
            script_dir: 脚本所在目录

        Returns:
            规则列表
        """
        rules = []
        rules_file = os.path.join(script_dir, "words.txt")

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
                        rule = Rule("simple", pattern, target, None)
                        rules.append(rule)

            print(f" 加载了 {len(rules)} 条替换规则")
            return rules

        except FileNotFoundError:
            print(f" 找不到 words.txt 文件")
            return []
