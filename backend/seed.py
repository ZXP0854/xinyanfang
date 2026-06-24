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
        ('1-1', 'ChatGPT辅助前沿追踪与选题', '研究初期方向模糊、前沿信息分散难抓，用ChatGPT5快速梳理近五年心理学研究前沿动态并辅助生成选题，帮你精准锁定有价值的研究方向，告别盲目摸索。'),
        ('1-2', 'Connected Papers+Zotero一键生成&管理文献图谱', '文献堆积却理不清脉络关联，用Connected Papers一键生成核心文献关联图谱，配合Zotero高效管理，快速构建领域知识框架，看清研究版图。'),
        ('1-3', 'ChatGPT多维评估选题可行性', '选题可行性难以判断、容易踩坑，让ChatGPT5联网检索近年心理学研究文献，从创新性和可行性多维度评估并给出具体建议，降低试错成本，让选题更稳妥。'),
        ('2-1', 'Deepseek辅助变量关系梳理与框架绘制', '心理学变量关系复杂抽象、难以形成清晰框架，结合AMOS与Deepseek绘制关系图并自动评估模型合理性，把模糊假设变成直观的研究蓝图。'),
        ('2-2-1', '实验设计方法手册与ChatGPT智能推荐', '心理学实验设计方法众多却选不准，系统对比6-8种经典设计并附核心期刊文献案例，再用ChatGPT根据你的选题智能推荐最优方案，设计决策有据可依。'),
        ('2-2-2', '前沿模型分析方法手册与ChatGPT/Gemini推荐', '心理学研究模型分析方法眼花缭乱、适用场景不清，梳理前沿模型的特点与场景，借助ChatGPT/Gemini匹配研究特征，找到最合适的分析路径，不再无从下手。'),
        ('3-1-1', 'Elicit辅助取样方法文献检索', '取样方法选择缺乏文献支撑，用Elicit快速定位各方法的心理学研究权威文献，系统对比特点与适用场景，让取样决策有理有据。'),
        ('3-1-2', 'Gemini+SPSS样本代表性评估与偏差识别', '样本代表性不足却难以量化评估，借助Gemini辅助SPSS完成卡方拟合优度检验，自动识别数据偏差，确保样本质量经得起学术推敲。'),
        ('3-2', 'G*Power与R语言样本量ChatGPT规划全攻略', '心理学实验样本量算不准、纵向流失没预案，用G*power完成功效分析与流失补偿，再用ChatGPT生成R代码，让样本规划科学高效。'),
        ('3-3', 'Gemini/ChatGPT起草知情同意书与Qualtrics伦理设置', '心理学研究伦理审查流程繁琐易遗漏，用Gemini/ChatGPT起草标准知情同意书，配合Qualtrics实现匿名化与合规跳转，全程守护研究伦理底线。'),
        ('4-1', '常用心理学量表库汇总与使用教程', '测量工具分散难找、筛选耗时，汇总全网心理学量表库资源，手把手教你快速检索与筛选，精准匹配研究需求的量表。'),
        ('4-2-1', 'EpiData与见数平台问卷收集全流程', '问卷发放回收效率低、管理混乱，从纸质问卷排版到EpiData录入，再到见数平台线上编制发布，覆盖心理学问卷数据收集的全流程。'),
        ('4-2-2', 'ChatGPT辅助PsychoPy编程与在线化部署', '心理学行为实验编程门槛高、搭建周期长，借助ChatGPT编写PsychoPy代码并生成实验材料，通过见数平台实现线上部署，让实验搭建不再困难。'),
        ('4-2-3', 'CEST/Gorilla/Pavlovia实验平台教程', '在线心理学实验平台众多却无从选择，对比CEST、Gorilla和Pavlovia三大平台，从搭建到运行全流程演示，找到最适合你的方案。'),
        ('4-3-1', 'SPSS与Dingo数据清洗、描述性统计实战教程', '原始数据脏乱、清洗步骤繁琐，用SPSS完成缺失值处理、插补与描述统计，再借助Dingo智能清洗，为后续分析准备好干净数据。'),
        ('4-4-1', 'ChatSPSS与AI对话实现信效度检验', '信效度检验步骤繁琐、软件操作复杂，用ChatSPSS和AI对话式完成信效度分析，自动生成检验报告，让测量质量评估轻松搞定。'),
        ('4-4-2', 'ChatGPT/Gemini辅助共同方法偏差识别与处理', '共同方法偏差隐蔽难察觉，用ChatGPT/Gemini辅助识别数据中的系统性偏差，以共同方法偏差为例给出处理方案，提升研究严谨性。'),
        ('4-5-1', 'ChatGPT/Gemini辅助批量中介分析快速上手', '中介分析批量处理耗时费力，借助ChatGPT/Gemini实现批量中介分析，从模型设定到结果输出一气呵成，大幅提升心理学研究统计分析效率。'),
        ('4-5-2', 'ChatGPT辅助Mplus与R语言高级统计分析', '高级统计方法上手难、软件总报错，用ChatGPT辅助Mplus模型选择与结果解读，配合Cursor生成R代码分析多层线性模型，攻克心理学研究中的高阶统计分析。'),
        ('5-1-1', '多种AI工具一键绘制研究结果图表', '图表制作反复调整，绘制费时且不够专业，用Gemini、Cursor或Claude等AI工具自动生成结果图表，精准表达心理学研究中的变量关系与实验逻辑，让结果可视化变得直观清晰。'),
        ('5-1-2', 'Gemini辅助图表生成与数据解读', '数据解读缺乏思路、表述不规范，用Gemini生成图表并自动撰写符合心理学学术规范的数据解读，从数字到文字无缝衔接，让结果陈述更加规范有力。'),
        ('5-2', 'ChatGPT定制目标期刊写作模板', '写作模板千篇一律、期刊风格难把握，用ChatGPT检索目标心理学期刊文献并生成个性化写作模板，匹配期刊特色，让研究报告撰写更有针对性。'),
        ('5-3', 'Gemini一键修订论文格式规范', '论文格式反复修改、细节易遗漏，用Gemini一键识别并修正格式问题，从引用规范到排版细节全面把关，让论文格式符合心理学论文发表要求。'),
    ]

    for node_id, title, desc in tutorials:
        content = f'<div class="tutorial-rich"><div class="rich-divider"></div><div class="rich-block"><div class="rich-text"><h4>{title}</h4><p>{desc}</p></div></div></div>'
        t = Tutorial(node_id=node_id, title=title, summary=desc[:500], content=content, is_published=True)
        db.session.add(t)

    db.session.commit()
    print(f'[OK] Seeded {len(tutorials)} tutorials')


def seed_resources():
    """导入科研资源数据"""
    if Resource.query.first():
        print('[SKIP] Resources already seeded')
        return

    resources = [
        # 文献与知识库
        {'module': '文献与知识库', 'name': 'PubMed — 生物医学与心理学文献检索', 'link_type': 'tutorial', 'link_value': 'PubMed 使用指南'},
        {'module': '文献与知识库', 'name': 'PsycINFO — APA心理学专业数据库', 'link_type': 'tutorial', 'link_value': 'PsycINFO 使用指南'},
        {'module': '文献与知识库', 'name': 'Google Scholar — 学术搜索引擎高级技巧', 'link_type': 'tutorial', 'link_value': 'Google Scholar 使用技巧'},
        {'module': '文献与知识库', 'name': '中国知网 (CNKI) — 中文学术资源检索', 'link_type': 'tutorial', 'link_value': 'CNKI 知网检索'},
        {'module': '文献与知识库', 'name': 'Zotero — 开源文献管理工具', 'link_type': 'tutorial', 'link_value': 'Zotero 文献管理'},
        {'module': '文献与知识库', 'name': 'Connected Papers — 文献关联图谱工具', 'link_type': 'tutorial', 'link_value': 'Connected Papers 文献网络'},
        # 工具与软件库
        {'module': '工具与软件库', 'name': 'SPSS — 社会科学统计软件包', 'link_type': 'tutorial', 'link_value': 'SPSS 入门教程'},
        {'module': '工具与软件库', 'name': 'R — 统计计算与图形语言', 'link_type': 'tutorial', 'link_value': 'R语言入门'},
        {'module': '工具与软件库', 'name': 'JASP — 开源贝叶斯统计软件', 'link_type': 'tutorial', 'link_value': 'JASP 使用指南'},
        {'module': '工具与软件库', 'name': 'Mplus — 结构方程建模工具', 'link_type': 'tutorial', 'link_value': 'Mplus 入门'},
        {'module': '工具与软件库', 'name': 'PsychoPy — 心理学实验编程', 'link_type': 'tutorial', 'link_value': 'PsychoPy 教程'},
        {'module': '工具与软件库', 'name': 'G*Power — 统计功效与样本量计算', 'link_type': 'tutorial', 'link_value': 'G*Power 功效分析'},
        # 量表与测量资源
        {'module': '量表与测量资源', 'name': 'BFI-2 — 大五人格量表第二版', 'link_type': 'tutorial', 'link_value': '大五人格量表'},
        {'module': '量表与测量资源', 'name': 'STAI — 状态-特质焦虑量表', 'link_type': 'tutorial', 'link_value': 'STAI 状态特质焦虑量表'},
        {'module': '量表与测量资源', 'name': 'CES-D — 流调中心抑郁量表', 'link_type': 'tutorial', 'link_value': 'CES-D 抑郁量表'},
        {'module': '量表与测量资源', 'name': 'PSS — 压力知觉量表', 'link_type': 'tutorial', 'link_value': 'PSS 压力知觉量表'},
        {'module': '量表与测量资源', 'name': 'RSES — Rosenberg自尊量表', 'link_type': 'tutorial', 'link_value': 'Rosenberg 自尊量表'},
        {'module': '量表与测量资源', 'name': 'PANAS — 积极与消极情绪量表', 'link_type': 'tutorial', 'link_value': 'PANAS 积极消极情绪量表'},
        # 公开数据集
        {'module': '公开数据集', 'name': 'Human Connectome Project — 脑成像公开数据', 'link_type': 'tutorial', 'link_value': 'HCP 公开数据'},
        {'module': '公开数据集', 'name': 'ABCD Study — 青少年脑与认知发展研究', 'link_type': 'tutorial', 'link_value': 'ABCD Study 数据'},
        {'module': '公开数据集', 'name': 'CGSS — 中国综合社会调查数据', 'link_type': 'tutorial', 'link_value': 'CGSS 中国综合社会调查'},
        {'module': '公开数据集', 'name': 'CFPS — 中国家庭追踪调查', 'link_type': 'tutorial', 'link_value': 'CFPS 中国家庭追踪调查'},
        {'module': '公开数据集', 'name': 'OSF — 开放科学框架数据共享平台', 'link_type': 'tutorial', 'link_value': 'OSF 开放科学框架'},
        {'module': '公开数据集', 'name': 'ICPSR — 校际政治与社会研究联盟数据', 'link_type': 'tutorial', 'link_value': 'ICPSR 社会科学数据'},
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

    for i, c in enumerate(cards):
        db.session.add(Card(
            title=c['title'],
            description=c['description'],
            icon=c['icon'],
            tag=c['tag'],
            height=c['height'],
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
