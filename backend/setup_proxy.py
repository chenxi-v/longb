#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能代理配置脚本
快速配置和测试 Cloudflare Worker 代理
"""
import os
import sys
import httpx


def test_worker(worker_url: str) -> bool:
    """测试 Worker 是否正常工作"""
    print(f"\n正在测试 Worker: {worker_url}")
    
    # 测试健康检查
    try:
        health_url = f"{worker_url}/health"
        print(f"测试健康检查: {health_url}")
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(health_url)
            
            if response.status_code == 200:
                print("✅ Worker 健康检查通过")
                return True
            else:
                print(f"❌ Worker 返回状态码: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Worker 连接失败: {e}")
        return False


def test_proxy_request(worker_url: str, test_url: str = "https://httpbin.org/get") -> bool:
    """测试代理请求"""
    print(f"\n正在测试代理请求: {test_url}")
    
    try:
        proxy_url = f"{worker_url}?targetUrl={test_url}"
        
        with httpx.Client(timeout=15.0) as client:
            response = client.get(proxy_url)
            
            if response.status_code == 200:
                print("✅ 代理请求成功")
                data = response.json()
                print(f"响应数据: {data.get('url', 'N/A')}")
                return True
            else:
                print(f"❌ 代理请求失败，状态码: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ 代理请求失败: {e}")
        return False


def save_env_file(worker_url: str):
    """保存配置到 .env 文件"""
    env_content = f"""# 智能代理配置
SMART_PROXY_URL={worker_url}

# 可选配置
# MAX_FAILURES=2
# RETRY_INTERVAL=3600
# REQUEST_TIMEOUT=10
"""
    
    env_file = ".env"
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n✅ 配置已保存到 {env_file}")


def main():
    print("=" * 60)
    print("LongTV 智能代理配置工具")
    print("=" * 60)
    
    # 获取 Worker URL
    if len(sys.argv) > 1:
        worker_url = sys.argv[1]
    else:
        worker_url = input("\n请输入 Cloudflare Worker URL: ").strip()
    
    # 移除末尾的斜杠
    worker_url = worker_url.rstrip('/')
    
    # 验证 URL 格式
    if not worker_url.startswith('http'):
        print("❌ URL 格式错误，必须以 http:// 或 https:// 开头")
        return
    
    print(f"\nWorker URL: {worker_url}")
    
    # 测试 Worker
    if not test_worker(worker_url):
        print("\n⚠️  Worker 测试失败，请检查 URL 是否正确")
        print("正确的 URL 格式示例：")
        print("  https://your-worker.your-subdomain.workers.dev")
        return
    
    # 测试代理请求
    if not test_proxy_request(worker_url):
        print("\n⚠️  代理请求测试失败")
        return
    
    # 保存配置
    save_env_file(worker_url)
    
    print("\n" + "=" * 60)
    print("✅ 配置完成！")
    print("=" * 60)
    print("\n下一步：")
    print("1. 重启后端服务")
    print("2. 查看日志确认智能代理已启用")
    print("3. 测试爬虫功能")
    print("\nAPI 接口：")
    print(f"  GET  /api/smart-proxy/stats     - 查看统计")
    print(f"  POST /api/smart-proxy/test-connection - 测试连接")
    print("=" * 60)


if __name__ == "__main__":
    main()
