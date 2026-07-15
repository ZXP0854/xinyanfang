function escapePromptHtml(value) {
    return String(value || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function getPromptCategories() {
    return window.PROMPT_LIBRARY_DATA || [];
}

function getPromptItem(id) {
    const categories = getPromptCategories();
    for (const category of categories) {
        const item = category.items.find(entry => entry.id === id);
        if (item) return { category, item };
    }
    return null;
}

function buildPromptTreeHTML() {
    return getPromptCategories().map(category => {
        const links = category.items.map(item => {
            return `<li><a href="#" class="tree-node-level2 prompt-tree-node" data-prompt-id="${item.id}">${escapePromptHtml(item.title)}</a></li>`;
        }).join('');
        return `
            <div class="prompt-tree-group" data-category-id="${category.id}">
                <div class="stage-title prompt-category-title">
                    <span>${escapePromptHtml(category.name)}</span>
                    <button type="button" class="prompt-category-toggle" aria-expanded="true" aria-label="收起${escapePromptHtml(category.name)}">
                        <i class="fa-solid fa-chevron-up"></i>
                    </button>
                </div>
                <ul class="prompt-category-list">${links}</ul>
            </div>
        `;
    }).join('');
}

function renderPromptDetail(id) {
    const detail = document.getElementById('prompt-detail');
    if (!detail) return;

    document.querySelectorAll('.prompt-tree-node').forEach(node => {
        node.classList.toggle('active', node.getAttribute('data-prompt-id') === id);
    });

    const resolved = getPromptItem(id);
    if (!resolved) {
        detail.innerHTML = `
            <div class="detail-title"><h3 class="serif serif-xs">选择提示词分支</h3></div>
            <div class="prompt-empty">
                <p>请从左侧树状分支中选择一个科研 AI 使用场景，右侧将显示可直接复制的提示词。</p>
            </div>
        `;
        return;
    }

    const prompt = escapePromptHtml(resolved.item.prompt);
    detail.innerHTML = `
        <div class="detail-title">
            <div class="prompt-detail-kicker">${escapePromptHtml(resolved.category.name)}</div>
            <h3 class="serif serif-xs">${escapePromptHtml(resolved.item.title)}</h3>
        </div>
        <div class="prompt-card">
            <div class="prompt-card__header">
                <span><i class="fa-solid fa-wand-magic-sparkles"></i> 推荐 Prompt</span>
                <button type="button" class="prompt-copy-btn" data-prompt-id="${resolved.item.id}">
                    <i class="fa-regular fa-copy"></i> 复制提示词
                </button>
            </div>
            <pre class="prompt-text">${prompt}</pre>
        </div>
    `;

    const copyBtn = detail.querySelector('.prompt-copy-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', function() {
            copyPromptText(resolved.item.prompt, copyBtn, resolved.item.title);
        });
    }
}

function copyPromptText(text, button, title) {
    const setCopied = () => {
        button.innerHTML = '<i class="fa-solid fa-check"></i> 已复制';
        window.setTimeout(() => {
            button.innerHTML = '<i class="fa-regular fa-copy"></i> 复制提示词';
        }, 1600);
        if (typeof trackStatsEvent === 'function') {
            trackStatsEvent('prompt_copy', title || text.slice(0, 80));
        }
    };

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(setCopied).catch(() => fallbackCopyPrompt(text, setCopied));
    } else {
        fallbackCopyPrompt(text, setCopied);
    }
}

function fallbackCopyPrompt(text, done) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    done();
}

function initPromptLibrary() {
    const tree = document.getElementById('prompt-tree-container');
    if (!tree) return;

    tree.innerHTML = buildPromptTreeHTML();
    tree.querySelectorAll('.prompt-category-toggle').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            event.stopPropagation();
            const group = this.closest('.prompt-tree-group');
            if (!group) return;
            const collapsed = group.classList.toggle('is-collapsed');
            this.setAttribute('aria-expanded', String(!collapsed));
            this.setAttribute('aria-label', (collapsed ? '展开' : '收起') + group.querySelector('.prompt-category-title span').textContent);
            this.innerHTML = collapsed
                ? '<i class="fa-solid fa-chevron-down"></i>'
                : '<i class="fa-solid fa-chevron-up"></i>';
        });
    });
    tree.querySelectorAll('.prompt-tree-node').forEach(node => {
        node.addEventListener('click', function(event) {
            event.preventDefault();
            renderPromptDetail(this.getAttribute('data-prompt-id'));
        });
    });

    const params = new URLSearchParams(window.location.search);
    const target = params.get('prompt');
    if (target && getPromptItem(target)) {
        renderPromptDetail(target);
        return;
    }
    renderPromptDetail(null);
}
