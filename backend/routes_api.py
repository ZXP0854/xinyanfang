"""
公开 API 接口
供前端（未来）或其他客户端调用，无需认证
"""

from flask import Blueprint, request, jsonify
from models import db, Tutorial, Resource, Card, SiteStat
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
