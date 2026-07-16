"""
管理后台路由：API CRUD 接口 + HTML 管理面板
所有路由需要 admin_required 认证
"""

import os
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, current_app
from models import db, Tutorial, Resource, Card, Upload, AuditLog, SiteStat, User, UserHistory
from auth import admin_required, _log_audit
from utils import save_upload, delete_upload_file, allowed_file, convert_docx_with_images
from middleware import sanitize_input, sanitize_html, validate_required

admin_bp = Blueprint('admin', __name__)


# ═══════════════════════════════════════════════════════════════
# 管理面板 — session 登录（浏览器用）
# ═══════════════════════════════════════════════════════════════

@admin_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login_page():
    """管理后台登录页"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        from models import User
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.is_active:
            session['admin_user_id'] = user.id
            session['admin_username'] = user.username
            user.last_login = datetime.utcnow()
            db.session.commit()
            _log_audit(user.id, 'login_panel', ip=request.remote_addr)
            return redirect(url_for('admin.dashboard'))
        return render_template('admin/login.html', error='用户名或密码错误')

    return render_template('admin/login.html', error=None)


@admin_bp.route('/admin/logout')
def admin_logout():
    """退出管理后台"""
    session.pop('admin_user_id', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin.admin_login_page'))


# ═══════════════════════════════════════════════════════════════
# 管理面板 — HTML 页面（浏览器渲染）
# ═══════════════════════════════════════════════════════════════

@admin_bp.route('/admin')
@admin_required
def dashboard():
    """管理后台首页/仪表盘"""
    from sqlalchemy import func

    counts = {
        'tutorials': Tutorial.query.count(),
        'published_tutorials': Tutorial.query.filter_by(is_published=True).count(),
        'resources': Resource.query.count(),
        'cards': Card.query.count(),
        'uploads': Upload.query.count(),
    }

    # 网站统计概览
    stat_counts = {}
    for event_type in ('page_view', 'tutorial_view', 'prompt_copy', 'resource_click'):
        stat_counts[event_type] = SiteStat.query.filter_by(event_type=event_type).count()
    stat_counts['total_visitors'] = (
        db.session.query(func.count(func.distinct(SiteStat.ip_address)))
        .scalar()
    ) or 0
    stat_counts['registered_users'] = User.query.count()

    recent_logs = (
        AuditLog.query
        .order_by(AuditLog.created_at.desc())
        .limit(20)
        .all()
    )

    # 最近用户浏览历史
    recent_histories = (
        UserHistory.query
        .order_by(UserHistory.created_at.desc())
        .limit(15)
        .all()
    )

    return render_template('admin/dashboard.html',
        counts=counts, stat_counts=stat_counts,
        logs=recent_logs, histories=recent_histories)


@admin_bp.route('/admin/tutorials')
@admin_required
def tutorial_list():
    """教程列表页"""
    tutorials = Tutorial.query.filter_by(category='workflow').order_by(Tutorial.node_id).all()
    return render_template('admin/tutorial_list.html', tutorials=tutorials)


@admin_bp.route('/admin/tutorials/new')
@admin_bp.route('/admin/tutorials/<int:tutorial_id>/edit')
@admin_required
def tutorial_edit(tutorial_id=None):
    """创建/编辑教程页"""
    tutorial = None
    if tutorial_id:
        tutorial = Tutorial.query.get_or_404(tutorial_id)
    return render_template('admin/tutorial_edit.html', tutorial=tutorial)


@admin_bp.route('/admin/aesthetics')
@admin_required
def aesthetic_list():
    """审美教程列表页"""
    tutorials = Tutorial.query.filter_by(category='aesthetics').order_by(Tutorial.sort_order).all()
    return render_template('admin/aesthetic_list.html', tutorials=tutorials)


@admin_bp.route('/admin/aesthetics/new')
@admin_bp.route('/admin/aesthetics/<int:tutorial_id>/edit')
@admin_required
def aesthetic_edit(tutorial_id=None):
    """创建/编辑审美教程页"""
    tutorial = None
    if tutorial_id:
        tutorial = Tutorial.query.get_or_404(tutorial_id)
    return render_template('admin/aesthetic_edit.html', tutorial=tutorial)


@admin_bp.route('/admin/resources')
@admin_required
def resource_list():
    """资源链接列表页"""
    resources = Resource.query.order_by(Resource.module, Resource.sort_order).all()
    return render_template('admin/resource_list.html', resources=resources)


@admin_bp.route('/admin/cards')
@admin_required
def card_list():
    """审美卡片列表页"""
    cards = Card.query.order_by(Card.sort_order).all()
    return render_template('admin/card_list.html', cards=cards)


@admin_bp.route('/admin/uploads')
@admin_required
def upload_list():
    """上传文件管理页"""
    uploads = Upload.query.order_by(Upload.created_at.desc()).limit(100).all()
    return render_template('admin/upload_list.html', uploads=uploads)


# ═══════════════════════════════════════════════════════════════
# 教程 CRUD API（JSON 接口）
# ═══════════════════════════════════════════════════════════════

@admin_bp.route('/api/admin/tutorials', methods=['GET'])
@admin_required
def api_tutorial_list():
    """获取所有教程（含未发布）"""
    tutorials = Tutorial.query.order_by(Tutorial.node_id).all()
    return jsonify({'tutorials': [t.to_dict() for t in tutorials]}), 200


@admin_bp.route('/api/admin/tutorials', methods=['POST'])
@admin_required
def api_tutorial_create():
    """创建教程"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供 JSON 数据'}), 400

    missing = validate_required(data, ['node_id', 'title'])
    if missing:
        return jsonify({'error': f'缺少必填字段: {", ".join(missing)}'}), 400

    if Tutorial.query.filter_by(node_id=data['node_id']).first():
        return jsonify({'error': f'节点 {data["node_id"]} 已存在'}), 409

    t = Tutorial(
        node_id=data['node_id'].strip(),
        category=data.get('category', 'workflow'),
        title=data['title'].strip(),
        summary=sanitize_html(data.get('summary', '')[:500]),
        content=data.get('content', ''),
        meta_keywords=data.get('meta_keywords', '')[:500],
        is_published=data.get('is_published', False),
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(t)
    db.session.commit()
    _log_audit(g.get('admin_user_id') or session.get('admin_user_id'), 'create_tutorial',
               target_type='tutorial', target_id=t.id,
               detail=f'node_id={t.node_id}')
    return jsonify({'tutorial': t.to_dict()}), 201


@admin_bp.route('/api/admin/tutorials/<int:tutorial_id>', methods=['PUT'])
@admin_required
def api_tutorial_update(tutorial_id):
    """更新教程"""
    t = Tutorial.query.get_or_404(tutorial_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供 JSON 数据'}), 400

    if 'node_id' in data:
        t.node_id = data['node_id'].strip()
    if 'category' in data:
        t.category = data['category'].strip()
    if 'title' in data:
        t.title = data['title'].strip()
    if 'summary' in data:
        t.summary = sanitize_html(data['summary'][:500])
    if 'content' in data:
        t.content = data['content']
    if 'meta_keywords' in data:
        t.meta_keywords = data['meta_keywords'][:500]
    if 'is_published' in data:
        t.is_published = bool(data['is_published'])
    if 'sort_order' in data:
        try: t.sort_order = int(data['sort_order'])
        except (ValueError, TypeError): return jsonify({'error': 'sort_order 必须为整数'}), 400
    t.updated_at = datetime.utcnow()

    db.session.commit()
    _log_audit(g.get('admin_user_id') or session.get('admin_user_id'), 'update_tutorial',
               target_type='tutorial', target_id=t.id,
               detail=f'node_id={t.node_id}')
    return jsonify({'tutorial': t.to_dict()}), 200


@admin_bp.route('/api/admin/tutorials/<int:tutorial_id>', methods=['DELETE'])
@admin_required
def api_tutorial_delete(tutorial_id):
    """删除教程"""
    t = Tutorial.query.get_or_404(tutorial_id)
    db.session.delete(t)
    db.session.commit()
    _log_audit(g.get('admin_user_id') or session.get('admin_user_id'), 'delete_tutorial',
               target_type='tutorial', target_id=tutorial_id)
    return jsonify({'message': '教程已删除'}), 200


# ═══════════════════════════════════════════════════════════════
# 资源 CRUD API
# ═══════════════════════════════════════════════════════════════

@admin_bp.route('/api/admin/resources', methods=['GET'])
@admin_required
def api_resource_list():
    resources = Resource.query.order_by(Resource.module, Resource.sort_order).all()
    return jsonify({'resources': [r.to_dict() for r in resources]}), 200


@admin_bp.route('/api/admin/resources', methods=['POST'])
@admin_required
def api_resource_create():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供 JSON 数据'}), 400

    missing = validate_required(data, ['name', 'link_value'])
    if missing:
        return jsonify({'error': f'缺少必填字段: {", ".join(missing)}'}), 400

    r = Resource(
        module=data.get('module', ''),
        name=data['name'].strip(),
        description=data.get('description', '')[:500],
        link_type=data.get('link_type', 'tutorial'),
        link_value=data['link_value'].strip(),
        sort_order=data.get('sort_order', 0),
        is_published=data.get('is_published', True),
    )
    db.session.add(r)
    db.session.commit()
    _log_audit(g.get('admin_user_id') or session.get('admin_user_id'), 'create_resource',
               target_type='resource', target_id=r.id)
    return jsonify({'resource': r.to_dict()}), 201


@admin_bp.route('/api/admin/resources/<int:resource_id>', methods=['PUT'])
@admin_required
def api_resource_update(resource_id):
    r = Resource.query.get_or_404(resource_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供 JSON 数据'}), 400

    for field in ['module', 'name', 'description', 'link_type', 'link_value', 'sort_order', 'is_published']:
        if field in data:
            val = data[field]
            if field == 'is_published':
                val = bool(val)
            elif field == 'sort_order':
                try: val = int(val)
                except (ValueError, TypeError): val = 0
            elif isinstance(val, str):
                val = val.strip()[:500]
            setattr(r, field, val)

    db.session.commit()
    return jsonify({'resource': r.to_dict()}), 200


@admin_bp.route('/api/admin/resources/<int:resource_id>', methods=['DELETE'])
@admin_required
def api_resource_delete(resource_id):
    r = Resource.query.get_or_404(resource_id)
    db.session.delete(r)
    db.session.commit()
    _log_audit(g.get('admin_user_id') or session.get('admin_user_id'), 'delete_resource',
               target_type='resource', target_id=resource_id)
    return jsonify({'message': '资源已删除'}), 200


# ═══════════════════════════════════════════════════════════════
# 卡片 CRUD API
# ═══════════════════════════════════════════════════════════════

@admin_bp.route('/api/admin/cards', methods=['GET'])
@admin_required
def api_card_list():
    cards = Card.query.order_by(Card.sort_order).all()
    return jsonify({'cards': [c.to_dict() for c in cards]}), 200


@admin_bp.route('/api/admin/cards', methods=['POST'])
@admin_required
def api_card_create():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供 JSON 数据'}), 400

    missing = validate_required(data, ['title'])
    if missing:
        return jsonify({'error': f'缺少必填字段: {", ".join(missing)}'}), 400

    c = Card(
        title=data['title'].strip(),
        description=data.get('description', '')[:500],
        icon=data.get('icon', 'fa-solid fa-star'),
        tag=data.get('tag', ''),
        category=data.get('category', ''),
        height=data.get('height', 200),
        image_url=data.get('image_url', ''),
        tutorial_title=data.get('tutorial_title', ''),
        link_url=data.get('link_url', ''),
        sort_order=data.get('sort_order', 0),
        is_published=data.get('is_published', True),
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({'card': c.to_dict()}), 201


@admin_bp.route('/api/admin/cards/<int:card_id>', methods=['PUT'])
@admin_required
def api_card_update(card_id):
    c = Card.query.get_or_404(card_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供 JSON 数据'}), 400

    for field in ['title', 'description', 'icon', 'tag', 'category', 'height', 'image_url',
                   'tutorial_title', 'link_url', 'sort_order', 'is_published']:
        if field in data:
            val = data[field]
            if field == 'is_published':
                val = bool(val)
            elif field in ('height', 'sort_order'):
                try: val = int(val)
                except (ValueError, TypeError): val = field == 'height' and 220 or 0
            elif isinstance(val, str):
                val = val.strip()[:500]
            setattr(c, field, val)

    db.session.commit()
    return jsonify({'card': c.to_dict()}), 200


@admin_bp.route('/api/admin/cards/<int:card_id>', methods=['DELETE'])
@admin_required
def api_card_delete(card_id):
    c = Card.query.get_or_404(card_id)
    db.session.delete(c)
    db.session.commit()
    return jsonify({'message': '卡片已删除'}), 200


# ═══════════════════════════════════════════════════════════════
# 文件上传 API
# ═══════════════════════════════════════════════════════════════

@admin_bp.route('/api/admin/upload', methods=['POST'])
@admin_required
def api_upload():
    """上传图片/文件"""
    if 'file' not in request.files:
        return jsonify({'error': '未选择文件'}), 400

    file = request.files['file']
    result = save_upload(file)

    if not result['success']:
        return jsonify({'error': result['error']}), 400

    # 记录到数据库
    upload = Upload(
        filename=result['filename'],
        original_name=result['original_name'],
        mime_type=result['mime_type'],
        file_size=result['size'],
        file_type=result.get('file_type', 'document'),
        relative_path=result['relative_path'],
    )
    db.session.add(upload)
    db.session.commit()
    _log_audit(g.get('admin_user_id') or session.get('admin_user_id'), 'upload_file',
               target_type='upload', target_id=upload.id,
               detail=f'file={result["original_name"]}')

    return jsonify({
        'upload': upload.to_dict(),
        'thumbnail': result.get('thumbnail'),
    }), 201


@admin_bp.route('/api/admin/uploads/<int:upload_id>', methods=['DELETE'])
@admin_required
def api_upload_delete(upload_id):
    """删除已上传文件"""
    upload = Upload.query.get_or_404(upload_id)
    delete_upload_file(upload.filename)
    db.session.delete(upload)
    db.session.commit()
    return jsonify({'message': '文件已删除'}), 200


@admin_bp.route('/api/admin/convert-docx', methods=['POST'])
@admin_required
def api_convert_docx():
    """上传 .docx 并转换为 HTML"""
    if 'file' not in request.files:
        return jsonify({'error': '未选择文件'}), 400

    file = request.files['file']
    if not file.filename or not file.filename.lower().endswith('.docx'):
        return jsonify({'error': '仅支持 .docx 文件'}), 400

    # 先保存文件
    result = save_upload(file)
    if not result['success']:
        return jsonify({'error': result['error']}), 400

    # 记录上传
    upload = Upload(
        filename=result['filename'],
        original_name=result['original_name'],
        mime_type=result['mime_type'],
        file_size=result['size'],
        file_type='document',
        relative_path=result['relative_path'],
    )
    db.session.add(upload)
    db.session.commit()

    # 转换（含图片提取）
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    conversion = convert_docx_with_images(result['path'], upload_folder)

    if not conversion['success']:
        return jsonify({'error': conversion['error']}), 500

    _log_audit(g.get('admin_user_id') or session.get('admin_user_id'), 'convert_docx',
               target_type='upload', target_id=upload.id,
               detail=f'file={result["original_name"]}')

    return jsonify({
        'html': conversion['html'],
        'images': conversion.get('images', []),
        'warnings': conversion.get('warnings', []),
        'upload': upload.to_dict(),
    }), 201


# ═══════════════════════════════════════════════════════════════
# 网站统计 API（管理后台）
# ═══════════════════════════════════════════════════════════════

@admin_bp.route('/api/admin/stats', methods=['GET'])
@admin_required
def api_stats():
    """获取网站统计数据"""
    from sqlalchemy import func
    from datetime import date, timedelta

    today = date.today()
    days = request.args.get('days', 30, type=int)
    days = min(days, 365)
    since = today - timedelta(days=days)

    stats = {}
    for event_type in ('page_view', 'tutorial_view', 'prompt_copy', 'resource_click'):
        total = SiteStat.query.filter(
            SiteStat.event_type == event_type,
            SiteStat.created_at >= since,
        ).count()
        unique_ips = (
            db.session.query(func.count(func.distinct(SiteStat.ip_address)))
            .filter(
                SiteStat.event_type == event_type,
                SiteStat.created_at >= since,
            )
            .scalar()
        ) or 0
        stats[event_type] = {'total': total, 'unique_ips': unique_ips}

    # 教程观看排行（top 20）
    top_tutorials = (
        db.session.query(SiteStat.event_key, func.count(SiteStat.id).label('cnt'))
        .filter(SiteStat.event_type == 'tutorial_view', SiteStat.created_at >= since)
        .group_by(SiteStat.event_key)
        .order_by(func.count(SiteStat.id).desc())
        .limit(20)
        .all()
    )
    stats['top_tutorials'] = [{'key': k, 'count': c} for k, c in top_tutorials if k]

    # 总体独立访客
    total_visitors = (
        db.session.query(func.count(func.distinct(SiteStat.ip_address)))
        .filter(SiteStat.created_at >= since)
        .scalar()
    ) or 0
    stats['total_visitors'] = total_visitors
    stats['period_days'] = days

    return jsonify({'stats': stats}), 200
