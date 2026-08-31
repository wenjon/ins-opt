# 💎 Crystal IG 运营体系

> 水晶手链 Instagram 内容运营 · 目标市场 MY + SG · 每日 1 小时可执行

一个轻量级、纯静态的 Instagram 内容运营站点，帮你从 0 到 1000 粉的完整节奏。
**所有内容采用第一人称用户视角**（"我"作为真实佩戴者分享），不是品牌方卖货。

## 🚀 快速开始

### 1. 打开主页

```bash
# 直接双击 index.html
# 或启动本地服务（推荐，避免 file:// 协议限制）
python -m http.server 8765
# 然后访问 http://127.0.0.1:8765/
```

### 2. 5 步上手

| 步骤 | 时间 | 做什么 | 入口 |
|---|---|---|---|
| 1 | 10 min | 试一下标签工具 | `02-hashtag-generator/index.html` |
| 2 | 30 min | 通读启动 7 天内容 | `04-content-drafts/00-launch-week.html` |
| 3 | 2-3 h | 按提示词库准备 30 张产品原图 | `_assets/image-prompts.html` |
| 4 | 持续 | 按每日 1 小时清单执行 | `01-content-calendar/daily-hour-checklist.html` |
| 5 | 1000 粉后 | 配置自动抓数据 | `06-instagram-automation/scheduling-guide.html` |

### 3. 快速查找

主页顶部有**搜索区**：
- 输入关键词（卖点、模板名、任务）
- 用"卖点"和"类型"chip 筛选
- 实时显示匹配数 + 页面卡片
- 快捷键：`Ctrl/Cmd + K` 聚焦搜索框

## 📂 目录结构

```
ins-opt/
├── index.html                      # 主入口（含搜索区 + 模块卡片 + 快速开始）
├── _assets/                        # 站点资源 + 工具脚本
│   ├── style.css                   # 共享样式（含搜索区样式）
│   ├── site_builder.py             # ⭐ 统一站点构建器（核心工具）
│   ├── convert.py / fix_layout.py  # 旧脚本的薄包装，调用 site_builder
│   ├── refresh_sidebars.py         # 同上
│   ├── gen_modules.py              # 同上
│   ├── clean_residual.py           # 清理残留关键词（独立工具）
│   └── image-prompts.html          # 找图提示词库
│
├── 01-content-calendar/            # 📅 内容日历
│   ├── two-week-cycle.html         # 2 周循环模板（核心节奏）
│   ├── four-week-launch-plan.html  # 4 周启动计划
│   └── daily-hour-checklist.html   # 每日 1 小时清单
│
├── 02-hashtag-generator/           # 🏷️ 标签生成器
│   ├── index.html                  # 交互式工具
│   └── README.html                 # 使用说明
│
├── 03-copy-templates/              # ✍️ 文案模板库
│   ├── 01-skin-brightening.html    # 显白
│   ├── 02-natural.html             # 天然（第一人称水晶旅程）
│   ├── 03-healing-stones.html      # 疗愈石
│   ├── 04-good-luck.html           # 好运
│   ├── 05-crystal-healing.html     # 水晶疗愈
│   ├── 06-handmade.html            # 手工制作
│   └── 07-diy-stack.html           # DIY 叠戴
│
├── 04-content-drafts/              # 📝 内容草稿
│   ├── 00-launch-week.html         # 启动 7 天
│   ├── 01-funnel-framework.html    # 5 篇递进式框架
│   ├── series-01-skin-brightening.html  # 显白系列 5 篇
│   ├── series-02-natural.html      # 天然系列 5 篇（水晶旅程）
│   ├── series-03-healing.html      # 疗愈系列 10 篇
│   ├── series-04-luck.html         # 好运系列 5 篇
│   ├── series-05-handmade.html     # 手工系列 5 篇
│   └── series-06-diy-stack.html    # 叠戴系列 5 篇
│
├── 05-data-tracking/               # 📊 数据追踪
│   ├── dashboard.html              # 数据看板（Chart.js）
│   ├── kpi-definitions.html        # KPI 定义
│   ├── posts-history.csv           # 历史帖记录模板
│   ├── weekly-log-template.csv     # 周记录模板
│   └── monthly-summary-template.csv # 月汇总模板
│
└── 06-instagram-automation/        # 🤖 IG 自动化
    ├── scheduling-guide.html       # 完整配置指南
    ├── README.html                 # 快速说明
    └── fetch_insights.py           # Meta Graph API 抓取脚本
```

## 🎯 7 大卖点（内容主轴）

| 卖点 | 用户心智 | 转化强度 | 内容方向 |
|---|---|---|---|
| 🌟 显白 | 颜值、穿搭、即时效果 | 高 | 冲动种草 |
| 🌿 天然 | 信任、材质、独一无二 | 中 | 个人旅程叙述 |
| 💎 疗愈石 | 能量、脉轮、灵性 | 中 | 灵性受众 |
| 🧘 水晶疗愈 | 情绪、减压、睡眠 | 中 | 身心灵 |
| 🍀 好运 | 财运、贵人、平安 | **最高** | 风水 / 旺运 |
| 👐 手工制作 | 温度、礼物、独一无二 | 中 | 礼物属性 |
| 💫 DIY 叠戴 | 搭配、客单 | 高 | 拉高客单 |

**心法**：
- 单条内容主推 1 个卖点 + 1 个辅助卖点（不堆 7 个）
- 2 周完成一轮 7 卖点循环
- 英文主、中文辅（覆盖 MY/SG 双语用户）

## 🛠️ 站点构建器（site_builder.py）

`site_builder.py` 是站点的"维护工具"，集中管理 `SITE_STRUCTURE` 和 4 个子命令：

### 子命令一览

```bash
python _assets/site_builder.py convert    # MD → HTML 转换
python _assets/site_builder.py fix        # 修复无侧边栏的页面
python _assets/site_builder.py refresh    # 刷新所有内容页的侧边栏
python _assets/site_builder.py modules    # 生成每个模块的 index.html 入口页
```

### 什么时候跑哪个？

| 场景 | 跑什么 |
|---|---|
| 新增一个内容页 | `refresh` |
| 修改了 SITE_STRUCTURE（如重命名某个卖点） | `refresh` |
| 发现某个页面没有侧边栏 | `fix` |
| 从 MD 重新生成 HTML | `convert`（需 `pip install markdown`） |
| 模块入口页丢了 | `modules` |

### SITE_STRUCTURE

所有页面的"真实清单"在 `site_builder.py` 的 `SITE_STRUCTURE` 列表里。
**这是唯一的数据源** — 侧边栏、面包屑、上下页、模块入口页都从这里生成。

要新增一个页面：
1. 在 `SITE_STRUCTURE` 对应模块的 `files` 里加一行
2. 跑 `python _assets/site_builder.py refresh`
3. 完成

## 📊 数据追踪工作流

### 周记录
1. 每周日打开 `05-data-tracking/dashboard.html`
2. 上传 `weekly-log-template.csv`（填好本周数据）
3. 看自动生成的图表，识别规律

### 关键比率

| 比率 | 公式 | 反映什么 |
|---|---|---|
| Engagement Rate | (Likes + Comments + Saves + Shares) / Reach | 整体互动 |
| Reach-to-Save | Saves / Reach | 工具价值 |
| Reach-to-Share | Shares / Reach | 社交价值 |
| Reach-to-DM | DM Inquiries / Reach | 转化价值 |

健康范围：Engagement 3-6% 正常，6-10% 优秀，>10% 爆款。

## 🤖 IG 自动化（可选）

达到 1000 粉后可以配置：
1. 申请 Meta developer 账号 + Instagram Graph API access token
2. 跑 `python _assets/fetch_insights.py --once` 验证连通
3. 用 Windows 任务计划程序每周自动跑一次

详见 `06-instagram-automation/scheduling-guide.html`。

## 💡 重要约定

> 疗愈类话术必加免责
> `For emotional and spiritual well-being only. Not a substitute for medical advice.`

> 好运类话术不承诺
> 用 "Believed to bring" 而不是 "Will bring"

> 真实比完美重要
> 手作的不完美才是真品的标记

> 不堆标签
> 每帖 13 个，5 个在文案末尾，8 个放第一条评论

## 🔄 开发与维护

### 添加新内容

```bash
# 1. 编辑 _assets/site_builder.py 的 SITE_STRUCTURE
# 2. 创建对应的 .html 文件（参考现有页面结构）
# 3. 跑 refresh
python _assets/site_builder.py refresh
```

### 验证站点

```bash
# 启动本地服务
python -m http.server 8765

# 浏览器访问
# http://127.0.0.1:8765/

# 检查所有链接
python _assets/_test_links.py  # 旧工具，可重写为 site_builder 子命令
```

### 备份与发布

整个仓库是纯静态 HTML/CSS/JS，可以：
- 直接 `git push` 到 GitHub Pages
- 用 Netlify / Vercel 部署
- 把整个目录打包发给别人

## 📋 30 秒规则

当你不知道下一步做什么时，按这个优先级：

1. 打开 `01-content-calendar/daily-hour-checklist.html`，按今日任务做
2. 找不到合适的文案？打开主页搜索 "XXX卖点"，复制模板
3. 数据看不懂？打开 `05-data-tracking/kpi-definitions.html`

## 📝 License

私人项目，按需使用。