"""
Python 爬虫加载器
"""
import importlib.util
import sys
import os
import tempfile
from pathlib import Path
from typing import Dict
from app.core.spider import Spider
from app.core.tvbox_adapter import TVBoxSpiderAdapter
import httpx


class PythonLoader:
    """Python 爬虫加载器"""

    def __init__(self):
        self.spiders: Dict[str, Spider] = {}
        self.modules: Dict[str, object] = {}
        self.temp_files: Dict[str, str] = {}

    def load_spider(self, key: str, path: str) -> Spider:
        """
        加载 Python 爬虫

        Args:
            key: 爬虫唯一标识
            path: Python 文件路径或 HTTP URL

        Returns:
            Spider 实例
        """
        if key in self.spiders:
            return self.spiders[key]

        try:
            local_path = path
            
            # 支持从 HTTP URL 加载爬虫
            if path.startswith('http://') or path.startswith('https://'):
                local_path = self._download_spider(key, path)
            
            # 动态加载 Python 模块
            spec = importlib.util.spec_from_file_location(key, local_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[key] = module
            spec.loader.exec_module(module)

            # 获取 Spider 类
            spider_class = getattr(module, "Spider")
            tvbox_spider = spider_class()
            tvbox_spider.site_key = key

            # 检测是否为TVBox风格的爬虫（使用驼峰命名）
            is_tvbox_style = hasattr(tvbox_spider, 'homeContent') or hasattr(tvbox_spider, 'categoryContent')

            if is_tvbox_style:
                # 使用适配器包装TVBox风格的爬虫
                spider = TVBoxSpiderAdapter(tvbox_spider)
                # 在初始化前注入fetch方法
                if not hasattr(tvbox_spider, 'fetch'):
                    tvbox_spider.fetch = spider.fetch
            else:
                # 直接使用我们的Spider
                spider = tvbox_spider

            self.spiders[key] = spider
            self.modules[key] = module

            return spider
        except Exception as e:
            print(f"加载 Python 爬虫失败: {e}")
            raise

    def _download_spider(self, key: str, url: str) -> str:
        """
        从 HTTP URL 下载爬虫文件

        Args:
            key: 爬虫唯一标识
            url: HTTP URL

        Returns:
            本地文件路径
        """
        try:
            response = httpx.get(url, follow_redirects=True, timeout=30)
            response.raise_for_status()
            
            # 创建临时目录
            temp_dir = os.path.join(tempfile.gettempdir(), 'longtv_spiders')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 保存到临时文件
            local_path = os.path.join(temp_dir, f'{key}.py')
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            self.temp_files[key] = local_path
            print(f"已下载爬虫文件: {url} -> {local_path}")
            
            return local_path
        except Exception as e:
            raise ValueError(f"下载爬虫文件失败: {url} - {e}")

    def unload_spider(self, key: str) -> bool:
        """
        卸载爬虫

        Args:
            key: 爬虫唯一标识

        Returns:
            是否成功卸载
        """
        if key in self.spiders:
            spider = self.spiders[key]
            spider.destroy()
            del self.spiders[key]

            if key in self.modules:
                del sys.modules[key]
                del self.modules[key]

            # 清理临时文件
            if key in self.temp_files:
                try:
                    os.remove(self.temp_files[key])
                    del self.temp_files[key]
                except:
                    pass

            return True
        return False

    def clear(self) -> None:
        """清空所有爬虫"""
        for key in list(self.spiders.keys()):
            self.unload_spider(key)
