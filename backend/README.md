# LongTV FastAPI Backend

LongTV 爬虫管理后端，支持 Python、JavaScript 和 JAR 三种类型的爬虫。

## 功能特性

- 支持多种爬虫类型（Python、JavaScript、JAR）
- 爬虫动态加载和卸载
- 爬虫配置管理
- 数据获取接口（首页、分类、详情、搜索、播放）
- 代理接口支持
- 爬虫状态监控
- Key 和文件唯一性检查

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 主应用
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   │
│   ├── api/                   # API 路由
│   │   ├── __init__.py
│   │   ├── spider.py          # 爬虫管理接口
│   │   ├── data.py            # 数据获取接口
│   │   ├── proxy.py          # 代理接口
│   │   └── config.py         # 配置管理接口
│   │
│   ├── core/                  # 核心功能
│   │   ├── __init__.py
│   │   ├── spider.py          # Spider 接口定义
│   │   └── manager.py        # SpiderManager
│   │
│   ├── loaders/               # 爬虫加载器
│   │   ├── __init__.py
│   │   ├── python_loader.py
│   │   ├── js_loader.py
│   │   └── jar_loader.py
│   │
│   ├── models/                # 数据模型
│   │   ├── __init__.py
│   │   └── spider.py
│   │
│   └── utils/                # 工具函数
│       ├── __init__.py
│       ├── http.py            # HTTP 客户端
│       └── logger.py          # 日志工具
│
├── spiders/                 # 爬虫文件存储
│   ├── python/               # Python 爬虫
│   ├── javascript/           # JavaScript 爬虫
│   └── jar/                 # JAR 爬虫
│
├── data/                    # 数据库文件
├── logs/                    # 日志文件
├── tests/                   # 测试文件
│
├── requirements.txt           # Python 依赖
├── .env.example             # 环境变量示例
├── .env                     # 环境变量配置
└── .gitignore
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并根据需要修改配置：

```bash
cp .env.example .env
```

### 3. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或者直接运行
python -m app.main
```

### 4. 访问 API 文档

启动服务后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 接口

### 爬虫管理

- `POST /api/spider/load` - 加载爬虫
- `POST /api/spider/unload` - 卸载爬虫
- `GET /api/spider/list` - 获取已加载的爬虫列表
- `POST /api/spider/clear` - 清空所有爬虫

### 数据获取

- `POST /api/home` - 获取首页内容
- `POST /api/category` - 获取分类内容
- `POST /api/detail` - 获取视频详情
- `POST /api/search` - 搜索内容
- `POST /api/player` - 获取播放地址

### 代理接口

- `POST /api/proxy/` - 代理接口

### 配置管理

- `POST /api/config/save` - 保存爬虫配置
- `GET /api/config/list` - 获取所有爬虫配置
- `GET /api/config/enabled` - 获取所有启用的爬虫配置
- `GET /api/config/{key}` - 获取单个爬虫配置
- `DELETE /api/config/{key}` - 删除爬虫配置

## 爬虫开发

### Python 爬虫示例

```python
from typing import Dict, List, Any

class Spider:
    def __init__(self):
        self.site_key = ""

    def init(self, extend: str = "") -> None:
        pass

    def home_content(self, filter: bool = False) -> Dict[str, Any]:
        return {
            "class": [{"type_id": 1, "type_name": "电影"}],
            "list": [{"vod_id": 1, "vod_name": "视频名"}]
        }

    def category_content(self, tid: str, pg: str = "1", filter: bool = False, extend: Dict = {}) -> Dict[str, Any]:
        return {
            "page": 1,
            "pagecount": 10,
            "limit": 20,
            "total": 200,
            "list": []
        }

    def detail_content(self, ids: List[str]) -> Dict[str, Any]:
        return {
            "vod_id": 1,
            "vod_name": "视频名",
            "vod_pic": "封面URL",
            "vod_play_from": "播放源",
            "vod_play_url": [{"name": "线路1", "url": ["url1", "url2"]}]
        }

    def search_content(self, key: str, quick: bool = False) -> Dict[str, Any]:
        return {
            "list": [],
            "page": 1,
            "pagecount": 1
        }

    def player_content(self, flag: str, id: str, vip_flags: List[str] = None) -> Dict[str, Any]:
        return {
            "parse": 0,
            "url": "播放地址",
            "header": {"User-Agent": "..."},
            "jx": "解析接口"
        }

    def destroy(self) -> None:
        pass
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| APP_NAME | 应用名称 | LongTV Backend |
| APP_VERSION | 应用版本 | 1.0.0 |
| DEBUG | 调试模式 | True |
| HOST | 服务器地址 | 0.0.0.0 |
| PORT | 服务器端口 | 8000 |
| DATABASE_URL | 数据库URL | sqlite:///./data/spiders.db |
| LOG_LEVEL | 日志级别 | INFO |
| LOG_FILE | 日志文件路径 | ./logs/app.log |
| PROXY_ENABLED | 是否启用代理 | False |
| PROXY_URL | 代理地址 | None |
| SPIDERS_DIR | 爬虫文件目录 | ./spiders |
| MAX_SPIDERS | 最大爬虫数量 | 100 |

## 注意事项

1. **Key 唯一性**: 每个爬虫的 key 必须唯一，不能重复
2. **文件唯一性**: 同一个爬虫文件不能被多个配置使用
3. **中文编码**: 数据库使用 UTF-8 编码，支持中文存储
4. **JAR 支持**: 使用 JAR 爬虫需要安装 Java 运行环境

## License

MIT
