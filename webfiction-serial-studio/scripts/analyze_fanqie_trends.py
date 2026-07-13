#!/usr/bin/env python3
"""Analyze public Fanqie rank-card signals without claiming access to novel prose."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


SIGNAL_GROUPS = {
    "主角身份": {
        "学生": ("大学", "学生", "校园"),
        "经营者": ("老板", "创业", "开店", "公司", "厂长", "首富"),
        "职业角色": ("医生", "警察", "律师", "教师", "教授", "厨师", "主播", "明星"),
        "高位身份": ("公主", "王爷", "太子", "皇后", "女帝", "将军"),
        "家庭身份": ("奶爸", "宝妈", "丈夫", "妻子", "老婆", "继母"),
    },
    "核心优势": {
        "重生先知": ("重生", "前世", "回到", "再活", "预知"),
        "穿越错位": ("穿越", "穿书", "魂穿", "替嫁"),
        "系统或空间": ("系统", "空间", "金手指", "签到"),
        "专业能力": ("厨艺", "医术", "技术", "商业", "科研", "破案"),
        "资源积累": ("赚钱", "财富", "首富", "囤货", "基建", "经营"),
    },
    "开局危机": {
        "生存危机": ("末世", "逃荒", "逃亡", "追杀", "死亡", "破产", "绝境"),
        "关系破裂": ("离婚", "退婚", "背叛", "替嫁", "分手", "续弦"),
        "身份跌落": ("亡国", "流放", "落魄", "被赶", "失业", "入狱"),
        "倒计时": ("千万不要死", "只剩", "倒计时", "来不及"),
    },
    "关系承诺": {
        "先婚后爱": ("先婚后爱", "闪婚", "替嫁", "冲喜", "契约婚姻"),
        "追妻或纠错": ("追妻", "后悔", "求娶", "不做续弦", "离婚后"),
        "家庭守护": ("宠妻", "奶爸", "养娃", "全家", "家人"),
        "强关系反差": ("教授老婆", "疯批", "死对头", "青梅", "暗恋"),
    },
}

TITLE_PATTERNS = {
    "时间重置+新选择": re.compile(r"重生|回到|再活|穿越|穿书|\d{2,4}年"),
    "身份反差直给": re.compile(r"大学|教授|老板|首富|公主|王爷|太子|女帝|奶爸|老婆|丈夫|妻子"),
    "危机直接入题": re.compile(r"死|逃|破产|离婚|退婚|替嫁|亡国|末世|追杀"),
    "行动与结果承诺": re.compile(r"靠.+(?:成|赚|建|养|救)|成了|成为|逆袭|崛起|开局|拿下"),
    "关系悬念句": re.compile(r"求娶|后悔|宠上天|不要死|敢跑|结婚|闪婚|先婚"),
}

DIRECTION_RULES = {
    "年代/都市重生创业": {
        "keywords": ("重生", "年代", "回到", "创业", "开店", "赚钱", "首富", "公司", "做生意"),
        "path": "现实困境或前世遗憾 → 第一笔现金流验证 → 渠道与团队扩张 → 行业竞争/资本门槛 → 家庭或身份回收",
    },
    "都市职业成长": {
        "keywords": ("职场", "医生", "警察", "律师", "教师", "教授", "科研", "主播", "明星"),
        "path": "职业难题切入 → 用专业能力建立可信胜利 → 同行/组织阻力升级 → 职业地位与关系同步变化",
    },
    "关系反差与情绪回收": {
        "keywords": ("老婆", "丈夫", "结婚", "替嫁", "先婚后爱", "离婚", "求娶", "宠妻", "疯批"),
        "path": "强制或意外绑定 → 误判与试探 → 利益合作 → 关键选择证明立场 → 关系确认后引入更大外部压力",
    },
    "生存积累与势力扩张": {
        "keywords": ("末世", "逃荒", "乱世", "基建", "囤货", "建国", "争霸", "种田"),
        "path": "即时生存危机 → 资源闭环 → 伙伴/领地形成 → 规则或势力对抗 → 阶段秩序重建",
    },
}


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object.")
    return data


def load_snapshot(path: Path) -> dict:
    data = load_json(path)
    if not isinstance(data.get("boards"), list):
        raise ValueError("Snapshot must be an object with a boards array.")
    return data


def normalize(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def private_use_ratio(value: str) -> float:
    if not value:
        return 0.0
    return sum(0xE000 <= ord(char) <= 0xF8FF for char in value) / len(value)


def merge_visual_review(snapshot: dict, review: dict | None) -> None:
    if not review:
        return
    rows = review.get("entries")
    if not isinstance(rows, list):
        raise ValueError("Visual review must contain an entries array.")
    allowed = {
        "title", "author", "public_blurb", "public_tags", "latest_update",
        "completion_status", "reading_count", "updated_at",
    }
    by_url = {normalize(row.get("url")): row for row in rows if isinstance(row, dict) and row.get("url")}
    for board in snapshot.get("boards", []):
        for entry in board.get("entries", []):
            row = by_url.get(normalize(entry.get("url")))
            if not row:
                continue
            for key in allowed:
                if key in row:
                    entry[key] = row[key]
            entry["evidence_method"] = "public_rank_card_visual_review"


def iter_entries(snapshot: dict) -> Iterable[tuple[dict, dict]]:
    for board in snapshot.get("boards", []):
        if not isinstance(board, dict):
            continue
        for entry in board.get("entries", []):
            if isinstance(entry, dict):
                yield board, entry


def entry_text(entry: dict) -> str:
    tags = entry.get("public_tags") or []
    if not isinstance(tags, list):
        tags = [tags]
    return " ".join(
        filter(None, [normalize(entry.get("title")), normalize(entry.get("public_blurb")), " ".join(map(normalize, tags))])
    )


def completion_status(entry: dict) -> str:
    explicit = normalize(entry.get("completion_status")).lower()
    if explicit in {"completed", "serializing"}:
        return explicit
    text = normalize(entry.get("latest_update"))
    return "completed" if re.search(r"完结|大结局|终章|全文完", text) else "unknown"


def classify_entry(entry: dict) -> dict[str, list[str]]:
    text = entry_text(entry)
    title = normalize(entry.get("title"))
    result: dict[str, list[str]] = {}
    for group, labels in SIGNAL_GROUPS.items():
        result[group] = [label for label, words in labels.items() if any(word in text for word in words)]
    result["标题公式"] = [label for label, pattern in TITLE_PATTERNS.items() if pattern.search(title)]
    result["发展方向"] = [
        label for label, rule in DIRECTION_RULES.items() if any(word in text for word in rule["keywords"])
    ]
    return result


def score_tracks(snapshot: dict) -> list[dict]:
    tracks: dict[str, dict] = defaultdict(
        lambda: {"boards": set(), "rank_points": 0, "entries": 0, "sources": set(), "completed": 0, "new": 0}
    )
    for board, entry in iter_entries(snapshot):
        genre = normalize(board.get("genre") or board.get("name") or "未标注赛道")
        record = tracks[genre]
        board_name = normalize(board.get("name") or "未命名榜单")
        record["boards"].add(board_name)
        if board.get("source_url"):
            record["sources"].add(str(board["source_url"]))
        try:
            rank = int(entry.get("rank", 21))
        except (TypeError, ValueError):
            rank = 21
        record["rank_points"] += max(0, 21 - rank)
        record["entries"] += 1
        record["new"] += int("新书榜" in board_name)
        record["completed"] += int("阅读榜" in board_name and completion_status(entry) == "completed")

    results = []
    for genre, record in tracks.items():
        boards = sorted(record["boards"])
        reading = any("阅读榜" in item for item in boards)
        new = any("新书榜" in item for item in boards)
        results.append(
            {
                "genre": genre,
                "score": record["rank_points"] + len(boards) * 12 + (10 if reading and new else 0),
                "boards": boards,
                "entries": record["entries"],
                "new": record["new"],
                "completed": record["completed"],
                "sources": sorted(record["sources"]),
            }
        )
    return sorted(results, key=lambda item: (-item["score"], item["genre"]))


def summarize_signals(rows: list[tuple[dict, dict]]) -> dict[str, Counter]:
    summary = {group: Counter() for group in (*SIGNAL_GROUPS, "标题公式", "发展方向")}
    for _, entry in rows:
        for group, labels in classify_entry(entry).items():
            summary[group].update(labels)
    return summary


def render_counter(counter: Counter, empty: str = "公开字段中未形成稳定信号") -> str:
    return "、".join(f"{name}（{count}）" for name, count in counter.most_common(6)) or empty


def compact(value: object, limit: int = 88) -> str:
    text = normalize(value).replace("|", "｜")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def target_alignment(target: str, rows: list[tuple[dict, dict]]) -> tuple[int, str]:
    if not target:
        return 0, "未指定目标方向，等待用户选择后再判断。"
    keyword_sets = []
    if any(word in target for word in ("重生", "年代", "2008", "08年")):
        keyword_sets.append(("重生", "年代", "回到", "前世", "再活", "2008", "08年"))
    if any(word in target for word in ("创业", "商业", "经营")):
        keyword_sets.append(("创业", "做生意", "经营", "公司", "开店", "赚钱", "老板", "首富"))
    if not keyword_sets:
        tokens = [token for token in re.split(r"[\s、+/，]+", target) if len(token) >= 2]
        keyword_sets = [tuple(tokens)] if tokens else []
    matched = 0
    for _, entry in rows:
        text = entry_text(entry)
        if keyword_sets and all(any(word in text for word in words) for words in keyword_sets):
            matched += 1
    if matched >= 3:
        verdict = "直接证据较强：可按目标方向继续拆书，但仍要以原创事件链实现。"
    elif matched >= 1:
        verdict = "只有相邻或少量证据：应扩大同赛道采样，再决定是趋势优先还是个人偏好优先。"
    else:
        verdict = "当前可用样本未支持该目标：不得把它写成‘当前热门推荐’，应扩大采样或明确按用户偏好立项。"
    return matched, verdict


def render_samples(rows: list[tuple[dict, dict]], limit: int = 6) -> list[str]:
    lines = ["| 榜单/赛道 | 排名 | 书名 | 公开内容承诺（简介节选） | 状态 |", "| --- | ---: | --- | --- | --- |"]
    for board, entry in rows[:limit]:
        status = {"completed": "已完结", "serializing": "连载中"}.get(completion_status(entry), "未确认")
        title = compact(entry.get("title"), 36) or "未采到标题"
        title_cell = f"[{title}]({entry.get('url')})" if entry.get("url") else title
        lines.append(
            f"| {compact(board.get('name'))}/{compact(board.get('genre'))} | {entry.get('rank', '?')} | "
            f"{title_cell} | {compact(entry.get('public_blurb')) or '未采到可用简介'} | {status} |"
        )
    if len(lines) == 2:
        lines.append("| 无样本 | - | - | - | - |")
    return lines


def render_report(snapshot: dict, tracks: list[dict], limit: int, target: str) -> str:
    all_rows = list(iter_entries(snapshot))
    obfuscated = [
        entry for _, entry in all_rows
        if private_use_ratio(entry_text(entry)) >= 0.08 or bool((entry.get("text_quality") or {}).get("needs_visual_review"))
    ]
    reviewed = [entry for _, entry in all_rows if entry.get("evidence_method") == "public_rank_card_visual_review"]
    usable_rows = [
        (board, entry) for board, entry in all_rows
        if entry.get("evidence_method") == "public_rank_card_visual_review"
        or (private_use_ratio(entry_text(entry)) < 0.08 and not bool((entry.get("text_quality") or {}).get("needs_visual_review")))
    ]
    new_rows = [(board, entry) for board, entry in usable_rows if "新书榜" in normalize(board.get("name"))]
    completed_rows = [
        (board, entry) for board, entry in usable_rows
        if "阅读榜" in normalize(board.get("name")) and completion_status(entry) == "completed"
    ]
    all_signals = summarize_signals(usable_rows)
    new_signals = summarize_signals(new_rows)
    completed_signals = summarize_signals(completed_rows)
    target_matches, target_verdict = target_alignment(target, usable_rows)

    lines = [
        "# 番茄公开榜单市场核心报告",
        "",
        f"- 采集时间：{snapshot.get('captured_at', '未知')}",
        f"- 缓存状态：{snapshot.get('status', '未知')}",
        f"- 榜单入口：{snapshot.get('source', '未知')}",
        f"- 采样赛道：{'、'.join(snapshot.get('sampled_genres') or []) or '快照内全部赛道'}",
        f"- 目标方向：{target or '尚未指定'}",
        "- 榜单口径：公开页仅有男女频阅读榜、新书榜；下文“完结观察集”来自阅读榜卡片的公开完结标记，不是虚构的独立完结榜。",
        "- 结论边界：标题、标签、公开简介可验证读者承诺和发展方向；不能据此声称掌握原书逐章结构或正文文风。",
        "",
        "## 数据质量",
        "",
        f"- 有效榜单：{len(snapshot.get('boards', []))}；作品卡片：{len(all_rows)}；可用于内容分析：{len(usable_rows)}；新书样本：{len(new_rows)}；阅读榜完结样本：{len(completed_rows)}。",
        f"- 自定义字体待视觉复核：{len(obfuscated)}；已人工视觉复核：{len(reviewed)}。待复核字段不参与强结论，只保留为线索。",
        "",
        "## 赛道覆盖",
        "",
        "| 赛道 | 信号分 | 新书样本 | 完结观察样本 | 公开榜单 | 来源 |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for track in tracks[:limit]:
        sources = " ".join(f"[来源]({url})" for url in track["sources"][:2]) or "未记录"
        lines.append(
            f"| {track['genre']} | {track['score']} | {track['new']} | {track['completed']} | {'、'.join(track['boards'])} | {sources} |"
        )
    if not tracks:
        lines.append("| 无可用数据 | 0 | 0 | 0 | 采集失败或受限 | 请查看快照 notes |")

    lines.extend([
        "",
        "## 当前市场核心（公开字段证据）",
        "",
        f"- **书名如何给承诺**：{render_counter(all_signals['标题公式'])}。",
        f"- **主角身份切口**：{render_counter(all_signals['主角身份'])}。",
        f"- **主角可依赖的优势**：{render_counter(all_signals['核心优势'])}。",
        f"- **开局压力**：{render_counter(all_signals['开局危机'])}。",
        f"- **关系与情绪承诺**：{render_counter(all_signals['关系承诺'])}。",
        f"- **公开简介展示的发展方向**：{render_counter(all_signals['发展方向'])}。",
        f"- **目标方向匹配**：{target_matches}/{len(usable_rows)} 个可用样本同时命中目标的关键约束。{target_verdict}",
        "",
        "这里的“核心”不是把高频词拼进一本书，而是同时完成四件事：标题让读者一眼知道人物/危机/结果之一；简介给出可立刻行动的开局；前三个阶段能看见升级路径；每次事业或生存推进都带来关系、身份或情绪变化。",
        "",
        "## 新书信号 vs 完结可持续性",
        "",
        "| 观察层 | 标题公式 | 发展方向 | 关系承诺 | 应如何使用 |",
        "| --- | --- | --- | --- | --- |",
        f"| 新书榜 | {render_counter(new_signals['标题公式'])} | {render_counter(new_signals['发展方向'])} | {render_counter(new_signals['关系承诺'])} | 用于判断近期点击入口与包装，不证明能撑长篇。 |",
        f"| 阅读榜完结观察集 | {render_counter(completed_signals['标题公式'], '当前采样未取得可用完结标题信号')} | {render_counter(completed_signals['发展方向'], '当前采样未取得可用完结发展信号')} | {render_counter(completed_signals['关系承诺'], '当前采样未取得可用完结关系信号')} | 用于判断公开承诺是否能延伸到完整阶段路径；样本不足时必须继续采样，不能硬推。 |",
        "",
        "## 可验证的发展路径",
        "",
    ])
    for label, count in all_signals["发展方向"].most_common():
        lines.append(f"- **{label}（{count} 个公开样本命中）**：{DIRECTION_RULES[label]['path']}。这是立项时要重新设计的升级骨架，不是来源作品剧情复述。")
    if not all_signals["发展方向"]:
        lines.append("- 当前公开文本质量不足，不能稳定提炼发展路径；先完成视觉复核或扩大合规采样。")

    lines.extend(["", "## 新书榜公开样本", ""])
    lines.extend(render_samples(new_rows))
    lines.extend(["", "## 阅读榜完结作品观察集", ""])
    lines.extend(render_samples(completed_rows))
    lines.extend([
        "",
        "## 原创立项使用规则",
        "",
        "1. 先选一个主承诺：事业增长、关系兑现、生存扩张或职业成长；其余只做副线，避免标签大杂烩。",
        "2. 用公开样本验证“读者为什么点开”，再独立设计主角欲望、人物关系和事件因果链；不得换名复刻样本简介中的事件顺序。",
        "3. 新书榜只能决定近期包装与前期压力；至少用一个完结观察集或用户授权长篇材料验证中后期升级，证据不足就标注待验证。",
        "4. 简介必须显式写出：开局处境、主角第一次主动选择、可见的三段升级路径、关系/身份回收；不能只写世界观和空泛逆袭。",
        "5. 若目标是都市重生创业，优先把年代节点变成具体经营限制与机会窗口，再设计第一笔现金流、第二增长曲线、组织升级和家庭回收，不能只靠先知连续捡漏。",
        "",
        "## 下一步门禁",
        "",
        "请先确认赛道与市场核心。未选择前不生成书名或大纲；未确认书名、简介和大纲前不得开始正文。",
        "",
        "## 采集备注",
        "",
    ])
    notes = snapshot.get("notes") or ["无"]
    lines.extend(f"- {note}" for note in notes)
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--visual-review", type=Path)
    parser.add_argument("--target", default="")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be at least 1")

    snapshot = load_snapshot(args.snapshot)
    review = load_json(args.visual_review) if args.visual_review else None
    merge_visual_review(snapshot, review)
    tracks = score_tracks(snapshot)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_report(snapshot, tracks, args.limit, normalize(args.target)), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
