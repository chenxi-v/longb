"""
智能代理管理 API 接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.smart_proxy import smart_proxy_manager

router = APIRouter(prefix="/api/smart-proxy", tags=["智能代理管理"])


class SetProxyUrlRequest(BaseModel):
    proxy_url: str


class TestConnectionRequest(BaseModel):
    url: str


@router.post("/set-url")
async def set_proxy_url(request: SetProxyUrlRequest):
    """
    设置智能代理URL
    
    Args:
        proxy_url: Cloudflare Worker 代理URL
        
    Returns:
        {
            "code": 0,
            "msg": "success"
        }
    """
    try:
        smart_proxy_manager.proxy_url = request.proxy_url
        return {"code": 0, "msg": "success", "data": {"proxy_url": request.proxy_url}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-url")
async def get_proxy_url():
    """
    获取当前智能代理URL
    
    Returns:
        {
            "code": 0,
            "data": {"proxy_url": "代理URL"}
        }
    """
    return {
        "code": 0,
        "data": {"proxy_url": smart_proxy_manager.proxy_url}
    }


@router.get("/stats")
async def get_proxy_stats():
    """
    获取智能代理统计信息
    
    Returns:
        {
            "code": 0,
            "data": {
                "proxy_domains": [...],
                "healthy_domains": [...],
                "total_proxy_domains": 5,
                "total_healthy_domains": 10
            }
        }
    """
    stats = smart_proxy_manager.get_stats()
    return {"code": 0, "data": stats}


@router.post("/test-connection")
async def test_connection(request: TestConnectionRequest):
    """
    测试连接
    
    Args:
        url: 测试URL
        
    Returns:
        {
            "code": 0,
            "data": {
                "direct_success": true,
                "proxy_success": true
            }
        }
    """
    try:
        direct_success, proxy_success = smart_proxy_manager.test_connection(request.url)
        return {
            "code": 0,
            "data": {
                "direct_success": direct_success,
                "proxy_success": proxy_success,
                "url": request.url
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache")
async def clear_proxy_cache():
    """
    清空代理缓存
    
    Returns:
        {
            "code": 0,
            "msg": "success"
        }
    """
    try:
        smart_proxy_manager.clear_cache()
        return {"code": 0, "msg": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remove-domain")
async def remove_proxy_domain(domain: str):
    """
    从代理列表中移除域名
    
    Args:
        domain: 域名
        
    Returns:
        {
            "code": 0,
            "msg": "success"
        }
    """
    try:
        if domain in smart_proxy_manager.proxy_domains:
            smart_proxy_manager.proxy_domains.remove(domain)
            smart_proxy_manager._save_cache()
        return {"code": 0, "msg": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
