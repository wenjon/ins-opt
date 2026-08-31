"""
Instagram Graph API 抓取脚本
============================
功能：自动抓取 Instagram Business 账号的账号级和帖子级数据，保存为 CSV
依赖：requests, python-dotenv
作者：ins-opt 仓库
"""

import os
import sys
import csv
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ 缺少 requests 库，请运行: pip install -r requirements.txt")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ 缺少 python-dotenv 库，请运行: pip install -r requirements.txt")
    sys.exit(1)

# ============== 配置 ==============

SCRIPT_DIR = Path(__file__).parent
load_dotenv(SCRIPT_DIR / ".env")

IG_BUSINESS_ID = os.getenv("IG_BUSINESS_ID", "").strip()
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", "").strip()
GRAPH_API_VERSION = os.getenv("GRAPH_API_VERSION", "v18.0")
DATA_DIR = SCRIPT_DIR / os.getenv("DATA_DIR", "data")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# 日志
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("ig-fetch")

# ============== 工具函数 ==============

def require_env():
    """检查必需的环境变量"""
    missing = []
    if not IG_BUSINESS_ID or IG_BUSINESS_ID == "your_instagram_business_account_id":
        missing.append("IG_BUSINESS_ID")
    if not IG_ACCESS_TOKEN or IG_ACCESS_TOKEN == "your_long_lived_access_token":
        missing.append("IG_ACCESS_TOKEN")
    if missing:
        log.error(f"❌ 配置缺失: {', '.join(missing)}")
        log.error("请复制 .env.example 为 .env 并填入真实值")
        sys.exit(1)


def api_get(endpoint, params=None):
    """调用 Graph API GET 接口"""
    base = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
    url = f"{base}{endpoint}"
    if params is None:
        params = {}
    params["access_token"] = IG_ACCESS_TOKEN
    log.debug(f"GET {url} params={list(params.keys())}")
    try:
        r = requests.get(url, params=params, timeout=30)
    except requests.exceptions.RequestException as e:
        log.error(f"网络错误: {e}")
        return None
    if r.status_code != 200:
        log.error(f"API 错误 {r.status_code}: {r.text}")
        return None
    return r.json()


def safe_get(d, *keys, default=0):
    """安全获取嵌套字典值"""
    for k in keys:
        if isinstance(d, dict) and k in d:
            d = d[k]
        else:
            return default
    return d


def today_str():
    return datetime.now().strftime("%Y-%m-%d")


def week_str():
    """ISO 周编号，如 2026-W33"""
    return datetime.now().strftime("%G-W%V")


# ============== 抓取逻辑 ==============

def fetch_account_insights():
    """抓取账号级数据（最近 7 天）"""
    log.info("📊 抓取账号级数据...")
    endpoint = f"/{IG_BUSINESS_ID}/insights"
    params = {
        "metric": "reach,impressions,profile_views,follower_count,website_clicks",
        "period": "day",
        "since": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        "until": today_str(),
    }
    data = api_get(endpoint, params)
    if not data or "data" not in data:
        return None

    # 汇总
    metrics = {}
    for item in data["data"]:
        name = item.get("name")
        values = item.get("values", [])
        total = sum(v.get("value", 0) for v in values if isinstance(v.get("value"), int))
        metrics[name] = total
    log.info(f"  ✓ Reach 7天: {metrics.get('reach', 0)}, 主页访问: {metrics.get('profile_views', 0)}")
    return metrics


def fetch_account_info():
    """抓取账号基本信息"""
    log.info("👤 抓取账号信息...")
    endpoint = f"/{IG_BUSINESS_ID}"
    params = {
        "fields": "username,name,biography,followers_count,follows_count,media_count,profile_picture_url"
    }
    return api_get(endpoint, params)


def fetch_media_list(limit=25):
    """抓取最近的帖子列表"""
    log.info(f"📷 抓取最近 {limit} 条帖子...")
    endpoint = f"/{IG_BUSINESS_ID}/media"
    params = {
        "fields": "id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,like_count,comments_count",
        "limit": limit,
    }
    data = api_get(endpoint, params)
    if not data or "data" not in data:
        return []
    return data["data"]


def fetch_media_insights(media_id, media_type):
    """抓取单条帖子的 insights（saves/shares/reach）"""
    endpoint = f"/{media_id}/insights"
    # 不同媒体类型支持不同 metrics
    if media_type == "REEL" or media_type == "VIDEO":
        metrics = "reach,saved,shares,likes,comments,plays"
    else:
        metrics = "reach,saved,shares,likes,comments"
    params = {"metric": metrics}
    data = api_get(endpoint, params)
    if not data or "data" not in data:
        return {}

    result = {}
    for item in data["data"]:
        values = item.get("values", [])
        if values and isinstance(values[0].get("value"), int):
            result[item["name"]] = values[0]["value"]
        elif values and isinstance(values[0].get("value"), dict):
            result[item["name"]] = values[0]["value"].get("value", 0)
    return result


# ============== 写入 CSV ==============

def append_to_csv(filepath, row, headers):
    """追加一行到 CSV（不存在则创建）"""
    file_exists = filepath.exists()
    with open(filepath, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def save_account_summary(metrics, account_info):
    """保存账号级汇总到 weekly log"""
    if not metrics:
        log.warning("⚠️ 无账号数据，跳过汇总写入")
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    weekly_path = DATA_DIR / "weekly-log.csv"

    # 找到项目根目录的 weekly-log-template.csv 复制表头
    template_path = SCRIPT_DIR.parent / "05-data-tracking" / "weekly-log-template.csv"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            headers = next(reader)
    else:
        headers = [
            "Week", "Date_Range", "Total_Reach", "Total_Likes", "Total_Comments",
            "Total_Saves", "Total_Shares", "Profile_Visits", "Link_Clicks",
            "DM_Inquiries", "New_Followers", "Unfollows", "Best_Selling_Point",
            "Best_Post_Type", "Best_Post_Time", "Notes"
        ]

    date_range = f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} ~ {today_str()}"
    row = {h: "" for h in headers}
    row["Week"] = week_str()
    row["Date_Range"] = date_range
    row["Total_Reach"] = metrics.get("reach", 0)
    row["Profile_Visits"] = metrics.get("profile_views", 0)
    row["Link_Clicks"] = metrics.get("website_clicks", 0)
    row["New_Followers"] = metrics.get("follower_count", 0)
    row["Notes"] = "由 fetch_insights.py 自动生成"

    append_to_csv(weekly_path, row, headers)
    log.info(f"  ✓ 账号汇总已写入: {weekly_path}")


def save_media_details(media_list):
    """保存帖子详情到 posts history"""
    if not media_list:
        log.warning("⚠️ 无帖子数据，跳过详情写入")
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    posts_path = DATA_DIR / "posts-history.csv"

    headers = [
        "Post_ID", "Date", "Type", "Permalink", "Caption_Snippet",
        "Reach", "Impressions", "Likes", "Comments", "Saves", "Shares"
    ]

    log.info(f"📝 抓取 {len(media_list)} 条帖子的 insights...")
    for media in media_list:
        media_id = media.get("id", "")
        media_type = media.get("media_type", "IMAGE")
        caption = media.get("caption", "")[:80].replace("\n", " ")
        timestamp = media.get("timestamp", "")[:10]
        permalink = media.get("permalink", "")

        insights = fetch_media_insights(media_id, media_type)
        row = {
            "Post_ID": media_id,
            "Date": timestamp,
            "Type": media_type,
            "Permalink": permalink,
            "Caption_Snippet": caption,
            "Reach": insights.get("reach", 0),
            "Impressions": safe_get(insights, "impressions", default=0),
            "Likes": media.get("like_count", 0),
            "Comments": media.get("comments_count", 0),
            "Saves": insights.get("saved", 0),
            "Shares": insights.get("shares", 0),
        }
        append_to_csv(posts_path, row, headers)
        log.info(f"  ✓ {timestamp} {media_type} | {row['Reach']} reach, {row['Saves']} saves")

    log.info(f"  ✓ 帖子详情已写入: {posts_path}")


# ============== 主流程 ==============

def main():
    log.info("=" * 50)
    log.info("💎 Crystal IG Insights Fetcher")
    log.info("=" * 50)

    require_env()

    # 1. 账号信息
    account_info = fetch_account_info()
    if not account_info:
        log.error("❌ 无法获取账号信息，请检查 IG_BUSINESS_ID 和 Access Token")
        sys.exit(1)
    log.info(f"  ✓ 账号: @{account_info.get('username', 'unknown')}")
    log.info(f"  ✓ 粉丝数: {account_info.get('followers_count', 0)}")

    # 2. 账号级 insights
    metrics = fetch_account_insights()

    # 3. 帖子级数据
    media_list = fetch_media_list(limit=25)

    # 4. 写入 CSV
    save_account_summary(metrics, account_info)
    save_media_details(media_list)

    log.info("=" * 50)
    log.info(f"✅ 全部完成！数据保存在: {DATA_DIR}")
    log.info("💡 双击 05-data-tracking/dashboard.html 可视化数据")
    log.info("=" * 50)


if __name__ == "__main__":
    main()
