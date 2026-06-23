"""
工具模块：文件上传处理、日志配置
"""

import os
import uuid
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image


# ─── 图片上传处理 ─────────────────────────────────────────────

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'}
ALLOWED_DOC_EXTENSIONS = {'pdf', 'doc', 'docx'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg', 'mov'}

# 文件幻数（magic bytes）验证，防止伪造 MIME
_MAGIC_SIGNATURES = {
    b'\xff\xd8\xff': 'jpg',
    b'\x89PNG\r\n\x1a\n': 'png',
    b'GIF87a': 'gif',
    b'GIF89a': 'gif',
    b'RIFF': 'webp',
    b'<svg': 'svg',
    b'%PDF': 'pdf',
}
_VIDEO_MAGIC_SIGNATURES = {
    b'\x00\x00\x00': 'mp4',   # ftyp box at offset 4
}


_ALL_ALLOWED = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOC_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS


def allowed_file(filename: str, allowed_set: set = None) -> bool:
    """检查文件扩展名是否允许（默认允许所有支持类型）"""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = allowed_set or _ALL_ALLOWED
    return ext in allowed


def validate_image_magic(file_data: bytes) -> bool:
    """通过文件头幻数验证是否为真实图片"""
    for magic, _ in _MAGIC_SIGNATURES.items():
        if file_data.startswith(magic):
            return True
    return False


def save_upload(file) -> dict:
    """
    保存上传文件
    返回: {'success': bool, 'filename': str, 'original_name': str, 'path': str, 'size': int, 'error': str}
    """
    if not file or not file.filename:
        return {'success': False, 'error': '未选择文件'}

    original_name = secure_filename(file.filename)

    if not allowed_file(original_name):
        return {'success': False, 'error': f'不支持的文件格式'}

    # 读取文件数据用于验证
    file_data = file.read()
    file.seek(0)

    # 生成唯一文件名
    ext = original_name.rsplit('.', 1)[1].lower()
    unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"

    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, unique_name)
    file.save(filepath)

    # 如果是图片，生成缩略图；视频和文档跳过
    thumbnail = None
    file_type = 'document'
    if ext in ALLOWED_IMAGE_EXTENSIONS and ext != 'svg':
        file_type = 'image'
        try:
            img = Image.open(filepath)
            img.thumbnail((800, 800), Image.LANCZOS)
            thumb_name = f"thumb_{unique_name}"
            thumb_path = os.path.join(upload_folder, thumb_name)
            img.save(thumb_path, quality=85, optimize=True)
            thumbnail = thumb_name
        except Exception:
            pass
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        file_type = 'video'

    file_size = os.path.getsize(filepath)

    return {
        'success': True,
        'filename': unique_name,
        'original_name': original_name,
        'path': filepath,
        'relative_path': f'static/uploads/{unique_name}',
        'size': file_size,
        'thumbnail': thumbnail,
        'file_type': file_type,
        'mime_type': file.content_type or '',
    }


def delete_upload_file(filename: str) -> bool:
    """删除上传的文件"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    filepath = os.path.join(upload_folder, secure_filename(filename))
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
        # 同时删除缩略图
        thumb_path = os.path.join(upload_folder, f"thumb_{filename}")
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        return True
    except OSError:
        return False


# ─── 日志配置 ──────────────────────────────────────────────────

def setup_logging(app):
    """配置应用日志：控制台 + 文件轮转"""
    if not app.debug:
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        # 应用日志
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10,
            encoding='utf-8',
        )
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # 错误日志单独记录
        error_handler = RotatingFileHandler(
            os.path.join(log_dir, 'error.log'),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding='utf-8',
        )
        error_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s'
        ))
        error_handler.setLevel(logging.ERROR)
        app.logger.addHandler(error_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Application logging configured')
