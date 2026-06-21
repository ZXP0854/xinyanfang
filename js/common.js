// ---------- 树状图数据 ----------
const treeData = [
    { id: "1-1", name: "研究兴趣、前沿、选题", stage: 1 },
    { id: "1-2", name: "全局图谱生成", stage: 1 },
    { id: "1-3", name: "研究选题的可行性评估", stage: 1 },
    { id: "2-1", name: "变量关系梳理", stage: 2 },
    { id: "2-2-1", name: "实验设计方法", stage: 2 },
    { id: "2-2-2", name: "模型分析方法", stage: 2 },
    { id: "3-1-1", name: "常见的取样方法", stage: 3 },
    { id: "3-1-2", name: "样本代表性评估及误区", stage: 3 },
    { id: "3-2", name: "样本量规划", stage: 3 },
    { id: "3-3", name: "伦理规范", stage: 3 },
    { id: "4-1", name: "变量量表选择", stage: 4 },
    { id: "4-2-1", name: "问卷类的数据收集", stage: 4 },
    { id: "4-2-2", name: "行为实验数据收集—Psychopy", stage: 4 },
    { id: "4-2-3", name: "行为实验数据收集—CEST", stage: 4 },
    { id: "4-2-4", name: "行为实验数据收集—Gorilla/Pavlovia", stage: 4 },
    { id: "4-3-1", name: "数据清洗", stage: 4 },
    { id: "4-3-2", name: "描述性统计", stage: 4 },
    { id: "4-4-1", name: "信度检验", stage: 4 },
    { id: "4-4-2", name: "效度检验", stage: 4 },
    { id: "4-4-3", name: "偏差识别", stage: 4 },
    { id: "4-5-1", name: "基础统计分析方法", stage: 4 },
    { id: "4-5-2", name: "高级统计分析方法", stage: 4 },
    { id: "5-1-1", name: "研究结果的呈现方式", stage: 5 },
    { id: "5-1-2", name: "研究结果的数据解读", stage: 5 },
    { id: "5-2", name: "研究报告的个性化撰写", stage: 5 }
];

// 分组名称映射（用于虚拟分组）
const groupNameMap = {
    "2-2": "研究方法选择",
    "3-1": "取样方法的选择",
    "4-2": "数据收集方法",
    "4-3": "初步数据处理",
    "4-4": "信效度与偏差",
    "4-5": "统计分析方法",
    "5-1": "研究结果的呈现与解读"
};

function getFirstNodeIdByStage(stage) {
    const node = treeData.find(n => n.stage === stage);
    return node ? node.id : null;
}

// 构建嵌套树状结构
function buildHierarchicalTree() {
    let stages = { 1: [], 2: [], 3: [], 4: [], 5: [] };
    treeData.forEach(node => { stages[node.stage].push(node); });
    let result = [];
    for (let s = 1; s <= 5; s++) {
        let stageNodes = stages[s];
        let realLevel2 = [];
        let level3Map = new Map();
        let childParentMap = new Map();
        stageNodes.forEach(node => {
            let parts = node.id.split('-');
            if (parts.length === 2) realLevel2.push(node);
            else if (parts.length === 3) {
                let parentId = parts[0] + '-' + parts[1];
                childParentMap.set(node.id, parentId);
                level3Map.set(node.id, node);
            }
        });
        let virtualParentIds = new Set();
        for (let [childId, parentId] of childParentMap.entries()) {
            if (!realLevel2.some(n => n.id === parentId)) virtualParentIds.add(parentId);
        }
        let virtualParents = [];
        for (let pid of virtualParentIds) {
            let displayName = groupNameMap[pid] || pid;
            virtualParents.push({ id: pid, name: displayName, isVirtual: true });
        }
        let allLevel2 = [...realLevel2, ...virtualParents];
        allLevel2.sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }));
        let childrenMap = new Map();
        for (let [childId, parentId] of childParentMap.entries()) {
            if (!childrenMap.has(parentId)) childrenMap.set(parentId, []);
            childrenMap.get(parentId).push(level3Map.get(childId));
        }
        for (let [parentId, children] of childrenMap.entries()) {
            children.sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }));
        }
        let ordered = [];
        for (let l2 of allLevel2) {
            ordered.push({ type: l2.isVirtual ? 'virtual' : 'level2', node: l2 });
            let kids = childrenMap.get(l2.id);
            if (kids && kids.length) {
                for (let kid of kids) ordered.push({ type: 'level3', node: kid, parentId: l2.id });
            }
        }
        result.push({ stage: s, items: ordered });
    }
    return result;
}

// 生成树状图HTML
function buildTreeHTML() {
    const stageNames = ['', '选题', '设计', '取样', '数据统计', '结果报告'];
    const hierarchical = buildHierarchicalTree();
    let html = '';
    for (let stageData of hierarchical) {
        let stageNum = stageData.stage;
        html += `<div class="stage-title">第${stageNum}阶段 · ${stageNames[stageNum]}</div><ul>`;
        for (let item of stageData.items) {
            if (item.type === 'level2') {
                html += `<li><a href="#" class="tree-node-level1" data-id="${item.node.id}">${item.node.id} ${item.node.name}</a></li>`;
            } else if (item.type === 'virtual') {
                html += `<li><div class="group-title">${item.node.id} ${item.node.name}</div></li>`;
            } else if (item.type === 'level3') {
                html += `<li><a href="#" class="tree-node-level2" data-id="${item.node.id}">${item.node.id} ${item.node.name}</a></li>`;
            }
        }
        html += `</ul>`;
    }
    return html;
}

// 教程详情模板
function getTutorialTemplate(nodeId, nodeName) {
    return `
        <div class="detail-title"><h3 class="serif serif-xs">${nodeId} ${nodeName}</h3></div>
        <div>
            <p style="margin-bottom: 20px;">【教程说明】此处将提供关于“${nodeName}”的详细方法介绍、操作步骤与心理学研究示例。</p>
            ${getRichContent(nodeId, nodeName)}
        </div>
    `;
}

// 针对特定节点的图文并茂排版（放在“教程说明”文字下面）
function getRichContent(nodeId, nodeName) {
    if (nodeId === '1-2') {
        return `
        <div class="tutorial-rich">
            <div class="rich-divider"></div>
            <div class="rich-block">
                <div class="rich-text">
                    <h4>图文教程：</h4>
                    <p>【一、在 Zotero 下载 Connected Papers 搜索】</p>
                    <p>打开 Zotero，在 Zotero 上方找到“编辑”→“设置”→“打开数据文件夹” →“locate”文件夹</p>
                </div>
                <div class="rich-gallery">
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image1.jpeg" alt="打开 Zotero 设置">
                        <div class="rich-figure-cap">图1</div>
                    </div>
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image2.jpeg" alt="定位 locate 文件夹">
                        <div class="rich-figure-cap">图2</div>
                    </div>
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image3.jpeg" alt="Connected Papers 搜索界面">
                        <div class="rich-figure-cap">图3</div>
                    </div>
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image4.jpeg" alt="Zotero 下载 Connected Papers">
                        <div class="rich-figure-cap">图4</div>
                    </div>
                </div>
            </div>
            <div class="rich-block">
                <div class="rich-text">
                    <p>方法一：利用记事本复制如下代码到 engines.json 文件里：</p>
                </div>
                <div class="rich-gallery">
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image5.jpeg" alt="编辑 engines.json 文件">
                        <div class="rich-figure-cap">图5</div>
                    </div>
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image6.jpeg" alt="Connected Papers 插件配置">
                        <div class="rich-figure-cap">图6</div>
                    </div>
                </div>
            </div>
            <div class="rich-block">
                <div class="rich-text">
                    <pre style="white-space: pre-wrap; font-size: 0.9rem; background: #f5f0eb; border-radius: 12px; padding: 16px; overflow-x: auto; border: 1px solid rgba(204,120,92,0.18);">
{
"_name": "Connected Papers",
"_alias": "Connected Papers文献网络",
"_description": "Connected Papers文献网络",
"_icon": "https://www.connectedpapers.com/favicon.ico",
"_hidden": false,
"_urlTemplate": "https://www.connectedpapers.com/search?q={z:title}+{z:year}",
"_urlParams": [],
"_urlNamespaces": {
"rft": "info:ofi/fmt:kev:mtx:journal",
"z": "http://www.zotero.org/namespaces/openSearch#",
"": "http://a9.com/-/spec/opensearch/1.1/"
},
"_iconSourceURI": "https://www.connectedpapers.com/favicon.ico"
}
                    </pre>
                </div>
            </div>
            <div class="rich-block">
                <div class="rich-text">
                    <p>方法二：下载 engines.json 文件（已附上超链接）。</p>
                    <p>这个文件里面包含了很多自定义的搜索引擎，其中就有我们需要的 Connected Papers，替换 locates 文件夹中的 engines.json，直接覆盖就行，之后重启 Zotero 使用 Connected Papers 搜索文献。</p>
                </div>
                <div class="rich-gallery">
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image7.jpeg" alt="下载 engines.json 文件">
                        <div class="rich-figure-cap">图7</div>
                    </div>
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image8.jpeg" alt="Connected Papers 配置文件示例">
                        <div class="rich-figure-cap">图8</div>
                    </div>
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image9.jpeg" alt="Zotero 插件设置界面">
                        <div class="rich-figure-cap">图9</div>
                    </div>
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image10.jpeg" alt="覆盖 engines.json 文件">
                        <div class="rich-figure-cap">图10</div>
                    </div>
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image11.jpeg" alt="重启 Zotero 使用 Connected Papers">
                        <div class="rich-figure-cap">图11</div>
                    </div>
                </div>
            </div>
            <div class="rich-block">
                <div class="rich-text">
                    <h4>【二、图谱的使用方式】</h4>
                    <p>①节点大小表示论文的引用量</p>
                    <p>节点面积越大，引用量越大。如下图的节点标记的论文，该节点比较大，引用量为 156 次。</p>
                </div>
                <div class="rich-figure">
                    <img src="images/extracted-docx/image12.jpeg" alt="节点大小表示引用量">
                    <div class="rich-figure-cap">图12</div>
                </div>
            </div>
            <div class="rich-block">
                <div class="rich-text">
                    <p>下图节点面积最小，由此可见其引用为 0。</p>
                </div>
                <div class="rich-figure">
                    <img src="images/extracted-docx/image13.jpeg" alt="最小节点引用为0">
                    <div class="rich-figure-cap">图13</div>
                </div>
            </div>
            <div class="rich-block">
                <div class="rich-text">
                    <p>②节点颜色表示发表的年份</p>
                    <p>节点的颜色代表了发表年份，颜色越深表示论文越新，颜色越浅表示论文发表年份越早。这可以直接通过颜色来帮助我们优先阅读的论文。</p>
                </div>
                <div class="rich-figure">
                    <img src="images/extracted-docx/image14.jpeg" alt="节点颜色表示发表年份">
                    <div class="rich-figure-cap">图14</div>
                </div>
            </div>
            <div class="rich-block">
                <div class="rich-text">
                    <p>③节点的距离表示相似度</p>
                    <p>每一个节点都和我们的原始文献有某种关系，主要是根据相似性判断。相似度越大两个节点的距离越近。</p>
                </div>
                <div class="rich-figure">
                    <img src="images/extracted-docx/image15.jpeg" alt="节点距离表示相似度">
                    <div class="rich-figure-cap">图15</div>
                </div>
            </div>
            <div class="rich-block">
                <div class="rich-text">
                    <p>④线条的粗细表示相似度</p>
                    <p>两篇文献的相似度越高，连接线条就越粗；相似度越低，连接线条越细。</p>
                    <p>⑤Prior works，图谱中文献高频引用的文献</p>
                    <p>点击 Prior works 按钮，可以查看被图谱所引用的文献。如果一篇文献被大部分节点引用，说明它可能更重要，值得主动阅读。</p>
                </div>
                <div class="rich-figure">
                    <img src="images/extracted-docx/image16.jpeg" alt="Prior works 高频引用文献">
                    <div class="rich-figure-cap">图16</div>
                </div>
            </div>
            <div class="rich-block">
                <div class="rich-text">
                    <p>⑥Derivative works 引用了图谱中节点文献的文献。</p>
                    <p>查看那些引用原始文献的论文，可以帮助我们快速掌握该领域的研究进展。</p>
                    <p>离此节点越近的文献相似度越高；节点越大表示引用量越高，意味着更值得优先阅读。</p>
                </div>
                <div class="rich-figure">
                    <img src="images/extracted-docx/image17.jpeg" alt="Derivative works 研究进展">
                    <div class="rich-figure-cap">图17</div>
                </div>
            </div>
            <div class="rich-block">
                <div class="rich-text">
                    <h4>【三、批量下载 Connected Papers 到 Zotero - 导入到 Zotero 中下载题录信息】</h4>
                    <p>如果找到了很多对应的论文，可以手动下载，也可以通过插件直接抓取到 Zotero 中。</p>
                    <p>点击 Connected Papers 的 download 按钮下载 bib 文件，打开后全选复制，进入 Zotero，选择“文件”→“从剪切板导入”，即可导入成功。</p>
                </div>
                <div class="rich-gallery">
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image18.jpeg" alt="批量下载 Connected Papers">
                        <div class="rich-figure-cap">图18</div>
                    </div>
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image19.jpeg" alt="Bib 文件导入 Zotero">
                        <div class="rich-figure-cap">图19</div>
                    </div>
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image20.jpeg" alt="从剪切板导入 Zotero">
                        <div class="rich-figure-cap">图20</div>
                    </div>
                    <div class="rich-figure">
                        <img src="images/extracted-docx/image21.jpeg" alt="导入成功界面">
                        <div class="rich-figure-cap">图21</div>
                    </div>
                </div>
            </div>
            <div class="rich-block">
                <div class="rich-text">
                    <h4>【总结】</h4>
                    <p>用 Connected Papers + Zotero，你可以：</p>
                    <ul>
                        <li>从一篇心理学文献出发，快速生成五年核心文献关系图</li>
                        <li>一眼看清引用量、发表年份、相似度、前置文献和衍生文献</li>
                        <li>重点关注 Prior works（高被引论文）和 Derivative works（研究进展）</li>
                        <li>一键批量导入 Zotero，省去手动整理时间</li>
                    </ul>
                </div>
            </div>
        </div>`;
    }
    return '';
}

// 渲染教程详情
function renderDetail(nodeId) {
    const node = treeData.find(n => n.id === nodeId);
    if (!node) return;
    const detailDiv = document.getElementById('tutorial-detail');
    if (detailDiv) detailDiv.innerHTML = getTutorialTemplate(node.id, node.name);
    document.querySelectorAll('.tree-node-level1, .tree-node-level2').forEach(el => {
        if (el.getAttribute('data-id') === nodeId) el.classList.add('active');
        else el.classList.remove('active');
    });
    // 为详情中的图片绑定模态放大交互
    attachImageModalHandlers();
}

// 图片模态交互：绑定和控制放大/关闭
function attachImageModalHandlers() {
    const detail = document.getElementById('tutorial-detail');
    if (!detail) return;
    const imgs = detail.querySelectorAll('.tutorial-rich img');
    imgs.forEach(img => {
        img.style.cursor = 'pointer';
        img.removeEventListener('click', imageClickHandler);
        img.addEventListener('click', imageClickHandler);
    });
    // 绑定模态的关闭事件（若存在）
    const modal = document.getElementById('image-modal');
    if (modal && !modal.__hasHandlers) {
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) closeBtn.addEventListener('click', closeImageModal);
        modal.addEventListener('click', function (e) { if (e.target === modal) closeImageModal(); });
        modal.__hasHandlers = true;
    }
}

function imageClickHandler(e) {
    const src = e.currentTarget.getAttribute('src');
    const alt = e.currentTarget.getAttribute('alt') || '';
    openImageModal(src, alt);
}

function openImageModal(src, alt) {
    const modal = document.getElementById('image-modal');
    if (!modal) return;
    const img = modal.querySelector('.modal-img');
    img.src = src;
    img.alt = alt || '';
    modal.classList.add('visible');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
}

function closeImageModal() {
    const modal = document.getElementById('image-modal');
    if (!modal) return;
    modal.classList.remove('visible');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
}

let currentPage = 'home';
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active-page'));
    const targetPage = document.getElementById(`${pageId}-page`);
    if (targetPage) targetPage.classList.add('active-page');
    currentPage = pageId;
    document.querySelectorAll('.nav-links a').forEach(link => {
        const navVal = link.getAttribute('data-nav');
        const active = (navVal === 'home' && pageId === 'home') ||
                       (navVal === 'flow' && pageId === 'flow') ||
                       (navVal === 'aesthetics' && pageId === 'aesthetics') ||
                       (navVal === 'resources' && pageId === 'resources') ||
                       (navVal === 'about' && pageId === 'about');
        if (active) link.classList.add('active');
        else link.classList.remove('active');
    });
    if (pageId === 'flow') attachTreeEvents();
}
function attachTreeEvents() {
    document.querySelectorAll('.tree-node-level1, .tree-node-level2').forEach(el => {
        el.removeEventListener('click', treeClickHandler);
        el.addEventListener('click', treeClickHandler);
    });
}
function treeClickHandler(e) {
    e.preventDefault();
    const id = this.getAttribute('data-id');
    if (id) renderDetail(id);
}

// ---------- 圆环生成（高级 3D 多段式导览环） ----------
function createRingSVG(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const SIZE = 560, CX = SIZE / 2, CY = SIZE / 2;
    const R_OUTER = 200, R_INNER = 104;
    const TOTAL = 5, ANGLE_PER = 360 / TOTAL;
    const GAP_DEG = 3.2;
    const HALF_SECTOR = (ANGLE_PER - GAP_DEG) / 2;
    const TENON_ANGLE = 12;
    const tenonR = (R_OUTER + R_INNER) / 2;
    const TEXT_R = (R_OUTER + R_INNER) / 2 + 2;
    const TEXT_SPAN = HALF_SECTOR - 4;

    const DRAWER_GAP = 14;
    const DRAWER_DEPTH = 58;
    const DR_INNER = R_OUTER + DRAWER_GAP;
    const DR_OUTER = DR_INNER + DRAWER_DEPTH;
    const DRAWER_COLLAPSE = R_OUTER / DR_OUTER;

    const segments = [
        { label: '选题探索', short: '选题探索', stage: 1, light: '#E7D2CC', main: '#DABAB0', dark: '#87736D', desc: '捕捉研究兴趣 · 追踪学科前沿 · 确定可行选题' },
        { label: '研究设计', short: '研究设计', stage: 2, light: '#D8B9AE', main: '#C39383', dark: '#795B51', desc: '梳理变量关系 · 选择实验或模型分析方法' },
        { label: '取样实施', short: '取样实施', stage: 3, light: '#D1CCC8', main: '#B8B1AB', dark: '#726E6A', desc: '确定取样方法 · 规划样本量 · 遵循伦理规范' },
        { label: '数据分析', short: '数据分析', stage: 4, light: '#C6D3D8', main: '#A8BCC3', dark: '#687579', desc: '收集与清洗数据 · 完成统计与信效度检验' },
        { label: '结果报告', short: '结果报告', stage: 5, light: '#C1C6A8', main: '#A0A779', dark: '#63684B', desc: '呈现与解读结果 · 完成研究报告撰写' }
    ];

    const rad = d => d * Math.PI / 180;
    const P = (deg, r) => [
        (CX + r * Math.cos(rad(deg))).toFixed(2),
        (CY + r * Math.sin(rad(deg))).toFixed(2)
    ];

    function segPath(c) {
        const a0 = c - HALF_SECTOR, a1 = c + HALF_SECTOR;
        const [osx, osy] = P(a0, R_OUTER);
        const [oex, oey] = P(a1, R_OUTER);
        const [ttx, tty] = P(a1 + TENON_ANGLE, tenonR);
        const [iex, iey] = P(a1, R_INNER);
        const [isx, isy] = P(a0, R_INNER);
        const [ntx, nty] = P(a0 + TENON_ANGLE, tenonR);
        return `M ${osx} ${osy} A ${R_OUTER} ${R_OUTER} 0 0 1 ${oex} ${oey} `
             + `L ${ttx} ${tty} L ${iex} ${iey} `
             + `A ${R_INNER} ${R_INNER} 0 0 0 ${isx} ${isy} `
             + `L ${ntx} ${nty} Z`;
    }

    function textPathD(c, bottom) {
        if (!bottom) {
            const [x0, y0] = P(c - TEXT_SPAN, TEXT_R);
            const [x1, y1] = P(c + TEXT_SPAN, TEXT_R);
            return `M ${x0} ${y0} A ${TEXT_R} ${TEXT_R} 0 0 1 ${x1} ${y1}`;
        }
        const [x0, y0] = P(c + TEXT_SPAN, TEXT_R);
        const [x1, y1] = P(c - TEXT_SPAN, TEXT_R);
        return `M ${x0} ${y0} A ${TEXT_R} ${TEXT_R} 0 0 0 ${x1} ${y1}`;
    }

    function drawerPath(c, halfSpan) {
        const a0 = c - halfSpan, a1 = c + halfSpan;
        const [oix, oiy] = P(a0, DR_INNER);
        const [oox, ooy] = P(a0, DR_OUTER);
        const [eox, eoy] = P(a1, DR_OUTER);
        const [eix, eiy] = P(a1, DR_INNER);
        return `M ${oix} ${oiy} L ${oox} ${ooy} `
             + `A ${DR_OUTER} ${DR_OUTER} 0 0 1 ${eox} ${eoy} `
             + `L ${eix} ${eiy} `
             + `A ${DR_INNER} ${DR_INNER} 0 0 0 ${oix} ${oiy} Z`;
    }

    function drawerTextPathD(c, halfSpan, bottom) {
        const r = (DR_INNER + DR_OUTER) / 2;
        const span = halfSpan - 1.5;
        if (!bottom) {
            const [x0, y0] = P(c - span, r);
            const [x1, y1] = P(c + span, r);
            return `M ${x0} ${y0} A ${r} ${r} 0 0 1 ${x1} ${y1}`;
        }
        const [x0, y0] = P(c + span, r);
        const [x1, y1] = P(c - span, r);
        return `M ${x0} ${y0} A ${r} ${r} 0 0 0 ${x1} ${y1}`;
    }

    let defs = '';
    let sectorsMarkup = '';
    let drawersMarkup = '';
    const arcLen = TEXT_R * rad(2 * TEXT_SPAN);
    const DRAWER_HALF = HALF_SECTOR + 1.2;

    for (let i = 0; i < TOTAL; i++) {
        const c = -90 + i * ANGLE_PER;
        const norm = ((c % 360) + 360) % 360;
        const bottom = norm > 0 && norm < 180;
        const seg = segments[i];

        defs += `
        <linearGradient id="draw${i}" gradientUnits="userSpaceOnUse" x1="${CX}" y1="${CY - DR_OUTER}" x2="${CX}" y2="${CY + DR_OUTER}">
            <stop offset="0" stop-color="#ffffff" stop-opacity="0.9"/>
            <stop offset="0.5" stop-color="${seg.light}" stop-opacity="0.82"/>
            <stop offset="1" stop-color="${seg.main}" stop-opacity="0.78"/>
        </linearGradient>`;
        defs += `<path id="dtpath${i}" d="${drawerTextPathD(c, DRAWER_HALF, bottom)}" fill="none"/>`;

        const drawerR = (DR_INNER + DR_OUTER) / 2;
        const drawerArc = drawerR * rad(2 * (DRAWER_HALF - 1.5));
        let dfs = drawerArc / (seg.desc.length * 1.04);
        dfs = Math.min(13, Math.max(8.5, dfs));
        const dNatural = dfs * 1.04 * seg.desc.length;
        const dLenAttr = dNatural > drawerArc ? ` textLength="${drawerArc.toFixed(1)}" lengthAdjust="spacingAndGlyphs"` : '';

        drawersMarkup += `
        <g class="ring-drawer" data-drawer="${i}" style="transform-origin:${CX}px ${CY}px;">
            <path d="${drawerPath(c, DRAWER_HALF)}" fill="url(#draw${i})" stroke="rgba(255,255,255,0.7)" stroke-width="1.1" style="filter:drop-shadow(0 6px 14px rgba(50,50,55,0.22));"/>
            <path d="${drawerPath(c, DRAWER_HALF)}" fill="#ffffff" filter="url(#frostNoise)" pointer-events="none"/>
            <text class="drawer-label" text-anchor="middle" dominant-baseline="central" pointer-events="none" style="font-size:${dfs.toFixed(1)}px;">
                <textPath href="#dtpath${i}" startOffset="50%"${dLenAttr}>${seg.desc}</textPath>
            </text>
        </g>`;

        defs += `
        <linearGradient id="frost${i}" gradientUnits="userSpaceOnUse" x1="${CX}" y1="${CY - R_OUTER}" x2="${CX}" y2="${CY + R_OUTER}">
            <stop offset="0" stop-color="#ffffff" stop-opacity="0.82"/>
            <stop offset="0.35" stop-color="${seg.light}" stop-opacity="0.72"/>
            <stop offset="0.70" stop-color="${seg.main}" stop-opacity="0.70"/>
            <stop offset="1" stop-color="${seg.dark}" stop-opacity="0.62"/>
        </linearGradient>`;
        defs += `<path id="tpath${i}" d="${textPathD(c, bottom)}" fill="none"/>`;

        let fs = arcLen / (seg.label.length * 1.08);
        fs = Math.min(14.5, Math.max(9.5, fs));
        const naturalWidth = fs * 1.08 * seg.label.length;
        const textLenAttr = naturalWidth > arcLen ? ` textLength="${arcLen.toFixed(1)}" lengthAdjust="spacingAndGlyphs"` : '';

        const d = segPath(c);
        sectorsMarkup += `
        <g class="ring-sector" data-sector="${i}" data-stage="${seg.stage}">
            <title>${seg.label}</title>
            <path class="seg-fill" d="${d}" fill="url(#frost${i})" stroke="rgba(255,255,255,0.6)" stroke-width="1.1"/>
            <path class="seg-grain" d="${d}" fill="#ffffff" filter="url(#frostNoise)" pointer-events="none"/>
            <path class="seg-gloss" d="${d}" fill="url(#glossGrad)" pointer-events="none"/>
            <text class="seg-label" text-anchor="middle" dominant-baseline="central" pointer-events="none" style="font-size:${fs.toFixed(1)}px;">
                <textPath href="#tpath${i}" startOffset="50%"${textLenAttr}>${seg.label}</textPath>
            </text>
        </g>`;
    }

    defs += `
        <linearGradient id="glossGrad" gradientUnits="userSpaceOnUse" x1="${CX}" y1="${CY - R_OUTER}" x2="${CX}" y2="${CY + R_OUTER}">
            <stop offset="0" stop-color="#ffffff" stop-opacity="0.5"/>
            <stop offset="0.16" stop-color="#ffffff" stop-opacity="0.14"/>
            <stop offset="0.42" stop-color="#ffffff" stop-opacity="0"/>
            <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
        </linearGradient>
        <radialGradient id="hubGrad" gradientUnits="userSpaceOnUse" cx="${CX - 26}" cy="${CY - 30}" r="160">
            <stop offset="0" stop-color="#ffffff" stop-opacity="0.92"/>
            <stop offset="0.45" stop-color="#F0E6DA" stop-opacity="0.78"/>
            <stop offset="0.80" stop-color="#D8C3AA" stop-opacity="0.66"/>
            <stop offset="1" stop-color="#C9A176" stop-opacity="0.60"/>
        </radialGradient>
        <linearGradient id="hubGloss" gradientUnits="userSpaceOnUse" x1="${CX}" y1="${CY - 98}" x2="${CX}" y2="${CY + 30}">
            <stop offset="0" stop-color="#ffffff" stop-opacity="0.8"/>
            <stop offset="0.55" stop-color="#ffffff" stop-opacity="0.04"/>
            <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
        </linearGradient>
        <radialGradient id="groundShadow" gradientUnits="userSpaceOnUse" cx="${CX}" cy="${CY}" r="${R_OUTER}">
            <stop offset="0" stop-color="rgba(20,20,19,0.22)"/>
            <stop offset="1" stop-color="rgba(20,20,19,0)"/>
        </radialGradient>
        <filter id="frostNoise" x="-20%" y="-20%" width="140%" height="140%">
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" stitchTiles="stitch" result="n"/>
            <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.06 0" result="grain"/>
            <feComposite in="grain" in2="SourceAlpha" operator="in"/>
        </filter>
        <filter id="hubFrost" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="8"/>
        </filter>`;

    const groundShadow = `<ellipse cx="${CX}" cy="${CY + R_OUTER - 6}" rx="${(R_OUTER * 0.82).toFixed(0)}" ry="34" fill="url(#groundShadow)"/>`;
    const hubBlobs = `<circle cx="${CX}" cy="${CY - 12}" r="118" fill="#C9A176"/>`
                   + `<circle cx="${CX + 28}" cy="${CY + 42}" r="86" fill="#0E4D66" opacity="0.5"/>`;
    const outerDeco = `<circle class="deco-ring" cx="${CX}" cy="${CY}" r="${R_OUTER + 12}" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.4" stroke-dasharray="9 7" style="transform-box:view-box; transform-origin:${CX}px ${CY}px; animation:spin 70s linear infinite;"/>`;
    const innerDeco = `<circle class="deco-ring" cx="${CX}" cy="${CY}" r="${R_INNER - 8}" fill="none" stroke="rgba(255,255,255,0.42)" stroke-width="1.2" stroke-dasharray="5 7" style="transform-box:view-box; transform-origin:${CX}px ${CY}px; animation:spin-reverse 55s linear infinite;"/>`;
    const hub = `
        <g class="ring-hub">
            <clipPath id="hubClip"><circle cx="${CX}" cy="${CY}" r="98"/></clipPath>
            <g clip-path="url(#hubClip)"><g filter="url(#hubFrost)">${hubBlobs}</g></g>
            <circle cx="${CX}" cy="${CY}" r="98" fill="url(#hubGrad)" stroke="rgba(255,255,255,0.72)" stroke-width="1.5" style="filter:drop-shadow(0 8px 18px rgba(70,55,40,0.3));"/>
            <circle cx="${CX}" cy="${CY}" r="98" fill="#ffffff" filter="url(#frostNoise)" clip-path="url(#hubClip)" pointer-events="none"/>
            <ellipse cx="${CX}" cy="${CY - 34}" rx="78" ry="48" fill="url(#hubGloss)" pointer-events="none"/>
            <circle cx="${CX}" cy="${CY}" r="94" fill="none" stroke="rgba(255,255,255,0.25)" stroke-width="1"/>
            <text id="ringCenterMain" x="${CX}" y="${CY - 6}" text-anchor="middle" dominant-baseline="central" style="font-family:Georgia,serif; font-size:26px; font-weight:600; fill:#9C7164; letter-spacing:2px;">科研流程</text>
            <text id="ringCenterSub" x="${CX}" y="${CY + 24}" text-anchor="middle" dominant-baseline="central" style="font-family:Inter,sans-serif; font-size:12.5px; font-weight:500; fill:#9C7164; letter-spacing:3px;">五步法 · 点击探索</text>
        </g>`;

    const svgHtml = `
        <svg viewBox="0 0 ${SIZE} ${SIZE}" class="ring-svg" xmlns="http://www.w3.org/2000/svg">
            <defs>${defs}</defs>
            ${groundShadow}
            ${outerDeco}
            <g class="ring-drawers">${drawersMarkup}</g>
            <g class="ring-sectors">${sectorsMarkup}</g>
            ${innerDeco}
            ${hub}
            <style>
                @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
                @keyframes spin-reverse { from { transform: rotate(360deg); } to { transform: rotate(0deg); } }
                .ring-sector {
                    cursor: pointer;
                    transform-box: view-box;
                    transform-origin: ${CX}px ${CY}px;
                    transition: transform .28s cubic-bezier(.2,.9,.4,1.1), filter .25s ease;
                    filter: drop-shadow(0 6px 12px rgba(50,50,55,0.16));
                }
                .ring-sector .seg-label {
                    fill: #9C7164;
                    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                    filter: drop-shadow(0 1px 1.5px rgba(255,255,255,0.55));
                }
                .ring-sector .seg-fill { transition: stroke .2s ease; }
                .ring-drawer {
                    transform-box: view-box;
                    opacity: 0;
                    transform: scale(${DRAWER_COLLAPSE.toFixed(4)});
                    pointer-events: none;
                    transition: transform .42s cubic-bezier(.18,.9,.32,1.2), opacity .3s ease;
                }
                .ring-drawer.open {
                    opacity: 1;
                    transform: scale(1);
                }
                .ring-drawer .drawer-label {
                    fill: #9C7164;
                    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
                    font-weight: 600;
                    letter-spacing: 0.3px;
                    filter: drop-shadow(0 1px 1.2px rgba(255,255,255,0.6));
                }
            </style>
        </svg>`;

    container.innerHTML = svgHtml;

    // ---------- 侧浮窗（副窗）：内容解析与几何（纯函数） ----------
    const GAP = 8; // 浮窗与圆环外缘的间隙
    const R_MID = (R_OUTER + R_INNER) / 2;

    const hasValidString = s => typeof s === 'string' && s.trim().length > 0;
    function resolvePanelContent(seg) {
        if (!seg || !hasValidString(seg.label) || !hasValidString(seg.desc)) return null;
        return { title: seg.label, desc: seg.desc, stage: seg.stage };
    }
    const segmentCenterAngle = i => -90 + i * ANGLE_PER;
    function chooseSide(angleDeg) {
        const xOffset = R_MID * Math.cos(rad(angleDeg));
        return xOffset < 0 ? 'left' : 'right';
    }
    const panelEdgeX = side => side === 'right' ? CX + R_OUTER + GAP : CX - R_OUTER - GAP;
    const radialMidpointY = angleDeg => CY + R_MID * Math.sin(rad(angleDeg));
    const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

    // ---------- 侧浮窗 DOM 与控制器 ----------
    const supportsHover = () => window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    const panel = document.createElement('div');
    panel.className = 'ring-side-panel';
    panel.setAttribute('role', 'status');
    panel.setAttribute('aria-live', 'polite');
    panel.setAttribute('aria-hidden', 'true');
    panel.innerHTML = '<div class="rsp-stage"></div><h4 class="rsp-title"></h4><p class="rsp-desc"></p>';
    container.appendChild(panel);
    const panelStage = panel.querySelector('.rsp-stage');
    const panelTitle = panel.querySelector('.rsp-title');
    const panelDesc = panel.querySelector('.rsp-desc');
    let hideTimer = null;

    function positionPanel(i) {
        const angle = segmentCenterAngle(i);
        const side = chooseSide(angle);
        // 仅决定左右侧；浮窗紧贴圆环容器水平外侧并垂直居中，由 CSS 定位，避开弧形抽屉
        panel.setAttribute('data-side', side);
        panel.style.left = '';
        panel.style.right = '';
        panel.style.top = '';
    }

    function showPanel(i) {
        if (!supportsHover()) return;
        const content = resolvePanelContent(segments[i]);
        if (!content) return;
        clearTimeout(hideTimer);
        panelStage.textContent = '第 ' + content.stage + ' 阶段';
        panelTitle.textContent = content.title;
        panelDesc.textContent = content.desc;
        positionPanel(i);
        panel.classList.add('visible');
        panel.setAttribute('aria-hidden', 'false');
    }

    function hidePanel() {
        clearTimeout(hideTimer);
        panel.classList.remove('visible');
        panel.setAttribute('aria-hidden', 'true');
    }

    function scheduleHide() {
        clearTimeout(hideTimer);
        hideTimer = setTimeout(hidePanel, 80);
    }

    const svgEl = container.querySelector('svg');
    const centerMain = svgEl.querySelector('#ringCenterMain');
    const centerSub = svgEl.querySelector('#ringCenterSub');
    const drawers = svgEl.querySelectorAll('.ring-drawer');

    svgEl.querySelectorAll('.ring-sector').forEach(g => {
        const i = parseInt(g.getAttribute('data-sector'), 10);
        const seg = segments[i];
        const drawer = drawers[i];
        // 键盘可达性
        g.setAttribute('tabindex', '0');
        g.setAttribute('role', 'button');
        g.setAttribute('aria-label', '第' + seg.stage + '阶段：' + seg.label);
        const activate = () => {
            g.style.transform = 'scale(1.05)';
            g.style.filter = 'drop-shadow(0 15px 24px rgba(50,50,55,0.28)) brightness(1.05) saturate(1.08)';
            g.querySelector('.seg-fill').setAttribute('stroke', 'rgba(255,255,255,0.95)');
            if (drawer) drawer.classList.add('open');
            if (centerMain) centerMain.textContent = seg.short;
            if (centerSub) centerSub.textContent = '第' + seg.stage + '阶段 →';
            showPanel(i);
        };
        const deactivate = () => {
            g.style.transform = '';
            g.style.filter = '';
            g.querySelector('.seg-fill').setAttribute('stroke', 'rgba(255,255,255,0.6)');
            if (drawer) drawer.classList.remove('open');
            if (centerMain) centerMain.textContent = '科研流程';
            if (centerSub) centerSub.textContent = '五步法 · 点击探索';
            scheduleHide();
        };
        g.addEventListener('mouseenter', activate);
        g.addEventListener('mouseleave', deactivate);
        g.addEventListener('focus', activate);
        g.addEventListener('blur', deactivate);
        const navigate = () => {
            const firstId = getFirstNodeIdByStage(seg.stage);
            if (firstId) {
                window.location.href = 'workflow.html?stage=' + seg.stage;
            } else {
                alert(`跳转至「${seg.short}」教程`);
            }
        };
        g.addEventListener('click', (e) => {
            e.stopPropagation();
            navigate();
        });
        g.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                navigate();
            }
        });
    });

    const resetAll = () => {
        hidePanel();
        drawers.forEach(d => d.classList.remove('open'));
        svgEl.querySelectorAll('.ring-sector').forEach(s => {
            s.style.transform = '';
            s.style.filter = '';
            const f = s.querySelector('.seg-fill');
            if (f) f.setAttribute('stroke', 'rgba(255,255,255,0.6)');
        });
        if (centerMain) centerMain.textContent = '科研流程';
        if (centerSub) centerSub.textContent = '五步法 · 点击探索';
    };
    svgEl.addEventListener('mouseleave', resetAll);
    container.addEventListener('mouseleave', resetAll);
}

// ---------- 登录 / 导航 / 搜索相关 ----------
function checkLogin() {
    if (sessionStorage.getItem('xinyanfang_logged_in') !== 'true') {
        window.location.href = 'index.html';
    }
}
function handleLogin() {
    sessionStorage.setItem('xinyanfang_logged_in', 'true');
    window.location.href = 'home.html';
}
function highlightNav() {
    const path = window.location.pathname;
    const filename = path.split('/').pop();
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href === filename) link.classList.add('active');
    });
}
function toggleNav() {
    const navLinks = document.getElementById('navLinks');
    if (navLinks) navLinks.classList.toggle('open');
}
function closeNav() {
    const navLinks = document.getElementById('navLinks');
    if (navLinks) navLinks.classList.remove('open');
}
function openTutorial(topicName) {
    window.location.href = 'tutorial.html?title=' + encodeURIComponent(topicName);
}
function handleSearch() {
    const keyword = document.getElementById('searchInput').value.trim();
    if (keyword) alert(`搜索功能开发中… 您搜索了：“${keyword}”`);
    else alert('请输入关键词');
}

document.addEventListener('DOMContentLoaded', () => {
    if (!window.location.pathname.includes('index.html') && !window.location.pathname.endsWith('/')) {
        checkLogin();
    }
    highlightNav();
    document.addEventListener('click', (e) => {
        const nav = document.getElementById('navLinks');
        const toggle = document.querySelector('.nav-toggle');
        if (nav && nav.classList.contains('open') && !nav.contains(e.target) && !toggle?.contains(e.target)) {
            nav.classList.remove('open');
        }
    });
});