"""
JavaScript 爬虫加载器
"""
import execjs
from typing import Dict, Optional
from app.core.spider import Spider


class JavaScriptSpider(Spider):
    """JavaScript 爬虫包装类"""

    def __init__(self, ctx: execjs.ExternalRuntime.Context, key: str):
        super().__init__()
        self.ctx = ctx
        self.key = key
        self.site_key = key

    def home_content(self, filter: bool = False) -> Dict:
        result = self.ctx.call("homeContent", filter)
        return result if isinstance(result, dict) else {}

    def category_content(self, tid: str, pg: str = "1", filter: bool = False, extend: Dict = {}) -> Dict:
        result = self.ctx.call("categoryContent", tid, pg, filter, extend)
        return result if isinstance(result, dict) else {}

    def detail_content(self, ids: list) -> Dict:
        result = self.ctx.call("detailContent", ids)
        return result if isinstance(result, dict) else {}

    def search_content(self, key: str, quick: bool = False) -> Dict:
        result = self.ctx.call("searchContent", key, quick)
        return result if isinstance(result, dict) else {}

    def player_content(self, flag: str, id: str, vip_flags: list = None) -> Dict:
        result = self.ctx.call("playerContent", flag, id, vip_flags or [])
        return result if isinstance(result, dict) else {}

    def proxy(self, params: Dict) -> Optional[list]:
        result = self.ctx.call("proxy", params)
        return result if isinstance(result, list) else None

    def destroy(self) -> None:
        pass


class JsLoader:
    """JavaScript 爬虫加载器"""

    def __init__(self):
        self.spiders: Dict[str, JavaScriptSpider] = {}
        self.contexts: Dict[str, execjs.ExternalRuntime.Context] = {}

    def load_spider(self, key: str, path: str) -> Spider:
        """
        加载 JavaScript 爬虫

        Args:
            key: 爬虫唯一标识
            path: JS 文件路径

        Returns:
            Spider 实例
        """
        if key in self.spiders:
            return self.spiders[key]

        try:
            # 读取 JS 文件
            with open(path, 'r', encoding='utf-8') as f:
                js_code = f.read()

            # 编译 JS 代码
            ctx = execjs.compile(js_code)

            # 创建包装类
            spider = JavaScriptSpider(ctx, key)

            self.spiders[key] = spider
            self.contexts[key] = ctx

            return spider
        except Exception as e:
            print(f"加载 JavaScript 爬虫失败: {e}")
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

            if key in self.contexts:
                del self.contexts[key]

            return True
        return False

    def clear(self) -> None:
        """清空所有爬虫"""
        for key in list(self.spiders.keys()):
            self.unload_spider(key)
