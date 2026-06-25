"""
批量导入审美教程
扫描 static/uploads/ 中所有文件，匹配19个审美教程并导入
用法: cd /www/wwwroot/xinyanfang/backend && source venv/bin/activate && python import_aesthetics.py
"""
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mammoth
from app import create_app
from models import db, Tutorial, Upload

# ── 19个审美教程映射 ──
# 格式: (原始文件名关键词, 教程标题, 分类)
TUTORIALS = [
    # ── Mplus语句 (5) ──
    ('BCHfx', 'BCH分析', 'Mplus语句'),
    ('dccjgfcmx', '多层次结构方程模型', 'Mplus语句'),
    ('djhxdqzzmx', '带交互项的潜增长模型', 'Mplus语句'),
    ('dxlhqlbzzmx', '单项+联合潜类别增长模型', 'Mplus语句'),
    ('jczhmx', '交叉滞后模型', 'Mplus语句'),

    # ── 拆解 (6) ──
    ('xlkxjzqkfx', '《心理科学进展》期刊分析', '拆解'),
    ('zdzwqkbt', '重点中文期刊标题、摘要、关键词分析', '拆解'),
    ('zdzwqkffjgfx', '重点中文期刊方法结果分析', '拆解'),
    ('zdzwqkjcxxfx', '重点中文期刊基础信息分析', '拆解'),
    ('zdzwqktlfx', '重点中文期刊讨论分析', '拆解'),
    ('zdzwqkyyfx', '重点中文期刊引言分析', '拆解'),

    # ── 方法 (7) ──
    ('Alfnkyht', 'AI赋能科研绘图', '方法'),
    ('jczhjhpxqblzzdyyjtlxzsl', '交叉滞后结合平行潜变量增长的引言及讨论写作思路文献', '方法'),
    ('jczhjhpxqzzdyyjtlxzsl', '交叉滞后结合平行潜变量增长的引言及讨论写作思路', '方法'),
    ('xlxbsgyjhf', '心理学报审稿意见回复', '方法'),
    ('ywhxlwxtjqkxz', '英文核心论文选题及期刊选择', '方法'),
    ('ywhxqkjfblcjs', '英文核心期刊及发表流程介绍', '方法'),
    ('ZxywWXZS', '撰写英文文献综述', '方法'),

    # ── 素材 (1) ──
    ('ywlwzyylsck', '英文论文摘要语料素材库', '素材'),
]

uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')

app = create_app('production')

def find_file(keyword):
    """在uploads目录中查找包含关键词的文件"""
    for fname in os.listdir(uploads_dir):
        if keyword.lower() in fname.lower():
            return os.path.join(uploads_dir, fname)
    # 也检查Upload表
    with app.app_context():
        uploads = Upload.query.all()
        for u in uploads:
            if keyword.lower() in (u.original_name or '').lower():
                return os.path.join(uploads_dir, u.filename)
    return None

def convert_file(filepath):
    """转换docx为HTML，PDF则返回下载链接"""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in ('.docx', '.doc'):
        try:
            with open(filepath, 'rb') as f:
                result = mammoth.convert_to_html(f)
            html = result.value
            # 图片路径修正
            html = html.replace('src="images/', 'src="/static/uploads/images/')
            return html, result.messages
        except Exception as e:
            return f'<p style="color:red;">文档转换失败: {e}</p>', [str(e)]
    elif ext == '.pdf':
        # PDF无法转换，提供下载链接
        fname = os.path.basename(filepath)
        url = f'/static/uploads/{fname}'
        return f'<div class="tutorial-rich"><div class="rich-divider"></div><div class="rich-block"><div class="rich-text"><p>此内容为PDF文档，请下载后查看。</p><p><a href="{url}" class="btn-primary" target="_blank"><i class="fa-solid fa-download"></i> 下载PDF文件</a></p></div></div></div>', []
    else:
        return '', ['不支持的文件格式']

with app.app_context():
    created = 0
    updated = 0
    skipped = 0

    for keyword, title, category in TUTORIALS:
        filepath = find_file(keyword)
        if not filepath:
            print(f'[SKIP] 未找到文件: {keyword} → {title}')
            skipped += 1
            continue

        basename = os.path.basename(filepath)
        print(f'[FOUND] {basename} → {title} ({category})')

        html_content, msgs = convert_file(filepath)
        if msgs:
            for m in msgs:
                if hasattr(m, 'message'):
                    print(f'  [WARN] {m.message}')
                else:
                    print(f'  [INFO] {m}')

        if not html_content.strip():
            print(f'  [SKIP] 转换结果为空')
            skipped += 1
            continue

        # 包裹在tutorial-rich容器中
        if not html_content.startswith('<div class="tutorial-rich"'):
            html_content = f'<div class="tutorial-rich"><div class="rich-divider"></div><div class="rich-block"><div class="rich-text">{html_content}</div></div></div>'

        # 更新或创建
        existing = Tutorial.query.filter_by(title=title, category='aesthetics').first()
        if existing:
            existing.content = html_content
            existing.summary = title
            existing.is_published = True
            updated += 1
            print(f'  [UPDATE]')
        else:
            t = Tutorial(
                node_id='',
                title=title,
                summary=title,
                content=html_content,
                category='aesthetics',
                is_published=True,
            )
            db.session.add(t)
            created += 1
            print(f'  [CREATE]')

    db.session.commit()

    print(f'\n{"="*50}')
    print(f'创建: {created}  更新: {updated}  跳过: {skipped}')
    print(f'总计 aesthetic 教程: {Tutorial.query.filter_by(category="aesthetics").count()}')
    print(f'{"="*50}')
    print('\n教程列表:')
    for t in Tutorial.query.filter_by(category='aesthetics').order_by(Tutorial.id).all():
        tag = t.title[:30]
        print(f'  [{t.id}] {tag:35s}  {len(t.content):6d} chars')
