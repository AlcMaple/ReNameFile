"""
主规则加载器
统一的规则加载接口
"""

from typing import List
from .types import Rule
from .simple_loader import SimpleRuleLoader
from .regex_loader import RegexRuleLoader
from .configurator import InteractiveConfigurator


class RuleLoader:
    """主规则加载器"""

    def __init__(self, script_dir: str):
        """
        初始化规则加载器

        Args:
            script_dir: 脚本所在目录
        """
        self.script_dir = script_dir

    def load_simple_rules(self) -> List[Rule]:
        """
        加载替换规则

        Returns:
            规则列表
        """
        return SimpleRuleLoader.load(self.script_dir)

    def load_regex_rules(self, interactive: bool = True) -> List[Rule]:
        """
        加载正则表达式规则

        Args:
            interactive: 是否进行交互式配置

        Returns:
            规则列表
        """
        rules = RegexRuleLoader.load(self.script_dir)

        if interactive and rules:
            InteractiveConfigurator.configure(rules)

        return rules
