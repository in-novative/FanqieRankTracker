import os
import json
import time
import argparse
from datetime import datetime
from playwright.sync_api import sync_playwright

from rank_config import RANK_SOURCES, RANK_IDS, snapshot_file, state_file

START_CODE = 58344  # 0xE3E8
CHAR_SEQUENCE = [
    "D", "在", "主", "特", "家", "军", "然", "表", "场", "4", "要", "只", "v", "和", "?", "6", "别", "还", "g", "现", "儿", "岁", "?", "?", "此", "象", "月", "3", "出", "战", "工", "相", "o", "男", "直", "失", "世", "F", "都", "平", "文", "什", "V", "O", "将", "真", "T", "那", "当", "?", "会", "立", "些", "u", "是", "十", "张", "学", "气", "大", "爱", "两", "命", "全", "后", "东", "性", "通", "被", "1", "它", "乐", "接", "而", "感", "车", "山", "公", "了", "常", "以", "何", "可", "话", "先", "p", "i", "叫", "轻", "M", "士", "w", "着", "变", "尔", "快", "l", "个", "说", "少", "色", "里", "安", "花", "远", "7", "难", "师", "放", "t", "报", "认", "面", "道", "S", "?", "克", "地", "度", "I", "好", "机", "U", "民", "写", "把", "万", "同", "水", "新", "没", "书", "电", "吃", "像", "斯", "5", "为", "y", "白", "几", "日", "教", "看", "但", "第", "加", "候", "作", "上", "拉", "住", "有", "法", "r", "事", "应", "位", "利", "你", "声", "身", "国", "问", "马", "女", "他", "Y", "比", "父", "x", "A", "H", "N", "s", "X", "边", "美", "对", "所", "金", "活", "回", "意", "到", "z", "从", "j", "知", "又", "内", "因", "点", "Q", "三", "定", "8", "R", "b", "正", "或", "夫", "向", "德", "听", "更", "?", "得", "告", "并", "本", "q", "过", "记", "L", "让", "打", "f", "人", "就", "者", "去", "原", "满", "体", "做", "经", "K", "走", "如", "孩", "c", "G", "给", "使", "物", "?", "最", "笑", "部", "?", "员", "等", "受", "k", "行", "一", "条", "果", "动", "光", "门", "头", "见", "往", "自", "解", "成", "处", "天", "能", "于", "名", "其", "发", "总", "母", "的", "死", "手", "入", "路", "进", "心", "来", "h", "时", "力", "多", "开", "已", "许", "d", "至", "由", "很", "界", "n", "小", "与", "Z", "想", "代", "么", "分", "生", "口", "再", "妈", "望", "次", "西", "风", "种", "带", "J", "?", "实", "情", "才", "这", "?", "E", "我", "神", "格", "长", "觉", "间", "年", "眼", "无", "不", "亲", "关", "结", "0", "友", "信", "下", "却", "重", "己", "老", "2", "音", "字", "m", "呢", "明", "之", "前", "高", "P", "B", "目", "太", "e", "9", "起", "稜", "她", "也", "W", "用", "方", "子", "英", "每", "理", "便", "四", "数", "期", "中", "C", "外", "样", "a", "海", "们", "任"
]

def decode_text(text: str) -> str:
    if not text:
        return ""
    result = []
    for char in text:
        code = ord(char)
        idx = code - START_CODE
        if 0 <= idx < len(CHAR_SEQUENCE):
            result.append(CHAR_SEQUENCE[idx])
        else:
            result.append(char)
    return "".join(result)

# 我们将直接从页面解析所有榜单类别目录，实现动态抓取

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# 从页面 DOM 抽取书籍卡片的脚本（沿用既有逻辑）
EXTRACT_JS = """
() => {
    const bookMap = new Map();
    const links = document.querySelectorAll('a[href^="/page/"]');
    links.forEach(link => {
        let container = link.parentElement;
        let depth = 0;
        while (container && depth < 6) {
            if (container.querySelector('img') && container.innerText.includes('在读')) {
                const href = link.getAttribute('href');
                if (!bookMap.has(href)) {
                    bookMap.set(href, container);
                }
                break;
            }
            container = container.parentElement;
            depth++;
        }
    });

    const cards = Array.from(bookMap.values());
    const results = [];
    for (const item of cards) {
        let imgNode = item.querySelector('img');
        let cover = imgNode ? imgNode.getAttribute('src') : "";

        let title = "";
        if (imgNode && imgNode.getAttribute('alt')) {
            title = imgNode.getAttribute('alt').trim();
        }
        if (!title) {
            let textTitleNode = item.querySelector('h4, .title, h1') || item.querySelector('a[href^="/page/"]');
            if (textTitleNode) {
                let text = textTitleNode.innerText.trim();
                if (text && !/^\\d+$/.test(text)) {
                    title = text;
                }
            }
        }
        if (!title) title = "未知";
        if (title.includes("榜单说明")) continue;

        let authorNode = item.querySelector('.author, .author-name') || item.querySelector('a[href^="/author-page/"]');
        let author = authorNode ? authorNode.innerText.trim() : "未知";

        let reads = "未知";
        const lines = item.innerText.split('\\n');
        for (let line of lines) {
            if (line.includes('在读')) {
                reads = line;  // We'll decode in Python
                break;
            }
        }

        let introNode = item.querySelector('.intro, .abstract, .desc');
        let intro = introNode ? introNode.innerText.trim() : "暂无简介";

        results.push({
            title: title,
            author: author,
            reads: reads,
            intro: intro,
            cover: cover,
            url: item.querySelector('a[href^="/page/"]').getAttribute('href')
        });
    }
    return results;
}
"""


def scrape_source(page, src: dict, date_str: str, limit=30, sleep_sec=5) -> bool:
    """抓取单个榜单源的所有分类。返回是否成功完成。"""
    rank_id = src["id"]
    rank_name = src["name"]
    output_file = os.path.join(OUTPUT_DIR, snapshot_file(rank_id, date_str))
    state_file_path = os.path.join(OUTPUT_DIR, state_file(rank_id, date_str))

    # ------------- 状态恢复逻辑（按榜单独立断点续传） -------------
    completed_cats = []
    all_categories = []
    if os.path.exists(state_file_path):
        try:
            with open(state_file_path, "r", encoding="utf-8") as f:
                completed_cats = json.load(f).get("completed", [])
        except Exception:
            pass
    if os.path.exists(output_file) and len(completed_cats) > 0:
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                all_categories = json.load(f).get("categories", [])
        except Exception:
            pass
    # ----------------------------------------------------------

    init_url = src["init_url"]
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 【{rank_name}】正在访问入口页：{init_url}")
    page.goto(init_url, wait_until="load", timeout=15000)
    page.wait_for_selector('a[href^="/page/"]', timeout=5000)

    # 动态解析页面左侧该榜单的所有类别目录（按榜单路由前缀匹配）
    categories = page.evaluate(
        """(prefix) => {
            return Array.from(document.querySelectorAll('a'))
                .filter(a => a.href.includes(prefix))
                .map(a => ({
                    name: a.innerText.trim(),
                    href: a.getAttribute('href')
                }));
        }""",
        src["link_prefix"],
    )
    print(f"✅ 【{rank_name}】自适应提取到 {len(categories)} 个分类标签。开始全量模拟点击抓取...")

    for cat in categories:
        cat_name = cat["name"]
        cat_href = cat["href"]

        if cat_name in completed_cats:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏭️ 【{rank_name}】跳过今日已完成类别：{cat_name}")
            continue

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 【{rank_name}】模拟点击类别切换 -> {cat_name}")
        try:
            page.locator(f"a[href='{cat_href}']").click()
            time.sleep(2)  # 等待 SPA 页面骨架和组件请求的动画渲染完毕
            page.wait_for_selector('a[href^="/page/"]', timeout=5000)
        except Exception as e:
            print(f"切换分类出错或加载超时 {cat_name}: {e}")

        # 滚动 3 屏加载 Top ~30
        for _ in range(3):
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            time.sleep(1.5)

        try:
            books_data = page.evaluate(EXTRACT_JS)
        except Exception as e:
            print(f"执行JS抽取失败 {cat_name}: {e}")
            books_data = []

        category_books = []
        for b in books_data[:limit]:
            t = decode_text(b.get("title", ""))
            a = decode_text(b.get("author", ""))
            r_raw = decode_text(b.get("reads", ""))
            i = decode_text(b.get("intro", "")).replace("\\n", " ")
            c = b.get("cover", "")

            # 清洗在读数（如 "已完结 在读：34.8万" -> "34.8万"）
            if "在读" in r_raw:
                parts = r_raw.split("在读")
                cleaned_r = parts[1].replace(":", "").replace("：", "").strip() if len(parts) > 1 else r_raw
            else:
                cleaned_r = r_raw

            category_books.append({
                "title": t,
                "author": a,
                "reads": cleaned_r,
                "intro": i,
                "cover": c,
                "url": "https://fanqienovel.com" + b.get("url", "")
            })

        all_categories.append({
            "name": cat_name,
            "books": category_books
        })

        # 每完成一个分类就写入 JSON（防止中断丢数据）
        snapshot = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "rank_id": rank_id,
            "categories": all_categories
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)

        completed_cats.append(cat_name)
        with open(state_file_path, "w", encoding="utf-8") as f:
            json.dump({"completed": completed_cats}, f, ensure_ascii=False)

        print(f"【{rank_name}】成功抓取 {cat_name} 类别的前 {len(category_books)} 本书，进度已存档。等待 {sleep_sec} 秒防拦截...")
        time.sleep(sleep_sec)

    print(f"\n✅ 【{rank_name}】当日任务完毕！数据源：{output_file}")
    return True


def run_scraper(rank_ids=None, limit=30, sleep_sec=5):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y%m%d")
    rank_ids = rank_ids or RANK_IDS
    sources = [s for s in RANK_SOURCES if s["id"] in rank_ids]

    results = {}
    with sync_playwright() as p:
        if os.environ.get("GITHUB_ACTIONS"):
            browser = p.chromium.launch(headless=True)
        else:
            browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for idx, src in enumerate(sources):
            if idx > 0:
                pause = sleep_sec * 2
                print(f"\n⏳ 榜单切换间隔 {pause} 秒防拦截...")
                time.sleep(pause)
            try:
                print(f"\n========== ({idx + 1}/{len(sources)}) 开始抓取【{src['name']}】==========")
                results[src["id"]] = scrape_source(page, src, date_str, limit=limit, sleep_sec=sleep_sec)
            except Exception as e:
                # 单个榜单失败不影响其他榜单
                print(f"❌ 【{src['name']}】抓取失败，跳过: {e}")
                results[src["id"]] = False

        browser.close()

    print("\n========== 全部榜单抓取汇总 ==========")
    for rank_id, ok in results.items():
        status = "✅ 成功" if ok else "❌ 失败"
        print(f"  {rank_id}: {status}")
    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="番茄小说多榜单抓取")
    parser.add_argument("--ranks", type=str, default="",
                        help=f"逗号分隔的榜单 ID（可选: {','.join(RANK_IDS)}），默认全部")
    parser.add_argument("--limit", type=int, default=30, help="每分类抓取数量")
    parser.add_argument("--sleep", type=int, default=5, help="分类间隔秒数")
    args = parser.parse_args()

    selected = [r.strip() for r in args.ranks.split(",") if r.strip()] if args.ranks else []
    invalid = [r for r in selected if r not in RANK_IDS]
    if invalid:
        raise SystemExit(f"未知榜单 ID: {invalid}，可选: {RANK_IDS}")

    print(f"开始执行番茄榜单抓取计划（{len(selected) if selected else '全部'} 个榜单）...")
    run_scraper(rank_ids=selected or None, limit=args.limit, sleep_sec=args.sleep)
