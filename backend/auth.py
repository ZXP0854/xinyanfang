"""
JWT 认证模块
提供：登录、登出、token 刷新、管理员保护装饰器
"""

from functools import wraps
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    verify_jwt_in_request
)
from models import db, User, AuditLog

auth_bp = Blueprint('auth', __name__)

# JWT 黑名单（登出后失效的 token，生产环境应存 Redis）
_token_blocklist = set()


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """管理员登录"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供 JSON 格式的登录信息'}), 400

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        _log_audit(None, 'login_failed', detail=f'username={username}',
                   ip=request.remote_addr)
        return jsonify({'error': '用户名或密码错误'}), 401

    if not user.is_active:
        return jsonify({'error': '账号已被禁用'}), 403

    user.last_login = datetime.utcnow()
    db.session.commit()

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'username': user.username}
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    _log_audit(user.id, 'login', ip=request.remote_addr)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(),
    }), 200


@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """注册新用户"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供 JSON 格式的注册信息'}), 400

    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    display_name = (data.get('display_name') or '').strip()

    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    if len(username) < 3:
        return jsonify({'error': '用户名至少需要 3 个字符'}), 400
    if len(password) < 6:
        return jsonify({'error': '密码至少需要 6 个字符'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 409

    user = User(
        username=username,
        display_name=display_name or username,
        is_active=True,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'username': user.username}
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    _log_audit(user.id, 'register', ip=request.remote_addr)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(),
    }), 201


@auth_bp.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新 access token"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or not user.is_active:
        return jsonify({'error': '用户无效'}), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'username': user.username}
    )
    return jsonify({'access_token': access_token}), 200


@auth_bp.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """登出（将当前 token 加入黑名单）"""
    jti = get_jwt()['jti']
    _token_blocklist.add(jti)
    _log_audit(int(get_jwt_identity()), 'logout', ip=request.remote_addr)
    return jsonify({'message': '已登出'}), 200


@auth_bp.route('/api/auth/me', methods=['GET'])
@jwt_required()
def me():
    """获取当前用户信息"""
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    return jsonify({'user': user.to_dict()}), 200


def admin_required(fn=None, *, optional=False):
    """
    管理员认证装饰器
    用于保护后端管理 API 和管理面板路由
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(optional=optional)
                user_id = get_jwt_identity()
                if user_id:
                    jti = get_jwt()['jti']
                    if jti in _token_blocklist:
                        from flask import redirect as _redirect
                        return _redirect('/admin/login')
                    user = User.query.get(int(user_id))
                    if user and user.is_active:
                        return f(*args, **kwargs)
            except Exception:
                pass

            # 检查 session 登录（用于管理面板）
            if session.get('admin_user_id'):
                user = User.query.get(int(session['admin_user_id']))
                if user and user.is_active:
                    return f(*args, **kwargs)

            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': '未授权访问'}), 401
            from flask import redirect as _redirect
            return _redirect('/admin/login')
        return wrapper

    if fn and callable(fn):
        return decorator(fn)
    return decorator


def is_token_blocked(jti: str) -> bool:
    """检查 token 是否在黑名单中"""
    return jti in _token_blocklist


def _log_audit(user_id, action, target_type='', target_id=None, detail='', ip=''):
    """写入审计日志"""
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
            ip_address=ip or request.remote_addr or '',
        )
        db.session.add(log)
        db.session.commit()
    except Exception:
        db.session.rollback()
