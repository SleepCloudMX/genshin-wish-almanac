import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common

PHASE_ORDER = {"上": 0, "中": 1, "下": 2}
REGIONS = {"蒙德", "璃月", "稻妻", "须弥", "枫丹"}
DATE_RE = re.compile(r"^\d{4}/\d{2}/\d{2}$")
VERSION_RE = re.compile(r"^\d+\.\d+$")


def main():
    data = common.load()
    problems = []

    def check(cond, msg):
        if not cond:
            problems.append(msg)

    star = {}
    for i, e in enumerate(data):
        tag = f"[{i + 1}] {e.get('version', '?')} {e.get('phase', '?')}"
        for key in ("version", "phase", "start", "end"):
            check(isinstance(e.get(key), str) and e[key], f"{tag} 缺字段或类型错误：{key}")
        check(VERSION_RE.match(e.get("version", "")), f"{tag} 版本格式错误")
        check(e.get("phase") in PHASE_ORDER, f"{tag} phase 非法：{e.get('phase')}")
        for key in ("start", "end"):
            check(DATE_RE.match(e.get(key, "")), f"{tag} {key} 日期格式错误：{e.get(key)}")
        if DATE_RE.match(e.get("start", "")) and DATE_RE.match(e.get("end", "")):
            check(e["start"] <= e["end"], f"{tag} start 晚于 end")

        banners = e.get("banners")
        check(isinstance(banners, list) and banners, f"{tag} banners 为空或类型错误")
        for b in banners or []:
            check(isinstance(b.get("name"), str) and b["name"], f"{tag} 卡池名非法")
            check(isinstance(b.get("five_star"), str) and b["five_star"], f"{tag} five_star 非法")
        five = [b.get("five_star") for b in banners or []]
        check(len(set(five)) == len(five), f"{tag} 五星重复")

        four = e.get("four_star")
        check(isinstance(four, list) and all(isinstance(x, str) and x for x in four or []),
              f"{tag} four_star 非法")
        four = four or []
        check(not (set(five) & set(four)), f"{tag} 同一期出现五星/四星重复")

        for n in five:
            if n in star:
                check(star[n] == "5", f"{tag} 星级冲突：{n} 此前为 {star[n]}★")
            star[n] = "5"
        for n in four:
            if n in star:
                check(star[n] == "4", f"{tag} 星级冲突：{n} 此前为 {star[n]}★")
            star[n] = "4"

        mb = e.get("mixed_banner")
        if mb is not None:
            check(isinstance(mb, dict), f"{tag} mixed_banner 类型错误")
            check(isinstance(mb.get("name"), str) and mb["name"], f"{tag} 混池名非法")
            region = mb.get("region")
            check(region is None or region in REGIONS, f"{tag} 混池地区非法：{region}")
            m5 = mb.get("five_star")
            m4 = mb.get("four_star")
            check(isinstance(m5, list) and m5, f"{tag} 混池五星为空或类型错误")
            check(isinstance(m4, list) and all(isinstance(x, str) for x in m4 or []),
                  f"{tag} 混池四星类型错误")
            m4 = m4 or []
            check(not (set(m5 or []) & set(m4)), f"{tag} 混池五星/四星重复")
            if region is None:
                check(not m4, f"{tag} 无地区混池却有四星（溯光祈愿应为空）")
            else:
                check(m4, f"{tag} 地区混池四星为空，疑似漏填")

    keys = []
    for e in data:
        keys.append((tuple(int(p) for p in e["version"].split(".")), PHASE_ORDER[e["phase"]]))
    check(keys == sorted(keys), "条目顺序异常（应按版本与 上/中/下 排列）")
    check(len(set(keys)) == len(keys), "存在重复的版本+阶段")

    by_version = {}
    for e in data:
        by_version.setdefault(e["version"], []).append(e["phase"])
    for v, phases in by_version.items():
        check(phases[0] == "上" and phases[-1] == "下", f"{v} 期次结构异常：{phases}")

    def d(s):
        return datetime.strptime(s, "%Y/%m/%d").date()

    for a, b in zip(data, data[1:]):
        if DATE_RE.match(a.get("end", "")) and DATE_RE.match(b.get("start", "")):
            check(d(b["start"]) >= d(a["end"]),
                  f"{a['version']} {a['phase']} 与下一期时间倒挂（下期开始早于上期结束）")

    if problems:
        print(f"发现 {len(problems)} 个问题：")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print(f"校验通过：{len(data)} 期，{len(star)} 名角色")


if __name__ == "__main__":
    main()
