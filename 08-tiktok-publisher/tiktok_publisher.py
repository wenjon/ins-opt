"""
TikTok 半自动发布包生成器（C 方案）
====================================
- 每天生成一个独立的发布包（MD 文件）：文案 + 图片清单 + 标签 + 排期
- 用户手动到 TikTok app 里点确认（粘贴文案 + 上传图片 + 加标签）
- posted_log.csv 记录已发布的日期

子命令：
  init                  生成 14 天的初始发布包
  today                 生成今日发布包
  day N                 生成第 N 天的发布包
  list                  列出所有已生成的包
  mark N                标记第 N 天为已发布
  status                显示进度
  open N                在浏览器中打开第 N 天的发布包
"""
import argparse
import csv
import json
import os
import sys
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
PKG_DIR = ROOT / "packages"
LOG_FILE = ROOT / "posted_log.csv"

SELL_LABELS = {
    "brightening": "🌟 显白",
    "natural": "🌿 天然",
    "healing": "💎 疗愈",
    "luck": "🍀 好运",
    "handmade": "👐 手工",
    "diy_stack": "💫 DIY 叠戴",
    "general": "🎁 日常",
}

FORM_LABELS = {
    "image": "图文",
    "video": "短视频",
}


def load_json(name):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def day_to_date(start_date, day_num):
    """第 N 天对应的实际日期（start_date 是 day 1）"""
    return start_date + timedelta(days=day_num - 1)


def pkg_path(start_date, day_num):
    d = day_to_date(start_date, day_num)
    return PKG_DIR / f"day{day_num:02d}-{d.isoformat()}.md"


def make_hashtags(sell, region="my-sg"):
    """生成 5-8 个标签（TK 标签数量过多会降权）"""
    data = load_json("hashtags.json")
    tags = list(data.get("always_include", []))
    sell_tags = data["by_sell"].get(sell, [])
    tags.extend(sell_tags[:3])  # 取卖点标签前 3
    region_tags = data["region"].get(region, [])
    tags.extend(region_tags[:2])  # 取地域标签前 2
    # 去重保持顺序
    seen = set()
    out = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out[:7]  # 最多 7 个


def pick_template(sell, day_num):
    """根据 day_num 选一条模板（不同天用不同模板避免重复）"""
    data = load_json("templates.json")
    pool = data.get(sell, data.get("general", {}))
    templates = pool.get("templates", [])
    if not templates:
        return "(暂无模板)"
    return templates[(day_num - 1) % len(templates)]


def pick_image_prompts(sell, day_num):
    data = load_json("templates.json")
    pool = data.get(sell, data.get("general", {}))
    return pool.get("image_prompts", [])


def render_package(day_num, start_date):
    """渲染第 N 天的发布包（返回 markdown 字符串）"""
    schedule = load_json("schedule.json")["schedule"]
    item = next((s for s in schedule if s["day"] == day_num), None)
    if not item:
        return None
    sell = item["sell"]
    form = item["form"]
    date = day_to_date(start_date, day_num)
    weekday_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]

    template = pick_template(sell, day_num)
    image_prompts = pick_image_prompts(sell, day_num)
    tags = make_hashtags(sell)
    tags_str = " ".join("#" + t for t in tags)

    md = f"""# Day {day_num:02d} · {date.isoformat()} ({weekday_cn})

> **主卖点**: {SELL_LABELS.get(sell, sell)} · **形式**: {FORM_LABELS.get(form, form)} · **建议发布时间**: {item['time']}

## 📝 文案（直接复制到 TK）

```
{template}
```

> 💡 模板里有 `[X]` `[Y]` 这样的占位符，请替换成具体水晶名（如 "粉水晶""黄水晶""绿幽灵"）。

## 🏷️ 标签（直接复制）

```
{tags_str}
```

> TK 标签建议 5-7 个，太多会降权。已经按"卖点 + 地域"自动筛选好了。

## 🖼️ 图片清单（{form}）

"""
    if form == "image":
        md += "需要 1-3 张图（图文帖）：\n\n"
    else:
        md += "需要 1 段视频（15-60s）：\n\n"
    for i, p in enumerate(image_prompts, 1):
        md += f"- [ ] 图/视频 {i}: **{p}**\n"
    md += "\n> 描述只是方向，实际拍摄时按你的产品调整。素材可去 `_assets/image-prompts.html` 找更多灵感。\n\n"

    md += f"""## 🎯 主题 / 钩子

**本条主题**: {item['topic']}

发布前自检：
- [ ] 文案里 `[X]` `[Y]` 全部替换成具体水晶名
- [ ] 图片/视频已准备好
- [ ] 标签已复制到剪贴板
- [ ] 发布后 10 分钟内回复前 5 条评论（提升算法权重）
- [ ] 24 小时后回来用 `python 08-tiktok-publisher/tiktok_publisher.py mark {day_num}` 标记已发

---

📦 **自动生成于** {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    return md


def cmd_init(args):
    PKG_DIR.mkdir(exist_ok=True)
    start = args.start
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
    except ValueError:
        print(f"❌ 日期格式错误: {start}（应为 YYYY-MM-DD）")
        return 1
    print(f"📦 从 {start_date} 开始生成 14 天发布包...")
    for day in range(1, 15):
        md = render_package(day, start_date)
        path = pkg_path(start_date, day)
        path.write_text(md, encoding="utf-8")
        print(f"  ✓ {path.name}")
    print(f"\n✅ 完成！共生成 14 个发布包到 {PKG_DIR}/")
    print(f"\n查看入口: 打开 08-tiktok-publisher/index.html")
    return 0


def cmd_today(args):
    """生成今日发布包（按当前日期推算 day N）"""
    LOG_FILE.touch(exist_ok=True)
    # 从最近的 package 反推 start_date
    if not PKG_DIR.exists():
        print("❌ packages 目录不存在，请先运行 init")
        return 1
    pkgs = sorted(PKG_DIR.glob("day*.md"))
    if not pkgs:
        print("❌ 没有发布包，请先运行 init")
        return 1
    # 从第一个 package 文件名解析 start_date
    first = pkgs[0].stem  # e.g., "day01-2026-08-19"
    start_str = first.split("-", 1)[1]  # "2026-08-19"
    start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
    today = datetime.now().date()
    day_num = (today - start_date).days + 1
    if day_num < 1 or day_num > 14:
        print(f"❌ 今天 (day {day_num}) 不在 14 天排期内")
        return 1
    md = render_package(day_num, start_date)
    path = pkg_path(start_date, day_num)
    path.write_text(md, encoding="utf-8")
    print(f"📦 已生成今日发布包: {path.name}")
    print(f"   路径: {path}")
    print(f"\n在浏览器打开: python 08-tiktok-publisher/tiktok_publisher.py open {day_num}")
    return 0


def cmd_day(args):
    """生成指定 day 的发布包"""
    LOG_FILE.touch(exist_ok=True)
    if not PKG_DIR.exists():
        print("❌ packages 目录不存在，请先运行 init")
        return 1
    pkgs = sorted(PKG_DIR.glob("day*.md"))
    if not pkgs:
        print("❌ 没有发布包，请先运行 init")
        return 1
    first = pkgs[0].stem
    start_str = first.split("-", 1)[1]
    start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
    day_num = args.n
    if day_num < 1 or day_num > 14:
        print(f"❌ day 必须在 1-14 之间")
        return 1
    md = render_package(day_num, start_date)
    path = pkg_path(start_date, day_num)
    path.write_text(md, encoding="utf-8")
    print(f"📦 已生成 day {day_num} 发布包: {path.name}")
    return 0


def cmd_list(args):
    if not PKG_DIR.exists():
        print("(packages 目录不存在)")
        return 0
    pkgs = sorted(PKG_DIR.glob("day*.md"))
    if not pkgs:
        print("(还没有发布包，运行 init 生成)")
        return 0
    posted = load_posted()
    print(f"{'Day':<5} {'Date':<12} {'Status':<10} File")
    print("-" * 60)
    for p in pkgs:
        # 解析 day 和 date
        parts = p.stem.split("-", 2)  # ["day01", "2026", "08-19"]
        day = parts[0].replace("day", "")
        date = parts[1] + "-" + parts[2]
        status = "✅ 已发" if date in posted else "⏳ 待发"
        print(f"{day:<5} {date:<12} {status:<10} {p.name}")
    return 0


def load_posted():
    if not LOG_FILE.exists():
        return set()
    posted = set()
    with open(LOG_FILE, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("date"):
                posted.add(row["date"])
    return posted


def cmd_mark(args):
    LOG_FILE.touch(exist_ok=True)
    if not PKG_DIR.exists():
        print("❌ packages 目录不存在")
        return 1
    pkgs = sorted(PKG_DIR.glob("day*.md"))
    if not pkgs:
        print("❌ 没有发布包")
        return 1
    first = pkgs[0].stem
    start_str = first.split("-", 1)[1]
    start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
    day_num = args.n
    date = day_to_date(start_date, day_num).isoformat()

    # 检查文件存在
    pkg_file = pkg_path(start_date, day_num)
    if not pkg_file.exists():
        print(f"❌ 发布包不存在: {pkg_file.name}，先运行 day {day_num}")
        return 1

    # 追加到 CSV
    with open(LOG_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if LOG_FILE.stat().st_size == 0:
            writer.writerow(["day", "date", "marked_at", "notes"])
        writer.writerow([day_num, date, datetime.now().isoformat(timespec="seconds"), args.notes or ""])
    print(f"✅ Day {day_num} ({date}) 已标记为发布")
    return 0


def cmd_status(args):
    if not LOG_FILE.exists():
        print("📊 进度: 0/14 已发布")
        return 0
    posted = load_posted()
    total = 14
    done = len(posted)
    print(f"📊 进度: {done}/{total} 已发布 ({done/total*100:.0f}%)")
    if posted:
        print("\n已发日期:")
        for d in sorted(posted):
            print(f"  ✅ {d}")
    return 0


def cmd_open(args):
    if not PKG_DIR.exists():
        print("❌ packages 目录不存在")
        return 1
    pkgs = sorted(PKG_DIR.glob("day*.md"))
    if not pkgs:
        print("❌ 没有发布包")
        return 1
    first = pkgs[0].stem
    start_str = first.split("-", 1)[1]
    start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
    day_num = args.n
    pkg_file = pkg_path(start_date, day_num)
    if not pkg_file.exists():
        print(f"❌ 发布包不存在: {pkg_file.name}")
        return 1
    # 转成 file:// URL 并打开
    url = "file:///" + str(pkg_file).replace("\\", "/")
    print(f"🌐 打开: {url}")
    webbrowser.open(url)
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="tiktok_publisher", description="TikTok 半自动发布包生成器")
    sub = p.add_subparsers(dest="cmd", required=True)

    s_init = sub.add_parser("init", help="生成 14 天发布包")
    s_init.add_argument("--start", default=datetime.now().strftime("%Y-%m-%d"), help="day 1 的日期 (YYYY-MM-DD)")
    s_init.set_defaults(func=cmd_init)

    s_today = sub.add_parser("today", help="生成今日发布包")
    s_today.set_defaults(func=cmd_today)

    s_day = sub.add_parser("day", help="生成指定 day 的发布包")
    s_day.add_argument("n", type=int, help="day 编号 (1-14)")
    s_day.set_defaults(func=cmd_day)

    sub.add_parser("list", help="列出所有发布包").set_defaults(func=cmd_list)

    s_mark = sub.add_parser("mark", help="标记某天已发布")
    s_mark.add_argument("n", type=int, help="day 编号")
    s_mark.add_argument("--notes", help="备注（如 'reach=500, 5 saves'）")
    s_mark.set_defaults(func=cmd_mark)

    sub.add_parser("status", help="显示发布进度").set_defaults(func=cmd_status)

    s_open = sub.add_parser("open", help="在浏览器中打开发布包")
    s_open.add_argument("n", type=int, help="day 编号")
    s_open.set_defaults(func=cmd_open)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())