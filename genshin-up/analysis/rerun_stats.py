import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common


def cell(rec):
    tag = ""
    if rec["mixed"] and rec["normal"]:
        tag = "(UP+混)"
    elif rec["mixed"]:
        tag = "(混)"
    return rec["date"] + tag


def fmt(value):
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)


def main():
    data = common.load()
    today = date.today()
    last = data[-1]
    app = common.appearances(data)
    sections = []
    for star, title in (("5", "五星"), ("4", "四星")):
        rows = []
        for name, recs in app.items():
            if recs[0]["star"] != star:
                continue
            if not any(r["normal"] for r in recs):
                continue
            ends = [common.parse_date(r["end"]) for r in recs]
            starts = [common.parse_date(r["date"]) for r in recs]
            gaps = [max(0, (starts[i] - ends[i - 1]).days - 1) for i in range(1, len(recs))]
            ongoing = (
                recs[-1]["version"] == last["version"]
                and recs[-1]["phase"] == last["phase"]
                and common.parse_date(last["end"]) >= today
            )
            rows.append({
                "name": name,
                "first": recs[0]["date"],
                "ups": len(recs),
                "reruns": len(recs) - 1,
                "cells": [cell(r) for r in recs],
                "gaps": gaps,
                "min": min(gaps) if gaps else None,
                "avg": (sum(gaps) / len(gaps)) if gaps else None,
                "max": max(gaps) if gaps else None,
                "waiting": "UP 中" if ongoing else str((today - ends[-1]).days),
                "mixed": sum(1 for r in recs if r["mixed"]),
            })
        rows.sort(key=lambda r: (-r["reruns"], r["first"], r["name"]))
        lines = [
            f"## {title}（{len(rows)} 名，按复刻次数降序）",
            "",
            "| 角色 | 首次UP | UP次数 | 复刻次数 | 各次UP日期 | 每次间隔(天) | 最短 | 平均 | 最长 | 未复刻(天) | 混池 |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for r in rows:
            lines.append(
                f"| {r['name']} | {r['first']} | {r['ups']} | {r['reruns']} | "
                f"{'、'.join(r['cells'])} | {'、'.join(str(g) for g in r['gaps']) or '—'} | "
                f"{fmt(r['min'])} | {fmt(r['avg'])} | {fmt(r['max'])} | {r['waiting']} | {r['mixed']} |"
            )
        sections.append("\n".join(lines))
    text = "\n\n".join(
        [
            "# 角色复刻统计",
            "",
            f"复刻 = 再次 UP（普通池与混池均计入）；常驻角色（无普通 UP）不计入本表。",
            f"间隔 = 上个卡池结束日 → 下个卡池开始日之间不含两端的天数；未复刻 = 距上次结束日至 {today.strftime('%Y/%m/%d')} 的天数，UP 中表示当前在池。",
            "标注：日期后缀 (混) = 仅在混池；(UP+混) = 同期普通池与混池都有。",
            "",
        ]
        + sections
    )
    common.write_output("rerun-stats", "rerun-stats.md", text + "\n")


if __name__ == "__main__":
    main()
