"""
批量导入审美教程（v3 — 健壮版）
扫描 static/uploads/ 中的【CJ】【FF】【Mplus】【SC】文件
匹配18个审美教程并导入，同步创建统一规格的审美卡片

用法:
  # 先通过宝塔面板将 F:\压缩\【科研审美】\ 中所有文件上传到
  # /www/wwwroot/xinyanfang/backend/static/uploads/
  # 然后执行:
  cd /www/wwwroot/xinyanfang/backend && source venv/bin/activate && python import_aesthetics.py
"""
import os, sys, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mammoth
from app import create_app
from models import db, Tutorial, Card, Upload

# ── 18个审美教程映射（关键词 → 标题 → 分类） ──
TUTORIALS = [
    # Mplus语句（5个DOCX）
    ('BCHfx',               'BCH分析',                                              'Mplus语句'),
    ('dccjgfcmx',           '多层次结构方程模型',                                    'Mplus语句'),
    ('djhxdqzzmx',          '带交互项的潜增长模型',                                  'Mplus语句'),
    ('dx+lhqlbzzmx',        '单项+联合潜类别增长模型',                               'Mplus语句'),
    ('jczhmx',              '交叉滞后模型',                                          'Mplus语句'),
    # 拆解（6个PDF）
    ('xlkxjzqkfx',          '《心理科学进展》期刊分析',                              '拆解'),
    ('zdzwqkbt',            '重点中文期刊标题、摘要、关键词分析',                     '拆解'),
    ('zdzwqkffjgfx',        '重点中文期刊方法结果分析',                               '拆解'),
    ('zdzwqkjcxxfx',        '重点中文期刊基础信息分析',                               '拆解'),
    ('zdzwqktlfx',          '重点中文期刊讨论分析',                                  '拆解'),
    ('zdzwqkyyfx',          '重点中文期刊引言分析',                                  '拆解'),
    # 方法（6个PDF）
    ('jczhjhpxqblzzdyyjtlxzsl', '交叉滞后+平行潜变量增长的引言及讨论写作思路（文献）', '方法'),
    ('jczhjhpxqzzdyyjtlxzsl',   '交叉滞后+平行潜变量增长的引言及讨论写作思路',         '方法'),
    ('xlxbsgyjhf',              '心理学报审稿意见回复',                               '方法'),
    ('ywhxlwxtjqkxz',           '英文核心论文选题及期刊选择',                         '方法'),
    ('ywhxqkjfblcjs',           '英文核心期刊及发表流程介绍',                         '方法'),
    ('ZxywWXZS',                '撰写英文文献综述',                                  '方法'),
    # 素材（1个DOCX）
    ('ywlwzyylsck',         '英文论文摘要语料素材库',                                 '素材'),
]

# ── 分类 → 图标 + 卡片配图 ──
CATEGORY_META = {
    'Mplus语句': {
        'icon': 'fa-solid fa-code',
        'image': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&h=300&fit=crop',
    },
    '拆解': {
        'icon': 'fa-solid fa-magnifying-glass-chart',
        'image': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400&h=300&fit=crop',
    },
    '方法': {
        'icon': 'fa-solid fa-flask',
        'image': 'https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400&h=300&fit=crop',
    },
    '素材': {
        'icon': 'fa-solid fa-layer-group',
        'image': 'https://images.unsplash.com/photo-1455390582262-044cdead277a?w=400&h=300&fit=crop',
    },
}

CARD_HEIGHT = 220  # 统一卡片高度

uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app = create_app('production')


def find_file(keyword):
    """在 uploads 目录中搜索匹配文件（忽略大小写）"""
    if not os.path.isdir(uploads_dir):
        return None
    for fname in os.listdir(uploads_dir):
        if keyword.lower() in fname.lower():
            return os.path.join(uploads_dir, fname)
    return None


def convert_file(filepath):
    """将 docx/pdf 转换为 HTML 内容"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ('.docx', '.doc'):
        with open(filepath, 'rb') as f:
            result = mammoth.convert_to_html(f)
        html = result.value.replace('src="images/', 'src="/static/uploads/images/')
        return html, result.messages
    elif ext == '.pdf':
        fname = os.path.basename(filepath)
        url = f'/static/uploads/{fname}'
        download_block = (
            f'<p>此内容为PDF文档，请下载后查看。</p>'
            f'<p><a href="{url}" class="btn-primary" target="_blank">'
            f'<i class="fa-solid fa-download"></i> 下载PDF文件</a></p>'
        )
        return download_block, []
    return '', ['不支持的文件格式']


with app.app_context():
    # ═══════════════════════════════════════════════════
    # 1) 清理旧数据
    # ═══════════════════════════════════════════════════
    old_t = Tutorial.query.filter_by(category='aesthetics').all()
    for o in old_t:
        db.session.delete(o)
    old_c = Card.query.all()
    for c in old_c:
        db.session.delete(c)
    db.session.commit()
    print(f'[CLEAN] 删除了 {len(old_t)} 条旧教程 + {len(old_c)} 张旧卡片')

    # ═══════════════════════════════════════════════════
    # 2) 逐个导入（独立 try/except，失败不中断）
    # ═══════════════════════════════════════════════════
    created = 0
    skipped = 0
    failed = 0
    errors = []

    for keyword, title, category in TUTORIALS:
        print(f'\n[{created+skipped+failed+1}/{len(TUTORIALS)}] {title}')
        try:
            # 2a) 查找文件
            filepath = find_file(keyword)
            if not filepath:
                print(f'  [SKIP] 未找到文件（关键词: {keyword}）')
                skipped += 1
                continue

            basename = os.path.basename(filepath)
            print(f'  [FOUND] {basename}')

            # 2b) 转换文件
            html_body, msgs = convert_file(filepath)
            for m in (msgs or []):
                msg = m.message if hasattr(m, 'message') else str(m)
                if msg:
                    print(f'  [INFO] mammoth: {msg}')

            if not html_body.strip():
                print(f'  [SKIP] 转换结果为空')
                skipped += 1
                continue

            # 2c) 包装为 tutorial-rich 格式
            if '<div class="tutorial-rich"' not in html_body:
                html_body = (
                    f'<div class="tutorial-rich"><div class="rich-divider"></div>'
                    f'<div class="rich-block"><div class="rich-text">{html_body}</div></div></div>'
                )

            # 2d) 创建教程记录
            t = Tutorial(
                node_id=f'aes-tmp-{created+1}',
                title=title,
                summary=title,
                content=html_body,
                category='aesthetics',
                is_published=True,
            )
            db.session.add(t)
            db.session.flush()
            t.node_id = f'aes-{t.id}'

            # 2e) 创建对应卡片
            meta = CATEGORY_META.get(category, {'icon': 'fa-solid fa-file', 'image': ''})
            c = Card(
                title=title,
                description='',
                icon=meta['icon'],
                tag=category,
                height=CARD_HEIGHT,
                image_url=meta['image'],
                category=category,
                tutorial_title=title,
                sort_order=created + 1,
                is_published=True,
            )
            db.session.add(c)

            # 2f) 每对提交一次（部分成功也保留）
            db.session.commit()
            created += 1
            print(f'  [OK] tutorial {t.node_id} + card #{c.id}')

        except Exception as e:
            db.session.rollback()
            failed += 1
            err_msg = f'{title}: {e}'
            errors.append(err_msg)
            print(f'  [FAIL] {err_msg}')
            traceback.print_exc()

    # ═══════════════════════════════════════════════════
    # 3) 收尾：修正残留的临时 node_id
    # ═══════════════════════════════════════════════════
    for t in Tutorial.query.filter(Tutorial.node_id.like('aes-tmp-%')).all():
        t.node_id = f'aes-{t.id}'
    db.session.commit()

    # ═══════════════════════════════════════════════════
    # 4) 打印总结
    # ═══════════════════════════════════════════════════
    print(f'\n{"=" * 65}')
    print(f'  导入结果:  {created} 成功  |  {skipped} 跳过  |  {failed} 失败')
    if errors:
        print(f'  失败明细:')
        for e in errors:
            print(f'    ✗ {e}')
    print(f'  教程总数:  {Tutorial.query.filter_by(category="aesthetics").count()}')
    print(f'  卡片总数:  {Card.query.count()}')
    print(f'{"=" * 65}')
    for t in Tutorial.query.filter_by(category='aesthetics').order_by(Tutorial.id).all():
        print(f'  [{t.node_id}] {t.title[:45]:45s} {len(t.content or ""):7d} chars')
    for c in Card.query.order_by(Card.sort_order).all():
        img = 'Y' if c.image_url else 'N'
        print(f'  [CARD #{c.id}] {c.title[:45]:45s} tag={c.tag} img={img}')
