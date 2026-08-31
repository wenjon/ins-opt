# 🎬 TikTok 半自动发布包（C 方案）

> 每天 5-10 分钟手动确认。脚本生成发布包，你只需要复制粘贴到 TikTok app。

## 为什么是"半自动"

完全自动发帖的方案（官方 API / 浏览器自动化）都**有显著风险**：
- 官方 Content Posting API 需要企业开发者认证，个人通过率低
- 浏览器模拟操作（Playwright/Selenium）容易被 TK 反作弊系统识别 → **封号**
- 疗愈、玄学类内容在 TK 风险更高，平台审核更严

**C 方案的核心理念**：
- 脚本负责"今天发什么、怎么写、几点发"（80% 的脑力活）
- 你负责最后 5 分钟在 TK app 里点"发布"（关键的人工审核）

## 快速上手

```bash
# 1. 生成 14 天发布包（一次性）
python 08-tiktok-publisher/tiktok_publisher.py init --start 2026-08-19

# 2. 每天打开 08-tiktok-publisher/index.html 看今天的任务
# 3. 点击"今日发布包"卡片，复制文案和标签
# 4. 在 TK app 里粘贴 + 上传图片 + 发布
# 5. 24 小时后回到命令行标记已发
python 08-tiktok-publisher/tiktok_publisher.py mark 1 --notes "reach=200, 5 saves"
```

## 子命令一览

| 命令 | 用途 |
|---|---|
| `init --start YYYY-MM-DD` | 生成 14 天初始发布包 |
| `today` | 重新生成今日发布包（修改模板后用） |
| `day N` | 重新生成第 N 天的发布包 |
| `list` | 列出所有包 + 状态 |
| `mark N --notes "..."` | 标记第 N 天已发布 + 备注数据 |
| `status` | 显示进度 |
| `open N` | 在浏览器中打开第 N 天的发布包 |

## 发布包长什么样

每个 `dayNN-YYYY-MM-DD.md` 包含：
- **📝 文案**：第一人称用户视角的现成中文文案（含 `[X]` 占位符）
- **🏷️ 标签**：按"卖点 + 地域"自动筛好的 5-7 个标签
- **🖼️ 图片清单**：每张图/视频的描述（自拍还是找图）
- **🎯 主题**：今日核心钩子
- **发布前自检清单**

## 数据文件

```
data/
├── schedule.json    # 2 周循环排期（7 卖点 × 14 天）
├── templates.json   # 7 卖点的文案模板（每卖点 3-4 条）
└── hashtags.json    # 标签数据（按卖点 + 地域）
```

要改文案模板？编辑 `data/templates.json` 然后跑 `python tiktok_publisher.py today` 重新生成。

## 排期策略

按"显白 → 天然 → 疗愈 → 好运 → 手工 → 叠戴"循环，2 周一轮：
- **Day 1-7**：第一轮，覆盖所有 7 个卖点
- **Day 8-14**：第二轮，重复但换角度（多一条视频，少一条图文）
- **每天 1 条**，不要堆
- 每天固定时间发（建议 19:00-22:00 MY/SG 时区）

## 注意事项

1. **疗愈话术**：每个疗愈类文案末尾**必须**保留免责 `For emotional and spiritual well-being only...`
2. **好运话术**：用 "Believed to bring" 而不是 "Will bring"
3. **TK 标签 5-7 个**：IG 可以堆 13 个，TK 不行
4. **占位符要替换**：发布前把 `[X]` `[Y]` 换成具体水晶名
5. **发布后互动**：发完 10 分钟内回前 5 条评论（算法权重）
6. **24h 后回填数据**：reach/saves/shares，记录到 `posted_log.csv`
7. **完全手动发布**：不要用模拟器或自动化工具（封号风险）

## 下一步升级

等账号做到 500-1000 粉、跑通 1-2 个月流程后：
- 考虑申请 TikTok Content Posting API（需要企业资质）
- 引入 Buffer / Later 等调度工具做半自动
- 接入 `06-instagram-automation` 的同样模式

## 进度跟踪

`posted_log.csv` 自动记录：
```csv
day,date,marked_at,notes
1,2026-08-19,2026-08-20T21:15:00,reach=200, 5 saves
```

可以导入到 `05-data-tracking/dashboard.html` 看趋势。