"""
配置加载和验证模块。
"""
from typing import Dict, Any
import os
import yaml
from pydantic import BaseModel, Field
from typing import List, Optional

class DatabaseConfig(BaseModel):
    """数据库连接配置基类。"""
    user: str
    password: str
    pool_size: int = Field(default=5, ge=1, le=100)
    pool_timeout: int = Field(default=30, ge=1)
    connect_timeout: int = Field(default=10, ge=1)

class OracleConfig(DatabaseConfig):
    """Oracle 特定配置。"""
    dsn: str

class PostgresConfig(DatabaseConfig):
    """PostgreSQL 特定配置。"""
    host: str
    port: int = Field(default=5432)
    database: str

class TableConfig(BaseModel):
    """表比较配置。"""
    name: str
    primary_key: str
    batch_columns: List[str]
    comparison_columns: List[str]

class MonitoringConfig(BaseModel):
    """监控配置。"""
    auto_refresh: Dict[str, Any]
    batch_size: int = Field(default=1000000, ge=1)
    parallel_queries: bool = True
    max_workers: int = Field(default=32, ge=1)

class MetricsConfig(BaseModel):
    """指标配置。"""
    labels: Dict[str, str] = Field(default_factory=dict)
    custom_labels: Dict[str, str] = Field(default_factory=dict)
    collection: Dict[str, bool]

class LoggingConfig(BaseModel):
    """日志配置。"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "dbdiff.log"
    max_size: int = Field(default=100, ge=1)
    backup_count: int = Field(default=5, ge=0)
    console_output: bool = True

class PerformanceConfig(BaseModel):
    """性能调优配置。"""
    use_parallel_processing: bool = True
    chunk_size: int = Field(default=100000, ge=1)
    max_concurrent_tables: int = Field(default=10, ge=1)
    connection_pool_size: int = Field(default=5, ge=1)
    query_timeout: int = Field(default=300, ge=1)

class AppConfig(BaseModel):
    """主应用配置。"""
    databases: Dict[str, DatabaseConfig]
    monitoring: MonitoringConfig
    tables: List[TableConfig]
    metrics: MetricsConfig
    logging: LoggingConfig
    performance: PerformanceConfig

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    从 YAML 文件加载并验证配置。
    
    参数:
        config_path: 配置文件路径。如果未提供，
                    将在当前目录查找 config.yaml 或
                    使用环境变量 CONFIG_PATH。
    
    返回:
        验证后的配置字典。
    
    异常:
        FileNotFoundError: 如果找不到配置文件。
        ValidationError: 如果配置无效。
    """
    if not config_path:
        config_path = os.getenv('CONFIG_PATH', 'config.yaml')
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"找不到配置文件: {config_path}")
    
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    # 验证配置
    config = AppConfig(**config_dict)
    
    # 转换为字典以保持向后兼容性
    return config.model_dump() 