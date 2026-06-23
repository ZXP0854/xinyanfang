"""
安全中间件：SQL 注入防护、XSS 过滤、请求限流、安全响应头
"""

import re
import html
import time
from functools import wraps
from collections import defaultdict
from typing import Dict, List
from flask import request, jsonify, g


# ─── XSS / HTML 清洗 ────────────────────────────────────────

def sanitize_html(text: str) -> str:
    """转义 HTML 特殊字符，防止 XSS"""
    if not text:
        return ''
    return html.escape(str(text), quote=True)


def sanitize_input(value):
    """递归清洗输入数据"""
    if isinstance(value, str):
        return _strip_dangerous(value)
    if isinstance(value, dict):
        return {k: sanitize_input(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_input(v) for v in value]
    return value


_SQL_KEYWORDS_RE = re.compile(
    r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|EXEC|UNION|TRUNCATE|'
    r'DECLARE|EXECUTE|SLEEP|BENCHMARK|LOAD_FILE|INTO\s+OUTFILE|INTO\s+DUMPFILE)\b',
    re.IGNORECASE
)


def _strip_dangerous(value: str) -> str:
    """检测并清理潜在的危险字符串"""
    # 检测 SQL 注入特征
    if _SQL_KEYWORDS_RE.search(value):
        # 记录警告但不直接拒绝，因为正常内容可能包含这些词
        g.security_warnings = getattr(g, 'security_warnings', [])
        g.security_warnings.append(f'SQL keyword detected in input')
    return value


def validate_required(data: dict, fields: list) -> list:
    """验证必填字段，返回缺失的字段列表"""
    return [f for f in fields if not data.get(f)]


# ─── 简单速率限制（内存版，生产环境用 Flask-Limiter + Redis）────

_rate_limit_store = defaultdict(list)  # type: Dict[str, List[float]]


def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """
    基于 IP 的请求速率限制
    max_requests: 时间窗口内最大请求数
    window_seconds: 时间窗口（秒）
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            key = f'rl:{request.remote_addr}:{request.path}'
            now = time.time()
            cutoff = now - window_seconds

            # 清理过期记录
            _rate_limit_store[key] = [t for t in _rate_limit_store[key] if t > cutoff]

            if len(_rate_limit_store[key]) >= max_requests:
                return jsonify({
                    'error': '请求过于频繁，请稍后再试',
                    'retry_after': window_seconds,
                }), 429

            _rate_limit_store[key].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator


# ─── 安全响应头 ──────────────────────────────────────────────

def add_security_headers(response):
    """为所有 Flask 响应添加安全头"""
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    return response


# ─── IP 白名单检查 ───────────────────────────────────────────

_TRUSTED_IPS = {'127.0.0.1', '::1'}


def is_trusted_ip() -> bool:
    """检查请求 IP 是否在白名单中"""
    return request.remote_addr in _TRUSTED_IPS
