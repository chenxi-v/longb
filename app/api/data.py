"""
数据获取 API 接口
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from app.core.manager import spider_manager

router = APIRouter(prefix="/api", tags=["数据获取"])


class HomeRequest(BaseModel):
    key: str
    filter: bool = False
    use_proxy: bool = False


class CategoryRequest(BaseModel):
    key: str
    tid: str
    pg: str = "1"
    filter: bool = False
    extend: Dict = {}
    use_proxy: bool = False


class DetailRequest(BaseModel):
    key: str
    ids: List[str]
    use_proxy: bool = False


class SearchRequest(BaseModel):
    key: str
    keyword: str
    quick: bool = False
    use_proxy: bool = False


class PlayerRequest(BaseModel):
    key: str
    flag: str
    id: str
    vip_flags: Optional[List[str]] = None


@router.post("/home")
async def home_content(request: HomeRequest):
    """
    获取首页内容

    Args:
        key: 爬虫唯一标识
        filter: 是否启用过滤
        use_proxy: 是否使用代理

    Returns:
        {
            "code": 0,
            "data": {
                "class": [...],
                "list": [...]
            }
        }
    """
    try:
        spider = spider_manager.get_spider(request.key)
        
        # 如果爬虫未加载，尝试自动加载
        if not spider:
            from app.api.config import load_spider_from_config
            spider = load_spider_from_config(request.key)
            
            if not spider:
                raise HTTPException(status_code=404, detail="爬虫不存在")

        # 如果需要使用代理，临时设置代理URL
        original_proxy_url = None
        if request.use_proxy and spider_manager.spider_proxy_url:
            if hasattr(spider, 'setSpiderProxyUrl'):
                original_proxy_url = spider._spider_proxy_url
                spider.setSpiderProxyUrl(spider_manager.spider_proxy_url)

        try:
            data = spider.home_content(request.filter)
            return {"code": 0, "data": data}
        finally:
            # 恢复原始代理设置
            if original_proxy_url is not None and hasattr(spider, 'setSpiderProxyUrl'):
                spider.setSpiderProxyUrl(original_proxy_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/category")
async def category_content(request: CategoryRequest):
    """
    获取分类内容

    Args:
        key: 爬虫唯一标识
        tid: 分类ID
        pg: 页码
        filter: 是否启用过滤
        extend: 扩展参数
        use_proxy: 是否使用代理

    Returns:
        {
            "code": 0,
            "data": {
                "page": 1,
                "pagecount": 10,
                "limit": 20,
                "total": 200,
                "list": [...]
            }
        }
    """
    try:
        spider = spider_manager.get_spider(request.key)
        
        # 如果爬虫未加载，尝试自动加载
        if not spider:
            from app.api.config import load_spider_from_config
            spider = load_spider_from_config(request.key)
            
            if not spider:
                raise HTTPException(status_code=404, detail="爬虫不存在")

        # 如果需要使用代理，临时设置代理URL
        original_proxy_url = None
        if request.use_proxy and spider_manager.spider_proxy_url:
            if hasattr(spider, 'setSpiderProxyUrl'):
                original_proxy_url = spider._spider_proxy_url
                spider.setSpiderProxyUrl(spider_manager.spider_proxy_url)

        try:
            data = spider.category_content(
                request.tid,
                request.pg,
                request.filter,
                request.extend
            )
            return {"code": 0, "data": data}
        finally:
            # 恢复原始代理设置
            if original_proxy_url is not None and hasattr(spider, 'setSpiderProxyUrl'):
                spider.setSpiderProxyUrl(original_proxy_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detail")
async def detail_content(request: DetailRequest):
    """
    获取视频详情

    Args:
        key: 爬虫唯一标识
        ids: 视频ID列表
        use_proxy: 是否使用代理

    Returns:
        {
            "code": 0,
            "data": {
                "vod_id": 1,
                "vod_name": "视频名",
                ...
            }
        }
    """
    try:
        spider = spider_manager.get_spider(request.key)
        
        # 如果爬虫未加载，尝试自动加载
        if not spider:
            from app.api.config import load_spider_from_config
            spider = load_spider_from_config(request.key)
            
            if not spider:
                raise HTTPException(status_code=404, detail="爬虫不存在")

        # 如果需要使用代理，临时设置代理URL
        original_proxy_url = None
        if request.use_proxy and spider_manager.spider_proxy_url:
            if hasattr(spider, 'setSpiderProxyUrl'):
                original_proxy_url = spider._spider_proxy_url
                spider.setSpiderProxyUrl(spider_manager.spider_proxy_url)

        try:
            data = spider.detail_content(request.ids)

            # 处理字符串形式的JSON数据
            if isinstance(data, dict):
                # 递归处理字典中的字符串值
                def parse_nested_strings(obj):
                    if isinstance(obj, dict):
                        return {k: parse_nested_strings(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [parse_nested_strings(item) for item in obj]
                    elif isinstance(obj, str):
                        try:
                            import json
                            parsed = json.loads(obj)
                            return parse_nested_strings(parsed)
                        except:
                            return obj
                    return obj

                data = parse_nested_strings(data)

            # 兼容不同的返回格式
            # 1. 如果返回的是 {'list': [vod]}，取第一个元素
            if isinstance(data, dict) and 'list' in data and len(data['list']) > 0:
                result = data['list'][0]
            # 2. 如果返回的是单个对象，直接使用
            elif isinstance(data, dict) and 'vod_id' in data:
                result = data
            # 3. 其他情况，原样返回
            else:
                result = data

            return {"code": 0, "data": result}
        finally:
            # 恢复原始代理设置
            if original_proxy_url is not None and hasattr(spider, 'setSpiderProxyUrl'):
                spider.setSpiderProxyUrl(original_proxy_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_content(request: SearchRequest):
    """
    搜索内容

    Args:
        key: 爬虫唯一标识
        keyword: 搜索关键词
        quick: 是否快速搜索
        use_proxy: 是否使用代理

    Returns:
        {
            "code": 0,
            "data": {
                "list": [...],
                "page": 1,
                "pagecount": 1
            }
        }
    """
    try:
        spider = spider_manager.get_spider(request.key)
        
        # 如果爬虫未加载，尝试自动加载
        if not spider:
            from app.api.config import load_spider_from_config
            spider = load_spider_from_config(request.key)
            
            if not spider:
                raise HTTPException(status_code=404, detail="爬虫不存在")

        # 如果需要使用代理，临时设置代理URL
        original_proxy_url = None
        if request.use_proxy and spider_manager.spider_proxy_url:
            if hasattr(spider, 'setSpiderProxyUrl'):
                original_proxy_url = spider._spider_proxy_url
                spider.setSpiderProxyUrl(spider_manager.spider_proxy_url)

        try:
            data = spider.search_content(request.keyword, request.quick)
            return {"code": 0, "data": data}
        finally:
            # 恢复原始代理设置
            if original_proxy_url is not None and hasattr(spider, 'setSpiderProxyUrl'):
                spider.setSpiderProxyUrl(original_proxy_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/player")
async def player_content(request: PlayerRequest):
    """
    获取播放地址

    Args:
        key: 爬虫唯一标识
        flag: 播放标识
        id: 视频ID
        vip_flags: VIP标识列表

    Returns:
        {
            "code": 0,
            "data": {
                "parse": 0,
                "url": "播放地址",
                "header": {...},
                "jx": "解析接口"
            }
        }
    """
    try:
        spider = spider_manager.get_spider(request.key)
        if not spider:
            raise HTTPException(status_code=404, detail="爬虫不存在")

        data = spider.player_content(
            request.flag,
            request.id,
            request.vip_flags or []
        )
        return {"code": 0, "data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
