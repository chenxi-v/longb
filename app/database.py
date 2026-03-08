"""
数据库连接和配置管理
"""
import sqlite3
import json
from typing import List, Dict, Optional
from pathlib import Path


class ConfigManager:
    """配置管理器"""

    def __init__(self, db_path: str = "./data/spiders.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        # 确保数据目录存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建爬虫配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spider_configs (
                key TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                api TEXT NOT NULL,
                ext TEXT DEFAULT '',
                jar TEXT,
                type TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                proxy_enabled INTEGER DEFAULT 0,
                proxy_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def save(self, config: Dict) -> bool:
        """保存配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 检查是否已存在相同key或相同api的配置
            cursor.execute(
                "SELECT key, api FROM spider_configs WHERE key = ? OR api = ?",
                (config['key'], config['api'])
            )
            existing = cursor.fetchone()

            if existing:
                # 如果存在相同key，更新配置
                if existing[0] == config['key']:
                    cursor.execute('''
                        UPDATE spider_configs
                        SET name = ?, api = ?, ext = ?, jar = ?, type = ?,
                            enabled = ?, proxy_enabled = ?, proxy_url = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE key = ?
                    ''', (
                        config['name'], config['api'], config.get('ext', ''),
                        config.get('jar'), config['type'], config.get('enabled', True),
                        config.get('proxy_enabled', False), config.get('proxy_url'),
                        config['key']
                    ))
                else:
                    # 如果存在相同api但不同key，拒绝保存
                    conn.close()
                    return False
            else:
                # 插入新配置
                cursor.execute('''
                    INSERT INTO spider_configs
                    (key, name, api, ext, jar, type, enabled, proxy_enabled, proxy_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    config['key'], config['name'], config['api'],
                    config.get('ext', ''), config.get('jar'), config['type'],
                    config.get('enabled', True), config.get('proxy_enabled', False),
                    config.get('proxy_url')
                ))

            conn.commit()
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
        finally:
            conn.close()

    def get_all(self) -> List[Dict]:
        """获取所有配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT key, name, api, ext, jar, type, enabled, proxy_enabled, proxy_url
            FROM spider_configs
            ORDER BY created_at DESC
        ''')

        configs = []
        for row in cursor.fetchall():
            configs.append({
                'key': row[0],
                'name': row[1],
                'api': row[2],
                'ext': row[3],
                'jar': row[4],
                'type': row[5],
                'enabled': bool(row[6]),
                'proxy_enabled': bool(row[7]),
                'proxy_url': row[8]
            })

        conn.close()
        return configs

    def get(self, key: str) -> Optional[Dict]:
        """获取单个配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT key, name, api, ext, jar, type, enabled, proxy_enabled, proxy_url
            FROM spider_configs
            WHERE key = ?
        ''', (key,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'key': row[0],
                'name': row[1],
                'api': row[2],
                'ext': row[3],
                'jar': row[4],
                'type': row[5],
                'enabled': bool(row[6]),
                'proxy_enabled': bool(row[7]),
                'proxy_url': row[8]
            }
        return None

    def delete(self, key: str) -> bool:
        """删除配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM spider_configs WHERE key = ?", (key,))
            conn.commit()
            return True
        except Exception as e:
            print(f"删除配置失败: {e}")
            return False
        finally:
            conn.close()

    def get_enabled(self) -> List[Dict]:
        """获取所有启用的配置"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT key, name, api, ext, jar, type, enabled, proxy_enabled, proxy_url
            FROM spider_configs
            WHERE enabled = 1
            ORDER BY created_at DESC
        ''')

        configs = []
        for row in cursor.fetchall():
            configs.append({
                'key': row[0],
                'name': row[1],
                'api': row[2],
                'ext': row[3],
                'jar': row[4],
                'type': row[5],
                'enabled': bool(row[6]),
                'proxy_enabled': bool(row[7]),
                'proxy_url': row[8]
            })

        conn.close()
        return configs


# 全局配置管理器实例
config_manager = ConfigManager()
