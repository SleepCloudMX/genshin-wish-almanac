import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "UP.json"


def load():
    return json.loads(DATA.read_text(encoding="utf-8"))


def parse_date(text):
    return datetime.strptime(text, "%Y/%m/%d").date()


def write_output(task, filename, text):
    path = ROOT / "output" / task / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"written: {path.relative_to(ROOT)}")


def appearances(data):
    """角色 -> 按时间排序的出场记录（含 star 与 mixed 标记）"""
    result = {}

    def add(name, entry, star, mixed):
        result.setdefault(name, []).append(
            {"date": entry["start"], "version": entry["version"], "star": star, "mixed": mixed}
        )

    for entry in data:
        for banner in entry["banners"]:
            add(banner["five_star"], entry, "5", False)
        for name in entry["four_star"]:
            add(name, entry, "4", False)
        mixed = entry["mixed_banner"]
        if mixed:
            for name in mixed["five_star"]:
                add(name, entry, "5", True)
            for name in mixed["four_star"]:
                add(name, entry, "4", True)
    for recs in result.values():
        recs.sort(key=lambda r: r["date"])
    return result
