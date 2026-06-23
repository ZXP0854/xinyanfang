"""
公开 API 接口
供前端（未来）或其他客户端调用，无需认证
"""

from flask import Blueprint, request, jsonify
from models import db, Tutorial, Resource, Card
from middleware import rate_limit

api_bp = Blueprint('api', __name__)


# ═══════════════════════════════════════════════════════════════
# 教程 API
# ═══════════════════════════════════════════════════════════════

@api_bp.route('/api/tutorials', methods=['GET'])
@rate_limit(max_requests=120, window_seconds=60)
def get_tutorials():
    """获取所有已发布的教程列表"""
    tutorials = (
        Tutorial.query
        .filter_by(is_published=True)
        .order_by(Tutorial.sort_order, Tutorial.node_id)
        .all()
    )
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
