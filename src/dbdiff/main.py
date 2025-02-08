"""
数据库差异对比导出器的主应用入口。
用于比较和监控不同数据库之间数据一致性。
"""
from fastapi import FastAPI, BackgroundTasks, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import logging
import yaml
from contextlib import asynccontextmanager
import asyncio
from typing import Dict, Any

from .config import load_config
from .db.connection import DatabaseConnectionManager
from .metrics.collectors import MetricsCollector
from .core.comparator import TableComparator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dbdiff.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 全局实例
config: Dict[str, Any] = {}
db_manager: DatabaseConnectionManager = None
metrics_collector: MetricsCollector = None
table_comparator: TableComparator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """管理应用生命周期。"""
    global config, db_manager, metrics_collector, table_comparator
    
    try:
        # 加载配置
        config = load_config()
        
        # 初始化组件
        metrics_collector = MetricsCollector(
            default_labels=config['metrics'].get('labels', {})
        )
        db_manager = DatabaseConnectionManager(config)
        table_comparator = TableComparator(db_manager, metrics_collector, config)
        
        # 如果启用了自动刷新，启动后台指标收集任务
        if config['monitoring']['auto_refresh']['enabled']:
            background_task = asyncio.create_task(update_metrics())
        
        logger.info("应用启动成功")
        yield
        
        # 清理资源
        if config['monitoring']['auto_refresh']['enabled']:
            background_task.cancel()
            try:
                await background_task
            except asyncio.CancelledError:
                pass
        
        await db_manager.close_pools()
        logger.info("应用关闭完成")
        
    except Exception as e:
        logger.error(f"应用生命周期出错: {str(e)}")
        raise

async def update_metrics():
    """后台任务：定期更新指标。"""
    while True:
        try:
            # 更新连接池指标
            pool_usage = db_manager.get_pool_usage()
            for db_name, usage in pool_usage.items():
                metrics_collector.set_connection_pool_usage(db_name, usage)
            
            # 比较所有配置的表
            for table_config in config['tables']:
                await table_comparator.compare_table(table_config)
                
        except Exception as e:
            logger.error(f"更新指标时出错: {str(e)}")
            
        # 等待下一次更新间隔
        await asyncio.sleep(config['monitoring']['auto_refresh']['interval'])

# 创建 FastAPI 应用
app = FastAPI(
    title="数据库差异对比导出器",
    description="用于比较和监控不同数据库之间数据一致性的 Prometheus 导出器",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/metrics")
async def metrics() -> Response:
    """Prometheus 指标接口。"""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.post("/check")
async def check(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """触发手动比较的接口。"""
    for table_config in config['tables']:
        background_tasks.add_task(
            table_comparator.compare_table,
            table_config
        )
    return {"message": "数据库比较检查已启动"}

@app.get("/health")
async def health() -> Dict[str, str]:
    """健康检查接口。"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=False
    ) 