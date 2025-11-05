"""
规则类型定义
"""

from typing import Pattern, Optional, Dict, Any


class Rule:
    """重命名规则"""

    def __init__(
        self,
        rule_type: str,
        pattern: Pattern,
        replacement: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.rule_type = rule_type
        self.pattern = pattern
        self.replacement = replacement
        self.metadata = metadata if metadata is not None else {}

    def __repr__(self):
        return f"Rule(type={self.rule_type}, pattern={self.pattern.pattern})"
