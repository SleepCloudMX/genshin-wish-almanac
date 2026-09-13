import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common


def main():
    app = common.appearances(common.load())
    sections = []
    for star, title in (("5", "五星"), ("4", "四星")):
        rows = []
        for name, recs in app.items():
            if recs[0]["star"] != star:
                continue
            ups = [r for r in recs if not r["mixed"]]
            if not ups:
                continue
            dates = [common.parse_date(r["date"]) for r in ups]
            gaps = [(b - a).days for a, b in zip(dates, dates[1:])]
            rows.append((name, ups, len(recs) - len(ups), gaps))
        rows.sort(key=lambda r: (-len(r[3]), r[1][0]["date"], r[0]))
        lines = [
            f"## {title}（{len(rows)} 名，按复刻次数降序）",
            "",
            "| 角色 | 首次UP | UP次数 | 复刻次数 | 各次UP日期 | 每次间隔(天) | 平均间隔(天) | 混池次数 |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for name, ups, mixed_count, gaps in rows:
            avg = f"{sum(gaps) / len(gaps):.1f}" if gaps else "—"
            lines.append(
                f"| {name} | {ups[0]['date']} | {len(ups)} | {len(ups) - 1} | "
                f"{'、'.join(r['date'] for r in ups)} | "
                f"{'、'.join(str(g) for g in gaps) or '—'} | {avg} | {mixed_count} |"
            )
        sections.append("\n".join(lines))
    text = "\n\n".join(
        ["# 角色复刻统计", "", "复刻 = 再次进入普通角色活动祈愿；混池单列，不计入复刻。", ""] + sections
    )
    common.write_output("rerun-stats", "rerun-stats.md", text + "\n")


if __name__ == "__main__":
    main()
