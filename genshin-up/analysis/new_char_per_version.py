import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common


def main():
    data = common.load()
    versions = sorted({e["version"] for e in data}, key=lambda v: [int(p) for p in v.split(".")])
    per = {v: {"5": [], "4": []} for v in versions}
    for name, recs in common.appearances(data).items():
        normal = [r for r in recs if r["normal"]]
        if normal:
            first = normal[0]
            per[first["version"]][first["star"]].append(name)
    lines = [
        "# 各版本新角色数量（按首次 UP 口径）",
        "",
        "| 版本 | 新五星数 | 新四星数 | 合计 | 新五星 | 新四星 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    total = {"5": 0, "4": 0}
    for version in versions:
        five, four = per[version]["5"], per[version]["4"]
        total["5"] += len(five)
        total["4"] += len(four)
        lines.append(
            f"| {version} | {len(five)} | {len(four)} | {len(five) + len(four)} | "
            f"{' '.join(five) or '—'} | {' '.join(four) or '—'} |"
        )
    lines.append(
        f"| **合计** | **{total['5']}** | **{total['4']}** | **{total['5'] + total['4']}** | | |"
    )
    common.write_output("new-char-per-version", "new-char-per-version.md", "\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
