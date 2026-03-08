"""
HTTP 客户端工具
"""
import httpx
from typing import Dict, Optional, Any
import asyncio


class HttpClient:
    """异步 HTTP 客户端"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """
        GET 请求

        Args:
            url: 请求URL
            params: 查询参数
            headers: 请求头

        Returns:
            响应数据
        """
        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def post(
        self,
        url: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Any:
        """
        POST 请求

        Args:
            url: 请求URL
            data: 表单数据
            json: JSON数据
            headers: 请求头

        Returns:
            响应数据
        """
        response = await self.client.post(url, data=data, json=json, headers=headers)
        response.raise_for_status()
        return response.json()

    async def get_text(
        self,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> str:
        """
        GET 请求返回文本

        Args:
            url: 请求URL
            params: 查询参数
            headers: 请求头

        Returns:
            响应文本
        """
        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.text

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


# 全局 HTTP 客户端实例
http_client = HttpClient()
