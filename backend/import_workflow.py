"""
批量导入科研流程教程（视频+图文）
扫描 static/uploads/ 中匹配的工作流文件，按字节大小精确匹配
DOCX → mammoth 转 HTML，MP4 → 下载链接

用法:
  cd /www/wwwroot/xinyanfang/backend && source venv/bin/activate && python import_workflow.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mammoth
from app import create_app
from models import db, Tutorial

# ── 工作流文件映射（文件大小 → node_id → 标题 → 类型） ──
WORKFLOW_FILES = [
    # DOCX 图文教程
    (2769099,  '1-1',   '文献全局图谱生成',           'docx'),
    (2215720,  '1-2',   '研究前沿选题与评估',          'docx'),
    (2203529,  '2-1',   '研究变量关系梳理',            'docx'),
    (737411,   '2-2-1', '实验设计方法（上）',          'docx'),
    (30854,    '2-2-1', '实验设计方法（下）',          'docx'),
    (1063537,  '2-2-2', '模型分析方法',                'docx'),
    # MP4 视频教程
    (221792028, '1-1',   '文献全局图谱生成',           'mp4'),
    (13331940,  '1-2',   '研究前沿选题与评估',          'mp4'),
    (16104013,  '2-1',   '研究变量关系梳理',            'mp4'),
    (16145159,  '2-2-1', '实验设计方法',               'mp4'),
    (11005045,  '2-2-2', '模型分析方法',               'mp4'),
]

uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app = create_app('production')


def find_file(size, ext):
    """按文件大小+扩展名精确匹配"""
    if not os.path.isdir(uploads_dir):
        return None
    for fname in os.listdir(uploads_dir):
        fpath = os.path.join(uploads_dir, fname)
        if not os.path.isfile(fpath):
            continue
        if os.path.getsize(fpath) == size and os.path.splitext(fname)[1].lower() == ext:
            return fpath
    return None


def convert_docx(filepath):
    """DOCX → HTML"""
    with open(filepath, 'rb') as f:
        result = mammoth.convert_to_html(f)
    html = result.value.replace('src="images/', 'src="/static/uploads/images/')
    for m in (result.messages or []):
        msg = m.message if hasattr(m, 'message') else str(m)
        if msg:
            print(f'    [mammoth] {msg}')
    return html


with app.app_context():
    # ── 按 node_id 分组收集内容 ──
    node_docx = {}   # node_id → [html_content, ...]
    node_videos = {} # node_id → [filename, ...]
    node_titles = {} # node_id → title

    found_docx = 0
    found_videos = 0
    skipped = 0

    for size, node_id, title, ftype in WORKFLOW_FILES:
        ext = '.docx' if ftype == 'docx' else '.mp4'
        filepath = find_file(size, ext)
        if not filepath:
            print(f'[SKIP] {node_id} {title} ({ftype}, {size} bytes) — 未找到')
            skipped += 1
            continue

        basename = os.path.basename(filepath)
        node_titles[node_id] = title

        if ftype == 'docx':
            print(f'[DOCX] {node_id} {title} ← {basename}')
            html = convert_docx(filepath)
            if html.strip():
                node_docx.setdefault(node_id, []).append(html)
                found_docx += 1
        else:
            print(f'[MP4]  {node_id} {title} ← {basename}')
            node_videos.setdefault(node_id, []).append(basename)
            found_videos += 1

    print(f'\n找到 {found_docx} 个 DOCX + {found_videos} 个 MP4，跳过 {skipped}')

    # ── 合并内容并更新 Tutorial ──
    updated = 0
    created = 0

    for node_id, title in sorted(node_titles.items()):
        parts = []

        # DOCX 内容（多个则合并）
        docx_list = node_docx.get(node_id, [])
        if docx_list:
            for i, html in enumerate(docx_list):
                if len(docx_list) > 1:
                    parts.append(f'<h4>第{i+1}部分</h4>')
                parts.append(html)

        # 视频下载链接
        video_list = node_videos.get(node_id, [])
        if video_list:
            vlinks = ''.join(
                f'<li><a href="/static/uploads/{v}" class="btn-primary" target="_blank">'
                f'<i class="fa-solid fa-download"></i> 下载视频：{v}</a></li>'
                for v in video_list
            )
            parts.append(
                f'<div class="tutorial-rich"><div class="rich-divider"></div>'
                f'<div class="rich-block"><div class="rich-text">'
                f'<h4>配套视频教程</h4><ul>{vlinks}</ul>'
                f'</div></div></div>'
            )

        full_html = '\n'.join(parts)
        if not full_html.strip():
            print(f'[WARN] {node_id} {title} — 无有效内容')
            continue

        # 包装（如果还没被包装）
        if '<div class="tutorial-rich"' not in full_html:
            full_html = (
                f'<div class="tutorial-rich"><div class="rich-divider"></div>'
                f'<div class="rich-block"><div class="rich-text">{full_html}</div></div></div>'
            )

        # 更新或创建 Tutorial
        t = Tutorial.query.filter_by(node_id=node_id, category='workflow').first()
        if t:
            t.content = full_html
            t.summary = title
            updated += 1
            print(f'[UPDATE] {node_id} {title} ({len(full_html)} chars)')
        else:
            t = Tutorial(
                node_id=node_id,
                title=title,
                summary=title,
                content=full_html,
                category='workflow',
                is_published=True,
            )
            db.session.add(t)
            created += 1
            print(f'[CREATE] {node_id} {title} ({len(full_html)} chars)')

    db.session.commit()

    print(f'\n{"=" * 55}')
    print(f'  更新: {updated}  新建: {created}  跳过: {skipped}')
    print(f'  工作流教程总数: {Tutorial.query.filter_by(category="workflow").count()}')
    print(f'{"=" * 55}')
