"""
爬虫管理 API 接口
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from app.core.manager import spider_manager

router = APIRouter(prefix="/api/spider", tags=["爬虫管理"])


class LoadSpiderRequest(BaseModel):
    key: str
    path: str
    spider_type: str  # python, javascript, jar
    extend: str = ""


class UnloadSpiderRequest(BaseModel):
    key: str


class SpiderProxyRequest(BaseModel):
    spider_proxy_url: Optional[str] = None


@router.get("/file/{spider_type}/{filename}")
async def get_spider_file(spider_type: str, filename: str):
    """
    获取爬虫文件内容

    Args:
        spider_type: 爬虫类型 (python, javascript)
        filename: 文件名

    Returns:
        文件内容
    """
    try:
        base_dir = Path("./spiders")
        file_path = base_dir / spider_type / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return FileResponse(
            path=file_path,
            media_type="text/plain",
            filename=filename
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load")
async def load_spider(request: LoadSpiderRequest):
    """
    加载爬虫

    Args:
        key: 爬虫唯一标识
        path: 爬虫文件路径
        spider_type: 爬虫类型
        extend: 扩展配置

    Returns:
        {
            "code": 0,
            "msg": "success",
            "data": {"key": "爬虫key"}
        }
    """
    try:
        spider = spider_manager.load_spider(
            request.key,
            request.path,
            request.spider_type,
            request.extend
        )
        return {
            "code": 0,
            "msg": "success",
            "data": {"key": spider.site_key}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unload")
async def unload_spider(request: UnloadSpiderRequest):
    """
    卸载爬虫

    Args:
        key: 爬虫唯一标识

    Returns:
        {
            "code": 0,
            "msg": "success"
        }
    """
    try:
        success = spider_manager.unload_spider(request.key)
        if success:
            return {"code": 0, "msg": "success"}
        else:
            raise HTTPException(status_code=404, detail="爬虫不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_spiders():
    """
    获取已加载的爬虫列表

    Returns:
        {
            "code": 0,
            "data": [
                {"key": "spider1", "type": "python"},
                {"key": "spider2", "type": "javascript"}
            ]
        }
    """
    spiders = []
    for key, spider in spider_manager.spiders.items():
        spider_type = spider_manager._detect_spider_type(spider)
        spiders.append({
            "key": key,
            "type": spider_type
        })

    return {
        "code": 0,
        "data": spiders
    }


@router.post("/clear")
async def clear_spiders():
    """
    清空所有爬虫

    Returns:
        {
            "code": 0,
            "msg": "success"
        }
    """
    spider_manager.clear()
    return {"code": 0, "msg": "success"}


@router.post("/set-proxy")
async def set_spider_proxy(request: SpiderProxyRequest):
    """
    设置爬虫代理URL

    Args:
        spider_proxy_url: 爬虫代理URL

    Returns:
        {
            "code": 0,
            "msg": "success"
        }
    """
    try:
        spider_manager.spider_proxy_url = request.spider_proxy_url
        return {"code": 0, "msg": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proxy")
async def get_spider_proxy():
    """
    获取当前爬虫代理URL

    Returns:
        {
            "code": 0,
            "data": {"spider_proxy_url": "代理URL"}
        }
    """
    return {
        "code": 0,
        "data": {"spider_proxy_url": spider_manager.spider_proxy_url}
    }
