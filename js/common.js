// ---------- 树状图数据 ----------
const treeData = [
    { id: "1-1", name: "文献全局图谱生成", stage: 1 },
    { id: "1-2", name: "研究前沿选题与评估", stage: 1 },
    { id: "2-1", name: "研究变量关系梳理", stage: 2 },
    { id: "2-2-1", name: "实验设计方法", stage: 2 },
    { id: "2-2-2", name: "模型分析方法", stage: 2 },
    { id: "3-1-1", name: "常见的取样方法", stage: 3 },
    { id: "3-1-2", name: "样本代表性评估及误区", stage: 3 },
    { id: "3-2", name: "样本量规划", stage: 3 },
    { id: "3-3", name: "知情同意与伦理规范", stage: 3 },
    { id: "4-1", name: "变量量表选择", stage: 4 },
    { id: "4-2-1", name: "问卷类的数据收集", stage: 4 },
    { id: "4-2-2", name: "行为实验数据收集—Psychopy", stage: 4 },
    { id: "4-2-3", name: "行为实验数据收集—CEST、Gorilla和Pavlovia", stage: 4 },
    { id: "4-3", name: "数据清洗与描述性统计", stage: 4 },
    { id: "4-4-1", name: "信效度检验", stage: 4 },
    { id: "4-4-2", name: "共同方法偏差识别", stage: 4 },
    { id: "4-5-1", name: "基础统计分析方法——中介分析", stage: 4 },
    { id: "4-5-2", name: "高级统计分析方法——Mplus模型和R语言", stage: 4 },
    { id: "5-1-1", name: "研究结果的呈现方式", stage: 5 },
    { id: "5-1-2", name: "研究结果的数据解读", stage: 5 },
    { id: "5-2", name: "研究报告的个性化撰写", stage: 5 },
    { id: "5-3", name: "研究报告的格式修订", stage: 5 }
];

// 分组名称映射（用于虚拟分组）
const groupNameMap = {
    "2-2": "研究方法选择",
    "3-1": "取样方法的选择",
    "4-2": "数据收集方法",
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
    const stageNames = ['', '选题探索', '研究设计', '取样实施', '数据分析', '结果报告'];
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
function getTutorialIntro(nodeId) {
    var meta = tutorialMeta[nodeId];
    if (!meta) return '';
    return '<div class="tutorial-rich"><div class="rich-divider"></div>' +
        '<div class="rich-block"><div class="rich-text">' +
        '<h4>' + meta.title + '</h4>' +
        '<p>' + meta.desc + '</p>' +
        '</div></div></div>';
}

function getWorkflowSectionContent(nodeId, sectionKey, nodeName) {
    var workflowData = (typeof window !== 'undefined' && window.WORKFLOW_SECTION_CONTENT) ? window.WORKFLOW_SECTION_CONTENT : null;
    if (workflowData && workflowData[nodeId] && Object.prototype.hasOwnProperty.call(workflowData[nodeId], sectionKey)) {
        return workflowData[nodeId][sectionKey] || '';
    }
    var sectionMap = {
        learningCost: '这一部分说明该教程需要的前置知识、时间投入和学习难度，帮助你先判断是否适合现在开始。',
        useScenarios: '这一部分说明该方法适合哪类研究问题、数据类型和论文阶段，方便你快速判断使用场景。',
        accomplishments: '这一部分说明学完后你能直接完成什么，帮助你把“看懂教程”转化为“拿到产出”。',
        recommendedTools: '这一部分列出常用工具和软件，帮助你在开始前先准备好对应环境。',
        commonMistakes: '这一部分总结最容易踩坑的地方，方便你在实际操作前提前规避。',
        finalTemplate: '这一部分提供最终可直接套用的写作或输出模板，方便你复制后继续调整。',
    };
    return sectionMap[sectionKey] || ('这里预留给 "' + nodeName + '" 的结构化内容。');
}

function buildWorkflowSection(index, title, bodyHtml, open) {
    return `
        <details class="workflow-section"${open ? ' open' : ''}>
            <summary class="workflow-section__summary">
                <span class="workflow-section__label">
                    <span class="workflow-section__index">${index}</span>
                    <span class="workflow-section__title">${title}</span>
                </span>
                <span class="workflow-section__state">
                    <span class="workflow-section__state-open">收起</span>
                    <span class="workflow-section__state-closed">展开</span>
                </span>
            </summary>
            <div class="workflow-section__body">
                ${bodyHtml}
            </div>
        </details>
    `;
}

const AI_WORKFLOW_NODE_IDS = new Set([
    '1-2',
    '2-1',
    '2-2-1',
    '2-2-2',
    '3-1-1',
    '3-1-2',
    '3-2',
    '3-3',
    '4-2-2',
    '4-3',
    '4-4-1',
    '4-4-2',
    '4-5-1',
    '4-5-2',
    '5-1-1',
    '5-1-2',
    '5-2',
    '5-3',
]);

function buildWorkflowAiNotice(nodeId) {
    if (!AI_WORKFLOW_NODE_IDS.has(nodeId)) return '';
    return `
        <div class="workflow-ai-notice" role="note">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <strong>注意：</strong>
            <span>AI可辅助，但不能替代伦理审查、统计判断和导师确认。</span>
        </div>
    `;
}

function buildWorkflowDetailHtml(nodeId, nodeName, html) {
    return `
        <div class="detail-title"><h3 class="serif serif-xs">${nodeId} ${nodeName}</h3></div>
        ${getTutorialIntro(nodeId)}
        <div class="workflow-accordion">
            ${buildWorkflowSection('01', '学习成本', '<div class="workflow-section-copy"><p>' + getWorkflowSectionContent(nodeId, 'learningCost', nodeName) + '</p></div>', true)}
            ${buildWorkflowSection('02', '适用场景', '<div class="workflow-section-copy"><p>' + getWorkflowSectionContent(nodeId, 'useScenarios', nodeName) + '</p></div>', true)}
            ${buildWorkflowSection('03', '你将完成什么', '<div class="workflow-section-copy"><p>' + getWorkflowSectionContent(nodeId, 'accomplishments', nodeName) + '</p></div>', true)}
            ${buildWorkflowSection('04', '推荐工具', '<div class="workflow-section-copy"><p>' + getWorkflowSectionContent(nodeId, 'recommendedTools', nodeName) + '</p></div>', true)}
            ${buildWorkflowSection('05', '视频及图文教程', '<div class="workflow-section-html">' + (html || '<p style="color:var(--muted);text-align:center;padding:2rem 0;">教程内容正在建设中，敬请期待……</p>') + '</div>', true)}
            ${buildWorkflowSection('06', '常见错误', '<div class="workflow-section-copy"><p>' + getWorkflowSectionContent(nodeId, 'commonMistakes', nodeName) + '</p></div>', true)}
            ${buildWorkflowSection('07', '最终产出模板', '<div class="workflow-section-copy"><p>' + getWorkflowSectionContent(nodeId, 'finalTemplate', nodeName) + '</p></div>', true)}
        </div>
        ${buildWorkflowAiNotice(nodeId)}
    `;
}

function escapeWorkflowPrefaceHtml(text) {
    return String(text || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function renderWorkflowPrefaceText(text) {
    const lines = String(text || '').split(/\r?\n/);
    const html = [];
    lines.forEach(function(rawLine) {
        const line = rawLine.trim();
        if (!line) return;
        const clean = escapeWorkflowPrefaceHtml(line.replace(/^#+\s*/, ''));
        if (line.indexOf('写在前面') !== -1) {
            html.push('<h4 class="workflow-preface-title">' + clean + '</h4>');
        } else if (/^###\s*/.test(line)) {
            html.push('<h5 class="workflow-preface-stage">' + clean + '</h5>');
        } else if (line.indexOf('当前节点：') !== -1) {
            html.push('<p class="workflow-preface-node">' + clean + '</p>');
        } else if (line.indexOf('教程标题：') === 0 || line.indexOf('我做了什么：') === 0 || line.indexOf('我得到了什么：') === 0) {
            html.push('<p class="workflow-preface-copy workflow-preface-emphasis">' + clean + '</p>');
        } else {
            html.push('<p class="workflow-preface-copy">' + clean + '</p>');
        }
    });
    return html.join('');
}

function loadWorkflowPreface() {
    const targets = Array.from(document.querySelectorAll('.workflow-preface-content, #workflow-preface'));
    if (!targets.length) return;
    const renderTargets = function(text) {
        const html = renderWorkflowPrefaceText(text);
        targets.forEach(function(target) {
            target.innerHTML = html;
            target.style.display = '';
        });
    };
    const inlineSource = document.getElementById('workflow-preface-source');
    if (inlineSource && inlineSource.textContent.trim()) {
        renderTargets(inlineSource.textContent);
        return;
    }
    fetch('workflow-preface.txt?v=1')
        .then(function(response) {
            if (!response.ok) throw new Error('preface not found');
            return response.text();
        })
        .then(function(text) {
            renderTargets(text);
        })
        .catch(function() {
            targets.forEach(function(target) {
                target.style.display = 'none';
            });
        });
}

function buildWorkflowEmptyState() {
    return `
        <div class="detail-title"><h3 class="serif serif-xs">选择教程节点</h3></div>
        <div id="detail-content">
            <p>请从左侧树状图中选择一个研究方法步骤，右侧将显示详细教程框架。</p>
            <div id="workflow-preface" class="workflow-preface workflow-preface-content" aria-live="polite"></div>
        </div>
    `;
}

function getTutorialTemplate(nodeId, nodeName) {
    return buildWorkflowDetailHtml(nodeId, nodeName, '');
}

// 针对特定节点的图文并茂排版（放在"教程说明"文字下面）
// 教程元数据（供搜索和教程渲染共用）
const tutorialMeta = {
    '1-1': { title: 'Connected Papers+Zotero一键生成&管理文献图谱', desc: '文献堆积却理不清脉络关联，用Connected Papers一键生成核心文献关联图谱，配合Zotero高效管理，快速构建领域知识框架，看清研究版图。' },
    '1-2': { title: 'ChatGPT辅助前沿追踪与选题并多维评估选题可行性', desc: '研究初期方向模糊、前沿信息分散难抓、选题可行性难以判断、容易踩坑，用ChatGPT5快速梳理近五年心理学研究前沿动态并辅助生成选题，帮你精准锁定有价值的研究方向，告别盲目摸索。联网检索近年来心理学研究文献，从创新性和可行性多维度评估并给出具体建议，降低试错成本，让选题更稳妥。' },
    '2-1': { title: 'Deepseek辅助变量关系梳理与框架绘制', desc: '心理学变量关系复杂抽象、难以形成清晰框架，结合AMOS与Deepseek绘制关系图并自动评估模型合理性，把模糊假设变成直观的研究蓝图。' },
    '2-2-1': { title: '实验设计方法手册与ChatGPT智能推荐', desc: '心理学实验设计方法众多却选不准，系统对比6-8种经典设计并附核心期刊文献案例，再用ChatGPT根据你的选题智能推荐最优方案，设计决策有据可依。' },
    '2-2-2': { title: '前沿模型分析方法手册与ChatGPT / Gemini推荐', desc: '心理学研究模型分析方法眼花缭乱、适用场景不清，梳理前沿模型的特点与场景，借助ChatGPT / Gemini匹配研究特征，找到最合适的分析路径，不再无从下手。' },
    '3-1-1': { title: 'Elicit辅助取样方法文献检索', desc: '取样方法选择缺乏文献支撑，用Elicit快速定位各方法的心理学研究权威文献，系统对比特点与适用场景，让取样决策有理有据。' },
    '3-1-2': { title: 'Gemini+SPSS样本代表性评估与偏差识别', desc: '样本代表性不足却难以量化评估，借助Gemini辅助SPSS完成卡方拟合优度检验，自动识别数据偏差，确保样本质量经得起学术推敲。' },
    '3-2': { title: 'G*Power与R语言样本量ChatGPT规划全攻略', desc: '心理学实验样本量算不准、纵向流失没预案，用G*power完成功效分析与流失补偿，再用ChatGPT生成R代码，让样本规划科学高效。' },
    '3-3': { title: 'Gemini/ChatGPT起草知情同意书与Qualtrics伦理设置', desc: '心理学研究伦理审查流程繁琐易遗漏，用Gemini/ChatGPT起草标准知情同意书，配合Qualtrics实现匿名化与合规跳转，全程守护研究伦理底线。' },
    '4-1': { title: '常用心理学量表库汇总与使用教程', desc: '测量工具分散难找、筛选耗时，汇总全网心理学量表库资源，手把手教你快速检索与筛选，精准匹配研究需求的量表。' },
    '4-2-1': { title: 'EpiData与见数平台问卷收集全流程', desc: '问卷发放回收效率低、管理混乱，从纸质问卷排版到EpiData录入，再到见数平台线上编制发布，覆盖心理学问卷数据收集的全流程。' },
    '4-2-2': { title: 'ChatGPT辅助PsychoPy编程与在线化部署', desc: '心理学行为实验编程门槛高、搭建周期长，借助ChatGPT编写PsychoPy代码并生成实验材料，通过见数平台实现线上部署，让实验搭建不再困难。' },
    '4-2-3': { title: 'CEST/Gorilla/Pavlovia实验平台教程', desc: '在线心理学实验平台众多却无从选择，对比CEST、Gorilla和Pavlovia三大平台，从搭建到运行全流程演示，找到最适合你的方案。' },
    '4-3': { title: 'SPSS与Dingo数据清洗、描述性统计实战教程', desc: '原始数据脏乱、清洗步骤繁琐，用SPSS完成缺失值处理、插补与描述统计，再借助Dingo智能清洗，为后续分析准备好干净数据。' },
    '4-4-1': { title: 'ChatSPSS与AI对话实现信效度检验', desc: '信效度检验步骤繁琐、软件操作复杂，用ChatSPSS和AI对话式完成信效度分析，自动生成检验报告，让测量质量评估轻松搞定。' },
    '4-4-2': { title: 'ChatGPT/Gemini辅助共同方法偏差识别与处理', desc: '共同方法偏差隐蔽难察觉，用ChatGPT/Gemini辅助识别数据中的系统性偏差，以共同方法偏差为例给出处理方案，提升研究严谨性。' },
    '4-5-1': { title: 'ChatGPT/Gemini辅助批量中介分析快速上手', desc: '中介分析批量处理耗时费力，借助ChatGPT/Gemini实现批量中介分析，从模型设定到结果输出一气呵成，大幅提升心理学研究统计分析效率。' },
    '4-5-2': { title: 'ChatGPT辅助Mplus与R语言高级统计分析', desc: '高级统计方法上手难、软件总报错，用ChatGPT辅助Mplus模型选择与结果解读，配合Cursor生成R代码分析多层线性模型，攻克心理学研究中的高阶统计分析。' },
    '5-1-1': { title: '多种AI工具绘制研究结果图表', desc: '图表制作反复调整，绘制费时且不够专业，用Gemini、Cursor或Claude等AI工具自动生成结果图表，精准表达心理学研究中的变量关系与实验逻辑，让结果可视化变得直观清晰。' },
    '5-1-2': { title: 'Gemini辅助图表生成与数据解读', desc: '数据解读缺乏思路、表述不规范，用Gemini生成图表并自动撰写符合心理学学术规范的数据解读，从数字到文字无缝衔接，让结果陈述更加规范有力。' },
    '5-2': { title: 'ChatGPT定制目标期刊写作模板', desc: '写作模板千篇一律、期刊风格难把握，用ChatGPT检索目标心理学期刊文献并生成个性化写作模板，匹配期刊特色，让研究报告撰写更有针对性。' },
    '5-3': { title: 'Gemini一键修订论文格式规范', desc: '论文格式反复修改、细节易遗漏，用Gemini一键识别并修正格式问题，从引用规范到排版细节全面把关，让论文格式符合心理学论文发表要求。' }
};

function getRichContent(nodeId, nodeName) {
    const t = tutorialMeta[nodeId];
    if (!t) return '';
    return `<div class="tutorial-rich">
        <div class="rich-divider"></div>
        <div class="rich-block">
            <div class="rich-text">
                <h4>${t.title}</h4>
                <p>${t.desc}</p>
            </div>
        </div>
    </div>`;
}

// 渲染教程详情（优先API，降级硬编码）
function renderDetail(nodeId) {
    const detailDiv = document.getElementById('tutorial-detail');
    if (!detailDiv) return;

    if (!nodeId) {
        detailDiv.innerHTML = buildWorkflowEmptyState();
        loadWorkflowPreface();
        return;
    }

    const node = treeData.find(n => n.id === nodeId);
    if (!node) return;

    // 高亮当前节点
    document.querySelectorAll('.tree-node-level1, .tree-node-level2').forEach(el => {
        if (el.getAttribute('data-id') === nodeId) el.classList.add('active');
        else el.classList.remove('active');
    });

    // 滚动到教程区域顶部
    detailDiv.scrollIntoView({ block: 'start', behavior: 'instant' });

    // 显示加载状态
    detailDiv.innerHTML = '<div style="text-align:center;padding:3rem;color:var(--muted)"><i class="fa-solid fa-spinner fa-pulse"></i><p>加载中……</p></div>';

    // 从API加载
    fetch('/api/tutorials/' + encodeURIComponent(nodeId))
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var tutorialHtml = '';
            if (data.tutorial && data.tutorial.content) {
                tutorialHtml = data.tutorial.content;
            }
            // 始终用结构化布局，API内容放入"视频及图文教程"区域
            detailDiv.innerHTML = buildWorkflowDetailHtml(node.id, node.name, tutorialHtml);
            fixPdfEmbeds();
            initCodeBlocks(detailDiv);
            attachImageModalHandlers();
        })
        .catch(function() {
            // 网络错误 → 降级
            detailDiv.innerHTML = buildWorkflowDetailHtml(node.id, node.name, '');
            fixPdfEmbeds();
            initCodeBlocks(detailDiv);
            attachImageModalHandlers();
        });
}

// ─── PDF.js 动态加载 ───
var _pdfJsReady = false;
var _pdfJsLoading = false;
var _pdfJsQueue = [];

function _loadPdfJs(cb) {
    if (_pdfJsReady) { cb(); return; }
    _pdfJsQueue.push(cb);
    if (_pdfJsLoading) return;
    _pdfJsLoading = true;
    var s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
    s.onload = function() {
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        _pdfJsReady = true;
        _pdfJsQueue.forEach(function(f) { f(); });
        _pdfJsQueue = [];
    };
    s.onerror = function() {
        _pdfJsLoading = false;
        _pdfJsQueue = [];
    };
    document.head.appendChild(s);
}

function _renderPdfJs(viewer, url) {
    var currentPage = 1;
    var totalPages = 0;
    var pdfDoc = null;
    var canvas = viewer.querySelector('.pdfjs-canvas');
    var curEl = viewer.querySelector('.pdfjs-current');
    var totalEl = viewer.querySelector('.pdfjs-total');
    var prevBtn = viewer.querySelector('.pdfjs-prev');
    var nextBtn = viewer.querySelector('.pdfjs-next');
    var loadingEl = viewer.querySelector('.pdfjs-loading');
    var wrap = viewer.querySelector('.pdfjs-canvas-wrap');

    function renderPage(num) {
        if (!canvas || !wrap) return;
        pdfDoc.getPage(num).then(function(page) {
            var scale = wrap.clientWidth / page.getViewport({scale: 1}).width;
            scale = Math.min(1.5, scale);
            var viewport = page.getViewport({scale: scale});
            var dpr = window.devicePixelRatio || 1;
            canvas.width = Math.floor(viewport.width * dpr);
            canvas.height = Math.floor(viewport.height * dpr);
            canvas.style.width = Math.floor(viewport.width) + 'px';
            canvas.style.height = Math.floor(viewport.height) + 'px';
            var ctx = canvas.getContext('2d');
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            page.render({canvasContext: ctx, viewport: viewport});
            curEl.textContent = num;
            prevBtn.disabled = num <= 1;
            nextBtn.disabled = num >= totalPages;
            loadingEl.style.display = 'none';
        }).catch(function() {
            loadingEl.style.display = 'flex';
            loadingEl.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> 页面渲染失败';
        });
    }

    function goPage(delta) {
        var np = currentPage + delta;
        if (np < 1 || np > totalPages) return;
        currentPage = np;
        renderPage(currentPage);
    }

    prevBtn.addEventListener('click', function() { goPage(-1); });
    nextBtn.addEventListener('click', function() { goPage(1); });
    viewer.setAttribute('tabindex', '0');
    viewer.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') { e.preventDefault(); goPage(-1); }
        if (e.key === 'ArrowRight') { e.preventDefault(); goPage(1); }
    });

    // 移动端触摸滑动翻页
    var touchStartX = 0;
    viewer.addEventListener('touchstart', function(e) {
        touchStartX = e.touches[0].clientX;
    }, {passive: true});
    viewer.addEventListener('touchend', function(e) {
        var dx = e.changedTouches[0].clientX - touchStartX;
        if (Math.abs(dx) > 50) goPage(dx < 0 ? 1 : -1);
    });

    pdfjsLib.getDocument(url).promise.then(function(pdf) {
        pdfDoc = pdf;
        totalPages = pdf.numPages;
        totalEl.textContent = totalPages;
        if (totalPages <= 1) {
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
            curEl.parentElement.style.display = 'none';
        }
        renderPage(1);
    }).catch(function() {
        loadingEl.style.display = 'flex';
        loadingEl.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i> PDF 加载失败，请刷新重试';
    });
}

// 用 PDF.js 画布渲染替换浏览器原生 PDF 查看器（消除移动端下载按钮）
function fixPdfEmbeds() {
    var pdfItems = [];

    // 旧 embed PDF → 先摘掉 src 阻止浏览器加载原生查看器
    var embeds = document.querySelectorAll('embed[type="application/pdf"]');
    embeds.forEach(function(embed) {
        var src = embed.getAttribute('src');
        if (src) {
            pdfItems.push({el: embed, url: src});
            embed.removeAttribute('src');
        }
    });

    // iframe PDF（在 .pdf-viewer 容器中）
    var pdfFrames = document.querySelectorAll('.pdf-viewer iframe[src]');
    pdfFrames.forEach(function(iframe) {
        var src = iframe.getAttribute('src');
        if (src && /\.pdf(\?|$)/i.test(src)) {
            pdfItems.push({el: iframe.parentNode, url: src});
            iframe.removeAttribute('src');
        }
    });

    // 清理旧数据中的下载条 / 提示
    var bars = document.querySelectorAll('.apdf-bar, .apdf-note, .apdf-dl');
    for (var i = 0; i < bars.length; i++) {
        bars[i].parentNode.removeChild(bars[i]);
    }

    if (pdfItems.length === 0) return;

    _loadPdfJs(function() {
        pdfItems.forEach(function(item) {
            var viewer = document.createElement('div');
            viewer.className = 'pdfjs-viewer';
            viewer.innerHTML =
                '<div class="pdfjs-toolbar">' +
                    '<button class="pdfjs-btn pdfjs-prev" title="上一页"><i class="fa-solid fa-chevron-left"></i></button>' +
                    '<span class="pdfjs-info"><span class="pdfjs-current">-</span> / <span class="pdfjs-total">-</span></span>' +
                    '<button class="pdfjs-btn pdfjs-next" title="下一页"><i class="fa-solid fa-chevron-right"></i></button>' +
                '</div>' +
                '<div class="pdfjs-canvas-wrap"><canvas class="pdfjs-canvas"></canvas></div>' +
                '<div class="pdfjs-loading" style="display:flex;"><i class="fa-solid fa-spinner fa-pulse"></i> 加载中……</div>';
            if (item.el && item.el.parentNode) {
                item.el.parentNode.replaceChild(viewer, item.el);
            }
            _renderPdfJs(viewer, item.url);
        });
    });
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
        { label: '选题探索', short: '选题探索', drawer: '捕捉研究兴趣 · 追踪学科前沿 · 确定可行选题', stage: 1, light: '#E7D2CC', main: '#DABAB0', dark: '#87736D', desc: '利用AI工具辅助完成前沿文献梳理、研究方向定位及选题可行性评估，解决选题阶段的信息获取与决策问题。' },
        { label: '研究设计', short: '研究设计', drawer: '梳理变量关系 · 选择实验或模型分析方法', stage: 2, light: '#D8B9AE', main: '#C39383', dark: '#795B51', desc: '系统整合实验设计与模型分析方法，借助AI工具实现变量关系梳理与方法智能推荐，协助建立清晰的研究框架与方法路径。' },
        { label: '取样实施', short: '取样实施', drawer: '确定取样方法 · 规划样本量 · 遵循伦理规范', stage: 3, light: '#D1CCC8', main: '#B8B1AB', dark: '#726E6A', desc: '围绕取样方法选择、样本代表性评估、样本量规划及伦理合规操作，提供从方法依据到实践操作的AI工具赋能系统指导。' },
        { label: '数据分析', short: '数据分析', drawer: '收集与清洗数据 · 完成统计与信效度检验', stage: 4, light: '#C6D3D8', main: '#A8BCC3', dark: '#687579', desc: '覆盖量表资源检索、问卷与实验平台部署、数据清洗与核查、信效度检验及各级统计分析，形成完整的AI工具辅助数据处理的工作流。' },
        { label: '结果报告', short: '结果报告', drawer: '呈现与解读结果 · 完成研究报告撰写', stage: 5, light: '#C1C6A8', main: '#A0A779', dark: '#63684B', desc: '聚焦图表生成、数据解读、个性化模板撰写与格式修订，借助AI工具提升研究成果呈现的规范性与效率。' }
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

        const drawerText = seg.drawer || seg.desc;
        const drawerR = (DR_INNER + DR_OUTER) / 2;
        const drawerArc = drawerR * rad(2 * (DRAWER_HALF - 1.5));
        let dfs = drawerArc / (drawerText.length * 1.04);
        dfs = Math.min(13, Math.max(8.5, dfs));
        const dNatural = dfs * 1.04 * drawerText.length;
        const dLenAttr = dNatural > drawerArc ? ` textLength="${drawerArc.toFixed(1)}" lengthAdjust="spacingAndGlyphs"` : '';

        drawersMarkup += `
        <g class="ring-drawer" data-drawer="${i}" style="transform-origin:${CX}px ${CY}px;">
            <path d="${drawerPath(c, DRAWER_HALF)}" fill="url(#draw${i})" stroke="rgba(255,255,255,0.7)" stroke-width="1.1" style="filter:drop-shadow(0 6px 14px rgba(50,50,55,0.22));"/>
            <path d="${drawerPath(c, DRAWER_HALF)}" fill="#ffffff" filter="url(#frostNoise)" pointer-events="none"/>
            <text class="drawer-label" text-anchor="middle" dominant-baseline="central" pointer-events="none" style="font-size:${dfs.toFixed(1)}px;">
                <textPath href="#dtpath${i}" startOffset="50%"${dLenAttr}>${drawerText}</textPath>
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
        return {
            title: seg.panelTitle || seg.label,
            desc: seg.panelDesc || seg.desc,
            stage: seg.stage
        };
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
        if (href === filename || (filename === 'prompt-library.html' && href === 'resources.html')) link.classList.add('active');
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
// ─── 搜索功能 ───
var cachedCards = [];
var cachedResources = {};

function buildSearchIndex() {
    var items = [];
    // 1. 科研流程教程
    treeData.forEach(function(node) {
        var meta = tutorialMeta[node.id];
        items.push({
            type: 'workflow',
            id: node.id,
            title: meta ? meta.title : node.name,
            desc: meta ? meta.desc : '',
            stage: node.stage
        });
    });
    // 2. 审美卡片
    cachedCards.forEach(function(card) {
        items.push({
            type: 'card',
            title: card.title || '',
            desc: card.description || '',
            tag: card.tag || card.category || '',
            category: card.category || '',
            tutorialTitle: card.tutorial_title || '',
            icon: card.icon || 'fa-solid fa-file'
        });
    });
    // 3. 科研资源
    for (var module in cachedResources) {
        if (cachedResources.hasOwnProperty(module)) {
            cachedResources[module].forEach(function(item) {
                items.push({
                    type: 'resource',
                    title: item.name || '',
                    desc: item.description || '',
                    module: module,
                    url: item.link_value || '#'
                });
            });
        }
    }
    return items;
}

function matchScore(item, keyword) {
    var lowerKeyword = keyword.toLowerCase();
    var score = 0;
    var title = (item.title || '').toLowerCase();
    var desc = (item.desc || '').toLowerCase();
    var tag = (item.tag || '').toLowerCase();
    var module = (item.module || '').toLowerCase();
    if (title === lowerKeyword) score += 100;
    else if (title.indexOf(lowerKeyword) === 0) score += 70;
    else if (title.indexOf(lowerKeyword) !== -1) score += 50;
    if (desc.indexOf(lowerKeyword) !== -1) score += 20;
    if (tag.indexOf(lowerKeyword) !== -1) score += 15;
    if (module.indexOf(lowerKeyword) !== -1) score += 10;
    if (item.type === 'workflow') score += 5;
    return score;
}

function performSearch() {
    var keyword = document.getElementById('searchInput').value.trim();
    var dropdown = document.getElementById('searchDropdown');
    closeSearchHotPanel();
    if (!dropdown) {
        // 创建下拉容器
        dropdown = document.createElement('div');
        dropdown.id = 'searchDropdown';
        dropdown.className = 'search-dropdown';
        var searchContainer = document.querySelector('.search-container');
        if (searchContainer) searchContainer.appendChild(dropdown);
    }

    if (!keyword) {
        dropdown.classList.remove('visible');
        return;
    }

    var items = buildSearchIndex();
    var results = [];
    items.forEach(function(item) {
        var score = matchScore(item, keyword);
        if (score > 0) {
            item._score = score;
            results.push(item);
        }
    });
    results.sort(function(a, b) { return b._score - a._score; });
    results = results.slice(0, 12);

    if (results.length === 0) {
        dropdown.innerHTML = '<div class="search-empty">未找到相关结果，请尝试其他关键词</div>';
    } else {
        var groups = { workflow: [], card: [], resource: [] };
        results.forEach(function(r) { groups[r.type].push(r); });
        var groupLabels = { workflow: '科研流程教程', card: '科研审美', resource: '科研资源' };
        var html = '';
        for (var type in groups) {
            if (groups[type].length === 0) continue;
            html += '<div class="search-dropdown-group">' + groupLabels[type] + '</div>';
            groups[type].forEach(function(r) {
                var icon, tagHtml = '';
                if (r.type === 'workflow') {
                    icon = 'fa-solid fa-diagram-project';
                    tagHtml = '<span class="sr-tag">第' + r.stage + '阶段</span>';
                } else if (r.type === 'card') {
                    icon = r.icon;
                    tagHtml = r.tag ? '<span class="sr-tag">' + r.tag + '</span>' : '';
                } else {
                    icon = 'fa-solid fa-link';
                    tagHtml = r.module ? '<span class="sr-tag">' + r.module + '</span>' : '';
                }
                var clickHandler;
                var esc = function(s) { return s.replace(/'/g, "\\'"); };
                if (r.type === 'workflow') {
                    clickHandler = "onclick=\"window.location.href='workflow.html?node=" + encodeURIComponent(r.id) + "'\"";
                } else if (r.type === 'card') {
                    if (r.tutorialTitle) {
                        clickHandler = "onclick=\"openTutorial('" + esc(r.tutorialTitle) + "')\"";
                    } else {
                        clickHandler = "onclick=\"window.location.href='aesthetics.html'\"";
                    }
                } else {
                    if (r.url && r.url !== '#') {
                        clickHandler = "onclick=\"var m=document.getElementById('resource-modal');if(m){showResourceModal('" + esc(r.title) + "','" + esc(r.desc || '暂无简介') + "','" + esc(r.url) + "')}else{window.open('" + esc(r.url) + "','_blank')}\"";
                    } else {
                        clickHandler = "onclick=\"window.location.href='resources.html'\"";
                    }
                }
                html += '<div class="search-result-item" ' + clickHandler + '>' +
                    '<div class="sr-icon"><i class="' + icon + '"></i></div>' +
                    '<div class="sr-body">' +
                        '<div class="sr-title">' + highlightMatch(r.title, keyword) + '</div>' +
                        '<div class="sr-desc">' + (r.desc || '') + '</div>' +
                    '</div>' + tagHtml +
                '</div>';
            });
        }
        dropdown.innerHTML = html;
    }
    dropdown.classList.add('visible');
}

function highlightMatch(text, keyword) {
    if (!text || !keyword) return text || '';
    var escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    var parts = text.split(new RegExp('(' + escaped + ')', 'gi'));
    return parts.map(function(p) {
        return p.toLowerCase() === keyword.toLowerCase() ? '<mark>' + p + '</mark>' : p;
    }).join('');
}

function closeSearchResults() {
    var dropdown = document.getElementById('searchDropdown');
    if (dropdown) dropdown.classList.remove('visible');
}

function closeSearchHotPanel() {
    var panel = document.getElementById('searchHotPanel');
    if (panel) panel.classList.remove('visible');
}

function openSearchHotPanel() {
    var panel = document.getElementById('searchHotPanel');
    var input = document.getElementById('searchInput');
    var results = document.getElementById('searchDropdown');
    if (!panel || !input) return;
    if (input.value.trim()) return;
    if (results && results.classList.contains('visible')) return;
    panel.classList.add('visible');
}

function initSearchHotPanel() {
    var searchContainer = document.querySelector('.search-container');
    var searchInput = document.getElementById('searchInput');
    if (!searchContainer || !searchInput || document.getElementById('searchHotPanel')) return;

    var hotTerms = ['AI提示词', '样本量规划', '数据清洗', '变量关系', '交叉滞后模型', 'Zotero'];
    var panel = document.createElement('div');
    panel.id = 'searchHotPanel';
    panel.className = 'search-hot-panel';
    panel.innerHTML =
        '<div class="search-hot-title"><i class="fa-solid fa-fire"></i><span>热搜词</span></div>' +
        '<div class="search-hot-list">' +
        hotTerms.map(function(term) {
            return '<button type="button" class="search-hot-term" data-term="' + term + '">' + term + '</button>';
        }).join('') +
        '</div>';
    searchContainer.appendChild(panel);

    var hideTimer = null;
    function scheduleHide() {
        clearTimeout(hideTimer);
        hideTimer = setTimeout(closeSearchHotPanel, 120);
    }
    function showPanel() {
        clearTimeout(hideTimer);
        openSearchHotPanel();
    }

    searchContainer.addEventListener('mouseenter', showPanel);
    searchContainer.addEventListener('mouseleave', scheduleHide);
    searchContainer.addEventListener('focusin', showPanel);
    searchContainer.addEventListener('focusout', scheduleHide);
    searchInput.addEventListener('input', function() {
        if (searchInput.value.trim()) closeSearchHotPanel();
        else openSearchHotPanel();
    });
    panel.querySelectorAll('.search-hot-term').forEach(function(button) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            searchInput.value = button.getAttribute('data-term') || '';
            closeSearchHotPanel();
            performSearch();
            searchInput.focus();
        });
    });
}

function handleSearch() {
    performSearch();
}

// 输入事件监听
(function initSearchListeners() {
    var searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') { closeSearchResults(); searchInput.blur(); }
    });
    searchInput.addEventListener('input', function() {
        clearTimeout(searchInput._debounce);
        searchInput._debounce = setTimeout(performSearch, 250);
    });
    searchInput.addEventListener('focus', function() {
        if (searchInput.value.trim()) performSearch();
    });
    // 点击页面其他地方关闭
    document.addEventListener('click', function(e) {
        var dropdown = document.getElementById('searchDropdown');
        var container = document.querySelector('.search-container');
        if (dropdown && container && !container.contains(e.target) && !dropdown.contains(e.target)) {
            closeSearchResults();
        }
    });
})();

// ---------- 滚动堆叠卡片（ScrollStack 的原生 JS 实现，使用窗口滚动） ----------
function initScrollStack() {
    const stack = document.querySelector('.scroll-stack');
    if (!stack) return;
    const cards = Array.from(stack.querySelectorAll('.scroll-stack-card'));
    if (!cards.length) return;
    const endEl = stack.querySelector('.scroll-stack-end');

    // 配置（对应 React 组件的 props 默认值）
    const itemDistance = 100;       // 卡片间距(px)
    const itemScale = 0.03;         // 每张卡片的缩放增量
    const itemStackDistance = 30;   // 堆叠时卡片之间的偏移
    const stackPositionPct = 20;    // 开始堆叠的位置（视口高度百分比）
    const scaleEndPositionPct = 10; // 缩放结束位置
    const baseScale = 0.85;         // 第一张卡片的基础缩放
    const rotationAmount = 0;
    const blurAmount = 3;           // 越靠后的卡片模糊越强，增强景深/层次感

    cards.forEach((card, i) => {
        if (i < cards.length - 1) card.style.marginBottom = itemDistance + 'px';
        card.style.willChange = 'transform, filter';
        card.style.transformOrigin = 'top center';
    });

    // 文档内绝对偏移：基于布局盒(offsetTop)，不受 transform 影响，避免反馈抖动
    const docTop = el => {
        let y = 0;
        while (el) { y += el.offsetTop; el = el.offsetParent; }
        return y;
    };
    const progress = (s, a, b) => (s < a ? 0 : s > b ? 1 : (s - a) / (b - a));

    function update() {
        const scrollTop = window.scrollY || window.pageYOffset;
        const containerHeight = window.innerHeight;
        const stackPositionPx = (stackPositionPct / 100) * containerHeight;
        const scaleEndPositionPx = (scaleEndPositionPct / 100) * containerHeight;
        const endTop = endEl ? docTop(endEl) : 0;

        // 计算当前最顶层卡片索引（用于模糊深度）
        let topCardIndex = 0;
        cards.forEach((c, j) => {
            const jStart = docTop(c) - stackPositionPx - itemStackDistance * j;
            if (scrollTop >= jStart) topCardIndex = j;
        });

        cards.forEach((card, i) => {
            const cardTop = docTop(card);
            const triggerStart = cardTop - stackPositionPx - itemStackDistance * i;
            const triggerEnd = cardTop - scaleEndPositionPx;
            const pinStart = triggerStart;
            const pinEnd = endTop - containerHeight / 2;

            const scaleProgress = progress(scrollTop, triggerStart, triggerEnd);
            const targetScale = baseScale + i * itemScale;
            const scale = 1 - scaleProgress * (1 - targetScale);
            const rotation = rotationAmount ? i * rotationAmount * scaleProgress : 0;

            let blur = 0;
            if (blurAmount && i < topCardIndex) {
                blur = Math.max(0, (topCardIndex - i) * blurAmount);
            }

            let translateY = 0;
            const isPinned = scrollTop >= pinStart && scrollTop <= pinEnd;
            if (isPinned) {
                translateY = scrollTop - cardTop + stackPositionPx + itemStackDistance * i;
            } else if (scrollTop > pinEnd) {
                translateY = pinEnd - cardTop + stackPositionPx + itemStackDistance * i;
            }

            card.style.transform =
                'translate3d(0,' + translateY.toFixed(2) + 'px,0) scale(' +
                scale.toFixed(3) + ') rotate(' + rotation.toFixed(2) + 'deg)';
            card.style.filter = blur > 0 ? 'blur(' + blur.toFixed(2) + 'px)' : '';
        });
    }

    let ticking = false;
    function onScroll() {
        if (!ticking) {
            ticking = true;
            requestAnimationFrame(() => { update(); ticking = false; });
        }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    update();
}

// ---------- 审美页面分类筛选 ----------
function initAestheticFilter() {
    const bar = document.getElementById('filterBar');
    if (!bar) return;
    const tags = bar.querySelectorAll('.filter-tag');
    const cards = document.querySelectorAll('.masonry-card');

    function applyFilter(category) {
        cards.forEach(card => {
            const match = !category || card.getAttribute('data-category') === category;
            card.classList.toggle('filtered-out', !match);
        });
    }

    tags.forEach(tag => {
        tag.addEventListener('click', () => {
            const category = tag.getAttribute('data-filter');
            // 再次点击当前选中的标签则取消筛选，显示全部
            if (tag.classList.contains('active')) {
                tag.classList.remove('active');
                applyFilter(null);
                return;
            }
            tags.forEach(t => t.classList.remove('active'));
            tag.classList.add('active');
            applyFilter(category);
        });
    });
}

// ---------- 瀑布流滚动错落淡入 ----------
function initMasonryReveal() {
    const cards = document.querySelectorAll('.masonry-card');
    if (!cards.length) return;

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduceMotion || !('IntersectionObserver' in window)) {
        cards.forEach(c => c.classList.add('reveal-in'));
        return;
    }

    const observer = new IntersectionObserver((entries, obs) => {
        // 同批次进入视口的卡片按顺序错落延迟，营造瀑布流动感
        const incoming = entries.filter(e => e.isIntersecting);
        incoming.forEach((entry, idx) => {
            const el = entry.target;
            el.style.transitionDelay = (idx * 90) + 'ms';
            el.classList.add('reveal-in');
            obs.unobserve(el);
            setTimeout(() => { el.style.transitionDelay = ''; }, 700 + idx * 90);
        });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    cards.forEach(c => observer.observe(c));
}

function initBlurText() {
    const elements = document.querySelectorAll('.blur-text');
    if (!elements.length) return;

    const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    elements.forEach(el => {
        const lineText = el.dataset.blurLines || '';
        const lines = lineText ? lineText.split('|') : null;
        const text = lines ? lines.join('') : el.textContent;
        el.setAttribute('aria-label', text);
        el.textContent = '';

        let charIndex = 0;
        const appendSegment = (parent, char) => {
            const span = document.createElement('span');
            span.className = 'blur-text-segment';
            span.setAttribute('aria-hidden', 'true');
            span.textContent = char === ' ' ? '\u00A0' : char;
            span.style.animationDelay = `${charIndex * 90}ms`;
            parent.appendChild(span);
            charIndex += 1;
        };

        if (lines) {
            lines.forEach(line => {
                const lineEl = document.createElement('span');
                lineEl.className = 'blur-text-line';
                lineEl.setAttribute('aria-hidden', 'true');
                Array.from(line).forEach(char => appendSegment(lineEl, char));
                el.appendChild(lineEl);
            });
        } else {
            Array.from(text).forEach(char => appendSegment(el, char));
        }

        if (reduceMotion) {
            el.classList.add('in-view');
            return;
        }

        if (!('IntersectionObserver' in window)) {
            el.classList.add('in-view');
            return;
        }

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                entry.target.classList.add('in-view');
                obs.unobserve(entry.target);
            });
        }, { threshold: 0.1, rootMargin: '0px' });

        observer.observe(el);
    });
}

function loadResources() {
    const modules = document.querySelector('.resource-modules');
    if (!modules) return;

    fetch('/api/resources')
        .then(res => res.json())
        .then(data => {
            if (data.modules) cachedResources = data.modules;
            if (!data.modules || !Object.keys(data.modules).length) {
                modules.innerHTML = '';
                return;
            }
            // 保留模块标题结构，只替换链接列表
            const moduleEls = modules.querySelectorAll('.resource-module');
            moduleEls.forEach(el => {
                const titleEl = el.querySelector('.rm-title');
                if (!titleEl) return;
                const moduleName = titleEl.textContent.trim();
                const items = data.modules[moduleName];
                const linksUl = el.querySelector('.rm-links');
                if (!linksUl) return;
                if (!items || !items.length) {
                    linksUl.innerHTML = '';
                    return;
                }
                linksUl.innerHTML = items.map(item => {
                    const name = item.name.replace(/'/g, "\\'");
                    const desc = (item.description || '').replace(/'/g, "\\'");
                    const url = (item.link_value || '#').replace(/'/g, "\\'");
                    return '<li><a href="#" onclick="showResourceModal(\'' + name + '\',\'' + desc + '\',\'' + url + '\');return false"><i class="fa-solid fa-caret-right"></i> ' + item.name + '</a></li>';
                }).join('');
            });
        })
        .catch(() => {});
}

function showResourceModal(name, description, url) {
    const modal = document.getElementById('resource-modal');
    if (!modal) return;
    document.getElementById('resource-modal-title').textContent = name;
    document.getElementById('resource-modal-desc').textContent = description || '暂无简介';
    const btn = document.getElementById('resource-modal-btn');
    btn.href = url;
    btn.style.display = url && url !== '#' ? 'inline-flex' : 'none';
    modal.classList.add('visible');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
}

function closeResourceModal() {
    const modal = document.getElementById('resource-modal');
    if (!modal) return;
    modal.classList.remove('visible');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
}

function initUserPanelShell() {
    const topNav = document.querySelector('.top-nav');
    if (!topNav || document.getElementById('user-avatar-btn')) return;

    const userShell = document.createElement('div');
    userShell.className = 'user-shell';
    userShell.innerHTML = `
        <button type="button" id="user-avatar-btn" class="user-avatar-btn" aria-label="打开用户信息">
            <i class="fa-solid fa-user"></i>
        </button>
    `;
    topNav.appendChild(userShell);

    const panel = document.createElement('div');
    panel.className = 'user-panel-overlay';
    panel.id = 'user-panel-overlay';
    panel.setAttribute('aria-hidden', 'true');
    panel.innerHTML = `
        <aside class="user-panel" aria-label="用户信息侧栏">
            <button type="button" class="user-panel-close" aria-label="关闭用户信息">&times;</button>
            <div class="user-panel-head">
                <div class="user-panel-avatar"><i class="fa-solid fa-user"></i></div>
                <div>
                    <h3>用户信息</h3>
                    <p>当前为空壳演示</p>
                </div>
            </div>
            <div class="user-panel-section">
                <div class="user-info-row"><span>账号状态</span><strong>未连接后端</strong></div>
                <div class="user-info-row"><span>账号名称</span><strong>暂未登录</strong></div>
                <a class="user-auth-link" href="auth.html">成为/已是注册用户</a>
            </div>
            <button type="button" class="user-history-trigger" id="user-history-trigger">
                <i class="fa-solid fa-clock-rotate-left"></i>
                <span>历史记录</span>
                <i class="fa-solid fa-chevron-right"></i>
            </button>
        </aside>
    `;
    document.body.appendChild(panel);

    const historyModal = document.createElement('div');
    historyModal.className = 'user-history-modal';
    historyModal.id = 'user-history-modal';
    historyModal.setAttribute('aria-hidden', 'true');
    historyModal.innerHTML = `
        <div class="user-history-card">
            <button type="button" class="user-history-close" aria-label="关闭历史记录">&times;</button>
            <div class="user-history-icon"><i class="fa-solid fa-clock-rotate-left"></i></div>
            <h3>历史记录</h3>
            <p>这里将显示用户之前的研究路径和浏览记录。</p>
            <div class="user-history-empty">暂无历史记录</div>
        </div>
    `;
    document.body.appendChild(historyModal);

    const openPanel = () => {
        panel.classList.add('visible');
        panel.setAttribute('aria-hidden', 'false');
    };
    const closePanel = () => {
        panel.classList.remove('visible');
        panel.setAttribute('aria-hidden', 'true');
    };
    const openHistory = () => {
        historyModal.classList.add('visible');
        historyModal.setAttribute('aria-hidden', 'false');
    };
    const closeHistory = () => {
        historyModal.classList.remove('visible');
        historyModal.setAttribute('aria-hidden', 'true');
    };

    document.getElementById('user-avatar-btn').addEventListener('click', openPanel);
    panel.querySelector('.user-panel-close').addEventListener('click', closePanel);
    panel.addEventListener('click', function(event) {
        if (event.target === panel) closePanel();
    });
    panel.querySelector('#user-history-trigger').addEventListener('click', openHistory);
    historyModal.querySelector('.user-history-close').addEventListener('click', closeHistory);
    historyModal.addEventListener('click', function(event) {
        if (event.target === historyModal) closeHistory();
    });
}

function loadAestheticCards() {
    const masonry = document.querySelector('.masonry');
    if (!masonry) return;

    fetch('/api/cards')
        .then(res => res.json())
        .then(data => {
            cachedCards = data.cards || [];
            if (!data.cards || !data.cards.length) {
                masonry.innerHTML = '';
                return;
            }
            masonry.innerHTML = '';
            data.cards.forEach(card => {
                const el = document.createElement('a');
                el.href = '#';
                el.className = 'masonry-card';
                el.setAttribute('data-category', card.category || '');

                const h = card.height || 220;
                const iconHtml = '<i class="' + (card.icon || 'fa-solid fa-file') + '"></i>';
                const iconDiv = '<div class="masonry-img" style="height:' + h + 'px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;color:rgba(255,255,255,0.7)">' + iconHtml + '</div>';

                var imgDiv;
                if (card.image_url) {
                    imgDiv = '<div class="masonry-img" style="height:' + h + 'px;"><img src="' + card.image_url + '" style="width:100%;height:100%;object-fit:cover;" alt="' + card.title + '" onerror="this.style.display=\'none\';this.parentElement.style.display=\'flex\';this.parentElement.style.alignItems=\'center\';this.parentElement.style.justifyContent=\'center\';this.parentElement.style.fontSize=\'2.5rem\';this.parentElement.style.color=\'rgba(255,255,255,0.7)\';this.parentElement.innerHTML=\'' + iconHtml + '\';"></div>';
                } else {
                    imgDiv = iconDiv;
                }

                el.setAttribute('onclick', card.tutorial_title
                    ? 'openTutorial(\'' + card.tutorial_title.replace(/'/g, "\\'") + '\');return false'
                    : '');

                el.innerHTML = imgDiv +
                    '<div class="masonry-body"><h4>' + card.title + '</h4><p>' + card.description + '</p><span class="tag">' + (card.tag || '') + '</span></div>';
                masonry.appendChild(el);
            });
            setTimeout(() => { initMasonryReveal(); initAestheticFilter(); }, 50);
        })
        .catch(() => {});
}

document.addEventListener('DOMContentLoaded', () => {
    if (!window.location.pathname.includes('index.html') && !window.location.pathname.endsWith('/')) {
        checkLogin();
    }
    highlightNav();
    loadResources();
    loadAestheticCards();
    initMasonryReveal();
    initScrollStack();
    initBlurText();
    initUserPanelShell();
    initSearchHotPanel();
    loadWorkflowPreface();
    // 资源弹窗关闭按钮
    const rmClose = document.querySelector('.resource-modal-close');
    if (rmClose) rmClose.addEventListener('click', closeResourceModal);
    document.addEventListener('click', (e) => {
        const nav = document.getElementById('navLinks');
        const toggle = document.querySelector('.nav-toggle');
        if (nav && nav.classList.contains('open') && !nav.contains(e.target) && !toggle?.contains(e.target)) {
            nav.classList.remove('open');
        }
        // 点击弹窗外部关闭
        const resourceModal = document.getElementById('resource-modal');
        if (resourceModal && resourceModal.classList.contains('visible') && !resourceModal.querySelector('.resource-modal-card').contains(e.target) && !e.target.closest('.rm-links a')) {
            closeResourceModal();
        }
    });

    // ─── 统计追踪 ───
    trackStatsEvent('page_view', window.location.pathname || '/');
    initPromptCopyTracking();
});

// ─── 统计追踪功能 ───
function trackStatsEvent(eventType, eventKey) {
    try {
        fetch('/api/stats/track', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event_type: eventType, event_key: eventKey || '' }),
        }).catch(function() {});
    } catch(e) {}
}

// ─── 用户浏览历史追踪 ───
function getUserToken() {
    try {
        return sessionStorage.getItem('xinyanfang_access_token') || null;
    } catch(e) { return null; }
}

function isLoggedIn() {
    return !!getUserToken();
}

function trackUserHistory(eventType, eventKey, eventLabel) {
    var token = getUserToken();
    if (!token) return;
    try {
        fetch('/api/user/history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token,
            },
            body: JSON.stringify({ event_type: eventType, event_key: eventKey || '', event_label: eventLabel || '' }),
        }).catch(function() {});
    } catch(e) {}
}

function loadUserHistory(limit) {
    var token = getUserToken();
    if (!token) return Promise.resolve([]);
    return fetch('/api/user/history?limit=' + (limit || 30), {
        headers: { 'Authorization': 'Bearer ' + token },
    })
        .then(function(r) { return r.json(); })
        .then(function(data) { return data.history || []; })
        .catch(function() { return []; });
}

// 资源点击追踪（在 showResourceModal 中调用）
var _origShowResourceModal = showResourceModal;
showResourceModal = function(name, description, url) {
    trackStatsEvent('resource_click', name);
    trackUserHistory('resource_click', name, name);
    _origShowResourceModal(name, description, url);
};

// 教程观看追踪：在 renderDetail 成功后调用
var _origRenderDetail = renderDetail;
renderDetail = function(nodeId) {
    if (nodeId) {
        trackStatsEvent('tutorial_view', nodeId);
        var node = treeData && treeData.find(function(n) { return n.id === nodeId; });
        trackUserHistory('tutorial_view', nodeId, node ? node.name : nodeId);
    }
    _origRenderDetail(nodeId);
};

// 提示词复制追踪：监听教程内容区的复制事件
var _promptCopyTimer = null;
function initPromptCopyTracking() {
    document.addEventListener('copy', function(e) {
        var sel = window.getSelection();
        if (!sel || !sel.toString().trim()) return;
        var text = sel.toString().trim();
        // 只追踪超过20个字符的复制（过滤短文本和误触）
        if (text.length < 20) return;
        // 检查是否在教程内容区域
        var container = e.target.closest('#tutorial-detail, #article-body, .tutorial-rich, .rich-text');
        if (!container) return;
        clearTimeout(_promptCopyTimer);
        _promptCopyTimer = setTimeout(function() {
            var label = text.substring(0, 80).replace(/\n/g, ' ');
            trackStatsEvent('prompt_copy', label);
        }, 500);
    });
}

// ─── 代码块 + 复制按钮 ───
function initCodeBlocks(root) {
    root = root || document;

    // 1. 处理现有 <pre> 标签
    var pres = root.querySelectorAll('pre');
    pres.forEach(function(pre) {
        if (pre.closest('.code-block')) return;
        wrapCodeBlock(pre);
    });

    // 2. 检测 <p> 标签中的代码内容（Mplus语法 / R代码 / SPSS语法等）
    var containers = root.querySelectorAll('#tutorial-detail, #article-body, .tutorial-rich, .rich-text, .atext, .workflow-section__body');
    if (!containers.length) containers = [root];

    containers.forEach(function(container) {
        var allP = container.querySelectorAll('p');
        var codeGroups = [];
        var currentGroup = [];

        allP.forEach(function(p) {
            if (p.closest('.code-block')) return;
            var text = p.textContent.trim();
            if (!text) {
                // 空行不中断代码组（Mplus代码中常有空行分隔段落）
                if (currentGroup.length) currentGroup.push(p);
                return;
            }
            if (isCodeLine(text)) {
                currentGroup.push(p);
            } else {
                if (currentGroup.length) { codeGroups.push(currentGroup); currentGroup = []; }
            }
        });
        if (currentGroup.length) codeGroups.push(currentGroup);

        // 包装代码组（至少2行才算代码块）
        codeGroups.forEach(function(group) {
            if (group.length < 2) return;
            var codeText = group.map(function(p) { return p.textContent; }).join('\n');
            var pre = document.createElement('pre');
            pre.innerHTML = '<code>' + escapeHtml(codeText) + '</code>';
            group[0].parentNode.insertBefore(pre, group[0]);
            group.forEach(function(p) { p.parentNode.removeChild(p); });
            wrapCodeBlock(pre);
        });
    });

    function isCodeLine(text) {
        if (!text) return false;
        // Mplus/R/SPSS 代码特征
        if (/^(TITLE|DATA|VARIABLE|NAMES|MISSING|USEVARIABLES|MODEL|ANALYSIS|OUTPUT|CLASSES|SAVEDATA|DEFINE|FILE|TYPE|ESTIMATOR|IDVARIABLE|CLUSTER|WITHIN|BETWEEN|AUXILIARY|WEIGHT|STRATIFICATION)\b[ :;]/i.test(text)) return true;
        if (/^[\s]*[A-Z][A-Z ]{3,}[ :;]/.test(text)) return true;  // 全大写关键字后跟冒号分号
        if (/[;]$/.test(text) && text.length < 120) return true;     // 分号结尾的短行
        if (/^\s{2,}[A-Za-z]/.test(text) && text.length < 150) return true;  // 缩进开头的短行
        if (/^(MODEL |ANALYSIS |OUTPUT )/i.test(text)) return true;
        return false;
    }

    function wrapCodeBlock(codeEl) {
        var wrapper = document.createElement('div');
        wrapper.className = 'code-block';

        var header = document.createElement('div');
        header.className = 'code-block__header';

        var label = document.createElement('span');
        label.className = 'code-block__label';
        label.innerHTML = '<i class="fa-solid fa-code"></i> 代码';

        var copyBtn = document.createElement('button');
        copyBtn.className = 'code-block__copy';
        copyBtn.type = 'button';
        copyBtn.innerHTML = '<i class="fa-solid fa-copy"></i> 复制';
        copyBtn.addEventListener('click', function() {
            var codeEl2 = wrapper.querySelector('code') || wrapper.querySelector('pre');
            var text = (codeEl2 ? codeEl2.textContent : '').trim();
            if (!text) return;
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(function() {
                    setCopied(copyBtn);
                }).catch(function() {
                    fallbackCopy(text, copyBtn);
                });
            } else {
                fallbackCopy(text, copyBtn);
            }
        });

        header.appendChild(label);
        header.appendChild(copyBtn);
        wrapper.appendChild(header);
        codeEl.parentNode.insertBefore(wrapper, codeEl);
        wrapper.appendChild(codeEl);
    }

    function setCopied(btn) {
        btn.classList.add('copied');
        btn.innerHTML = '<i class="fa-solid fa-check"></i> 已复制';
        setTimeout(function() {
            btn.classList.remove('copied');
            btn.innerHTML = '<i class="fa-solid fa-copy"></i> 复制';
        }, 2000);
    }

    function fallbackCopy(text, btn) {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        ta.style.top = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); setCopied(btn); } catch(e) {}
        document.body.removeChild(ta);
    }

    function escapeHtml(str) {
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }
}
