"""
Prometheus 指标收集器模块。
"""
from typing import Dict
from prometheus_client import Gauge, Counter, Histogram

class MetricsCollector:
    """数据库比较指标的收集器。"""
    
    def __init__(self, default_labels: Dict[str, str] = None):
        self.default_labels = default_labels or {}
        
        # 表比较指标
        self.table_row_count = Gauge(
            'db_table_row_count',
            '表中的行数',
            ['database', 'table', 'environment'] + list(self.default_labels.keys())
        )
        
        self.table_comparison_status = Gauge(
            'db_table_comparison_status',
            '表比较状态 (1: 一致, 0: 不一致, -1: 错误)',
            ['table', 'environment'] + list(self.default_labels.keys())
        )
        
        self.row_difference = Gauge(
            'db_table_row_difference',
            '数据库之间的行数差异',
            ['table', 'environment'] + list(self.default_labels.keys())
        )
        
        # 性能指标
        self.comparison_duration = Histogram(
            'db_table_comparison_duration_seconds',
            '比较表所需的时间',
            ['table', 'environment'] + list(self.default_labels.keys()),
            buckets=(1, 5, 10, 30, 60, 120, 300, 600)
        )
        
        self.query_duration = Histogram(
            'db_query_duration_seconds',
            '数据库查询所需的时间',
            ['database', 'table', 'query_type', 'environment'] + list(self.default_labels.keys()),
            buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0)
        )
        
        # 错误指标
        self.comparison_errors = Counter(
            'db_table_comparison_errors_total',
            '比较错误的总数',
            ['table', 'error_type', 'environment'] + list(self.default_labels.keys())
        )
        
        self.query_errors = Counter(
            'db_query_errors_total',
            '查询错误的总数',
            ['database', 'table', 'error_type', 'environment'] + list(self.default_labels.keys())
        )
        
        # 数据一致性指标
        self.checksum_status = Gauge(
            'db_table_checksum_status',
            '表校验和比较状态 (1: 匹配, 0: 不匹配, -1: 错误)',
            ['table', 'chunk_id', 'environment'] + list(self.default_labels.keys())
        )
        
        self.last_successful_comparison = Gauge(
            'db_table_last_successful_comparison',
            '最后一次成功比较的时间戳',
            ['table', 'environment'] + list(self.default_labels.keys())
        )
        
        # 资源使用指标
        self.connection_pool_usage = Gauge(
            'db_connection_pool_usage',
            '当前使用的连接数',
            ['database', 'environment'] + list(self.default_labels.keys())
        )
        
        self.worker_pool_usage = Gauge(
            'db_worker_pool_usage',
            '当前使用的工作线程数',
            ['environment'] + list(self.default_labels.keys())
        )
    
    def set_table_row_count(self, database: str, table: str, count: int, environment: str = 'production'):
        """设置特定数据库中表的行数。"""
        labels = {**self.default_labels, 'database': database, 'table': table, 'environment': environment}
        self.table_row_count.labels(**labels).set(count)
    
    def set_comparison_status(self, table: str, status: int, environment: str = 'production'):
        """设置表的比较状态。"""
        labels = {**self.default_labels, 'table': table, 'environment': environment}
        self.table_comparison_status.labels(**labels).set(status)
    
    def set_row_difference(self, table: str, difference: int, environment: str = 'production'):
        """设置表的行数差异。"""
        labels = {**self.default_labels, 'table': table, 'environment': environment}
        self.row_difference.labels(**labels).set(difference)
    
    def observe_comparison_duration(self, table: str, duration: float, environment: str = 'production'):
        """记录表比较的持续时间。"""
        labels = {**self.default_labels, 'table': table, 'environment': environment}
        self.comparison_duration.labels(**labels).observe(duration)
    
    def observe_query_duration(self, database: str, table: str, query_type: str, 
                             duration: float, environment: str = 'production'):
        """记录数据库查询的持续时间。"""
        labels = {
            **self.default_labels,
            'database': database,
            'table': table,
            'query_type': query_type,
            'environment': environment
        }
        self.query_duration.labels(**labels).observe(duration)
    
    def increment_comparison_error(self, table: str, error_type: str, environment: str = 'production'):
        """增加比较错误计数。"""
        labels = {**self.default_labels, 'table': table, 'error_type': error_type, 'environment': environment}
        self.comparison_errors.labels(**labels).inc()
    
    def increment_query_error(self, database: str, table: str, error_type: str, 
                            environment: str = 'production'):
        """增加查询错误计数。"""
        labels = {
            **self.default_labels,
            'database': database,
            'table': table,
            'error_type': error_type,
            'environment': environment
        }
        self.query_errors.labels(**labels).inc()
    
    def set_checksum_status(self, table: str, chunk_id: str, status: int, environment: str = 'production'):
        """设置表块的校验和比较状态。"""
        labels = {
            **self.default_labels,
            'table': table,
            'chunk_id': chunk_id,
            'environment': environment
        }
        self.checksum_status.labels(**labels).set(status)
    
    def update_last_successful_comparison(self, table: str, timestamp: float, 
                                        environment: str = 'production'):
        """更新最后一次成功比较的时间戳。"""
        labels = {**self.default_labels, 'table': table, 'environment': environment}
        self.last_successful_comparison.labels(**labels).set(timestamp)
    
    def set_connection_pool_usage(self, database: str, usage: int, environment: str = 'production'):
        """设置当前连接池使用情况。"""
        labels = {**self.default_labels, 'database': database, 'environment': environment}
        self.connection_pool_usage.labels(**labels).set(usage)
    
    def set_worker_pool_usage(self, usage: int, environment: str = 'production'):
        """设置当前工作线程池使用情况。"""
        labels = {**self.default_labels, 'environment': environment}
        self.worker_pool_usage.labels(**labels).set(usage) 