"""
心研坊后端配置
环境切换：开发环境用 SQLite，生产环境用 MySQL
"""

import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'xinyanfang-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # 上传文件配置
    MAX_CONTENT_LENGTH = 512 * 1024 * 1024  # 512MB（支持视频）
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'ico', 'pdf', 'doc', 'docx', 'mp4', 'webm', 'ogg', 'mov'}
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg', 'mov'}

    # Redis（生产环境使用）
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

    # 分页
    API_PER_PAGE = 20

    # AI API (DeepSeek 免费额度: 10M tokens, 注册即用)
    # 注册地址: https://platform.deepseek.com → API Keys → 创建
    # 免费额度用完可换用硅基流动: https://siliconflow.cn (新用户送14元)
    AI_API_KEY = os.environ.get('AI_API_KEY', os.environ.get('DEEPSEEK_API_KEY', ''))
    AI_API_URL = os.environ.get('AI_API_URL', 'https://api.deepseek.com/v1/chat/completions')
    AI_MODEL = os.environ.get('AI_MODEL', 'deepseek-chat')


class DevelopmentConfig(Config):
    """开发环境"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "data.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 开发环境不使用 Redis，用内存缓存
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300


class ProductionConfig(Config):
    """生产环境（阿里云 Linux + 宝塔），默认 SQLite，可通过环境变量切换 MySQL/Redis"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "data.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 缓存：设置 REDIS_URL 环境变量可启用 Redis，否则用内存缓存
    CACHE_TYPE = 'RedisCache' if os.environ.get('REDIS_URL') else 'SimpleCache'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', Config.REDIS_URL)
    CACHE_DEFAULT_TIMEOUT = 600


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
