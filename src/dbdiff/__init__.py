"""
DBDiff-Exporter
用于比较和监控不同数据库之间数据一致性的 Prometheus 导出器。

主要功能：
- 支持 Oracle 和 PostgreSQL 数据库比较
- 提供 Prometheus 指标接口
- 支持大表分块比较
- 自动定期比较和监控
- 支持手动触发比较
"""

__version__ = "1.0.0"
__author__ = "Theo Zhang"
__description__ = "用于比较和监控不同数据库之间数据一致性的 Prometheus 导出器"

from .core import TableComparator
from .db import DatabaseConnectionManager
from .metrics import MetricsCollector
from .config import load_config

__all__ = [
    'TableComparator',
    'DatabaseConnectionManager',
    'MetricsCollector',
    'load_config',
    '__version__',
    '__author__',
    '__description__'
] 