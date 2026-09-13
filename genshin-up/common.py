import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "UP.json"

STANDARD_5 = {"迪卢克", "琴", "莫娜", "七七", "刻晴", "提纳里", "迪希雅", "梦见月瑞希"}


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
    """角色 -> 按时间排序的出场记录；同一期同时进普通池与混池时合并为一条（normal/mixed 可同时为真）"""
    result = {}
    index = {}

    def add(name, entry, star, mixed, banner, four, region):
        key = (name, entry["version"], entry["phase"])
        rec = index.get(key)
        if rec is None:
            rec = {
                "date": entry["start"], "end": entry["end"],
                "version": entry["version"], "phase": entry["phase"],
                "star": star, "normal": False, "mixed": False,
                "banner": None, "mix_name": None, "four": four, "region": None,
            }
            index[key] = rec
            result.setdefault(name, []).append(rec)
        if mixed:
            rec["mixed"] = True
            rec["mix_name"] = banner
            rec["region"] = region
        else:
            rec["normal"] = True
            rec["banner"] = banner

    for entry in data:
        banner_label = " / ".join(b["name"] for b in entry["banners"])
        for banner in entry["banners"]:
            add(banner["five_star"], entry, "5", False, banner["name"], entry["four_star"], None)
        for name in entry["four_star"]:
            add(name, entry, "4", False, banner_label, entry["four_star"], None)
        mixed = entry["mixed_banner"]
        if mixed:
            for name in mixed["five_star"]:
                add(name, entry, "5", True, mixed["name"], mixed["four_star"], mixed["region"])
            for name in mixed["four_star"]:
                add(name, entry, "4", True, mixed["name"], mixed["four_star"], mixed["region"])
    for recs in result.values():
        recs.sort(key=lambda r: (r["date"], r["phase"]))
    return result
