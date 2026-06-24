"""
数据库模型：用户、教程、资源链接、审美卡片、上传文件
支持 SQLite（开发）和 MySQL（生产）
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """管理员用户"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(120), default='')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'display_name': self.display_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Tutorial(db.Model):
    """教程内容（对应 workflow.html 的树节点）"""
    __tablename__ = 'tutorials'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    node_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    category = db.Column(db.String(20), default='workflow', index=True)  # 'workflow' | 'aesthetics'
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text, default='')
    content = db.Column(db.Text, default='')          # HTML 富文本内容
    meta_keywords = db.Column(db.String(500), default='')  # SEO 关键词
    is_published = db.Column(db.Boolean, default=False)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'node_id': self.node_id,
            'category': self.category,
            'title': self.title,
            'summary': self.summary,
            'content': self.content,
            'meta_keywords': self.meta_keywords,
            'is_published': self.is_published,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Resource(db.Model):
    """科研资源链接（对应 resources.html）"""
    __tablename__ = 'resources'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module = db.Column(db.String(100), nullable=False, index=True)   # 所属模块
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), default='')
    link_type = db.Column(db.String(20), default='tutorial')  # 'tutorial' 或 'external'
    link_value = db.Column(db.String(500), nullable=False)    # 教程标题 或 外部URL
    sort_order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'module': self.module,
            'name': self.name,
            'description': self.description,
            'link_type': self.link_type,
            'link_value': self.link_value,
            'sort_order': self.sort_order,
            'is_published': self.is_published,
        }


class Card(db.Model):
    """审美卡片（对应 aesthetics.html 瀑布流）"""
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    icon = db.Column(db.String(100), default='fa-solid fa-star')      # Font Awesome 图标类名
    tag = db.Column(db.String(100), default='')
    category = db.Column(db.String(50), default='', index=True)         # 筛选分类：Mplus语句/拆解/方法/素材
    height = db.Column(db.Integer, default=200)                        # 卡片图片区高度（px）
    image_url = db.Column(db.String(500), default='')                  # 自定义图片URL（可选）
    tutorial_title = db.Column(db.String(200), default='')             # 关联的教程标题
    link_url = db.Column(db.String(500), default='')                   # 外部链接（可选）
    sort_order = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'tag': self.tag,
            'category': self.category,
            'height': self.height,
            'image_url': self.image_url,
            'tutorial_title': self.tutorial_title,
            'link_url': self.link_url,
            'sort_order': self.sort_order,
            'is_published': self.is_published,
        }


class Upload(db.Model):
    """上传文件记录"""
    __tablename__ = 'uploads'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(300), nullable=False)        # 存储文件名（UUID）
    original_name = db.Column(db.String(300), nullable=False)   # 原始文件名
    mime_type = db.Column(db.String(100), default='')
    file_size = db.Column(db.Integer, default=0)               # 字节
    file_type = db.Column(db.String(20), default='document')   # 'image', 'video', 'document'
    relative_path = db.Column(db.String(500), default='')      # 相对路径
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_name': self.original_name,
            'mime_type': self.mime_type,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'relative_path': self.relative_path,
            'url': f'/static/uploads/{self.filename}',
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class AuditLog(db.Model):
    """操作审计日志"""
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)
    action = db.Column(db.String(100), nullable=False)       # 'login', 'create_tutorial', 'upload_file' 等
    target_type = db.Column(db.String(50), default='')        # 'tutorial', 'resource', 'card', 'upload'
    target_id = db.Column(db.Integer, nullable=True)
    detail = db.Column(db.Text, default='')                   # JSON 格式的操作详情
    ip_address = db.Column(db.String(45), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
