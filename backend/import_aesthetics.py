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

# ── 18个审美教程映射（文件大小(字节) → 标题 → 分类 → 扩展名） ──
# 文件大小用于精确匹配（宝塔面板上传时会重命名，中文文件名丢失）
TUTORIALS = [
    # Mplus语句（5个DOCX）
    (10772,    'BCH分析',                           'Mplus语句', '.docx'),
    (10839,    '多层次结构方程模型',                   'Mplus语句', '.docx'),
    (15843,    '带交互项的潜增长模型',                  'Mplus语句', '.docx'),
    (12743,    '单项+联合潜类别增长模型',               'Mplus语句', '.docx'),
    (10730,    '交叉滞后模型',                        'Mplus语句', '.docx'),
    # 拆解（6个PDF）
    (2609909,  '《心理科学进展》期刊分析',              '拆解', '.pdf'),
    (5596740,  '重点中文期刊标题、摘要、关键词分析',      '拆解', '.pdf'),
    (8365071,  '重点中文期刊方法结果分析',               '拆解', '.pdf'),
    (6689501,  '重点中文期刊基础信息分析',               '拆解', '.pdf'),
    (10203726, '重点中文期刊讨论分析',                  '拆解', '.pdf'),
    (19579742, '重点中文期刊引言分析',                  '拆解', '.pdf'),
    # 方法（6个PDF）
    (903530,   '交叉滞后+平行潜变量增长的引言及讨论写作思路（文献）', '方法', '.pdf'),
    (2743761,  '交叉滞后+平行潜变量增长的引言及讨论写作思路',       '方法', '.pdf'),
    (18676832, '心理学报审稿意见回复',                             '方法', '.pdf'),
    (7105662,  '英文核心论文选题及期刊选择',                       '方法', '.pdf'),
    (21119026, '英文核心期刊及发表流程介绍',                       '方法', '.pdf'),
    (21129977, '撰写英文文献综述',                                '方法', '.pdf'),
    # 素材（1个DOCX）
    (48789,    '英文论文摘要语料素材库',               '素材', '.docx'),
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

CARD_SUMMARIES = {
    10772: '提供BCH三步法核心语句框架，帮助新手完成潜类别在远端结果变量上的均值差异检验。',
    10839: '提供多层次结构方程模型语句，解决嵌套数据带来的标准误偏误问题，使结果更可靠。',
    15843: '提供带交互项的增长模型语句，帮助新手检验协变量间的调节效应如何影响个体发展轨迹的截距与斜率',
    12743: '提供单指标与并行过程潜类别增长模型语句，便于新手对比拟合指标并结合轨迹图形状与类别概率，初步筛选合理的增长轨迹类型。',
    10730: '提供交叉滞后模型代码，帮助新手考察纵向数据中变量间跨时间的优先性关系。',
    2609909: '通过数据视角梳理该刊发文热点，帮助新手明确选题偏好和投稿方向。',
    5596740: '拆解顶刊标题与摘要的常见结构，提供可直接套用的拟题和写作模板。',
    8365071: '拆解顶刊的图表呈现方式和统计汇报话术，规范新手的数据展示写法。',
    6689501: '提供顶刊的基础格式规范，避免因格式问题被退稿或反复修改。',
    10203726: '拆解顶刊如何将数据结果上升为理论贡献，帮助新手写出有深度的讨论。',
    19579742: '拆解顶刊“漏斗式”引言结构，提供段落逻辑模板，解决引言写作无从下笔的问题。',
    903530: '提供针对复杂动态模型的写作切入点，帮助新手清晰解释变量间的纵向关系。',
    2743761: '提供论述框架，帮助新手理顺纵向中介的写作逻辑。',
    18676832: '提供审稿意见回复的话术模板，帮助新手礼貌且有效地回应审稿人，提高复审通过率。',
    7105662: '教新手根据关键词匹配目标期刊，避免因选刊不当而延误发表。',
    21119026: '梳理从投稿到接收的完整流程，帮助新手了解各阶段时间节点，缓解等待焦虑。',
    21129977: '提供英文文献综述结构教学，帮助新手避免文献堆砌，写出有见地的综述。',
    48789: '汇总顶刊高频句式模板，方便新手直接替换生成地道、规范的英文摘要。',
}

uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app = create_app('production')


def find_file(size, ext):
    """在 uploads 目录中按文件大小+扩展名精确匹配（宝塔上传会重命名文件）"""
    if not os.path.isdir(uploads_dir):
        return None
    for fname in os.listdir(uploads_dir):
        fpath = os.path.join(uploads_dir, fname)
        if not os.path.isfile(fpath):
            continue
        fsize = os.path.getsize(fpath)
        fext = os.path.splitext(fname)[1].lower()
        if fsize == size and fext == ext:
            return fpath
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
        pdf_block = (
            f'<div class="pdf-viewer">'
            f'<iframe src="{url}" '
            f'style="width:100%;height:80vh;min-height:500px;border-radius:12px;border:1px solid var(--hairline);" '
            f'frameborder="0" allowfullscreen="true"></iframe>'
            f'</div>'
        )
        return pdf_block, []
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

    for size, title, category, ext in TUTORIALS:
        print(f'\n[{created+skipped+failed+1}/{len(TUTORIALS)}] {title}')
        try:
            # 2a) 按文件大小精确匹配
            filepath = find_file(size, ext)
            summary = CARD_SUMMARIES.get(size, title)
            if not filepath:
                print(f'  [SKIP] 未找到 {ext} 文件（大小: {size} 字节）')
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
                summary=summary,
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
                description=summary,
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


