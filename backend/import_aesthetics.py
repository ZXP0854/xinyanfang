"""
批量导入审美教程
扫描 static/uploads/ 中所有文件，匹配19个审美教程并导入
同步创建对应的审美卡片(Card)
用法: cd /www/wwwroot/xinyanfang/backend && source venv/bin/activate && python import_aesthetics.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mammoth
from app import create_app
from models import db, Tutorial, Card, Upload

# ── 19个审美教程映射 ──
TUTORIALS = [
    ('BCHfx', 'BCH分析', 'Mplus语句'),
    ('dccjgfcmx', '多层次结构方程模型', 'Mplus语句'),
    ('djhxdqzzmx', '带交互项的潜增长模型', 'Mplus语句'),
    ('dxlhqlbzzmx', '单项+联合潜类别增长模型', 'Mplus语句'),
    ('jczhmx', '交叉滞后模型', 'Mplus语句'),
    ('xlkxjzqkfx', '《心理科学进展》期刊分析', '拆解'),
    ('zdzwqkbt', '重点中文期刊标题、摘要、关键词分析', '拆解'),
    ('zdzwqkffjgfx', '重点中文期刊方法结果分析', '拆解'),
    ('zdzwqkjcxxfx', '重点中文期刊基础信息分析', '拆解'),
    ('zdzwqktlfx', '重点中文期刊讨论分析', '拆解'),
    ('zdzwqkyyfx', '重点中文期刊引言分析', '拆解'),
    ('Alfnkyht', 'AI赋能科研绘图', '方法'),
    ('jczhjhpxqblzzdyyjtlxzsl', '交叉滞后结合平行潜变量增长的引言及讨论写作思路文献', '方法'),
    ('jczhjhpxqzzdyyjtlxzsl', '交叉滞后结合平行潜变量增长的引言及讨论写作思路', '方法'),
    ('xlxbsgyjhf', '心理学报审稿意见回复', '方法'),
    ('ywhxlwxtjqkxz', '英文核心论文选题及期刊选择', '方法'),
    ('ywhxqkjfblcjs', '英文核心期刊及发表流程介绍', '方法'),
    ('ZxywWXZS', '撰写英文文献综述', '方法'),
    ('ywlwzyylsck', '英文论文摘要语料素材库', '素材'),
]

CATEGORY_ICONS = {
    'Mplus语句': 'fa-solid fa-code',
    '拆解': 'fa-solid fa-magnifying-glass-chart',
    '方法': 'fa-solid fa-flask',
    '素材': 'fa-solid fa-layer-group',
}

uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app = create_app('production')

def find_file(keyword):
    for fname in os.listdir(uploads_dir):
        if keyword.lower() in fname.lower():
            return os.path.join(uploads_dir, fname)
    with app.app_context():
        for u in Upload.query.all():
            if keyword.lower() in (u.original_name or '').lower():
                candidate = os.path.join(uploads_dir, u.filename)
                if os.path.exists(candidate):
                    return candidate
    return None

def convert_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ('.docx', '.doc'):
        with open(filepath, 'rb') as f:
            result = mammoth.convert_to_html(f)
        html = result.value.replace('src="images/', 'src="/static/uploads/images/')
        return html, result.messages
    elif ext == '.pdf':
        fname = os.path.basename(filepath)
        url = f'/static/uploads/{fname}'
        return f'<div class="tutorial-rich"><div class="rich-divider"></div><div class="rich-block"><div class="rich-text"><p>此内容为PDF文档，请下载后查看。</p><p><a href="{url}" class="btn-primary" target="_blank"><i class="fa-solid fa-download"></i> 下载PDF文件</a></p></div></div></div>', []
    return '', ['不支持的文件格式']

with app.app_context():
    # ── 1) 清理旧数据 ──
    # 删除所有旧教程（aesthetics类的）
    old_t = Tutorial.query.filter_by(category='aesthetics').all()
    for o in old_t:
        db.session.delete(o)
    # 删除所有旧卡片
    old_c = Card.query.all()
    for c in old_c:
        db.session.delete(c)
    db.session.commit()
    print(f'[CLEAN] 已清理 {len(old_t)} 条旧教程 + {len(old_c)} 张旧卡片')

    # ── 2) 导入教程 + 创建对应卡片 ──
    created = skipped = 0

    for keyword, title, category in TUTORIALS:
        filepath = find_file(keyword)
        if not filepath:
            print(f'[SKIP] 未找到: {keyword} → {title}')
            skipped += 1
            continue

        basename = os.path.basename(filepath)
        print(f'[FOUND] {basename} → {title} ({category})')

        html_content, msgs = convert_file(filepath)
        for m in (msgs or []):
            msg = m.message if hasattr(m, 'message') else str(m)
            print(f'  [INFO] {msg}')

        if not html_content.strip():
            print(f'  [SKIP] 转换结果为空')
            skipped += 1
            continue

        if '<div class="tutorial-rich"' not in html_content:
            html_content = f'<div class="tutorial-rich"><div class="rich-divider"></div><div class="rich-block"><div class="rich-text">{html_content}</div></div></div>'

        # 创建教程
        t = Tutorial(
            node_id=f'aes-tmp-{created+1}',
            title=title,
            summary=title,
            content=html_content,
            category='aesthetics',
            is_published=True,
        )
        db.session.add(t)
        db.session.flush()
        t.node_id = f'aes-{t.id}'
        created += 1
        print(f'  [CREATE] tutorial aes-{t.id}')

        # 为该教程创建对应的卡片
        c = Card(
            title=title,
            description='',
            icon=CATEGORY_ICONS.get(category, 'fa-solid fa-file'),
            tag=category,
            height=200,
            category=category,
            tutorial_title=title,
            sort_order=created,
            is_published=True,
        )
        db.session.add(c)
        print(f'  [CARD] #{created}')

    db.session.commit()

    # ── 3) 修正所有 node_id ──
    for t in Tutorial.query.filter(Tutorial.node_id.like('aes-tmp-%')).all():
        t.node_id = f'aes-{t.id}'
    db.session.commit()

    print(f'\n{"="*50}')
    print(f'导入: {created}  跳过: {skipped}')
    print(f'教程总计: {Tutorial.query.filter_by(category="aesthetics").count()}')
    print(f'卡片总计: {Card.query.count()}')
    print(f'{"="*50}')
    for t in Tutorial.query.filter_by(category='aesthetics').order_by(Tutorial.id).all():
        print(f'  [{t.node_id}] {t.title[:40]:40s} {len(t.content or ""):6d} chars')
