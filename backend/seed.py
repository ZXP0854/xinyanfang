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

    node_content = {
        '1-1': {
            'title': '什么是研究问题',
            'content': '<div class="tutorial-rich"><div class="rich-divider"></div><div class="rich-block"><div class="rich-text"><h4>研究问题的起点</h4><p>研究问题是一切的起点。一个清晰、有价值的研究问题能够为整个研究过程提供方向。</p></div></div></div>',
        },
        '1-2': {
            'title': '文献综述方法',
            'content': '<div class="tutorial-rich"><div class="rich-divider"></div><div class="rich-block"><div class="rich-text"><h4>文献综述方法</h4><p>系统性地查阅、整理和分析已有研究文献，是科研工作的基础技能。</p></div></div></div>',
        },
    }

    for node_id, data in node_content.items():
        t = Tutorial(
            node_id=node_id,
            title=data['title'],
            content=data.get('content', ''),
            is_published=True,
        )
        db.session.add(t)

    db.session.commit()
    print(f'[OK] Seeded {len(node_content)} tutorials')


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
