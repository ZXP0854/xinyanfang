"""
数据初始化脚本
从现有前端代码中解析硬编码内容，导入数据库
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, init_db
from models import db, Tutorial, Resource, Card

app = create_app(os.environ.get('FLASK_ENV', 'development'))


def seed_admin():
    """确保管理员账号存在"""
    from models import User
    if User.query.filter_by(username='admin').first():
        print('[OK] Admin account already exists')
        return
    admin = User(username='admin', display_name='管理员', is_active=True)
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    print('[OK] Admin account created (admin / admin123)')


def seed_tutorials():
    """导入教程节点数据"""
    if Tutorial.query.first():
        print('[SKIP] Tutorials already seeded')
        return

    tutorials = [
        ('1-1', '文献全局图谱生成', '文献堆积却理不清脉络关联，用Connected Papers一键生成核心文献关联图谱，配合Zotero高效管理，快速构建领域知识框架，看清研究版图。'),
        ('1-2', '研究前沿选题与评估', '研究初期方向模糊、前沿信息分散难抓，用ChatGPT5快速梳理近五年心理学研究前沿动态并辅助生成选题，从创新性和可行性多维度评估，帮你精准锁定有价值的研究方向。'),
        ('2-1', '研究变量关系梳理', '心理学变量关系复杂抽象、难以形成清晰框架，结合AMOS与Deepseek绘制关系图并自动评估模型合理性，把模糊假设变成直观的研究蓝图。'),
        ('2-2-1', '实验设计方法', '心理学实验设计方法众多却选不准，系统对比6-8种经典设计并附核心期刊文献案例，再用ChatGPT根据你的选题智能推荐最优方案，设计决策有据可依。'),
        ('2-2-2', '模型分析方法', '心理学研究模型分析方法眼花缭乱、适用场景不清，梳理前沿模型的特点与场景，借助ChatGPT/Gemini匹配研究特征，找到最合适的分析路径，不再无从下手。'),
        ('3-1-1', '常见的取样方法', '取样方法选择缺乏文献支撑，用Elicit快速定位各方法的心理学研究权威文献，系统对比特点与适用场景，让取样决策有理有据。'),
        ('3-1-2', '样本代表性评估及误区', '样本代表性不足却难以量化评估，借助Gemini辅助SPSS完成卡方拟合优度检验，自动识别数据偏差，确保样本质量经得起学术推敲。'),
        ('3-2', '样本量规划', '心理学实验样本量算不准、纵向流失没预案，用G*power完成功效分析与流失补偿，再用ChatGPT生成R代码，让样本规划科学高效。'),
        ('3-3', '知情同意与伦理规范', '心理学研究伦理审查流程繁琐易遗漏，用Gemini/ChatGPT起草标准知情同意书，配合Qualtrics实现匿名化与合规跳转，全程守护研究伦理底线。'),
        ('4-1', '变量量表选择', '测量工具分散难找、筛选耗时，汇总全网心理学量表库资源，手把手教你快速检索与筛选，精准匹配研究需求的量表。'),
        ('4-2-1', '问卷类的数据收集', '问卷发放回收效率低、管理混乱，从纸质问卷排版到EpiData录入，再到见数平台线上编制发布，覆盖心理学问卷数据收集的全流程。'),
        ('4-2-2', '行为实验数据收集—Psychopy', '心理学行为实验编程门槛高、搭建周期长，借助ChatGPT编写PsychoPy代码并生成实验材料，通过见数平台实现线上部署，让实验搭建不再困难。'),
        ('4-2-3', '行为实验数据收集—CEST、Gorilla和Pavlovia', '在线心理学实验平台众多却无从选择，对比CEST、Gorilla和Pavlovia三大平台，从搭建到运行全流程演示，找到最适合你的方案。'),
        ('4-3', '数据清洗与描述性统计', '原始数据脏乱、清洗步骤繁琐，用SPSS完成缺失值处理、插补与描述统计，再借助Dingo智能清洗，为后续分析准备好干净数据。'),
        ('4-4-1', '信效度检验', '信效度检验步骤繁琐、软件操作复杂，用ChatSPSS和AI对话式完成信效度分析，自动生成检验报告，让测量质量评估轻松搞定。'),
        ('4-4-2', '共同方法偏差识别', '共同方法偏差隐蔽难察觉，用ChatGPT/Gemini辅助识别数据中的系统性偏差，以共同方法偏差为例给出处理方案，提升研究严谨性。'),
        ('4-5-1', '基础统计分析方法——中介分析', '中介分析批量处理耗时费力，借助ChatGPT/Gemini实现批量中介分析，从模型设定到结果输出一气呵成，大幅提升心理学研究统计分析效率。'),
        ('4-5-2', '高级统计分析方法——Mplus模型和R语言', '高级统计方法上手难、软件总报错，用ChatGPT辅助Mplus模型选择与结果解读，配合Cursor生成R代码分析多层线性模型，攻克心理学研究中的高阶统计分析。'),
        ('5-1-1', '研究结果的呈现方式', '图表制作反复调整，绘制费时且不够专业，用Gemini、Cursor或Claude等AI工具自动生成结果图表，精准表达心理学研究中的变量关系与实验逻辑，让结果可视化变得直观清晰。'),
        ('5-1-2', '研究结果的数据解读', '数据解读缺乏思路、表述不规范，用Gemini生成图表并自动撰写符合心理学学术规范的数据解读，从数字到文字无缝衔接，让结果陈述更加规范有力。'),
        ('5-2', '研究报告的个性化撰写', '写作模板千篇一律、期刊风格难把握，用ChatGPT检索目标心理学期刊文献并生成个性化写作模板，匹配期刊特色，让研究报告撰写更有针对性。'),
        ('5-3', '研究报告的格式修订', '论文格式反复修改、细节易遗漏，用Gemini一键识别并修正格式问题，从引用规范到排版细节全面把关，让论文格式符合心理学论文发表要求。'),
    ]

    for node_id, title, desc in tutorials:
        content = f'<div class="tutorial-rich"><div class="rich-divider"></div><div class="rich-block"><div class="rich-text"><h4>{title}</h4><p>{desc}</p></div></div></div>'
        t = Tutorial(node_id=node_id, title=title, summary=desc[:500], content=content, category="workflow", is_published=True)
        db.session.add(t)

    db.session.commit()
    print(f'[OK] Seeded {len(tutorials)} tutorials')


def seed_resources():
    """导入科研资源数据"""
    if Resource.query.first():
        print('[SKIP] Resources already seeded')
        return

    resources = [
        # ── 文献与知识库 ──
        {'module': '文献与知识库', 'name': '中国知网 (CNKI)', 'description': '国内最核心的中文学术文献数据库，收录期刊、博硕士论文、会议论文等。', 'link_type': 'external', 'link_value': 'https://www.cnki.net'},
        {'module': '文献与知识库', 'name': '万方数据知识服务平台', 'description': '综合性中文文献数据库，涵盖期刊、学位论文、会议论文等。', 'link_type': 'external', 'link_value': 'https://www.wanfangdata.com.cn'},
        {'module': '文献与知识库', 'name': '维普中文期刊服务平台', 'description': '中文科技期刊全文数据库。', 'link_type': 'external', 'link_value': 'http://qikan.cqvip.com'},
        {'module': '文献与知识库', 'name': '中国心理科学数据中心', 'description': '中国科学院心理研究所与ChinaXiv共建，预印本平台。', 'link_type': 'external', 'link_value': 'https://psych.chinaxiv.org'},
        {'module': '文献与知识库', 'name': '国家哲学社会科学文献中心', 'description': '国家级社科文献平台。', 'link_type': 'external', 'link_value': 'https://www.nssd.cn'},
        {'module': '文献与知识库', 'name': '《心理学报》', 'description': '中国心理学会和中科院心理所主办，我国最高水平的心理学综合性期刊。', 'link_type': 'external', 'link_value': 'http://journal.psych.ac.cn'},
        {'module': '文献与知识库', 'name': '《心理科学》', 'description': '中国心理学会主办，华东师范大学承办的综合性学术期刊。', 'link_type': 'external', 'link_value': 'https://jps.ecnu.edu.cn'},
        {'module': '文献与知识库', 'name': '《心理科学进展》', 'description': '中科院心理所主办，主要刊登心理学各领域综述与评论。', 'link_type': 'external', 'link_value': 'https://journal.psych.ac.cn/xlkxjz'},
        {'module': '文献与知识库', 'name': '《心理发展与教育》', 'description': '北京师范大学主办，国内唯一的发展与教育心理学专业刊物。', 'link_type': 'external', 'link_value': 'https://devpsy.bnu.edu.cn'},
        {'module': '文献与知识库', 'name': '《中国临床心理学杂志》', 'description': '中国心理卫生协会和中南大学主办。', 'link_type': 'external', 'link_value': 'http://www.clinicalpsychojournal.com'},
        {'module': '文献与知识库', 'name': '《心理与行为研究》', 'description': '天津师范大学主办。', 'link_type': 'external', 'link_value': 'https://psybeh.tjnu.edu.cn'},
        {'module': '文献与知识库', 'name': '《心理学探新》', 'description': '江西师范大学主办，涵盖理论、认知、应用心理学等。', 'link_type': 'external', 'link_value': 'https://psytxjx.jxnu.edu.cn'},
        {'module': '文献与知识库', 'name': '《应用心理学》', 'description': '浙江省心理学会主办。', 'link_type': 'external', 'link_value': 'https://www.appliedpsy.cn'},
        {'module': '文献与知识库', 'name': 'PsyArXiv', 'description': '心理学开放获取预印本平台，快速传播最新研究。', 'link_type': 'external', 'link_value': 'https://psyarxiv.com'},
        {'module': '文献与知识库', 'name': 'PubMed', 'description': '美国国家医学图书馆的免费生物医学文献数据库，含大量行为科学与精神病学文献。', 'link_type': 'external', 'link_value': 'https://pubmed.ncbi.nlm.nih.gov'},
        {'module': '文献与知识库', 'name': 'PubScholar', 'description': '中科院推出的公益学术平台。', 'link_type': 'external', 'link_value': 'https://pubscholar.cn'},
        {'module': '文献与知识库', 'name': 'DOAJ', 'description': '全球开放获取期刊索引，可按学科筛选心理学OA期刊。', 'link_type': 'external', 'link_value': 'https://doaj.org'},
        {'module': '文献与知识库', 'name': 'PLOS ONE', 'description': '开放获取综合期刊，发表大量心理学研究。', 'link_type': 'external', 'link_value': 'https://journals.plos.org/plosone'},
        # ── 工具与软件库 ──
        {'module': '工具与软件库', 'name': 'PsychoPy', 'description': '开源的心理学实验刺激呈现与编制软件，基于Python构建，支持文本、图片、语音、视频等多种刺激类型，可与脑电、眼动、磁共振设备对接。', 'link_type': 'external', 'link_value': 'https://www.psychopy.org'},
        {'module': '工具与软件库', 'name': 'Psychtoolbox', 'description': '基于MATLAB的开源工具包，用于精确的视觉/听觉刺激呈现和行为实验控制，适合有编程基础的研究者。', 'link_type': 'external', 'link_value': 'http://psychtoolbox.org'},
        {'module': '工具与软件库', 'name': 'jsPsych', 'description': '基于JavaScript的在线实验框架，用于在浏览器中运行行为实验，适合在线数据收集。', 'link_type': 'external', 'link_value': 'https://www.jspsych.org'},
        {'module': '工具与软件库', 'name': 'Gorilla', 'description': '基于浏览器的在线实验与问卷构建平台，无需编程经验即可设计复杂实验。', 'link_type': 'external', 'link_value': 'https://gorilla.sc'},
        {'module': '工具与软件库', 'name': 'Inquisit', 'description': '专业的认知与神经心理学测试管理平台，内置大量标准化任务模板。', 'link_type': 'external', 'link_value': 'https://www.millisecond.com'},
        {'module': '工具与软件库', 'name': 'G*Power', 'description': '统计检验力分析与样本量估算的免费工具。', 'link_type': 'external', 'link_value': 'https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower'},
        {'module': '工具与软件库', 'name': 'SPSS', 'description': '社会科学界最主流的统计分析软件，涵盖数据管理、描述统计、推断统计等功能。', 'link_type': 'external', 'link_value': 'https://www.ibm.com/products/spss-statistics'},
        {'module': '工具与软件库', 'name': 'R / RStudio', 'description': '免费开源的统计编程语言与环境，拥有庞大的心理统计包生态。', 'link_type': 'external', 'link_value': 'https://www.r-project.org'},
        {'module': '工具与软件库', 'name': 'Mplus', 'description': '潜变量建模与结构方程模型的专业软件，支持验证性因素分析、路径分析、多层模型等。', 'link_type': 'external', 'link_value': 'https://www.statmodel.com'},
        {'module': '工具与软件库', 'name': 'JASP', 'description': '免费开源的统计软件，提供友好的图形界面，同时支持频率学派与贝叶斯统计。', 'link_type': 'external', 'link_value': 'https://jasp-stats.org'},
        {'module': '工具与软件库', 'name': 'Python (NumPy/Pandas/SciPy/Matplotlib)', 'description': '通用编程语言，搭配科学计算库可实现数据处理、统计分析和专业级可视化。', 'link_type': 'external', 'link_value': 'https://www.python.org'},
        {'module': '工具与软件库', 'name': 'Zotero', 'description': '免费开源的文献管理工具，支持浏览器插件自动抓取元数据、Word/LibreOffice/Google Docs插件、9000+引用格式。', 'link_type': 'external', 'link_value': 'https://www.zotero.org'},
        {'module': '工具与软件库', 'name': 'PsyToolkit', 'description': '免费的在线心理学实验与问卷平台，内置100+经过同行评议的量表库和实验库。', 'link_type': 'external', 'link_value': 'https://www.psytoolkit.org'},
        {'module': '工具与软件库', 'name': '问卷星', 'description': '国内最主流的在线问卷调查平台之一，支持自助设计问卷、回收答卷、数据统计分析等功能，可直接下载Excel/SPSS格式数据。', 'link_type': 'external', 'link_value': 'https://www.wjx.cn'},
        {'module': '工具与软件库', 'name': '问卷网', 'description': '国内常用的在线调研与数据收集平台。', 'link_type': 'external', 'link_value': 'https://www.wenjuan.com'},
        {'module': '工具与软件库', 'name': '乐调查', 'description': '在线调研与问卷平台。', 'link_type': 'external', 'link_value': 'https://www.lediaocha.com'},
        {'module': '工具与软件库', 'name': '金数据', 'description': '国内数据收集平台，支持多种题型、多渠道发布和可视化报告。', 'link_type': 'external', 'link_value': 'https://jinshuju.net'},
        {'module': '工具与软件库', 'name': 'ODK (Open Data Kit)', 'description': '开源的移动数据收集平台，支持自定义表单和多媒体数据采集。', 'link_type': 'external', 'link_value': 'https://getodk.org'},
        # ── 量表与测量资源 ──
        {'module': '量表与测量资源', 'name': 'OBHRM百科', 'description': '提供中英文量表，包括信效度、计分方式、文献来源，适合论文写作、规范量表获取。', 'link_type': 'external', 'link_value': 'http://obhrm.net'},
        {'module': '量表与测量资源', 'name': 'sup量表网', 'description': '量表数量多，支持"求助获取"。注意：网站资源由用户上传，质量不稳定。', 'link_type': 'external', 'link_value': 'https://www.suplb.cn'},
        {'module': '量表与测量资源', 'name': 'Psychological Scales & Instruments Database', 'description': '英文量表数据库，提供文献与信效度信息，适合查找英文原版量表。', 'link_type': 'external', 'link_value': 'https://db.arabpsychology.com'},
        {'module': '量表与测量资源', 'name': 'NovoPsych Assessment Library', 'description': '在线测评平台，提供结果解释与报告，适合自测、实验或教学使用。', 'link_type': 'external', 'link_value': 'https://novopsych.com/assessments'},
        {'module': '量表与测量资源', 'name': '量表库 (floating.cn)', 'description': '量表自测网站，提供多种心理测评工具。', 'link_type': 'external', 'link_value': 'http://www.floating.cn/home/index'},
        {'module': '量表与测量资源', 'name': 'Psychology Tools（主站）', 'description': '英文量表及治疗资源网站，提供循证心理治疗相关量表与工作表。', 'link_type': 'external', 'link_value': 'https://www.psychologytools.com'},
        {'module': '量表与测量资源', 'name': '常笑医学网·医学量表', 'description': '医学量表在线评估与计算平台，侧重于临床医学领域。', 'link_type': 'external', 'link_value': 'https://www.cxmed.cn/ms.html'},
        {'module': '量表与测量资源', 'name': '心理量表（心理学网）', 'description': '提供多种心理量表在线测试，上层网站为心理学网。', 'link_type': 'external', 'link_value': 'https://scale.xinlixue.cn'},
        {'module': '量表与测量资源', 'name': 'Psychology Tools（测量工具子站）', 'description': '英文量表测量网站，提供在线心理测试与评估工具。', 'link_type': 'external', 'link_value': 'https://psychology-tools.com'},
        {'module': '量表与测量资源', 'name': 'Open-Source Psychometrics Project', 'description': '开源人格测量项目，提供多种人格测试及开源数据集，适合研究与教学使用。', 'link_type': 'external', 'link_value': 'https://openpsychometrics.org'},
        # ── 公开数据集 ──
        {'module': '公开数据集', 'name': 'World Database of Happiness', 'description': '世界幸福数据库，收录全球幸福感相关研究与测量工具。', 'link_type': 'external', 'link_value': 'http://worlddatabaseofhappiness.eur.nl'},
        {'module': '公开数据集', 'name': '心理科学数据银行', 'description': '由科学数据银行（ScienceDB）和中国科学院心理研究所合作共建的心理学开放数据平台，专注于心理科学数据的发布与共享。', 'link_type': 'external', 'link_value': 'https://www.scidb.cn/psych'},
        {'module': '公开数据集', 'name': 'OpenNeuro', 'description': '免费的神经影像数据存储与共享平台，支持MRI/MEG/EEG等BIDS标准数据，是BRAIN Initiative指定的数据存档平台。', 'link_type': 'external', 'link_value': 'https://openneuro.org'},
        {'module': '公开数据集', 'name': 're3data.org', 'description': '全球研究数据存储库注册平台，可按学科筛选心理学相关数据集。', 'link_type': 'external', 'link_value': 'https://www.re3data.org/'},
        {'module': '公开数据集', 'name': 'SNAP', 'description': '斯坦福大学提供的社交网络与信息网络数据集。', 'link_type': 'external', 'link_value': 'http://snap.stanford.edu/data'},
    ]

    for i, r in enumerate(resources):
        db.session.add(Resource(
            module=r['module'],
            name=r['name'],
            description=r.get('description', ''),
            link_type=r['link_type'],
            link_value=r['link_value'],
            sort_order=i,
            is_published=True,
        ))

    db.session.commit()
    print(f'[OK] Seeded {len(resources)} resources')


def seed_cards():
    """导入审美卡片数据"""
    if Card.query.first():
        print('[SKIP] Cards already seeded')
        return

    cards = [
        {'title': '实验设计', 'description': '从完全随机到多因素设计，掌握心理学实验的黄金标准', 'icon': 'fa-solid fa-flask', 'tag': '实验设计', 'height': 200},
        {'title': '数据可视化', 'description': '用图表讲述数据故事，从入门到高级可视化', 'icon': 'fa-solid fa-chart-line', 'tag': '数据可视化', 'height': 230},
        {'title': '学术写作', 'description': 'APA格式规范与学术论文写作技巧全指南', 'icon': 'fa-solid fa-pen-fancy', 'tag': '学术写作', 'height': 180},
        {'title': '统计方法', 'description': '从t检验到结构方程模型，系统学习统计', 'icon': 'fa-solid fa-calculator', 'tag': '统计方法', 'height': 250},
        {'title': '测量工具', 'description': '心理测量学基础与常用量表使用指南', 'icon': 'fa-solid fa-ruler', 'tag': '测量工具', 'height': 200},
        {'title': '开放科学', 'description': '预注册、开放数据、可重复性，践行透明科研', 'icon': 'fa-solid fa-lock-open', 'tag': '开放科学', 'height': 260},
        {'title': '脑成像方法', 'description': 'fMRI、EEG、fNIRS 脑成像技术入门', 'icon': 'fa-solid fa-brain', 'tag': '脑成像', 'height': 220},
        {'title': '元分析', 'description': '系统综述与元分析：从文献检索到效应量计算', 'icon': 'fa-solid fa-magnifying-glass-chart', 'tag': '元分析', 'height': 230},
    ]

    # 分类映射
    card_categories = {
        '实验设计': 'Mplus语句',
        '数据可视化': '拆解',
        '学术写作': '方法',
        '统计方法': '拆解',
        '测量工具': '素材',
        '开放科学': '素材',
        '脑成像方法': '方法',
        '元分析': '素材',
    }
    for i, c in enumerate(cards):
        db.session.add(Card(
            title=c['title'],
            description=c['description'],
            icon=c['icon'],
            tag=c['tag'],
            height=c['height'],
            category=card_categories.get(c['tag'], ''),
            sort_order=i,
            is_published=True,
        ))

    db.session.commit()
    print(f'[OK] Seeded {len(cards)} cards')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_admin()
        seed_tutorials()
        seed_resources()
        seed_cards()
        print('✓ Seed completed successfully')
