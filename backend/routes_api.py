"""
公开 API 接口
供前端（未来）或其他客户端调用，无需认证
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models import db, Tutorial, Resource, Card, SiteStat, UserHistory
from middleware import rate_limit, get_client_ip

api_bp = Blueprint('api', __name__)


# ═══════════════════════════════════════════════════════════════
# 教程 API
# ═══════════════════════════════════════════════════════════════

@api_bp.route('/api/tutorials', methods=['GET'])
@rate_limit(max_requests=120, window_seconds=60)
def get_tutorials():
    """获取所有已发布的教程列表（支持 ?category=workflow|aesthetics 过滤）"""
    query = Tutorial.query.filter_by(is_published=True)
    cat = request.args.get('category', None)
    if cat:
        query = query.filter_by(category=cat)
    tutorials = query.order_by(Tutorial.sort_order, Tutorial.node_id).all()
    return jsonify({
        'tutorials': [t.to_dict() for t in tutorials],
        'total': len(tutorials),
    }), 200


@api_bp.route('/api/tutorials/<node_id>', methods=['GET'])
@rate_limit(max_requests=120, window_seconds=60)
def get_tutorial(node_id):
    """获取单个教程详情"""
    t = Tutorial.query.filter_by(node_id=node_id, is_published=True).first()
    if not t:
        return jsonify({'error': '教程不存在'}), 404
    return jsonify({'tutorial': t.to_dict()}), 200


@api_bp.route('/api/tutorials/by-title/<title>', methods=['GET'])
@rate_limit(max_requests=120, window_seconds=60)
def get_tutorial_by_title(title):
    """通过标题查找教程（用于 openTutorial 兼容）"""
    t = Tutorial.query.filter_by(title=title, is_published=True).first()
    if not t:
        t = Tutorial.query.filter(
            Tutorial.title.contains(title),
            Tutorial.is_published == True
        ).first()
    if not t:
        return jsonify({'tutorial': None, 'message': '教程不存在'}), 200
    return jsonify({'tutorial': t.to_dict()}), 200


# ═══════════════════════════════════════════════════════════════
# 资源 API
# ═══════════════════════════════════════════════════════════════

@api_bp.route('/api/resources', methods=['GET'])
@rate_limit(max_requests=120, window_seconds=60)
def get_resources():
    """获取所有已发布的资源链接（按模块分组）"""
    resources = (
        Resource.query
        .filter_by(is_published=True)
        .order_by(Resource.module, Resource.sort_order)
        .all()
    )
    # 按模块分组
    modules = {}
    for r in resources:
        modules.setdefault(r.module, []).append(r.to_dict())

    return jsonify({
        'modules': modules,
        'total': len(resources),
    }), 200


@api_bp.route('/api/resources/module/<module_name>', methods=['GET'])
@rate_limit(max_requests=120, window_seconds=60)
def get_resources_by_module(module_name):
    """获取指定模块的资源链接"""
    resources = (
        Resource.query
        .filter_by(module=module_name, is_published=True)
        .order_by(Resource.sort_order)
        .all()
    )
    return jsonify({
        'module': module_name,
        'items': [r.to_dict() for r in resources],
    }), 200


# ═══════════════════════════════════════════════════════════════
# 审美卡片 API
# ═══════════════════════════════════════════════════════════════

@api_bp.route('/api/cards', methods=['GET'])
@rate_limit(max_requests=120, window_seconds=60)
def get_cards():
    """获取所有已发布的审美卡片"""
    cards = (
        Card.query
        .filter_by(is_published=True)
        .order_by(Card.sort_order)
        .all()
    )
    return jsonify({
        'cards': [c.to_dict() for c in cards],
        'total': len(cards),
    }), 200


# ═══════════════════════════════════════════════════════════════
# 网站统计 API
# ═══════════════════════════════════════════════════════════════

@api_bp.route('/api/stats/track', methods=['POST'])
@rate_limit(max_requests=60, window_seconds=60)
def track_event():
    """记录网站统计事件
    请求体: {"event_type": "page_view|tutorial_view|prompt_copy|resource_click",
              "event_key": "标识（页面路径/教程ID/资源名称等）"}"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供 JSON 数据'}), 400

    event_type = (data.get('event_type') or '').strip()
    if event_type not in ('page_view', 'tutorial_view', 'prompt_copy', 'resource_click'):
        return jsonify({'error': '无效的事件类型'}), 400

    event_key = (data.get('event_key') or '')[:300]
    ip = get_client_ip()
    ua = (request.headers.get('User-Agent', '') or '')[:500]

    stat = SiteStat(
        event_type=event_type,
        event_key=event_key,
        ip_address=ip,
        user_agent=ua,
    )
    db.session.add(stat)
    db.session.commit()
    return jsonify({'ok': True}), 201


# ═══════════════════════════════════════════════════════════════
# 搜索热词 API
# ═══════════════════════════════════════════════════════════════

@api_bp.route('/api/search/hot', methods=['GET'])
@rate_limit(max_requests=30, window_seconds=60)
def get_hot_search_terms():
    """获取热搜词（基于实际搜索/教程观看/资源点击统计，补齐到limit个）"""
    from sqlalchemy import func
    from datetime import timedelta
    limit = request.args.get('limit', 8, type=int)
    limit = min(limit, 12)
    since = datetime.utcnow() - timedelta(days=14)

    hot = {}
    # 1. 统计教程观看
    tutorial_hits = (
        db.session.query(
            SiteStat.event_key,
            func.count(SiteStat.id).label('cnt')
        )
        .filter(
            SiteStat.event_type == 'tutorial_view',
            SiteStat.event_key != '',
            SiteStat.created_at >= since
        )
        .group_by(SiteStat.event_key)
        .all()
    )
    # 2. 统计资源点击
    resource_hits = (
        db.session.query(
            SiteStat.event_key,
            func.count(SiteStat.id).label('cnt')
        )
        .filter(
            SiteStat.event_type == 'resource_click',
            SiteStat.event_key != '',
            SiteStat.created_at >= since
        )
        .group_by(SiteStat.event_key)
        .all()
    )
    # 3. 统计页面浏览（排除 path-like keys）
    page_hits = (
        db.session.query(
            SiteStat.event_key,
            func.count(SiteStat.id).label('cnt')
        )
        .filter(
            SiteStat.event_type == 'page_view',
            SiteStat.event_key != '',
            SiteStat.event_key.notlike('/%'),
            SiteStat.created_at >= since
        )
        .group_by(SiteStat.event_key)
        .all()
    )

    # 合并计数
    for key, cnt in tutorial_hits + resource_hits + page_hits:
        if not key: continue
        hot[key] = hot.get(key, 0) + cnt

    # 解析名称：node_id → 教程标题（仅返回有真实搜索数据的）
    result = []
    for key, cnt in sorted(hot.items(), key=lambda x: -x[1]):
        if cnt <= 0: continue  # 跳过无真实搜索量的
        name = key
        t = Tutorial.query.filter_by(node_id=key, is_published=True).first()
        if t:
            name = t.title
        r = Resource.query.filter_by(name=key, is_published=True).first()
        if r:
            name = r.name
        if len(name) > 18: name = name[:18] + '…'
        result.append({'term': name, 'count': cnt})
        if len(result) >= limit: break

    return jsonify({'hot': result}), 200


# ═══════════════════════════════════════════════════════════════
# 用户浏览历史 API
# ═══════════════════════════════════════════════════════════════

@api_bp.route('/api/user/history', methods=['GET'])
def get_user_history():
    """获取当前用户的浏览历史（需登录）"""
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        uid = get_jwt_identity()
        if uid:
            user_id = int(uid)
    except Exception:
        pass

    if not user_id:
        return jsonify({'history': [], 'message': '未登录'}), 200

    limit = request.args.get('limit', 30, type=int)
    limit = min(limit, 100)
    history = (
        UserHistory.query
        .filter_by(user_id=user_id)
        .order_by(UserHistory.created_at.desc())
        .limit(limit)
        .all()
    )
    return jsonify({'history': [h.to_dict() for h in history]}), 200


@api_bp.route('/api/user/history', methods=['POST'])
def save_user_history():
    """保存用户浏览记录（需登录）"""
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        uid = get_jwt_identity()
        if uid:
            user_id = int(uid)
    except Exception:
        pass

    if not user_id:
        return jsonify({'ok': False, 'message': '未登录'}), 200

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供 JSON 数据'}), 400

    event_type = (data.get('event_type') or '').strip()
    if event_type not in ('page_view', 'tutorial_view', 'resource_click', 'prompt_view'):
        return jsonify({'error': '无效的事件类型'}), 400

    event_key = (data.get('event_key') or '')[:300]
    event_label = (data.get('event_label') or '')[:300]

    # 同一用户同一教程节点30分钟内的重复记录跳过
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(minutes=30)
    existing = UserHistory.query.filter(
        UserHistory.user_id == user_id,
        UserHistory.event_type == event_type,
        UserHistory.event_key == event_key,
        UserHistory.created_at >= cutoff,
    ).first()
    if existing:
        return jsonify({'ok': True, 'skipped': True}), 200

    h = UserHistory(
        user_id=user_id,
        event_type=event_type,
        event_key=event_key,
        event_label=event_label,
    )
    db.session.add(h)
    db.session.commit()
    return jsonify({'ok': True}), 201
