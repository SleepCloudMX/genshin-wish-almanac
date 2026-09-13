import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

CDN = "https://cdn.jsdelivr.net/gh/BTMuli/TeyvatGuide@master/"
CACHE = common.ROOT / ".cache" / "chars"
PHASE_ORDER = {"上": 0, "中": 1, "下": 2}
REGIONS = {"晨风之诗": "蒙德", "玉岩之忆": "璃月", "鸣雷贯天原": "稻妻", "露草的行盏": "须弥", "露景涓然": "枫丹"}

fetched = 0


def fetch(path):
    url = CDN + path
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(req, timeout=60))


def char_name(cid):
    global fetched
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{cid}.json"
    if not f.exists():
        d = fetch(f"src/data/WIKI/character/{cid}.json")
        f.write_text(
            json.dumps({"id": d.get("id"), "name": d.get("name")}, ensure_ascii=False),
            encoding="utf-8",
        )
        fetched += 1
        if fetched % 25 == 0:
            print(f"  已拉取角色 {fetched} 个…")
    return json.loads(f.read_text(encoding="utf-8"))["name"]


def build_phases(rows):
    groups = {}
    mix = {}
    for e in rows:
        if e["type"] in (301, 400):
            groups.setdefault((e["version"], e["order"]), []).append(e)
        elif e["type"] == 500:
            mix[(e["version"], e["order"])] = e
    maxord = {}
    for (v, o) in groups:
        maxord[v] = max(maxord.get(v, 0), o)
    out = {}
    for (v, o), es in groups.items():
        es.sort(key=lambda x: x["type"] == 400)
        label = "上" if o == 1 else ("下" if o == maxord[v] else "中")
        entry = {
            "version": v,
            "phase": label,
            "start": es[0]["from"][:10].replace("-", "/"),
            "end": max(e["to"] for e in es)[:10].replace("-", "/"),
            "banners": [{"name": e["name"], "five_star": char_name(e["up5List"][0])} for e in es],
            "four_star": [char_name(i) for i in es[0]["up4List"]],
            "mixed_banner": None,
        }
        if (v, o) in mix:
            m = mix[(v, o)]
            entry["mixed_banner"] = {
                "name": m["name"],
                "region": REGIONS.get(m["name"]),
                "five_star": [char_name(i) for i in m["up5List"] if i >= 10000000],
                "four_star": [char_name(i) for i in m["up4List"] if i >= 10000000],
            }
        out[(v, label)] = entry
    return out


def sort_key(e):
    return ([int(p) for p in e["version"].split(".")], PHASE_ORDER[e["phase"]])


def dump(data):
    lines = ["["]
    for i, e in enumerate(data):
        body = ", ".join(f'"{k}": {json.dumps(v, ensure_ascii=False)}' for k, v in e.items())
        lines.append("  {" + body + "}" + ("," if i < len(data) - 1 else ""))
    lines.append("]")
    return "\n".join(lines) + "\n"


def report_existing(local, built):
    changed = 0
    for e in local:
        b = built.get((e["version"], e["phase"]))
        if not b:
            print(f"  ! 本地 {e['version']} {e['phase']} 在上游数据中找不到（手工补充的期次？）")
            continue
        diffs = []
        for key in ("start", "end"):
            if e[key] != b[key]:
                diffs.append(f"{key}: {e[key]} -> {b[key]}")
        if [x["name"] for x in e["banners"]] != [x["name"] for x in b["banners"]]:
            diffs.append("卡池名变化")
        if [x["five_star"] for x in e["banners"]] != [x["five_star"] for x in b["banners"]]:
            diffs.append("五星变化")
        if e["four_star"] != b["four_star"]:
            diffs.append("四星变化")
        if diffs:
            changed += 1
            print(f"  ~ {e['version']} {e['phase']}: " + "；".join(diffs))
    if not changed:
        print("既有期次与上游一致，无差异")


def main():
    print("拉取 TeyvatGuide gacha.json …")
    rows = fetch("src/data/app/gacha.json")
    built = build_phases(rows)
    local = common.load()
    print(f"上游 {len(built)} 期，本地 {len(local)} 期（首次运行会下载角色名到 .cache/）")
    report_existing(local, built)
    local_keys = {(e["version"], e["phase"]) for e in local}
    new_keys = sorted(
        (k for k in built if k not in local_keys),
        key=lambda k: ([int(p) for p in k[0].split(".")], PHASE_ORDER[k[1]]),
    )
    if not new_keys:
        print("没有新期次，UP.json 未改动")
        return
    merged = local + [built[k] for k in new_keys]
    merged.sort(key=sort_key)
    common.DATA.write_text(dump(merged), encoding="utf-8")
    print(f"已追加 {len(new_keys)} 期：")
    for k in new_keys:
        e = built[k]
        mix = ""
        if e["mixed_banner"]:
            mb = e["mixed_banner"]
            mix = f" | 混池「{mb['name']}」地区={mb['region'] or '【待人工确认】'}"
        five = "、".join(b["five_star"] for b in e["banners"])
        print(f"  + {e['version']} {e['phase']} {e['start']}~{e['end']} 五星：{five}{mix}")
    print("请复核 git diff（尤其混池与手工补充内容）后提交")


if __name__ == "__main__":
    main()
