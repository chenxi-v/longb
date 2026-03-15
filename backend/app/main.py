"""
FastAPI 主应用
"""
import os
import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import spider, data, proxy, config, smart_proxy
from app.utils.logger import logger
from app.json_config import JsonConfigManager

# 强制设置智能代理URL（用于Vercel等serverless环境）
if not os.getenv('SMART_PROXY_URL'):
    os.environ['SMART_PROXY_URL'] = 'https://corspy.longz.cc.cd'


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="LongTV 爬虫管理后端 API",
        debug=settings.DEBUG
    )

    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应该限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 请求日志中间件
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # 记录请求开始
        request_id = f"{time.time():.0f}-{id(request)}"
        logger.info(f"[{request_id}] 请求开始: {request.method} {request.url.path}")
        
        # 记录请求体（仅POST/PUT）
        if request.method in ["POST", "PUT"]:
            try:
                body = await request.body()
                if body:
                    import json
                    try:
                        body_json = json.loads(body)
                        # 隐藏敏感信息
                        if 'ext' in body_json and len(str(body_json.get('ext', ''))) > 100:
                            body_json['ext'] = body_json['ext'][:100] + '...(truncated)'
                        logger.debug(f"[{request_id}] 请求体: {body_json}")
                    except:
                        logger.debug(f"[{request_id}] 请求体长度: {len(body)} bytes")
            except Exception as e:
                logger.debug(f"[{request_id}] 无法读取请求体: {e}")
        
        try:
            response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录请求完成
            status_code = response.status_code
            log_level = "info" if status_code < 400 else "warning" if status_code < 500 else "error"
            
            getattr(logger, log_level)(
                f"[{request_id}] 请求完成: {request.method} {request.url.path} "
                f"- 状态码: {status_code} - 耗时: {process_time:.3f}s"
            )
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] 请求异常: {request.method} {request.url.path} "
                f"- 错误: {str(e)} - 耗时: {process_time:.3f}s"
            )
            raise

    # 注册路由
    app.include_router(spider.router)
    app.include_router(data.router)
    app.include_router(proxy.router)
    app.include_router(config.router)
    app.include_router(smart_proxy.router)

    # 根路径
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running"
        }

    # 健康检查
    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} 启动成功")

    return app


# 创建应用实例
app = create_app()


@app.on_event("startup")
async def startup_event():
    """应用启动时自动加载爬虫"""
    from app.core.manager import spider_manager
    from app.core.smart_proxy import smart_proxy_manager
    from app.json_config import JsonConfigManager
    
    # 初始化智能代理
    smart_proxy_manager.init_from_settings()
    smart_proxy_manager.print_status()
    
    try:
        config_manager = JsonConfigManager()
        configs = config_manager.get_all()
        
        for spider_config in configs:
            if spider_config.get("enabled", False):
                try:
                    spider_manager.load_spider(
                        spider_config["key"],
                        spider_config["api"],
                        spider_config["type"],
                        spider_config.get("ext", "")
                    )
                    logger.info(f"自动加载爬虫: {spider_config['name']} ({spider_config['key']})")
                except Exception as e:
                    logger.error(f"自动加载爬虫失败: {spider_config['name']} - {e}")
    except Exception as e:
        logger.error(f"启动时加载爬虫配置失败: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
