"""
爬虫管理器
"""
from typing import Dict, Optional
from app.core.spider import Spider
from app.loaders.python_loader import PythonLoader
from app.loaders.js_loader import JsLoader, JavaScriptSpider

# JAR支持需要Java环境，暂时禁用
try:
    from app.loaders.jar_loader import JarLoader, JarSpider
    JAR_SUPPORT = True
except ImportError:
    JAR_SUPPORT = False
    JarLoader = None
    JarSpider = None


class SpiderManager:
    """爬虫管理器"""

    def __init__(self):
        self.python_loader = PythonLoader()
        self.js_loader = JsLoader()
        self.jar_loader = JarLoader() if JAR_SUPPORT else None
        self.spiders: Dict[str, Spider] = {}
        self.recent: Optional[str] = None
        self.spider_proxy_url: Optional[str] = None

    def load_spider(self, key: str, path: str, spider_type: str, extend: str = "") -> Spider:
        """
        加载爬虫

        Args:
            key: 爬虫唯一标识
            path: 爬虫文件路径
            spider_type: 爬虫类型 (python, javascript, jar)
            extend: 扩展配置

        Returns:
            Spider 实例
        """
        if spider_type == "python":
            spider = self.python_loader.load_spider(key, path)
        elif spider_type == "javascript":
            spider = self.js_loader.load_spider(key, path)
        elif spider_type == "jar":
            if not JAR_SUPPORT or not self.jar_loader:
                raise ValueError("JAR支持未启用，请安装JPype和Java环境")
            spider = self.jar_loader.load_spider(key, path)
        else:
            raise ValueError(f"不支持的爬虫类型: {spider_type}")

        # 初始化爬虫
        spider.init(extend)
        
        # 应用爬虫代理设置
        if self.spider_proxy_url and hasattr(spider, 'setSpiderProxyUrl'):
            spider.setSpiderProxyUrl(self.spider_proxy_url)

        # 缓存爬虫
        self.spiders[key] = spider
        self.recent = key

        return spider

    def unload_spider(self, key: str) -> bool:
        """
        卸载爬虫

        Args:
            key: 爬虫唯一标识

        Returns:
            是否成功卸载
        """
        if key not in self.spiders:
            return False

        spider = self.spiders[key]
        spider_type = self._detect_spider_type(spider)

        if spider_type == "python":
            self.python_loader.unload_spider(key)
        elif spider_type == "javascript":
            self.js_loader.unload_spider(key)
        elif spider_type == "jar":
            if self.jar_loader:
                self.jar_loader.unload_spider(key)

        del self.spiders[key]
        return True

    def get_spider(self, key: str) -> Optional[Spider]:
        """
        获取爬虫实例

        Args:
            key: 爬虫唯一标识

        Returns:
            Spider 实例或 None
        """
        return self.spiders.get(key)

    def set_recent(self, key: str) -> None:
        """
        设置最近使用的爬虫

        Args:
            key: 爬虫唯一标识
        """
        self.recent = key

    def proxy(self, params: Dict) -> Optional[list]:
        """
        代理调用

        Args:
            params: 代理参数

        Returns:
            代理结果
        """
        if "siteKey" in params:
            spider = self.get_spider(params["siteKey"])
            if spider:
                return spider.proxy(params)

        # 尝试其他爬虫
        for key, spider in self.spiders.items():
            if key != self.recent:
                result = spider.proxy(params)
                if result:
                    return result

        return None

    def clear(self) -> None:
        """清空所有爬虫"""
        self.python_loader.clear()
        self.js_loader.clear()
        if self.jar_loader:
            self.jar_loader.clear()
        self.spiders.clear()
        self.recent = None

    def _detect_spider_type(self, spider: Spider) -> str:
        """
        检测爬虫类型

        Args:
            spider: 爬虫实例

        Returns:
            爬虫类型
        """
        if JAR_SUPPORT and JarSpider and isinstance(spider, JarSpider):
            return "jar"
        elif isinstance(spider, JavaScriptSpider):
            return "javascript"
        else:
            return "python"


# 全局爬虫管理器实例
spider_manager = SpiderManager()
