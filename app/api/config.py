"""
配置管理 API 接口
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from app.json_config import config_manager
from app.core.manager import spider_manager

router = APIRouter(prefix="/api/config", tags=["配置管理"])


def load_spider_from_config(key: str):
    """
    从配置文件加载爬虫
    
    Args:
        key: 爬虫唯一标识
        
    Returns:
        Spider实例或None
    """
    try:
        config = config_manager.get(key)
        if not config:
            return None
        
        spider = spider_manager.load_spider(
            key,
            config.get('api', ''),
            config.get('type', 'python'),
            config.get('ext', '')
        )
        return spider
    except Exception as e:
        print(f"自动加载爬虫失败: {e}")
        return None


class SpiderConfigRequest(BaseModel):
    key: str
    name: str
    api: str
    ext: str = ""
    jar: Optional[str] = None
    type: str
    enabled: bool = True
    proxy_enabled: bool = False
    proxy_url: Optional[str] = None


@router.post("/save")
async def save_config(request: SpiderConfigRequest):
    """
    保存爬虫配置

    Args:
        request: 爬虫配置

    Returns:
        {
            "code": 0,
            "msg": "success"
        }
    """
    try:
        success = config_manager.save(request.dict())
        if success:
            return {"code": 0, "msg": "success"}
        else:
            raise HTTPException(status_code=500, detail="保存配置失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_configs():
    """
    获取所有爬虫配置

    Returns:
        {
            "code": 0,
            "data": [...]
        }
    """
    try:
        configs = config_manager.get_all()
        return JSONResponse(
            content={"code": 0, "data": configs},
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/enabled")
async def list_enabled_configs():
    """
    获取所有启用的爬虫配置

    Returns:
        {
            "code": 0,
            "data": [...]
        }
    """
    try:
        configs = config_manager.get_enabled()
        return {"code": 0, "data": configs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{key}")
async def get_config(key: str):
    """
    获取单个爬虫配置

    Args:
        key: 爬虫唯一标识

    Returns:
        {
            "code": 0,
            "data": {...}
        }
    """
    try:
        config = config_manager.get(key)
        if config:
            return {"code": 0, "data": config}
        else:
            raise HTTPException(status_code=404, detail="配置不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{key}")
async def delete_config(key: str):
    """
    删除爬虫配置

    Args:
        key: 爬虫唯一标识

    Returns:
        {
            "code": 0,
            "msg": "success"
        }
    """
    try:
        success = config_manager.delete(key)
        if success:
            return {"code": 0, "msg": "success"}
        else:
            raise HTTPException(status_code=500, detail="删除配置失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/toggle/{key}")
async def toggle_config(key: str, enabled: bool):
    """
    切换爬虫配置启用状态

    Args:
        key: 爬虫唯一标识
        enabled: 是否启用

    Returns:
        {
            "code": 0,
            "msg": "success"
        }
    """
    try:
        success = config_manager.update_enabled(key, enabled)
        if success:
            return {"code": 0, "msg": "success"}
        else:
            raise HTTPException(status_code=404, detail="配置不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
