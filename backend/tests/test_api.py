"""
API 测试
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["status"] == "running"


def test_health():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_spiders():
    """测试获取爬虫列表"""
    response = client.get("/api/spider/list")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert isinstance(data["data"], list)


def test_list_configs():
    """测试获取配置列表"""
    response = client.get("/api/config/list")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert isinstance(data["data"], list)


def test_save_and_delete_config():
    """测试保存和删除配置"""
    # 保存配置
    config_data = {
        "key": "test_spider",
        "name": "测试爬虫",
        "api": "./spiders/python/example_spider.py",
        "ext": "",
        "type": "python",
        "enabled": True
    }

    response = client.post("/api/config/save", json=config_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0

    # 获取配置
    response = client.get(f"/api/config/{config_data['key']}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["key"] == config_data["key"]

    # 删除配置
    response = client.delete(f"/api/config/{config_data['key']}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0


def test_load_and_unload_spider():
    """测试加载和卸载爬虫"""
    # 加载爬虫
    load_data = {
        "key": "test_spider",
        "path": "./spiders/python/example_spider.py",
        "spider_type": "python",
        "extend": ""
    }

    response = client.post("/api/spider/load", json=load_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["key"] == load_data["key"]

    # 获取爬虫列表
    response = client.get("/api/spider/list")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]) > 0

    # 卸载爬虫
    unload_data = {"key": "test_spider"}
    response = client.post("/api/spider/unload", json=unload_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0


def test_home_content():
    """测试获取首页内容"""
    # 先加载爬虫
    load_data = {
        "key": "test_spider",
        "path": "./spiders/python/example_spider.py",
        "spider_type": "python",
        "extend": ""
    }
    client.post("/api/spider/load", json=load_data)

    # 获取首页内容
    home_data = {
        "key": "test_spider",
        "filter": False
    }
    response = client.post("/api/home", json=home_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "class" in data["data"]
    assert "list" in data["data"]

    # 清理
    client.post("/api/spider/unload", json={"key": "test_spider"})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
