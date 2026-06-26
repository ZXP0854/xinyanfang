"""
批量导入科研流程教程（第三、第五阶段）
扫描 static/uploads/ 中匹配的文件，按字节大小精确匹配
DOCX → mammoth 转 HTML，MP4/MOV → 内嵌播放器，PDF → 下载链接

用法:
  cd /www/wwwroot/xinyanfang/backend && source venv/bin/activate && python import_workflow_35.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mammoth
from app import create_app
from models import db, Tutorial

# ── 工作流文件映射（文件大小 → node_id → 标题 → 类型） ──
WORKFLOW_FILES = [
    # ═══ 第三阶段：数据收集 ═══
    # 3-1-1 常见的取样方法
    (80706822,  '3-1-1', '常见的取样方法',                'mp4'),   # 3-1-1SP.mp4
    (1121269,   '3-1-1', '常见的取样方法',                'docx'),  # 3-1-1TW.docx
    (5028926,   '3-1-1', '常见的取样方法',                'pdf'),   # WX-BIANLI.pdf
    (1553862,   '3-1-1', '常见的取样方法',                'pdf'),   # WX-FENCENG.pdf
    (129545,    '3-1-1', '常见的取样方法',                'pdf'),   # WX-GUNXUEQIU.pdf
    (741932,    '3-1-1', '常见的取样方法',                'pdf'),   # WX-JINGYANQUYANG.pdf
    (2719306,   '3-1-1', '常见的取样方法',                'pdf'),   # WX-ZHENGQUNQUYANG.pdf
    # 3-1-2 样本代表性评估及误区
    (90652227,  '3-1-2', '样本代表性评估及误区',           'mp4'),   # 3-1-2SP.mp4
    (869299,    '3-1-2', '样本代表性评估及误区',           'docx'),  # 3-1-2TW.docx
    # 3-2 样本量规划
    (52549763,  '3-2',   '样本量规划',                   'mov'),   # 3-2SP1.mov
    (66534555,  '3-2',   '样本量规划',                   'mov'),   # 3-2SP2.mov
    (105294219, '3-2',   '样本量规划',                   'mov'),   # 3-2SP3.mov
    (74789222,  '3-2',   '样本量规划',                   'mov'),   # 3-2SP4.mov
    (623282,    '3-2',   '样本量规划',                   'docx'),  # 3-2TW1.docx
    (1162767,   '3-2',   '样本量规划',                   'docx'),  # 3-2TW2.docx
    (707434,    '3-2',   '样本量规划',                   'docx'),  # 3-2TW3.docx
    (2788006,   '3-2',   '样本量规划',                   'docx'),  # 3-2TW4.docx
    # 3-3 知情同意与伦理规范
    (70131326,  '3-3',   '知情同意与伦理规范',             'mp4'),   # 3-3SP2.mp4
    (2495631,   '3-3',   '知情同意与伦理规范',             'docx'),  # 3-3TW1.docx
    (8121627,   '3-3',   '知情同意与伦理规范',             'docx'),  # 3-3TW2.docx

    # ═══ 第五阶段：论文撰写 ═══
    # 5-1-1 研究结果的呈现方式
    (30451194,  '5-1-1', '研究结果的呈现方式',             'mp4'),   # 5-1-1SP1.mp4
    (71722204,  '5-1-1', '研究结果的呈现方式',             'mp4'),   # 5-1-1SP2.mp4
    (59306654,  '5-1-1', '研究结果的呈现方式',             'mp4'),   # 5-1-1SP3.mp4
    (51075982,  '5-1-1', '研究结果的呈现方式',             'mp4'),   # 5-1-1SP4.mp4
    (41965519,  '5-1-1', '研究结果的呈现方式',             'mp4'),   # 5-1-1SP5.mp4
    (459741,    '5-1-1', '研究结果的呈现方式',             'docx'),  # 5-1-1TW1.docx
    (1381002,   '5-1-1', '研究结果的呈现方式',             'docx'),  # 5-1-1TW2.docx
    (1301482,   '5-1-1', '研究结果的呈现方式',             'docx'),  # 5-1-1TW3.docx
    (1049333,   '5-1-1', '研究结果的呈现方式',             'docx'),  # 5-1-1TW4.docx
    (983374,    '5-1-1', '研究结果的呈现方式',             'docx'),  # 5-1-1TW5.docx
    # 5-1-2 研究结果的数据解读
    (191478033, '5-1-2', '研究结果的数据解读',             'mp4'),   # 5-1-2SP.mp4
    (1496867,   '5-1-2', '研究结果的数据解读',             'docx'),  # 5-1-2TW.docx
    # 5-2 研究报告的个性化撰写
    (51779614,  '5-2',   '研究报告的个性化撰写',           'mp4'),   # 5-2SP.mp4
    (205179,    '5-2',   '研究报告的个性化撰写',           'docx'),  # 5-2TW.docx
    # 5-3 研究报告的格式修订
    (7130121,   '5-3',   '研究报告的格式修订',             'mp4'),   # 5-3SP.mp4
    (2406783,   '5-3',   '研究报告的格式修订',             'docx'),  # 5-3TW.docx
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
        if os.path.getsize(fpath) == size and os.path.splitext(fname)[1].lower() == ('.' + ext if not ext.startswith('.') else ext):
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
    node_docx = {}    # node_id → [html_content, ...]
    node_videos = {}  # node_id → [(filename, is_mov), ...]
    node_pdfs = {}    # node_id → [(filename, title_index), ...]  supplementary PDFs
    node_titles = {}  # node_id → title

    found_docx = 0
    found_videos = 0
    found_pdfs = 0
    skipped = 0

    for size, node_id, title, ftype in WORKFLOW_FILES:
        ext_map = {'docx': '.docx', 'mp4': '.mp4', 'mov': '.mov', 'pdf': '.pdf'}
        ext = ext_map.get(ftype, '.' + ftype)
        filepath = find_file(size, ext.lstrip('.'))
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
        elif ftype in ('mp4', 'mov'):
            print(f'[{ftype.upper()}]  {node_id} {title} ← {basename}')
            node_videos.setdefault(node_id, []).append((basename, ftype == 'mov'))
            found_videos += 1
        elif ftype == 'pdf':
            print(f'[PDF]  {node_id} {title} ← {basename}')
            node_pdfs.setdefault(node_id, []).append(basename)
            found_pdfs += 1

    print(f'\n找到 {found_docx} 个 DOCX + {found_videos} 个视频 + {found_pdfs} 个 PDF，跳过 {skipped}')

    # ── 合并内容并更新 Tutorial ──
    updated = 0
    created = 0

    for node_id, title in sorted(node_titles.items()):
        parts = []

        # 视频内嵌播放器（标题下方最前面）
        video_list = node_videos.get(node_id, [])
        if video_list:
            vtags = ''.join(
                f'<video controls preload="metadata" '
                f'style="width:100%;max-width:100%;border-radius:12px;display:block;margin-bottom:12px;" '
                f'poster="/static/uploads/{v.replace(".mp4","").replace(".mov","")}.jpg">'
                f'<source src="/static/uploads/{v}" type="video/mp4">'
                f'</video>'
                for v, is_mov in video_list
            )
            parts.append(
                f'<h4><i class="fa-solid fa-play"></i> 配套视频教程</h4>'
                f'{vtags}'
                f'<div class="rich-divider"></div>'
            )

        # DOCX 图文内容
        docx_list = node_docx.get(node_id, [])
        if docx_list:
            for i, html in enumerate(docx_list):
                if len(docx_list) > 1:
                    parts.append(f'<h4>第{i+1}部分</h4>')
                parts.append(html)

        # 补充参考文献（PDF 下载链接）
        pdf_list = node_pdfs.get(node_id, [])
        if pdf_list:
            pdf_links = ''.join(
                f'<li><a href="/static/uploads/{p}" target="_blank" class="text-link">'
                f'<i class="fa-solid fa-file-pdf"></i> {p}</a></li>'
                for p in pdf_list
            )
            parts.append(
                f'<div class="rich-divider"></div>'
                f'<h4><i class="fa-solid fa-book"></i> 参考文献推荐</h4>'
                f'<ul>{pdf_links}</ul>'
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
