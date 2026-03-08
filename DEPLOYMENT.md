# LongTV 后端部署指南

## 部署到 Zeabur

### 1. 准备工作

1. 注册 [Zeabur](https://zeabur.com) 账号
2. 安装 Zeabur CLI（可选）：
   ```bash
   npm install -g @zeabur/cli
   ```

### 2. 部署步骤

#### 方式一：通过 Zeabur Dashboard（推荐）

1. 登录 [Zeabur Dashboard](https://dash.zeabur.com)
2. 创建新项目
3. 添加服务 → 选择 "Git"
4. 连接你的 Git 仓库
5. 选择 `backend` 目录作为根目录
6. Zeabur 会自动检测 Dockerfile 并构建

#### 方式二：通过 CLI

```bash
cd backend
zeabur deploy
```

### 3. 环境变量配置

在 Zeabur Dashboard 中设置以下环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `APP_NAME` | LongTV Backend | 应用名称 |
| `APP_VERSION` | 1.0.0 | 版本号 |
| `DEBUG` | False | 生产环境关闭调试 |
| `HOST` | 0.0.0.0 | 监听地址 |
| `PORT` | 8000 | 端口号 |
| `LOG_LEVEL` | INFO | 日志级别 |

### 4. 持久化存储

Zeabur 默认不提供持久化存储，需要配置：

1. 在 Zeabur Dashboard 中添加 Volume
2. 挂载路径：`/app/data`
3. 这样 `spider_configs.json` 和 `spiders.db` 才能持久保存

### 5. 域名配置

1. 在 Zeabur Dashboard 中生成域名
2. 或绑定自定义域名
3. 记录后端 URL，例如：`https://longtv-backend.zeabur.app`

### 6. 前端配置

修改前端环境变量，连接到部署的后端：

创建 `frontend/.env.production`：
```env
NEXT_PUBLIC_API_URL=https://longtv-backend.zeabur.app
```

## 部署到其他平台

### Railway

1. 创建 `railway.toml`：
```toml
[build]
builder = "dockerfile"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"
```

2. 连接 Git 仓库，选择 `backend` 目录

### Render

1. 创建 `render.yaml`：
```yaml
services:
  - type: web
    name: longtv-backend
    env: docker
    plan: free
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DEBUG
        value: False
      - key: LOG_LEVEL
        value: INFO
```

### Fly.io

1. 创建 `fly.toml`：
```toml
app = "longtv-backend"
primary_region = "sin"

[build]
  dockerfile = "Dockerfile"

[env]
  DEBUG = "False"
  LOG_LEVEL = "INFO"

[[services]]
  http_checks = []
  internal_port = 8000
  protocol = "tcp"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

2. 部署：
```bash
fly launch
fly deploy
```

## 注意事项

### 1. 爬虫文件管理

- `spiders/python/` 目录下的爬虫文件会随代码一起部署
- 如需动态添加爬虫，需要：
  - 使用持久化存储
  - 或通过 Git 提交更新

### 2. 数据库

- 默认使用 SQLite，存储在 `/app/data/spiders.db`
- 生产环境建议：
  - 使用 PostgreSQL/MySQL
  - 或确保 Volume 持久化

### 3. 日志

- 日志文件存储在 `/app/logs/app.log`
- 建议使用云平台的日志服务

### 4. 安全配置

生产环境建议修改 CORS 配置：

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # 限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 健康检查

部署后访问以下端点验证：

- `https://your-backend-url/` - 应用信息
- `https://your-backend-url/health` - 健康检查
- `https://your-backend-url/api/configs` - 爬虫配置列表

## 故障排查

### 1. 构建失败

- 检查 `requirements.txt` 是否完整
- 查看 Zeabur 构建日志

### 2. 启动失败

- 检查环境变量配置
- 查看应用日志

### 3. 无法访问

- 检查端口配置（默认 8000）
- 检查防火墙规则

### 4. 数据丢失

- 确保配置了持久化存储
- 检查 Volume 挂载路径
