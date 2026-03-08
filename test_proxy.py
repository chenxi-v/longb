#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能代理是否工作
"""
import httpx
import json
import sys

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_smart_proxy():
    """测试智能代理"""
    print("=" * 60)
    print("测试智能代理功能")
    print("=" * 60)
    
    # 1. 检查代理URL配置
    print("\n1. 检查代理URL配置...")
    try:
        response = httpx.get("http://localhost:8000/api/smart-proxy/get-url")
        data = response.json()
        proxy_url = data.get("data", {}).get("proxy_url", "")
        if proxy_url:
            print(f"[OK] 代理URL已配置: {proxy_url}")
        else:
            print("[ERROR] 代理URL未配置")
            return
    except Exception as e:
        print(f"[ERROR] 检查代理URL失败: {e}")
        return
    
    # 2. 测试Worker健康检查
    print(f"\n2. 测试Worker健康检查...")
    try:
        health_url = f"{proxy_url}/health"
        response = httpx.get(health_url, timeout=10.0)
        if response.status_code == 200:
            print(f"[OK] Worker健康检查通过")
            print(f"   响应: {response.text}")
        else:
            print(f"[ERROR] Worker返回状态码: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Worker健康检查失败: {e}")
    
    # 3. 测试代理请求
    print(f"\n3. 测试代理请求...")
    test_url = "https://httpbin.org/get"
    try:
        proxy_request_url = f"{proxy_url}?targetUrl={test_url}"
        response = httpx.get(proxy_request_url, timeout=15.0)
        if response.status_code == 200:
            print(f"[OK] 代理请求成功")
            data = response.json()
            print(f"   目标URL: {data.get('url', 'N/A')}")
        else:
            print(f"[ERROR] 代理请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] 代理请求失败: {e}")
    
    # 4. 测试爬虫API
    print(f"\n4. 测试爬虫API...")
    try:
        # 获取爬虫列表
        response = httpx.get("http://localhost:8000/api/config/list")
        configs = response.json().get("data", [])
        
        if configs:
            spider = configs[0]
            print(f"   测试爬虫: {spider.get('name')} ({spider.get('key')})")
            
            # 测试首页接口
            home_response = httpx.post(
                "http://localhost:8000/api/home",
                json={
                    "key": spider.get("key"),
                    "filter": False,
                    "use_proxy": True
                },
                timeout=30.0
            )
            
            if home_response.status_code == 200:
                print(f"[OK] 爬虫API请求成功")
                data = home_response.json()
                if data.get("data"):
                    print(f"   返回数据: {len(data['data'].get('list', []))} 个视频")
            else:
                print(f"[ERROR] 爬虫API请求失败: {home_response.status_code}")
        else:
            print("[ERROR] 没有可用的爬虫")
    except Exception as e:
        print(f"[ERROR] 爬虫API测试失败: {e}")
    
    # 5. 查看统计信息
    print(f"\n5. 查看统计信息...")
    try:
        response = httpx.get("http://localhost:8000/api/smart-proxy/stats")
        stats = response.json().get("data", {})
        print(f"   代理域名数: {stats.get('total_proxy_domains', 0)}")
        print(f"   健康域名数: {stats.get('total_healthy_domains', 0)}")
        if stats.get('proxy_domains'):
            print(f"   需要代理的域名: {', '.join(stats['proxy_domains'])}")
        if stats.get('healthy_domains'):
            print(f"   健康的域名: {', '.join(stats['healthy_domains'])}")
    except Exception as e:
        print(f"[ERROR] 获取统计信息失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_smart_proxy()
