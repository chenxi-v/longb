"""
数据模型定义
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class SpiderConfig(BaseModel):
    """爬虫配置"""
    key: str
    name: str
    api: str
    ext: str = ""
    jar: Optional[str] = None
    type: str  # python, javascript, jar
    enabled: bool = True
    proxy_enabled: bool = False
    proxy_url: Optional[str] = None


class VideoItem(BaseModel):
    """视频项"""
    vod_id: int
    vod_name: str
    vod_pic: Optional[str] = None
    vod_remarks: Optional[str] = None
    vod_actor: Optional[str] = None
    vod_director: Optional[str] = None
    vod_area: Optional[str] = None
    vod_year: Optional[str] = None
    vod_score: Optional[str] = None
    vod_play_from: Optional[str] = None
    vod_play_url: Optional[List[Dict]] = None
    type_id: int
    type_name: str


class CategoryItem(BaseModel):
    """分类项"""
    type_id: int
    type_name: str


class PlayUrlItem(BaseModel):
    """播放地址项"""
    name: str
    url: List[str]


class ApiResponse(BaseModel):
    """API 响应"""
    code: int = 0
    msg: str = "success"
    data: Optional[Any] = None
