"""
Vercel Serverless Function 入口
"""
from app.main import app

# Vercel Python runtime 需要 ASGI handler
handler = app
