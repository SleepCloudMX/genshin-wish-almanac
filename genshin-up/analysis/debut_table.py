import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common


def main():
    app = common.appearances(common.load())
    debuted, resident = [], []
    for name, recs in app.items():
        normal = [r for r in recs if not r["mixed"]]
        mixed_count = len(recs) - len(normal)
        if normal:
            first = normal[0]
            debuted.append((first["date"], first["version"], name, first["star"]))
        else:
            resident.append((name, recs[0]["star"], mixed_count))
    debuted.sort(key=lambda r: (r[0], r[1], r[2]))
    lines = [
        "# 角色首次 UP 时间表",
        "",
        f"共 {len(debuted)} 名角色按首发时间排列；另 {len(resident)} 名常驻角色无首发 UP（见文末）。",
        "",
        "| 首次UP日期 | 版本 | 角色 | 星级 |",
        "| --- | --- | --- | --- |",
    ]
    for date, version, name, star in debuted:
        lines.append(f"| {date} | {version} | {name} | {star}★ |")
    lines += [
        "",
        "## 无首发 UP（常驻池角色）",
        "",
        "| 角色 | 星级 | 混池次数 |",
        "| --- | --- | --- |",
    ]
    for name, star, mixed_count in sorted(resident):
        lines.append(f"| {name} | {star}★ | {mixed_count} |")
    common.write_output("debut-table", "debut-table.md", "\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
