"""
数据库连接管理模块。
"""
from typing import Dict, Any, Optional
import asyncio
import logging
import oracledb
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabaseConnectionManager:
    """管理数据库连接和连接池。"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._oracle_pool = None
        self._pg_pool = None
        self.setup_connection_pools()
    
    def setup_connection_pools(self):
        """初始化数据库连接池。"""
        try:
            # 设置 Oracle 连接池
            oracle_config = self.config['databases']['oracle']
            self._oracle_pool = oracledb.SessionPool(
                user=oracle_config['user'],
                password=oracle_config['password'],
                dsn=oracle_config['dsn'],
                min=1,
                max=oracle_config['pool_size'],
                increment=1,
                getmode=oracledb.SPOOL_ATTRVAL_WAIT,
                timeout=oracle_config['pool_timeout']
            )
            logger.info("Oracle 连接池初始化完成")
            
            # 设置 PostgreSQL 连接池
            pg_config = self.config['databases']['postgresql']
            self._pg_pool = ThreadedConnectionPool(
                minconn=1,
                maxconn=pg_config['pool_size'],
                host=pg_config['host'],
                port=pg_config['port'],
                database=pg_config['database'],
                user=pg_config['user'],
                password=pg_config['password'],
                connect_timeout=pg_config['connect_timeout']
            )
            logger.info("PostgreSQL 连接池初始化完成")
            
        except Exception as e:
            logger.error(f"初始化连接池时出错: {str(e)}")
            raise
    
    @asynccontextmanager
    async def get_oracle_connection(self):
        """从 Oracle 连接池获取连接。"""
        connection = None
        try:
            connection = await asyncio.get_event_loop().run_in_executor(
                None, self._oracle_pool.acquire
            )
            yield connection
        finally:
            if connection:
                await asyncio.get_event_loop().run_in_executor(
                    None, self._oracle_pool.release, connection
                )
    
    @asynccontextmanager
    async def get_pg_connection(self):
        """从 PostgreSQL 连接池获取连接。"""
        connection = None
        try:
            connection = await asyncio.get_event_loop().run_in_executor(
                None, self._pg_pool.getconn
            )
            yield connection
        finally:
            if connection:
                await asyncio.get_event_loop().run_in_executor(
                    None, self._pg_pool.putconn, connection
                )
    
    def get_pool_usage(self) -> Dict[str, int]:
        """获取当前连接池使用统计。"""
        return {
            'oracle': self._oracle_pool.busy if self._oracle_pool else 0,
            'postgresql': self._pg_pool.used if self._pg_pool else 0
        }
    
    async def close_pools(self):
        """关闭所有连接池。"""
        if self._oracle_pool:
            await asyncio.get_event_loop().run_in_executor(
                None, self._oracle_pool.close
            )
        if self._pg_pool:
            await asyncio.get_event_loop().run_in_executor(
                None, self._pg_pool.closeall
            )
        logger.info("所有数据库连接池已关闭") 