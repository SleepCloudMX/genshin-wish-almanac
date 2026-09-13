import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def cell(items):
    return " ".join(items)


def main():
    data = json.loads((ROOT / "UP.json").read_text(encoding="utf-8"))
    lines = [
        "<!-- 本文件由 export_md.py 从 UP.json 生成，请勿手动编辑 -->",
        "",
        "# 原神 UP 池一览",
        "",
        "| 版本 | 日期 | 五星 | 四星 | 混池 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for e in data:
        five = cell(f"{b['five_star']}（{b['name']}）" for b in e["banners"])
        four = cell(e["four_star"])
        mb = e["mixed_banner"]
        col = "" if not mb else (mb["region"] or "跨地区")
        lines.append(
            f"| {e['version']} {e['phase']} | {e['start']} ~ {e['end']} | "
            f"{five} | {four} | {col} |"
        )
    lines += [
        "",
        "## 混池明细",
        "",
        "| 版本 | 名称 | 地区 | 五星 | 四星 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for e in data:
        mb = e["mixed_banner"]
        if not mb:
            continue
        region = mb["region"] or "跨地区（非地区主题）"
        lines.append(
            f"| {e['version']} {e['phase']} | {mb['name']} | {region} | "
            f"{cell(mb['five_star'])} | {cell(mb['four_star'])} |"
        )
    (ROOT / "UP.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"UP.md 已生成：{len(data)} 期卡池")


if __name__ == "__main__":
    main()
