# -*- coding: utf-8 -*-
"""
智能代理管理器
自动检测请求失败并切换到代理模式
"""
import time
import json
import os
from typing import Dict, Optional, Set
from urllib.parse import urlparse
import httpx
from pathlib import Path


class SmartProxyManager:
    """智能代理管理器"""
    
    def __init__(self, proxy_url: Optional[str] = None, cache_file: str = "proxy_cache.json"):
        """
        初始化智能代理管理器
        
        Args:
            proxy_url: Cloudflare Worker 代理URL
            cache_file: 缓存文件路径
        """
        # 从环境变量或配置读取
        self.proxy_url = proxy_url or os.getenv('SMART_PROXY_URL', '')
        self.cache_file = cache_file
        
        # 需要使用代理的域名集合
        self.proxy_domains: Set[str] = set()
        
        # 直连健康的域名集合
        self.healthy_domains: Set[str] = set()
        
        # 域名失败次数记录
        self.failure_counts: Dict[str, int] = {}
        
        # 域名最后检查时间
        self.last_check_time: Dict[str, float] = {}
        
        # 配置参数（从环境变量读取）
        self.max_failures = int(os.getenv('MAX_FAILURES', '2'))
        self.retry_interval = int(os.getenv('RETRY_INTERVAL', '3600'))
        self.timeout = int(os.getenv('REQUEST_TIMEOUT', '10'))
        
        # 加载缓存
        self._load_cache()
    
    def init_from_settings(self):
        """从配置文件初始化代理URL"""
        try:
            from app.config import settings
            if settings.SMART_PROXY_URL and not self.proxy_url:
                self.proxy_url = settings.SMART_PROXY_URL
                self.max_failures = settings.MAX_FAILURES
                self.retry_interval = settings.RETRY_INTERVAL
                self.timeout = settings.REQUEST_TIMEOUT
                print(f"智能代理已启用: {self.proxy_url}")
        except Exception as e:
            print(f"加载智能代理配置失败: {e}")
    
    def print_status(self):
        """打印代理状态"""
        if self.proxy_url:
            print(f"智能代理已启用: {self.proxy_url}")
        else:
            print("智能代理未配置，请设置 SMART_PROXY_URL 环境变量")
    
    def _load_cache(self):
        """从文件加载缓存"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.proxy_domains = set(data.get('proxy_domains', []))
                    self.healthy_domains = set(data.get('healthy_domains', []))
                    self.failure_counts = data.get('failure_counts', {})
                    self.last_check_time = data.get('last_check_time', {})
        except Exception as e:
            print(f"加载代理缓存失败: {e}")
    
    def _save_cache(self):
        """保存缓存到文件"""
        try:
            data = {
                'proxy_domains': list(self.proxy_domains),
                'healthy_domains': list(self.healthy_domains),
                'failure_counts': self.failure_counts,
                'last_check_time': self.last_check_time
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存代理缓存失败: {e}")
    
    def _extract_domain(self, url: str) -> str:
        """
        从URL中提取域名
        
        Args:
            url: 完整URL
            
        Returns:
            域名
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url
    
    def should_use_proxy(self, url: str) -> bool:
        """
        判断是否应该使用代理
        
        Args:
            url: 目标URL
            
        Returns:
            是否使用代理
        """
        if not self.proxy_url:
            return False
        
        domain = self._extract_domain(url)
        
        # 如果域名在代理列表中，检查是否需要重试直连
        if domain in self.proxy_domains:
            last_check = self.last_check_time.get(domain, 0)
            if time.time() - last_check > self.retry_interval:
                # 超过重试间隔，尝试直连
                return False
            return True
        
        # 如果域名在健康列表中，不使用代理
        if domain in self.healthy_domains:
            return False
        
        # 默认不使用代理
        return False
    
    def record_success(self, url: str, used_proxy: bool = False):
        """
        记录请求成功
        
        Args:
            url: 目标URL
            used_proxy: 是否使用了代理
        """
        domain = self._extract_domain(url)
        
        if used_proxy:
            # 使用代理成功，记录域名需要代理
            if domain not in self.proxy_domains:
                self.proxy_domains.add(domain)
                self._save_cache()
        else:
            # 直连成功，记录域名健康
            if domain not in self.healthy_domains:
                self.healthy_domains.add(domain)
                self.failure_counts[domain] = 0
                self._save_cache()
    
    def record_failure(self, url: str, used_proxy: bool = False):
        """
        记录请求失败
        
        Args:
            url: 目标URL
            used_proxy: 是否使用了代理
        """
        domain = self._extract_domain(url)
        
        if used_proxy:
            # 代理也失败了，记录但保持代理状态
            print(f"代理请求失败: {domain}")
        else:
            # 直连失败，增加失败计数
            self.failure_counts[domain] = self.failure_counts.get(domain, 0) + 1
            self.last_check_time[domain] = time.time()
            
            # 超过最大失败次数，加入代理列表
            if self.failure_counts[domain] >= self.max_failures:
                if domain not in self.proxy_domains:
                    self.proxy_domains.add(domain)
                    print(f"域名 {domain} 连续失败 {self.failure_counts[domain]} 次，已加入代理列表")
                    self._save_cache()
    
    def build_proxy_url(self, target_url: str) -> str:
        """
        构建代理URL
        
        Args:
            target_url: 目标URL
            
        Returns:
            代理URL
        """
        if not self.proxy_url:
            return target_url
        
        return f"{self.proxy_url}?targetUrl={target_url}"
    
    def test_connection(self, url: str) -> tuple[bool, bool]:
        """
        测试连接，返回 (直连是否成功, 代理是否成功)
        
        Args:
            url: 测试URL
            
        Returns:
            (直连成功, 代理成功)
        """
        direct_success = False
        proxy_success = False
        
        # 测试直连
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, follow_redirects=True)
                direct_success = response.status_code < 500
        except:
            pass
        
        # 测试代理
        if self.proxy_url:
            try:
                proxy_url = self.build_proxy_url(url)
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.get(proxy_url, follow_redirects=True)
                    proxy_success = response.status_code < 500
            except:
                pass
        
        return direct_success, proxy_success
    
    def clear_cache(self):
        """清空缓存"""
        self.proxy_domains.clear()
        self.healthy_domains.clear()
        self.failure_counts.clear()
        self.last_check_time.clear()
        self._save_cache()
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'proxy_domains': list(self.proxy_domains),
            'healthy_domains': list(self.healthy_domains),
            'failure_counts': self.failure_counts,
            'total_proxy_domains': len(self.proxy_domains),
            'total_healthy_domains': len(self.healthy_domains),
            'proxy_url': self.proxy_url
        }


# 全局智能代理管理器实例
smart_proxy_manager = SmartProxyManager()
