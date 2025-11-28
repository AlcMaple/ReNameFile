"""
交互式规则配置器
负责配置需要用户输入的规则参数
"""

import re
from typing import List, Callable, Optional
from .types import Rule


class InteractiveConfigurator:
    """交互式规则配置器"""

    def __init__(
        self,
        input_func: Optional[Callable[[str], str]] = None,
        output_func: Optional[Callable[[str], None]] = None,
    ):
        """
        初始化配置器

        Args:
            input_func: 自定义输入函数，默认使用 input()
            output_func: 自定义输出函数，默认使用 print()
        """
        self.input_func = input_func or input
        self.output_func = output_func or print

    def configure(self, rules: List[Rule]) -> None:
        """
        配置交互式规则的参数

        Args:
            rules: 规则列表
        """
        for i, rule in enumerate(rules):
            if rule.rule_type == "extract_number":
                self._configure_extract_number(i, rule)

            elif rule.rule_type == "extract_text":
                self._configure_extract_text(i, rule)

            elif rule.rule_type == "custom_format":
                self._configure_custom_format(i, rule)

    def _configure_extract_number(self, index: int, rule: Rule) -> None:
        """配置提取数字规则"""
        self.output_func(f"\n检测到规则 #{index+1}: 提取数字规则")
        self.output_func(f"  模式: {rule.pattern.pattern}")

        while True:
            try:
                digits = self.input_func(
                    "  你想把数字格式化成几位数？(输入数字，如 2 表示两位数): "
                ).strip()
                digits = int(digits)
                if digits > 0:
                    rule.metadata["digits"] = digits
                    self.output_func(f"   已设置为 {digits} 位数")
                    break
                else:
                    self.output_func("  请输入大于0的数字")
            except ValueError:
                self.output_func("  请输入有效的数字")

    def _configure_extract_text(self, index: int, rule: Rule) -> None:
        """配置提取文本规则"""
        self.output_func(f"\n检测到规则 #{index+1}: 提取文本规则")
        self.output_func(f"  模式: {rule.pattern.pattern}")

        choice = self.input_func("  是否转换为大写？(y/n): ").strip().lower()
        rule.metadata["uppercase"] = choice in ["y", "yes"]

        choice = self.input_func("  是否转换为小写？(y/n): ").strip().lower()
        rule.metadata["lowercase"] = choice in ["y", "yes"]

        self.output_func(f"   已配置文本提取规则")

    def _configure_custom_format(self, index: int, rule: Rule) -> None:
        """配置自定义格式规则"""
        self.output_func(f"\n检测到规则 #{index+1}: 自定义格式规则")
        self.output_func(f"  模式: {rule.pattern.pattern}")
        self.output_func(f"  格式: {rule.replacement}")

        # 提取所有占位符
        placeholders = re.findall(r"\{(\w+)(?::(\d+))?\}", rule.replacement)
        for placeholder, width in placeholders:
            if placeholder == "number" and not width:
                while True:
                    try:
                        digits = self.input_func(
                            f"  占位符 {{{placeholder}}} 要格式化成几位数？: "
                        ).strip()
                        digits = int(digits)
                        if digits > 0:
                            if "format_params" not in rule.metadata:
                                rule.metadata["format_params"] = {}
                            rule.metadata["format_params"][placeholder] = digits
                            break
                        else:
                            self.output_func("  请输入大于0的数字")
                    except ValueError:
                        self.output_func("  请输入有效的数字")

        self.output_func(f"   已配置自定义格式规则")
