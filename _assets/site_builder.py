"""
Crystal IG 运营站点构建器（统一工具）
======================================
集中管理 SITE_STRUCTURE，并提供 4 个子命令：
- convert : MD → HTML 转换
- fix     : 修复无侧边栏的 HTML 页面（重新包入框架）
- refresh : 刷新所有内容页的侧边栏（统一应用最新 SITE_STRUCTURE）
- modules : 生成每个模块的 index.html 入口页

历史脚本 convert.py / fix_layout.py / refresh_sidebars.py / gen_modules.py 仍保留为薄包装，
以兼容旧的调用方式。新代码请使用 site_builder.py。
"""

import argparse
import os
import re
import sys
from pathlib import Path

try:
    import markdown as _markdown  # 仅 convert 需要
except ImportError:
    _markdown = None

ROOT = Path(__file__).resolve().parent.parent
CSS_REL = "_assets/style.css"
SITE_STRUCTURE = [
    {
        "id": "product", "num": "01", "name": "产品素材库", "name_en": "Product Assets",
        "icon": "🖼️", "desc": "413 张手链产品图，按系列 + 卖点分类筛选",
        "files": [
            ("product-gallery", "📷 图库浏览器", "系列 / 卖点筛选 + 灯箱预览",
             None, "09-product-assets/index.html"),
        ],
    },
    {
        "id": "calendar", "num": "02", "name": "内容日历", "name_en": "Content Calendar",
        "icon": "📅", "desc": "2 周循环排期、4 周启动计划、每日 1 小时任务",
        "files": [
            ("calendar-cycle", "2 周循环模板", "7 个卖点 2 周轮换的核心节奏",
             "01-content-calendar/two-week-cycle.md", "01-content-calendar/two-week-cycle.html"),
            ("calendar-launch", "4 周启动计划", "从 0 到 1000 粉的详细排期",
             "01-content-calendar/four-week-launch-plan.md", "01-content-calendar/four-week-launch-plan.html"),
            ("calendar-daily", "每日 1 小时清单", "工作日 1 小时 / 周末 2 小时的具体分配",
             "01-content-calendar/daily-hour-checklist.md", "01-content-calendar/daily-hour-checklist.html"),
        ],
    },
    {
        "id": "hashtag", "num": "03", "name": "标签生成器", "name_en": "Hashtag Generator",
        "icon": "🏷️", "desc": "交互式 HTML 工具，按卖点 + 地域生成 13 个分级标签",
        "files": [
            ("hashtag-tool", "✨ 打开工具", "双击 index.html 开始使用",
             None, "02-hashtag-generator/index.html"),
            ("hashtag-readme", "使用说明", "标签分级策略和放置方法",
             "02-hashtag-generator/README.md", "02-hashtag-generator/README.html"),
        ],
    },
    {
        "id": "templates", "num": "04", "name": "文案模板库", "name_en": "Copy Templates",
        "icon": "✍️", "desc": "7 个卖点 × 5 种格式的现成中英文文案模板",
        "files": [
            ("tpl-1", "🌟 显白 Skin Brightening", "颜值驱动、冲动种草",
             "03-copy-templates/01-skin-brightening.md", "03-copy-templates/01-skin-brightening.html"),
            ("tpl-2", "🌿 天然 Natural", "信任背书、个人旅程叙述",
             "03-copy-templates/02-natural.md", "03-copy-templates/02-natural.html"),
            ("tpl-3", "💎 疗愈石 Healing Stones", "能量、脉轮、灵性受众",
             "03-copy-templates/03-healing-stones.md", "03-copy-templates/03-healing-stones.html"),
            ("tpl-4", "🍀 好运 Good Luck", "风水、旺运、转化最强",
             "03-copy-templates/04-good-luck.md", "03-copy-templates/04-good-luck.html"),
            ("tpl-5", "🧘 水晶疗愈 Crystal Healing", "减压、失眠、专注、情绪",
             "03-copy-templates/05-crystal-healing.md", "03-copy-templates/05-crystal-healing.html"),
            ("tpl-6", "👐 手工制作 Handmade", "温度、礼物、独一无二",
             "03-copy-templates/06-handmade.md", "03-copy-templates/06-handmade.html"),
            ("tpl-7", "💫 DIY 叠戴 Stack", "搭配公式、拉高客单",
             "03-copy-templates/07-diy-stack.md", "03-copy-templates/07-diy-stack.html"),
        ],
    },    {
        "id": "drafts", "num": "05", "name": "内容草稿", "name_en": "Content Drafts",
        "icon": "📝", "desc": "6 个系列 × 5 篇递进式种草（含完整文案 + 图片描述）",
        "files": [
            ("draft-launch", "🚀 启动 7 天内容", "新账号前 7 条内容",
             "04-content-drafts/00-launch-week.md", "04-content-drafts/00-launch-week.html"),
            ("draft-funnel", "🎯 5 篇递进式框架", "所有系列共用的种草方法论",
             "04-content-drafts/01-funnel-framework.md", "04-content-drafts/01-funnel-framework.html"),
            ("draft-1", "🌟 显白系列", "5 篇递进：认知 → 信任 → 共鸣 → 欲望 → 转化",
             "04-content-drafts/series-01-skin-brightening.md", "04-content-drafts/series-01-skin-brightening.html"),
            ("draft-2", "🌿 天然系列", "我的水晶旅程（第一人称叙述）",
             "04-content-drafts/series-02-natural.md", "04-content-drafts/series-02-natural.html"),
            ("draft-3", "🧘 疗愈 + 水晶疗愈系列", "10 篇：脉轮 + 日常情绪",
             "04-content-drafts/series-03-healing.md", "04-content-drafts/series-03-healing.html"),
            ("draft-4", "🍀 好运系列", "事业 / 财运 / 平安 / 学业",
             "04-content-drafts/series-04-luck.md", "04-content-drafts/series-04-luck.html"),
            ("draft-5", "👐 手工制作系列", "过程沉浸 + 礼物属性",
             "04-content-drafts/series-05-handmade.md", "04-content-drafts/series-05-handmade.html"),
            ("draft-6", "💫 DIY 叠戴系列", "搭配公式 + 多件客单",
             "04-content-drafts/series-06-diy-stack.md", "04-content-drafts/series-06-diy-stack.html"),
        ],
    },
    {
        "id": "tracking", "num": "06", "name": "数据追踪", "name_en": "Data Tracking",
        "icon": "📊", "desc": "数据看板、KPI 定义、周月记录 CSV",
        "files": [
            ("track-dashboard", "📈 数据看板 Dashboard", "浏览器内可视化",
             None, "05-data-tracking/dashboard.html"),
            ("track-kpi", "KPI 定义", "北极星指标 + 7 个二级指标",
             "05-data-tracking/kpi-definitions.md", "05-data-tracking/kpi-definitions.html"),
        ],
    },
    {
        "id": "automation", "num": "07", "name": "IG 自动化", "name_en": "IG Automation",
        "icon": "🤖", "desc": "fetch_insights.py + 调度指南（Meta Graph API）",
        "files": [
            ("auto-guide", "📖 完整配置指南", "Token + 调度 + 错误处理",
             "06-instagram-automation/scheduling-guide.md", "06-instagram-automation/scheduling-guide.html"),
            ("auto-readme", "快速说明", "一句话总结 + 链接",
             "06-instagram-automation/README.md", "06-instagram-automation/README.html"),
        ],
    },
    {
        "id": "assets", "num": "08", "name": "素材库", "name_en": "Assets",
        "icon": "🖼️", "desc": "找图提示词库（按卖点 + 场景分组）",
        "files": [
            ("assets-prompts", "找图提示词库", "按 7 个卖点 × 5 种场景",
             "_assets/image-prompts.md", "_assets/image-prompts.html"),
        ],
    },
    {
        "id": "tiktok", "num": "09", "name": "TikTok 发布", "name_en": "TikTok Publisher",
        "icon": "🎬", "desc": "C 方案：脚本生成每日发布包，人工 TK app 粘贴发布",
        "files": [
            ("tiktok-index", "🎬 今日发布包", "14 天排期 + 进度看板",
             None, "08-tiktok-publisher/index.html"),
            ("tiktok-readme", "📖 使用说明", "C 方案完整流程",
             None, "08-tiktok-publisher/README.html"),
        ],
    },
]

FOLDER_MAP = {
    "product": "09-product-assets",
    "calendar": "01-content-calendar",
    "hashtag": "02-hashtag-generator",
    "templates": "03-copy-templates",
    "drafts": "04-content-drafts",
    "tracking": "05-data-tracking",
    "automation": "06-instagram-automation",
    "assets": "_assets",
    "tiktok": "08-tiktok-publisher",
}

# 自建页面：这些目录的 index.html 是手写的交互页/图库页，
# modules 子命令不得用模块入口页模板覆盖它们。
SELF_MANAGED_INDEX = (
    "02-hashtag-generator",
    "05-data-tracking",
    "09-product-assets",
)

def rel_path(from_file, to_file):
    from_dir = (ROOT / from_file).parent
    to_path = ROOT / to_file
    rel = os.path.relpath(to_path, from_dir)
    return rel.replace(os.sep, "/")


def make_sidebar(current_file):
    home_rel = rel_path(current_file, "index.html")
    parts = [f'<a href="{home_rel}" class="sidebar-home">🏠 首页 Home</a>']
    for module in SITE_STRUCTURE:
        parts.append('<div class="nav-module">')
        parts.append(f'<div class="nav-module-header">{module["icon"]} {module["num"]} {module["name"]}</div>')
        parts.append('<div class="nav-module-items">')
        for _fid, fname, _fdesc, _md, hpath in module["files"]:
            if hpath is None:
                continue
            rel = rel_path(current_file, hpath)
            active = "active" if current_file == hpath else ""
            parts.append(f'<a href="{rel}" class="nav-item {active}">{fname}</a>')
        parts.append('</div></div>')
    return "\n".join(parts)


def make_breadcrumb(current_file):
    if not current_file or current_file == "index.html":
        return '<span class="current">首页</span>'
    home_rel = rel_path(current_file, "index.html")
    parts = [f'<a href="{home_rel}">首页</a>']
    for module in SITE_STRUCTURE:
        for _fid, fname, _fdesc, _md, hpath in module["files"]:
            if hpath == current_file:
                parts.append(f'<span class="sep">›</span><span class="current">{fname}</span>')
                return '<div class="breadcrumb">' + "".join(parts) + '</div>'
    return '<div class="breadcrumb">' + "".join(parts) + '</div>'


def make_page_nav(current_file):
    flat = []
    for module in SITE_STRUCTURE:
        for _fid, fname, _fdesc, _md, hpath in module["files"]:
            if hpath:
                flat.append((hpath, fname))
    cur_idx = next((i for i, (p, _) in enumerate(flat) if p == current_file), None)
    if cur_idx is None:
        return ""
    prev_link = next_link = ""
    if cur_idx > 0:
        prev_path, prev_name = flat[cur_idx - 1]
        prev_link = f'<a href="{rel_path(current_file, prev_path)}" class="prev"><span class="nav-label">← 上一篇</span>{prev_name}</a>'
    if cur_idx < len(flat) - 1:
        next_path, next_name = flat[cur_idx + 1]
        next_link = f'<a href="{rel_path(current_file, next_path)}" class="next"><span class="nav-label">下一篇 →</span>{next_name}</a>'
    return f'<div class="page-nav">{prev_link}{next_link}</div>'

def render_page(title, content_html, current_file):
    sidebar = make_sidebar(current_file)
    breadcrumb = make_breadcrumb(current_file)
    page_nav = make_page_nav(current_file)
    css_rel = rel_path(current_file, CSS_REL) if current_file else CSS_REL
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · Crystal IG 运营</title>
<link rel="stylesheet" href="{css_rel}">
</head>
<body>
<button class="mobile-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰ 菜单</button>
<div class="layout">
<aside class="sidebar">
<div class="sidebar-brand">
<h1>💎 Crystal IG 运营</h1>
<div class="sub">内容运营体系 v1.0</div>
</div>
{sidebar}
</aside>
<main class="main">
<header class="header">
{breadcrumb}
</header>
<article class="content">
{content_html}
{page_nav}
</article>
<footer class="footer">
Crystal Bracelet IG 运营体系 · 由 <a href="{rel_path(current_file, 'index.html')}">ins-opt</a> 仓库生成 · 最近更新 2026-08
</footer>
</main>
</div>
</body>
</html>
"""


def _strip_old_wrappers(raw):
    """移除已存在的侧边栏、页脚、面包屑容器（迭代清理，避免多次 refresh 嵌套）"""
    pattern_aside = re.compile(r'<aside\s+class="sidebar">.*?</aside>', re.DOTALL)
    pattern_aside_any = re.compile(r'<aside[^>]*>.*?</aside>', re.DOTALL)
    pattern_header = re.compile(r'<header\s+class="header">.*?</header>', re.DOTALL)
    pattern_footer = re.compile(r'<footer\s+class="footer">.*?</footer>', re.DOTALL)
    # 迭代去掉嵌套残留
    for _ in range(10):
        before = raw
        raw = pattern_aside.sub('', raw)
        raw = pattern_aside_any.sub('', raw)
        raw = pattern_header.sub('', raw)
        raw = pattern_footer.sub('', raw)
        if raw == before:
            break
    # 清理可能残留的裸 </aside>
    raw = re.sub(r'</aside>', '', raw)
    return raw


BRAND_H1_PATTERNS = [
    re.compile(r'<h1>\s*💎\s*Crystal IG 运营\s*</h1>'),
    re.compile(r'<div class="sub">\s*内容运营体系 v1\.0\s*</div>'),
    re.compile(r'<a href="[^"]*" class="sidebar-home">.*?</a>'),
    re.compile(r'<div class="nav-module">.*?</div>\s*</div>', re.DOTALL),
    re.compile(r'<div class="nav-module">.*?</div></div>', re.DOTALL),
]


def _strip_brand_block(raw):
    """移除嵌套在 body 里的 sidebar-brand + 旧侧边栏导航块。多次 refresh 后可能有多份。"""
    for pat in BRAND_H1_PATTERNS:
        raw = pat.sub('', raw)
    # 清除可能残留的空 div 配对
    for _ in range(3):
        before = raw
        raw = re.sub(r'<div class="nav-module">\s*</div>\s*</div>', '', raw)
        raw = re.sub(r'<div class="nav-module-header">[^<]*</div>\s*<div class="nav-module-items">\s*</div></div>', '', raw)
        if raw == before:
            break
    return raw


def _strip_residual_wrappers(raw):
    """清理 body 里的残留包装伪标签：未配对的 <main>/<aside>/<article>/<header> 开闭标签"""
    for tag in ("main", "aside", "header", "footer"):
        raw = re.sub(rf'<{tag}\s+class="{tag}">', "", raw)
        raw = re.sub(rf'<{tag}>', "", raw)
        raw = re.sub(rf'</{tag}>', "", raw)
    raw = re.sub(r'<article\s+class="content">', "", raw)
    raw = re.sub(r"<article[^>]*>", "", raw)
    raw = re.sub(r"</article>", "", raw)
    return raw


def wrap_with_layout(html_path):
    full_path = ROOT / html_path
    raw = full_path.read_text(encoding="utf-8")
    raw = _strip_old_wrappers(raw)
    raw = _strip_brand_block(raw)
    # 取最后一个完整 <article class="content">...</article> 的内容
    article_matches = list(re.finditer(r'<article class="content">(.*?)</article>', raw, re.DOTALL))
    article_match = article_matches[-1] if article_matches else None
    if article_match:
        body_content = article_match.group(1).strip()
        # 页面标题 = 第一个 H1（brand H1 已经被清掉）
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', body_content, re.DOTALL)
        if h1_match:
            h1_text = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
        else:
            # body 没有 h1，从 SITE_STRUCTURE 取默认标题，并补到 body 顶部
            h1_text = "Crystal IG 运营"
            for _mod in SITE_STRUCTURE:
                for _fid, _fname, _fdesc, _md, _hpath in _mod["files"]:
                    if _hpath == html_path:
                        h1_text = _fname
                        break
                if h1_text != "Crystal IG 运营":
                    break
            body_content = "<h1>" + h1_text + "</h1>\n" + body_content
        # 移除 body 里残留的 page-nav（让 render_page 重新生成）
        body_content = re.sub(r'<div class="page-nav">.*?</div>', '', body_content, flags=re.DOTALL).strip()
        # 如果 body 包含多个 <article>，取最后一个开始的内容
        last_art = body_content.rfind('<article class="content">')
        if last_art > 0:
            tag = '<article class="content">'
            body_content = body_content[last_art + len(tag):].strip()
    else:
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', raw, re.DOTALL)
        if not h1_match:
            return None
        h1_text = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
        after_h1 = raw[h1_match.end():]
        footer_idx = after_h1.find('<footer class="footer">')
        if footer_idx > 0:
            after_h1 = after_h1[:footer_idx]
        body_content = after_h1.strip()
    # 最后清理 body 里的残留包装伪标签（多次 refresh 累积）
    body_content = _strip_residual_wrappers(body_content)
    return render_page(h1_text, body_content, html_path)

def cmd_convert(_args):
    if _markdown is None:
        print("❌ 缺少 markdown 库。请先运行：pip install markdown")
        return 1
    print("🔄 开始转换 MD → HTML...")
    converted = 0
    for module in SITE_STRUCTURE:
        for _fid, fname, _fdesc, md_path, html_path in module["files"]:
            if md_path is None or html_path is None:
                continue
            md_full = ROOT / md_path
            html_full = ROOT / html_path
            if not md_full.exists():
                print(f"  ⚠️  跳过（MD 不存在）: {md_path}")
                continue
            md_text = md_full.read_text(encoding="utf-8")
            md = _markdown.Markdown(extensions=["fenced_code", "tables", "nl2br", "sane_lists"])
            content_html = md.convert(md_text)
            title_match = re.search(r"<h1[^>]*>(.*?)</h1>", content_html)
            page_title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip() if title_match else fname
            full_html = render_page(page_title, content_html, html_path)
            html_full.write_text(full_html, encoding="utf-8")
            converted += 1
            print(f"  ✓ {html_path}")
    print(f"\n✅ 完成！共转换 {converted} 个文件")
    return 0


def _iter_content_pages():
    """所有需要被 fix / refresh 处理的 HTML 页面（只排除根 index 和有独立布局的工具页）"""
    html_files = list(ROOT.rglob("*.html"))
    exempt_files = {"index.html"}  # 只排除根 index
    tool_index_with_own_layout = {"02-hashtag-generator/index.html", "05-data-tracking/dashboard.html"}
    for f in html_files:
        rel = f.relative_to(ROOT).as_posix()
        if f.name in exempt_files or rel in tool_index_with_own_layout:
            continue
        yield rel


def cmd_fix(_args):
    print("🔧 扫描并修复无侧边栏的 HTML 页面...")
    fixed = 0
    for rel in _iter_content_pages():
        full = ROOT / rel
        txt = full.read_text(encoding="utf-8", errors="ignore")
        if 'class="sidebar"' in txt:
            continue
        new_html = wrap_with_layout(rel)
        if new_html is None:
            print(f"  ✗ 失败: {rel}（找不到 H1）")
            continue
        full.write_text(new_html, encoding="utf-8")
        fixed += 1
        print(f"  ✓ {rel}")
    print(f"\n✅ 修复完成！共 {fixed} 个文件")
    return 0


def cmd_refresh(_args):
    print("🔄 刷新所有内容页的侧边栏...")
    refreshed = 0
    for rel in _iter_content_pages():
        full = ROOT / rel
        new_html = wrap_with_layout(rel)
        if new_html is None:
            print(f"  ✗ 失败: {rel}（找不到 H1）")
            continue
        full.write_text(new_html, encoding="utf-8")
        refreshed += 1
        print(f"  ✓ {rel}")
    print(f"\n✅ 完成！共刷新 {refreshed} 个页面")
    return 0

def render_module_page(module, current_file):
    sidebar = make_sidebar(current_file)
    breadcrumb = make_breadcrumb(current_file)
    file_list_html = []
    folder = FOLDER_MAP.get(module["id"], module["num"] + "-" + module["id"])
    for fid, fname, fdesc, _md, hpath in module["files"]:
        if hpath is None:
            continue
        if current_file.startswith(folder + "/"):
            rel = hpath[len(folder) + 1:]
        else:
            rel = hpath
        if "tool" in fid or "dashboard" in fid:
            icon = "🛠️"
        elif "guide" in fid or "launch" in fid or "framework" in fid or "prompts" in fid:
            icon = "📖"
        else:
            icon = "📄"
        file_list_html.append(f"""
<a href="{rel}" class="file-item">
<div class="icon">{icon}</div>
<div class="info">
<div class="title">{fname}</div>
<div class="desc">{fdesc}</div>
</div>
<div class="arrow">→</div>
</a>""")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{module["icon"]} {module["name"]} · Crystal IG 运营</title>
<link rel="stylesheet" href="../{CSS_REL}">
</head>
<body>
<button class="mobile-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰ 菜单</button>
<div class="layout">
<aside class="sidebar">
<div class="sidebar-brand">
<h1>💎 Crystal IG 运营</h1>
<div class="sub">内容运营体系 v1.0</div>
</div>
{sidebar}
</aside>
<main class="main">
<header class="header">
{breadcrumb}
</header>
<article class="content">
<h1>{module["icon"]} {module["num"]} · {module["name"]}</h1>
<p style="color: var(--color-text-soft); margin-bottom: 8px;"><strong>{module["name_en"]}</strong></p>
<p>{module["desc"]}</p>
<div class="file-list">
{"".join(file_list_html)}
</div>
</article>
<footer class="footer">
Crystal Bracelet IG 运营体系 · 由 <a href="../index.html">ins-opt</a> 仓库生成
</footer>
</main>
</div>
</body>
</html>
"""


def cmd_modules(_args):
    print("🔄 生成模块入口页...")
    for module in SITE_STRUCTURE:
        folder = FOLDER_MAP.get(module["id"])
        if folder in SELF_MANAGED_INDEX:
            print(f"  ⏭  跳过 {folder}/index.html（自建页面，不覆盖）")
            continue
        index_path = ROOT / folder / "index.html"
        current_file = f"{folder}/index.html"
        html = render_module_page(module, current_file)
        index_path.write_text(html, encoding="utf-8")
        print(f"  ✓ {folder}/index.html")
    print("\n✅ 完成！")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog="site_builder",
        description="Crystal IG 运营站点构建器（统一工具）",
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("convert", help="MD → HTML 转换").set_defaults(func=cmd_convert)
    sub.add_parser("fix", help="修复无侧边栏的 HTML 页面").set_defaults(func=cmd_fix)
    sub.add_parser("refresh", help="刷新所有内容页的侧边栏").set_defaults(func=cmd_refresh)
    sub.add_parser("modules", help="生成每个模块的 index.html 入口页").set_defaults(func=cmd_modules)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

