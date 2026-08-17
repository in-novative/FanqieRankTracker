# 🏆 Fanqie Rank Tracker

[![中文](https://img.shields.io/badge/lang-中文-red)](README.md)

> 👗📚 Tracks **Fanqie Novel's four rankings** (Female New / Male New / Female Hot / Male Hot), featuring daily automated rank tracking and AI-powered trend analysis, deployed as a premium multi-rank online dashboard.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🕷️ Auto Scraping | Daily automated scraping of Top 30 books across all sub-categories of the four rankings (female/male × new/hot) |
| 🔖 Rank Switching | Top tabs on the dashboard and trend pages switch between rankings; `?rank=` URL parameter supported |
| 📊 Trend Analysis | Automatic day-over-day comparison per rank: new entries / dropped / rank changes / readership growth |
| 🤖 AI Summary | OpenAI-compatible API integration for per-category market trend analysis |
| 🧭 Trend Compass | Dedicated trend page aggregating multi-day data per rank: AI-summarized track groups, hot categories and trending themes; rule-based fallback without API |
| 🖥️ Dashboard | Dashboard with typewriter animation and waterfall book cards; book detail page supports cross-rank history lookup |
| 📱 Responsive | Full mobile support with slide-out sidebar menu |
| ⚡ Fully Automated | GitHub Actions + GitHub Pages, zero server maintenance |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **Git**
- A GitHub account
- (Optional) An OpenAI-compatible API key for AI analysis

### Step 1: Fork the Repository

Click the **Fork** button on the top-right corner of the GitHub page to fork this repository to your own account.

### Step 2: Enable GitHub Pages

1. Go to your forked repo → **Settings** → **Pages**
2. Under **Build and deployment**, select **GitHub Actions** as Source (do NOT choose Deploy from a branch)
3. Go to **Settings** → **Actions** → **General** → **Workflow permissions**, select **Read and write permissions** and save

> **💡 Tip:** The repo ships with its own Pages deploy workflow, which creates the Pages site on first run. If the log shows `Resource not accessible by integration`, the two settings above are not in effect — fix them and re-run.

After a few minutes, your dashboard will be live at: `https://<your-username>.github.io/FanqieRankTracker/`

### Step 3: Configure Secrets (Optional, for AI Analysis)

Go to repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**, and add the following three secrets:

| Secret Name | Description | Example |
|---|---|---|
| `API_BASE_URL` | OpenAI-compatible API endpoint | `https://api.openai.com/v1` |
| `API_KEY` | API key | `sk-xxxxxxxxxxxxx` |
| `API_MODEL` | Model name | `gpt-4o-mini` |

> **💡 Tip:** Any OpenAI-compatible API works (e.g., Moonshot / DeepSeek / self-hosted endpoints). If these secrets are not configured, the system will automatically fall back to rule-based summaries — **core functionality is unaffected**.

### Step 4: Trigger the First Run Manually

1. Go to repo → **Actions** → Select **Daily Fanqie Rank Scraper** on the left
2. Click **Run workflow** → **Run workflow** on the top-right
3. Wait for the workflow to complete (~3–5 minutes)

After a successful run, data files for all four rankings will be generated in the `data/` directory. Open the GitHub Pages link to view your dashboard and switch rankings via the top tabs.

### Step 5: Sit Back and Relax

GitHub Actions is configured to run automatically at **UTC 00:00 (08:00 Beijing Time)** every day. No further manual action is needed — data and dashboard will auto-update daily.

Use the top tabs to switch between the **Female New / Male New / Female Hot / Male Hot** rankings. The **Trend Compass** link opens `trend.html`, which aggregates multi-day data per rank — AI-summarized track groups, hot categories and trending themes — plus per-category trend analysis over 7 / 14 / 30 days or all time. Rule-based fallback applies when no API is configured.

To re-scrape or re-summarize selected rankings, run **Force Update (Re-scrape + Re-summarize)** in Actions with `target_date` and `ranks` inputs (e.g. `male_new,female_hot`; empty means all).

---

## 🔌 Latest Data API

The build script generates static JSON endpoints per ranking, directly accessible via GitHub Pages. `rank_id` options: `female_new` / `male_new` / `female_hot` / `male_hot`.

| Type | Path | Description |
|---|---|---|
| Rank metadata | `data/ranks.json` | IDs, names, track groups and theme keywords of all rankings |
| Date index | `data/dates.json` | Available snapshot dates per ranking |
| Category index | `api/<rank_id>/lastest/index.json` | Available categories and URLs for a ranking |
| All data | `api/<rank_id>/lastest/all.json` | All categories, trends and books of a ranking |
| Single category | `api/<rank_id>/lastest/<category>.json` | e.g. `api/male_new/lastest/东方玄幻.json` |

---

## 🔧 Local Development

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/FanqieRankTracker.git
cd FanqieRankTracker

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 4. Run the scraper (Top 30 per category; all 4 rankings by default)
python scrape_fanqie_ranks.py
# Scrape selected rankings only:
python scrape_fanqie_ranks.py --ranks female_new,male_new

# 5. Build dashboard data (optional, set env vars for AI analysis)
pip install openai
export API_BASE_URL="https://your-api-endpoint/v1"
export API_KEY="your-api-key"
export API_MODEL="your-model-name"
python scripts/build_latest.py
# Build selected rankings only:
python scripts/build_latest.py --rank female_new

# 6. Preview frontend locally
python -m http.server 8000
# Then open http://localhost:8000
```

---

## 📁 Project Structure

```
FanqieRankTracker/
├── .github/workflows/
│   ├── scrape.yml              # Daily scheduled scrape + build + deploy
│   ├── force_update.yml        # Manual re-scrape / re-summarize (per-rank)
│   └── pages.yml               # Deploy Pages on push
├── css/
│   └── style.css               # Dashboard theme (incl. rank switch tabs)
├── js/
│   ├── app.js                  # Dashboard rendering (rank tabs + waterfall + typewriter)
│   ├── trend.js                # Trend compass rendering (data-driven groups)
│   └── book.js                 # Book detail (cross-rank history lookup)
├── scripts/
│   └── build_latest.py         # Trend comparison + AI analysis build script (multi-rank loop)
├── data/
│   ├── fanqie_<rank_id>_ranks_YYYYMMDD.json  # Daily raw snapshots (per-rank naming)
│   ├── task_state_<rank_id>_YYYYMMDD.json    # Resume state (per-rank independent)
│   ├── latest/<rank_id>.json   # Latest aggregated data per ranking
│   ├── trends/<rank_id>/YYYY-MM-DD.json      # Trend archives (per-rank folders)
│   ├── ranks.json              # Rank metadata (frontend tabs / groups / keywords)
│   ├── dates.json              # Available date index per ranking
│   └── market_summary.json     # Per-rank AI/rule summaries (by_rank)
├── api/
│   └── <rank_id>/lastest/      # Static latest-data endpoints (all + per-category)
├── index.html                  # Dashboard entry page
├── trend.html                  # Trend compass analysis page
├── book.html                   # Book detail page
├── scrape_fanqie_ranks.py      # Fanqie multi-rank scraper (Playwright)
├── rank_config.py              # Single source of rank config (URLs / groups / keywords)
├── requirements.txt            # Python dependencies
└── README.md                   # Chinese documentation
```

---

## ⚙️ How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                GitHub Actions (Daily at 08:00 CST)          │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Playwright   │───▶│  build_latest │───▶│  git commit  │  │
│  │  Scrape rank  │    │  Trend diff   │    │  Auto push   │  │
│  │  data         │    │  + AI summary │    │  to main     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                    GitHub Pages auto-deploy
                    User visits dashboard 🌐
```

---

## 📝 FAQ

<details>
<summary><b>Q: What if the workflow fails?</b></summary>

Check the error message in the Actions log. Common causes:
- Fanqie Novel page structure changed → Update the scraper selectors
- Playwright installation timeout → Try re-running the workflow

</details>

<details>
<summary><b>Q: Can I use it without configuring AI secrets?</b></summary>

Yes! The system will automatically fall back to rule-based summaries (e.g., "3 new entries; Book X rose +5 ranks"). You just won't have the AI natural language analysis.

</details>

<details>
<summary><b>Q: Can I add or remove rankings?</b></summary>

Yes. All rankings are defined in `RANK_SOURCES` in `rank_config.py`; adding or removing entries automatically affects the scraper, build script and frontend tabs. The URL pattern is `/rank/{gender}_{kind}_{categoryId}` (gender: 0=female / 1=male; kind: 1=new / 2=hot). `GENRE_GROUPS` (track groups) and `MARKET_KEYWORDS` (theme keywords) are maintained per gender in the same file.

</details>

<details>
<summary><b>Q: What if one ranking fails on a given day?</b></summary>

A single ranking failing does not affect the others, and resume state is tracked per ranking. The next daily run automatically backfills missing rankings; you can also run **Force Update** in Actions with the `ranks` parameter to retry just the failed ones.

</details>

---

## 📜 License

MIT

---

<p align="center">
  <sub>Made with ☕ and 🤖 — Data updates daily via automation, zero manual maintenance required</sub>
</p>
