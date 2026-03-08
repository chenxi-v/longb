"""
JAR 爬虫加载器
"""
import jpype
from jpype.types import *
from typing import Dict, Optional
from app.core.spider import Spider
import json


class JarSpider(Spider):
    """JAR 爬虫包装类"""

    def __init__(self, key: str, jar_path: str):
        super().__init__()
        self.key = key
        self.jar_path = jar_path
        self.site_key = key
        self._init_jvm()
        self._load_spider()

    def _init_jvm(self) -> None:
        """初始化 JVM"""
        if not jpype.isJVMStarted():
            # 添加 JAR 到 classpath
            jpype.addClassPath(self.jar_path)
            # 启动 JVM
            jpype.startJVM()

    def _load_spider(self) -> None:
        """加载 Java Spider 类"""
        SpiderClass = jpype.JClass("com.github.catvod.crawler.Spider")
        self.spider = SpiderClass()
        self.spider.siteKey = self.key

    def _convert_result(self, java_result) -> Dict:
        """转换 Java 结果为 Python 字典"""
        if java_result is None:
            return {}

        # 转换为 JSON 字符串再解析
        result_str = str(java_result)
        try:
            return json.loads(result_str)
        except:
            return {}

    def home_content(self, filter: bool = False) -> Dict:
        result = self.spider.homeContent(filter)
        return self._convert_result(result)

    def category_content(self, tid: str, pg: str = "1", filter: bool = False, extend: Dict = {}) -> Dict:
        java_extend = JMap(extend)
        result = self.spider.categoryContent(tid, pg, filter, java_extend)
        return self._convert_result(result)

    def detail_content(self, ids: list) -> Dict:
        java_ids = JString[ids]
        result = self.spider.detailContent(java_ids)
        return self._convert_result(result)

    def search_content(self, key: str, quick: bool = False) -> Dict:
        result = self.spider.searchContent(key, quick)
        return self._convert_result(result)

    def player_content(self, flag: str, id: str, vip_flags: list = None) -> Dict:
        java_vip_flags = JString[vip_flags or []]
        result = self.spider.playerContent(flag, id, java_vip_flags)
        return self._convert_result(result)

    def proxy(self, params: Dict) -> Optional[list]:
        java_params = JMap(params)
        result = self.spider.proxy(java_params)

        if result is None:
            return None

        # 转换 Java 数组为 Python 列表
        return [self._convert_result(item) for item in result]

    def destroy(self) -> None:
        """销毁爬虫"""
        if hasattr(self, 'spider'):
            self.spider.destroy()


class JarLoader:
    """JAR 爬虫加载器"""

    def __init__(self):
        self.spiders: Dict[str, JarSpider] = {}
        self.jvm_started = False

    def _ensure_jvm(self) -> None:
        """确保 JVM 已启动"""
        if not self.jvm_started and not jpype.isJVMStarted():
            jpype.startJVM()
            self.jvm_started = True

    def load_spider(self, key: str, path: str) -> Spider:
        """
        加载 JAR 爬虫

        Args:
            key: 爬虫唯一标识
            path: JAR 文件路径

        Returns:
            Spider 实例
        """
        if key in self.spiders:
            return self.spiders[key]

        try:
            self._ensure_jvm()
            spider = JarSpider(key, path)
            self.spiders[key] = spider
            return spider
        except Exception as e:
            print(f"加载 JAR 爬虫失败: {e}")
            raise

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
            return True
        return False

    def clear(self) -> None:
        """清空所有爬虫"""
        for key in list(self.spiders.keys()):
            self.unload_spider(key)
