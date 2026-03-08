"""
代理 API 接口
"""
from fastapi import APIRouter, HTTPException, Response, Query
from pydantic import BaseModel
from typing import Dict, Optional
from app.core.manager import spider_manager

router = APIRouter(prefix="/api/proxy", tags=["代理"])


class ProxyRequest(BaseModel):
    params: Dict


@router.post("/")
async def proxy(params: Dict):
    """
    代理接口

    Args:
        params: 代理参数字典

    Returns:
        {
            "code": 0,
            "data": [result1, result2, ...]
        }
    """
    try:
        result = spider_manager.proxy(params)
        return {"code": 0, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def proxy_get(siteKey: str = Query(None), url: str = Query(None)):
    """
    代理接口 (GET) - 用于图片代理

    Args:
        siteKey: 爬虫站点key
        url: 图片URL

    Returns:
        图片数据
    """
    try:
        params = {"siteKey": siteKey, "url": url}
        result = spider_manager.proxy(params)
        if result and len(result) >= 3:
            status_code, content_type, data = result
            return Response(content=data, media_type=content_type, status_code=status_code)
        else:
            raise HTTPException(status_code=500, detail="代理返回数据格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/spider-proxy")
async def spider_proxy(params: Dict):
    """
    爬虫代理接口 - 用于图片代理

    Args:
        params: 代理参数字典，包含url等信息

    Returns:
        图片数据或错误信息
    """
    try:
        result = spider_manager.proxy(params)
        if result and len(result) >= 3:
            status_code, content_type, data = result
            return Response(content=data, media_type=content_type, status_code=status_code)
        else:
            raise HTTPException(status_code=500, detail="代理返回数据格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
