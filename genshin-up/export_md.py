import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common


def main():
    data = common.load()
    lines = [
        "<!-- 本文件由 genshin-up/export_md.py 从 data/UP.json 生成，请勿手动编辑 -->",
        "",
        "# 原神 UP 池一览",
        "",
        "| 版本 | 日期 | 五星 | 四星 | 混池 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in data:
        five = " ".join(b["five_star"] for b in entry["banners"])
        four = " ".join(entry["four_star"])
        mixed = entry["mixed_banner"]
        mixed_col = "" if not mixed else (mixed["region"] or "跨地区")
        lines.append(
            f"| {entry['version']} {entry['phase']} | {entry['start']} | "
            f"{five} | {four} | {mixed_col} |"
        )
    lines += [
        "",
        "## 混池明细",
        "",
        "| 版本 | 名称 | 地区 | 五星 | 四星 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in data:
        mixed = entry["mixed_banner"]
        if not mixed:
            continue
        region = mixed["region"] or "跨地区（非地区主题）"
        lines.append(
            f"| {entry['version']} {entry['phase']} | {mixed['name']} | {region} | "
            f"{' '.join(mixed['five_star'])} | {' '.join(mixed['four_star'])} |"
        )
    (common.ROOT / "UP.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"UP.md 已生成：{len(data)} 期卡池")


if __name__ == "__main__":
    main()
