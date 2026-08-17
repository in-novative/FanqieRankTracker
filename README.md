# 🏆 番茄风向标 · Fanqie Rank Tracker

[![English](https://img.shields.io/badge/lang-English-blue)](README_EN.md)

> 👗📚 追踪**番茄小说四大榜单**（女频新书榜 / 男频新书榜 / 女频阅读榜 / 男频阅读榜），每日自动抓取排行数据并结合 AI 生成趋势分析，部署为精美的在线多榜单看板。

---

## ✨ 功能概览

| 功能 | 说明 |
|------|------|
| 🕷️ 自动爬取 | 每日定时抓取四大榜单（女频/男频 × 新书榜/阅读榜）各分类 Top 30 |
| 🔖 榜单切换 | 看板与风向标页面顶部 Tab 一键切换频道榜单，`?rank=` 参数直达 |
| 📊 趋势对比 | 自动对比相邻两天数据：新上榜 / 掉榜 / 排名变化 / 阅读量增长（按榜单独立统计） |
| 🤖 AI 风向分析 | 接入 OpenAI 兼容 API，按分类生成市场趋势速评 |
| 🧭 类型风向标 | 独立趋势页按榜单聚合多日数据，AI 总结综合赛道、热门分类和高频题材；未配置 API 时自动规则兜底 |
| 🖥️ 精美看板 | 仪表盘带打字机动画和瀑布流书籍卡片，书籍详情支持跨榜单历史上榜查询 |
| 📱 移动适配 | 完整的移动端适配，侧边栏抽屉式菜单 |
| 🔌 数据接口 | 生成静态 `lastest` JSON 接口，按榜单 + 类型读取最新数据 |
| ⚡ 全自动化 | GitHub Actions + GitHub Pages，零服务器运维 |

---

## 🚀 食用指南

### 前置条件

- **Python 3.9+**
- **Git**
- 一个 GitHub 账号
- （可选）一个 OpenAI 兼容 API 的密钥，用于 AI 分析

### 第一步：Fork 仓库

点击 GitHub 页面右上角的 **Fork** 按钮，将项目 Fork 到你自己的账号下。

### 第二步：开启 GitHub Pages

1. 进入你 Fork 后的仓库 → **Settings** → **Pages**
2. **Build and deployment** 下的 Source 选择 **GitHub Actions**（不要选 Deploy from a branch）
3. 进入 **Settings** → **Actions** → **General** → **Workflow permissions**，选择 **Read and write permissions** 并保存

> **💡 提示：** 项目自带 Pages 部署工作流，首次运行 Actions 时会自动创建 Pages 站点。若日志出现 `Resource not accessible by integration`，说明上面两处配置未生效，检查后重跑即可。

稍等几分钟，你的看板就会上线：`https://<你的用户名>.github.io/FanqieRankTracker/`

### 第三步：配置 Secrets（可选，开启 AI 分析）

进入仓库 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**，添加以下三个 Secret：

| Secret 名称 | 说明 | 示例 |
|---|---|---|
| `API_BASE_URL` | OpenAI 兼容 API 的地址 | `https://api.openai.com/v1` |
| `API_KEY` | API 密钥 | `sk-xxxxxxxxxxxxx` |
| `API_MODEL` | 模型名称 | `gpt-4o-mini` |

> **💡 提示：** 任何 OpenAI 兼容接口均可使用（如 Moonshot / DeepSeek / 自建服务等）。如果不配置这三个 Secret，系统将自动使用基于规则的摘要替代 AI 分析，**不影响核心功能**。

### 第四步：手动触发首次运行

1. 进入仓库 → **Actions** → 左侧选择 **Daily Fanqie Rank Scraper**
2. 点击右上角 **Run workflow** → **Run workflow**
3. 等待 Workflow 运行完成（约 3–5 分钟）

运行成功后，`data/` 目录下会自动生成四个榜单的数据文件，打开 GitHub Pages 链接即可看到看板，顶部 Tab 可切换榜单。

### 第五步：坐等自动更新

GitHub Actions 已配置为 **每天 UTC 00:00（北京时间 08:00）** 自动运行。之后无需任何手动操作，数据和看板会每天自动更新。

看板顶部 Tab 可在**女频新书榜 / 男频新书榜 / 女频阅读榜 / 男频阅读榜**之间切换。看板右上角的 **风向标** 可进入 `trend.html`，按榜单先查看当下火热综合赛道（如古风言情、东方玄幻）、具体热门分类和高频题材，再按具体类型查看近 7 / 14 / 30 日或全部周期的趋势分析。全站热点会优先使用 AI 总结，未配置 API 或生成失败时使用规则统计文案兜底。

如需手动补抓或重新总结某几个榜单，可在 Actions 中运行 **Force Update (Re-scrape + Re-summarize)**，通过 `target_date` 指定日期、`ranks` 指定榜单 ID（如 `male_new,female_hot`，留空则全部）。

---

## 🔌 最新数据接口

构建脚本会按榜单生成 GitHub Pages 可直接访问的静态 JSON 接口。`rank_id` 取值：`female_new` / `male_new` / `female_hot` / `male_hot`。

| 类型 | 路径 | 说明 |
|---|---|---|
| 榜单元数据 | `data/ranks.json` | 所有榜单的 ID、名称、赛道分组与题材关键词 |
| 日期索引 | `data/dates.json` | 每个榜单可用的快照日期列表 |
| 类型索引 | `api/<rank_id>/lastest/index.json` | 该榜单所有可用类型及对应 URL |
| 全量数据 | `api/<rank_id>/lastest/all.json` | 该榜单全部分类、趋势和书籍 |
| 单类型数据 | `api/<rank_id>/lastest/<类型>.json` | 例如 `api/male_new/lastest/东方玄幻.json` |

示例：

```bash
curl https://<你的用户名>.github.io/FanqieRankTracker/api/female_new/lastest/all.json
curl https://<你的用户名>.github.io/FanqieRankTracker/api/male_new/lastest/东方玄幻.json
```

---

## 🔧 本地开发

```bash
# 1. 克隆仓库
git clone https://github.com/<你的用户名>/FanqieRankTracker.git
cd FanqieRankTracker

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 4. 运行爬虫（每个分类抓取 Top 30；默认抓取全部 4 个榜单）
python scrape_fanqie_ranks.py
# 只抓取指定榜单：
python scrape_fanqie_ranks.py --ranks female_new,male_new

# 5. 构建看板数据（可选，带 AI 分析需设置环境变量）
pip install openai
export API_BASE_URL="https://your-api-endpoint/v1"
export API_KEY="your-api-key"
export API_MODEL="your-model-name"
python scripts/build_latest.py
# 只构建指定榜单：
python scripts/build_latest.py --rank female_new

# 6. 本地预览前端
python -m http.server 8000
# 打开 http://localhost:8000
```

---

## 📁 项目结构

```
FanqieRankTracker/
├── .github/workflows/
│   ├── scrape.yml              # 每日定时爬取 + 构建部署
│   ├── force_update.yml        # 手动补抓 / 重新总结（可按榜单）
│   └── pages.yml               # push 时部署 Pages
├── css/
│   └── style.css               # 看板主题样式（含榜单切换 Tab）
├── js/
│   ├── app.js                  # 首页渲染（榜单 Tab + 瀑布流 + 打字机动画）
│   ├── trend.js                # 风向标渲染（数据驱动赛道分组）
│   └── book.js                 # 书籍详情（跨榜单历史上榜查询）
├── scripts/
│   └── build_latest.py         # 趋势对比 + AI 分析构建脚本（多榜单循环）
├── data/
│   ├── fanqie_<rank_id>_ranks_YYYYMMDD.json  # 每日原始快照（按榜单命名）
│   ├── task_state_<rank_id>_YYYYMMDD.json    # 断点续传状态（按榜单独立）
│   ├── latest/<rank_id>.json   # 各榜单最新聚合数据
│   ├── trends/<rank_id>/YYYY-MM-DD.json      # 趋势归档（按榜单分目录）
│   ├── ranks.json              # 榜单元数据（前端 Tab / 赛道 / 关键词）
│   ├── dates.json              # 各榜单可用日期索引
│   └── market_summary.json     # 各榜单热点 AI/规则总结（by_rank）
├── api/
│   └── <rank_id>/lastest/      # 最新数据静态接口（all + 按类型拆分）
├── index.html                  # 仪表盘入口页
├── trend.html                  # 类型风向标趋势分析页
├── book.html                   # 书籍详情页
├── scrape_fanqie_ranks.py      # 番茄小说多榜单爬虫（Playwright）
├── rank_config.py              # 榜单配置源（URL / 赛道分组 / 题材关键词）
├── requirements.txt            # Python 依赖
└── README.md                   # 本文件
```

---

## ⚙️ 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                   GitHub Actions (每日 08:00)                │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Playwright   │───▶│  build_latest │───▶│  git commit  │  │
│  │  爬取榜单数据  │    │  趋势对比      │    │  自动提交     │  │
│  │              │    │  + AI 分析     │    │  到 main     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                    GitHub Pages 自动部署
                    用户访问在线看板 🌐
```

---

## 📝 常见问题

<details>
<summary><b>Q: Workflow 运行失败怎么办？</b></summary>

检查 Actions 日志中的错误信息。常见原因：
- 番茄小说页面结构变更 → 需要更新爬虫选择器
- Playwright 安装超时 → 尝试重新运行

</details>

<details>
<summary><b>Q: 不配置 AI Secret 也能用吗？</b></summary>

可以！系统会自动 fallback 到基于规则的摘要（如"新增3本上榜；《XX》排名上升+5位"）。只是没有 AI 自然语言分析而已。

</details>

<details>
<summary><b>Q: 可以增删榜单或换成其他频道吗？</b></summary>

可以。所有榜单定义集中在 `rank_config.py` 的 `RANK_SOURCES` 中，增删条目即可同步影响爬虫、构建脚本与前端 Tab。榜单 URL 规律为 `/rank/{频道}_{榜单类型}_{分类ID}`（频道 0=女频 / 1=男频；榜单类型 1=新书榜 / 2=阅读榜）。同文件中的 `GENRE_GROUPS`（赛道分组）和 `MARKET_KEYWORDS`（题材关键词）也按频道维护。

</details>

<details>
<summary><b>Q: 某个榜单当天抓取失败了怎么办？</b></summary>

单个榜单失败不影响其他榜单，断点续传按榜单独立记录进度。次日定时任务会自动补抓当天缺失的榜单；也可在 Actions 中运行 **Force Update**，用 `ranks` 参数只重跑失败的榜单。

</details>

---

## 📜 License

MIT

---

<p align="center">
  <sub>Made with ☕ and 🤖 — 数据每日自动更新，无需手动维护</sub>
</p>
