# DBDiff-Exporter

用于比较和监控不同数据库之间数据一致性的 Prometheus Exporter。

## 功能特点

- 支持 Oracle 和 PostgreSQL 数据库比较
- 提供 Prometheus 指标接口
- 支持大表分块比较
- 自动定期比较和监控
- 支持手动触发比较
- 提供详细的指标和日志
- Docker 容器化部署
- 支持 Windows 和 Linux 环境

## 快速开始

### 使用预编译二进制文件

1. 下载最新的发布包：
   - Linux: `dbdiff-exporter-linux.tar.gz`

2. 解压文件：
   ```bash
   tar xzf dbdiff-exporter-linux.tar.gz
   cd dbdiff-exporter
   ```

3. 配置数据库连接：
   ```bash
   cp config/default.yaml config/config.yaml
   # 编辑 config.yaml 文件，填写数据库连接信息
   ```

4. 运行程序：
   ```bash
   ./start.sh  # Linux
   start.bat   # Windows
   ```

### 使用 Docker

```bash
docker pull dbdiff/dbdiff-exporter:latest

docker run -d \
  --name dbdiff-exporter \
  -p 5000:5000 \
  -v $(pwd)/config.yaml:/config/config.yaml \
  dbdiff/dbdiff-exporter:latest
```

## 配置说明

配置文件使用 YAML 格式，主要包含以下部分：

```yaml
# 数据库配置
databases:
  oracle:
    user: ""
    password: ""
    dsn: ""
  postgresql:
    host: ""
    port: 5432
    database: ""
    user: ""
    password: ""

# 监控配置
monitoring:
  auto_refresh:
    enabled: true
    interval: 60  # 秒

# 表配置
tables:
  - name: "table1"
    primary_key: "id"
    batch_columns: ["id", "updated_at"]
    comparison_columns: ["*"]
```

## API 接口

- `GET /metrics` - Prometheus 指标接口
- `POST /check` - 触发手动比较
- `GET /health` - 健康检查接口

## 指标说明

- `db_table_row_count` - 表行数
- `db_table_comparison_status` - 比较状态
- `db_table_row_difference` - 行数差异
- `db_table_comparison_duration_seconds` - 比较耗时
- `db_query_duration_seconds` - 查询耗时
- `db_table_comparison_errors_total` - 比较错误数
- `db_query_errors_total` - 查询错误数

## 构建说明

### 从源码构建

```bash
# 克隆仓库
git clone https://github.com/your-org/dbdiff-exporter.git
cd dbdiff-exporter

# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest

# 构建可执行文件
pyinstaller --clean \
           --name dbdiff-exporter \
           --add-data "src/dbdiff/config/default.yaml:config" \
           src/dbdiff/main.py
```

## 许可证

MIT License

## 贡献指南

欢迎提交 Issue 和 Pull Request！ 