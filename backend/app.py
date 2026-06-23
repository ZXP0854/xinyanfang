"""
心研坊后端服务
Flask 应用工厂模式：API + 管理后台
"""

import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from config import config_map

jwt = JWTManager()
cache = Cache()


def create_app(config_name: str = None) -> Flask:
    """应用工厂"""
    env = config_name or os.environ.get('FLASK_ENV', 'production')
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(config_map.get(env, config_map['production']))

    # 初始化扩展（db 从 models 导入，确保与其他模块共用同一实例）
    from models import db
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)

    # JWT 黑名单检查
    @jwt.token_in_blocklist_loader
    def check_token_blocklist(jwt_header, jwt_payload):
        from auth import is_token_blocked
        return is_token_blocked(jwt_payload['jti'])

    # 日志
    from utils import setup_logging
    setup_logging(app)

    # 安全响应头
    from middleware import add_security_headers
    app.after_request(add_security_headers)

    # ─── 注册蓝图 ──────────────────────────────────────────

    from auth import auth_bp
    app.register_blueprint(auth_bp)

    from routes_api import api_bp
    app.register_blueprint(api_bp)

    from routes_admin import admin_bp
    app.register_blueprint(admin_bp)

    # ─── 确保上传目录存在 ──────────────────────────────────

    with app.app_context():
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder:
            os.makedirs(upload_folder, exist_ok=True)

        # 自动建表 + 迁移（Gunicorn 启动时也会执行）
        db.create_all()
        _run_migrations(db)

    return app


def _run_migrations(db):
    """每次启动时执行的安全迁移（幂等，失败不中断）"""
    from sqlalchemy import text
    migrations = [
        "ALTER TABLE uploads ADD COLUMN file_type VARCHAR(20) DEFAULT 'document'",
    ]
    for sql in migrations:
        try:
            db.session.execute(text(sql))
            db.session.commit()
        except Exception:
            db.session.rollback()


def init_db(app: Flask):
    """初始化管理员账号（建表和迁移已在 create_app 中自动执行）"""
    from models import db, User
    with app.app_context():
        if User.query.count() == 0:
            admin = User(
                username='admin',
                display_name='管理员',
                is_active=True,
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            app.logger.info('Default admin account created (admin / admin123)')


def init_scheduler(app: Flask):
    """初始化定时任务"""
    from tasks import init_scheduler as start_scheduler
    start_scheduler(app)


# 模块级 WSGI 应用实例（Gunicorn 用）
application = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == '__main__':
    init_db(application)
    init_scheduler(application)
    application.run(
        host='0.0.0.0',
        port=5000,
        debug=os.environ.get('FLASK_ENV') == 'development',
    )
