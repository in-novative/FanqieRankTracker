"""
榜单源共享配置。

番茄小说榜单 URL 规律: /rank/{频道}_{榜单类型}_{分类ID}
  频道: 0=女频, 1=男频
  榜单类型: 1=新书榜, 2=阅读榜

所有数据产物路径均由 rank_id 派生：
  快照:     data/fanqie_{rank_id}_ranks_YYYYMMDD.json （female_new 与历史命名完全一致）
  断点状态: data/task_state_{rank_id}_YYYYMMDD.json
  趋势归档: data/trends/{rank_id}/YYYY-MM-DD.json
  最新聚合: data/latest/{rank_id}.json
  静态接口: api/{rank_id}/lastest/...
"""

BASE_HOST = "https://fanqienovel.com"

RANK_SOURCES = [
    {
        "id": "female_new",
        "name": "女频新书榜",
        "gender": "female",   # 决定赛道分组与题材关键词
        "kind": "new",        # new=新书榜, hot=阅读榜
        "init_url": f"{BASE_HOST}/rank/0_1_1139",
        "link_prefix": "/rank/0_1_",
    },
    {
        "id": "male_new",
        "name": "男频新书榜",
        "gender": "male",
        "kind": "new",
        "init_url": f"{BASE_HOST}/rank/1_1_261",
        "link_prefix": "/rank/1_1_",
    },
    {
        "id": "female_hot",
        "name": "女频阅读榜",
        "gender": "female",
        "kind": "hot",
        "init_url": f"{BASE_HOST}/rank/0_2_1139",
        "link_prefix": "/rank/0_2_",
    },
    {
        "id": "male_hot",
        "name": "男频阅读榜",
        "gender": "male",
        "kind": "hot",
        "init_url": f"{BASE_HOST}/rank/1_2_261",
        "link_prefix": "/rank/1_2_",
    },
]

RANK_IDS = [s["id"] for s in RANK_SOURCES]


def get_source(rank_id: str) -> dict:
    for s in RANK_SOURCES:
        if s["id"] == rank_id:
            return s
    raise KeyError(f"未知榜单: {rank_id}")


def snapshot_prefix(rank_id: str) -> str:
    """快照文件名前缀: fanqie_{rank_id}_ranks（female_new 兼容历史命名）"""
    return f"fanqie_{get_source(rank_id)['id']}_ranks"


def snapshot_file(rank_id: str, date_compact: str) -> str:
    return f"{snapshot_prefix(rank_id)}_{date_compact}.json"


def state_file(rank_id: str, date_compact: str) -> str:
    return f"task_state_{rank_id}_{date_compact}.json"


def trends_dirname(rank_id: str) -> str:
    return rank_id


# 综合赛道分组（按频道）。未匹配到现有分类的分组会被自动跳过，
# 未被任何分组收纳的具体分类仍会独立参与统计。
GENRE_GROUPS = {
    "female": [
        {"name": "古风言情", "categories": ["古风世情", "古言脑洞", "宫斗宅斗", "种田"]},
        {"name": "现代言情", "categories": ["现言脑洞", "豪门总裁", "职场婚恋", "青春甜宠"]},
        {"name": "幻想言情", "categories": ["玄幻言情", "科幻末世", "悬疑脑洞", "女频悬疑"]},
        {"name": "快穿衍生", "categories": ["快穿", "女频衍生"]},
        {"name": "年代民国", "categories": ["年代", "民国言情"]},
        {"name": "娱乐星光", "categories": ["星光璀璨"]},
        {"name": "游戏体育", "categories": ["游戏体育"]},
    ],
    # 男频 19 个真实分类（2026-08 实测）：西方奇幻/东方仙侠/科幻末世/都市日常/都市修真/
    # 都市高武/历史古代/战神赘婿/都市种田/传统玄幻/历史脑洞/悬疑脑洞/都市脑洞/玄幻脑洞/
    # 悬疑灵异/抗战谍战/游戏体育/动漫衍生/男频衍生
    "male": [
        {"name": "现代都市", "categories": ["都市日常", "都市修真", "都市高武", "战神赘婿", "都市种田", "都市脑洞"]},
        {"name": "东方玄幻", "categories": ["传统玄幻", "玄幻脑洞", "东方仙侠", "西方奇幻"]},
        {"name": "历史军事", "categories": ["历史古代", "历史脑洞", "抗战谍战"]},
        {"name": "悬疑科幻", "categories": ["悬疑脑洞", "悬疑灵异", "科幻末世"]},
        {"name": "游戏衍生", "categories": ["游戏体育", "动漫衍生", "男频衍生"]},
    ],
}

# 高频题材关键词（按频道），用于全站热点统计
MARKET_KEYWORDS = {
    "female": [
        "重生", "穿书", "快穿", "系统", "空间", "团宠", "萌宝", "幼崽", "女配", "炮灰",
        "反派", "权臣", "宅斗", "宫斗", "和离", "替嫁", "逃荒", "种田", "美食", "经商",
        "年代", "七零", "八零", "军婚", "豪门", "总裁", "真假千金", "先婚后爱", "追妻",
        "甜宠", "双洁", "强制爱", "无CP", "末世", "废土", "天灾", "囤货", "异能",
        "国运", "星际", "修仙", "玄学", "无限流", "悬疑", "直播", "综艺", "娱乐圈",
        "校园", "暗恋", "青梅竹马", "民国", "兽世", "远古", "基建",
    ],
    "male": [
        "重生", "穿越", "系统", "无敌", "签到", "开局", "天骄", "战神", "神豪",
        "赘婿", "兵王", "神医", "鉴宝", "直播", "宗门", "修仙", "炼丹", "炼器",
        "御兽", "诡秘", "克苏鲁", "规则怪谈", "天灾", "末世", "废土", "高武",
        "异能", "官场", "谍战", "抗战", "争霸", "领主", "基建", "种田", "无限流",
        "同人", "电竞", "马甲", "反派", "金手指", "多子多福", "长生", "气运",
    ],
}


def genre_groups_for(rank_id: str) -> list:
    return GENRE_GROUPS.get(get_source(rank_id)["gender"], [])


def market_keywords_for(rank_id: str) -> list:
    return MARKET_KEYWORDS.get(get_source(rank_id)["gender"], [])


def frontend_meta() -> list:
    """下发给前端的榜单元数据（含赛道分组与关键词），使前端零硬编码。"""
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "gender": s["gender"],
            "kind": s["kind"],
            "genre_groups": genre_groups_for(s["id"]),
            "market_keywords": market_keywords_for(s["id"]),
        }
        for s in RANK_SOURCES
    ]
