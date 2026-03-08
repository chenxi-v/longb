# -*- coding: utf-8 -*-
"""
TVBox爬虫适配器
将TVBox风格的爬虫适配到我们的框架
"""
from typing import Dict, List, Optional, Any
from app.core.spider import Spider as BaseSpider


class TVBoxSpiderAdapter(BaseSpider):
    """
    TVBox爬虫适配器
    将驼峰命名的方法映射到下划线命名
    """

    def __init__(self, tvbox_spider):
        """
        初始化适配器

        Args:
            tvbox_spider: TVBox风格的爬虫实例
        """
        super().__init__()
        self.tvbox_spider = tvbox_spider
        self.site_key = tvbox_spider.site_key if hasattr(tvbox_spider, 'site_key') else ""

        # 将我们的方法注入到TVBox爬虫中
        if not hasattr(self.tvbox_spider, 'fetch'):
            self.tvbox_spider.fetch = self._wrapped_fetch
        
        # 为TVBox爬虫添加getProxyUrl方法
        if not hasattr(self.tvbox_spider, 'getProxyUrl'):
            self.tvbox_spider.getProxyUrl = self._get_proxy_url

    def _wrapped_fetch(self, url: str, **kwargs):
        """包装fetch方法，自动处理响应中的JSON字符串"""
        response = self.fetch(url, **kwargs)
        # 包装response对象，使其json方法自动解析嵌套的字符串
        original_json = response.json

        def wrapped_json():
            data = original_json()
            return self._parse_nested_strings(data)

        response.json = wrapped_json
        return response

    def _parse_nested_strings(self, obj):
        """递归解析嵌套的字符串JSON"""
        import json
        if isinstance(obj, dict):
            return {k: self._parse_nested_strings(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._parse_nested_strings(item) for item in obj]
        elif isinstance(obj, str):
            try:
                parsed = json.loads(obj)
                return self._parse_nested_strings(parsed)
            except:
                return obj
        return obj

    def _get_proxy_url(self) -> str:
        """获取代理URL"""
        return ""

    def init(self, extend: str = "") -> None:
        """初始化爬虫"""
        if hasattr(self.tvbox_spider, 'init'):
            self.tvbox_spider.init(extend)

    def home_content(self, filter: bool = False) -> Dict[str, Any]:
        """获取首页内容"""
        if hasattr(self.tvbox_spider, 'homeContent'):
            return self.tvbox_spider.homeContent(filter)
        return {}

    def category_content(self, tid: str, pg: str = "1", filter: bool = False, extend: Dict = {}) -> Dict[str, Any]:
        """获取分类内容"""
        if hasattr(self.tvbox_spider, 'categoryContent'):
            return self.tvbox_spider.categoryContent(tid, pg, filter, extend)
        return {}

    def detail_content(self, ids: List[str]) -> Dict[str, Any]:
        """获取视频详情"""
        if hasattr(self.tvbox_spider, 'detailContent'):
            result = self.tvbox_spider.detailContent(ids)
            # 递归处理字符串形式的JSON
            result = self._parse_nested_strings(result)
            return result
        return {}

    def search_content(self, key: str, quick: bool = False) -> Dict[str, Any]:
        """搜索内容"""
        if hasattr(self.tvbox_spider, 'searchContent'):
            return self.tvbox_spider.searchContent(key, quick)
        return {}

    def player_content(self, flag: str, id: str, vip_flags: List[str] = None) -> Dict[str, Any]:
        """获取播放地址"""
        if hasattr(self.tvbox_spider, 'playerContent'):
            return self.tvbox_spider.playerContent(flag, id, vip_flags or [])
        return {}

    def proxy(self, params: Dict[str, str]) -> Optional[List[Any]]:
        """代理接口"""
        if hasattr(self.tvbox_spider, 'localProxy'):
            return self.tvbox_spider.localProxy(params)
        return None

    def destroy(self) -> None:
        """销毁爬虫"""
        if hasattr(self.tvbox_spider, 'destroy'):
            self.tvbox_spider.destroy()
        super().destroy()
