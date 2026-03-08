"""
JSON配置管理
"""
import json
from typing import List, Dict, Optional
from pathlib import Path


class JsonConfigManager:
    """JSON配置管理器"""

    def __init__(self, config_path: str = "./data/spider_configs.json"):
        self.config_path = config_path
        self._init_config()

    def _init_config(self):
        """初始化配置文件"""
        # 确保数据目录存在
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)

        # 如果配置文件不存在，创建空配置
        if not Path(self.config_path).exists():
            self._save_configs([])

    def _load_configs(self) -> List[Dict]:
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 确保正确处理BOM
                if content.startswith('\ufeff'):
                    content = content[1:]
                return json.loads(content)
        except:
            return []

    def _save_configs(self, configs: List[Dict]):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(configs, f, ensure_ascii=False, indent=2)

    def save(self, config: Dict) -> bool:
        """保存配置"""
        configs = self._load_configs()

        # 检查是否已存在相同key
        existing_index = None
        for i, c in enumerate(configs):
            if c['key'] == config['key']:
                existing_index = i
                break

        if existing_index is not None:
            # 更新现有配置
            configs[existing_index] = config
        else:
            # 添加新配置
            configs.append(config)

        self._save_configs(configs)
        return True

    def get_all(self) -> List[Dict]:
        """获取所有配置"""
        return self._load_configs()

    def get(self, key: str) -> Optional[Dict]:
        """获取单个配置"""
        configs = self._load_configs()
        for config in configs:
            if config['key'] == key:
                return config
        return None

    def delete(self, key: str) -> bool:
        """删除配置"""
        configs = self._load_configs()
        new_configs = [c for c in configs if c['key'] != key]
        self._save_configs(new_configs)
        return True

    def get_enabled(self) -> List[Dict]:
        """获取所有启用的配置"""
        configs = self._load_configs()
        return [c for c in configs if c.get('enabled', True)]

    def update_enabled(self, key: str, enabled: bool) -> bool:
        """更新启用状态"""
        configs = self._load_configs()
        for config in configs:
            if config['key'] == key:
                config['enabled'] = enabled
                self._save_configs(configs)
                return True
        return False


# 全局配置管理器实例
config_manager = JsonConfigManager()
