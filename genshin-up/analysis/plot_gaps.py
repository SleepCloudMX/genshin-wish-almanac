import sys
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

BG = "#0d1424"
PANEL = "#121a2c"
PANEL_EDGE = "#26304a"
TEXT = "#e9e5d9"
MUTED = "#8d93a5"
GOLD = "#d3bc8e"
GOLD_B = "#f2ddab"
SILVER = "#9fb2c8"
VIOLET = "#b48ce0"
BIN = 21
EDGES = np.arange(0, BIN * 34 + 1, BIN)

RNG = np.random.default_rng(20260913)


def style_ax(ax):
    ax.set_facecolor(PANEL)
    for s in ax.spines.values():
        s.set_color(PANEL_EDGE)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.grid(axis="y", color=PANEL_EDGE, lw=0.6, alpha=0.7)
    ax.set_axisbelow(True)


def gap_records(app, star):
    out = []
    for name, recs in app.items():
        if recs[0]["star"] != star or name in common.STANDARD_5:
            continue
        normal = [r for r in recs if r["normal"]]
        debut_year = common.parse_date((normal[0] if normal else recs[0])["date"]).year
        ends = [common.parse_date(r["end"]) for r in recs]
        starts = [common.parse_date(r["date"]) for r in recs]
        for i in range(1, len(recs)):
            out.append(
                {"name": name, "gap": max(0, (starts[i] - ends[i - 1]).days - 1), "year": debut_year}
            )
    return out


def fmt_gap(v):
    return f"{v:.0f}" if float(v).is_integer() else f"{v:.1f}"


def extremes(pts, reverse, k=3):
    groups = {}
    for p in pts:
        groups.setdefault(p["gap"], []).append(p["name"])
    lines = []
    for v in sorted(groups, reverse=reverse)[:k]:
        names = sorted(set(groups[v]))
        label = "、".join(names[:2]) + (f" 等 {len(names)} 人" if len(names) > 2 else "")
        lines.append(f"{fmt_gap(v)}（{label}）")
    return lines


def draw_hist(ax, pts, color, title):
    vals = [p["gap"] for p in pts]
    ax.hist(vals, bins=EDGES, color=color, edgecolor=BG, linewidth=1.1, alpha=0.95)
    ymax = ax.get_ylim()[1]
    ax.set_ylim(0, ymax * 1.42)

    med = float(np.median(vals))
    mean = float(np.mean(vals))
    ax.axvline(med, color=GOLD_B, lw=1.3, ls="-", alpha=0.9)
    ax.axvline(mean, color=VIOLET, lw=1.2, ls=(0, (4, 3)), alpha=0.9)

    hi = extremes(pts, True)
    lo = extremes(pts, False)
    box = (
        f"N={len(vals)} ｜ 中位 {med:.0f} · 均值 {mean:.0f} 天\n"
        f"最长 {hi[0]} · {hi[1]}\n　　 {hi[2]}\n"
        f"最短 {lo[0]} · {lo[1]}\n　　 {lo[2]}"
    )
    ax.text(
        0.98, 0.97, box, transform=ax.transAxes, ha="right", va="top",
        fontsize=8.2, color=TEXT, linespacing=1.5,
        bbox=dict(facecolor=BG, edgecolor=PANEL_EDGE, boxstyle="round,pad=0.5", alpha=0.92),
    )
    ax.set_title(title, color=TEXT, fontsize=12, pad=10)
    ax.set_xlabel("天（每箱 = 21 天 = 半个版本周期）", color=MUTED, fontsize=9)


def fig_distribution(app, out_dir):
    fig, axes = plt.subplots(2, 2, figsize=(13.5, 8.6))
    fig.patch.set_facecolor(BG)
    plan = [
        (axes[0][0], "5", GOLD, "五星 · 逐次复刻间隔"),
        (axes[0][1], "4", SILVER, "四星 · 逐次复刻间隔"),
        (axes[1][0], "5", GOLD, "五星 · 角色平均间隔"),
        (axes[1][1], "4", SILVER, "四星 · 角色平均间隔"),
    ]
    for ax, star, color, title in plan:
        style_ax(ax)
        recs = gap_records(app, star)
        if "逐次" in title:
            pts = recs
        else:
            by_char = {}
            for p in recs:
                by_char.setdefault(p["name"], []).append(p["gap"])
            pts = [
                {"name": n, "gap": sum(v) / len(v), "year": 0} for n, v in by_char.items()
            ]
        draw_hist(ax, pts, color, title)
    handles = [
        Line2D([], [], color=GOLD_B, lw=1.3, label="中位"),
        Line2D([], [], color=VIOLET, lw=1.2, ls=(0, (4, 3)), label="均值"),
        Line2D([], [], color=GOLD, lw=6, alpha=0.9, label="五星"),
        Line2D([], [], color=SILVER, lw=6, alpha=0.9, label="四星"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False,
               labelcolor=MUTED, fontsize=10, bbox_to_anchor=(0.5, 0.012))
    fig.suptitle("复刻间隔分布", color=TEXT, fontsize=16, y=0.975)
    fig.text(0.5, 0.925, "间隔 = 上个卡池结束 → 下个卡池开始（含混池；常驻五星不计）",
             color=MUTED, fontsize=9.5, ha="center")
    fig.tight_layout(rect=(0, 0.045, 1, 0.915))
    path = out_dir / "gap-distribution.png"
    fig.savefig(path, dpi=144, facecolor=BG)
    plt.close(fig)
    print(f"written: {path.relative_to(common.ROOT)}")


def bucket_of(year):
    if year <= 2021:
        return "2020–2021 首发"
    if year <= 2023:
        return "2022–2023 首发"
    return "2024–2026 首发"


def fig_trend(app, out_dir):
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.2))
    fig.patch.set_facecolor(BG)
    order = ["2020–2021 首发", "2022–2023 首发", "2024–2026 首发"]
    for ax, star, color, title in (
        (axes[0], "5", GOLD, "五星"),
        (axes[1], "4", SILVER, "四星"),
    ):
        style_ax(ax)
        recs = gap_records(app, star)
        groups = {b: [] for b in order}
        for p in recs:
            groups[bucket_of(p["year"])].append(p["gap"])
        data = [groups[b] for b in order]
        bp = ax.boxplot(
            data, positions=[1, 2, 3], widths=0.42, patch_artist=True, showfliers=False,
            boxprops=dict(facecolor=PANEL, edgecolor=color, linewidth=1.3),
            medianprops=dict(color=GOLD_B, linewidth=1.6),
            whiskerprops=dict(color=MUTED), capprops=dict(color=MUTED),
        )
        top = max(v for d in data for v in d)
        ax.set_ylim(-top * 0.04, top * 1.26)
        for i, vals in enumerate(data):
            x = np.full(len(vals), 1 + i) + RNG.uniform(-0.16, 0.16, len(vals))
            ax.scatter(x, vals, s=7, color=color, alpha=0.55, zorder=3)
            ax.text(
                1 + i, ax.get_ylim()[1] * 0.98,
                f"n={len(vals)}\n中位 {np.median(vals):.0f}",
                ha="center", va="top", fontsize=8.5, color=TEXT, linespacing=1.4,
                bbox=dict(facecolor=BG, edgecolor=PANEL_EDGE, boxstyle="round,pad=0.35", alpha=0.9),
            )
        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(order, fontsize=9.5)
        ax.set_title(f"{title} · 按首发年代", color=TEXT, fontsize=12, pad=10)
        ax.set_ylabel("复刻间隔（天）", color=MUTED, fontsize=9.5)
    fig.suptitle("复刻间隔的年代趋势", color=TEXT, fontsize=16, y=0.98)
    fig.text(0.5, 0.915,
             "箱线 + 个体散点；新角色观察窗口短，后期样本的间隔天然偏短（截断偏差），看整体走势即可",
             color=MUTED, fontsize=9.5, ha="center")
    fig.tight_layout(rect=(0, 0.02, 1, 0.89))
    path = out_dir / "gap-trend.png"
    fig.savefig(path, dpi=144, facecolor=BG)
    plt.close(fig)
    print(f"written: {path.relative_to(common.ROOT)}")


def main():
    app = common.appearances(common.load())
    out_dir = common.ROOT / "output" / "gap-dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_distribution(app, out_dir)
    fig_trend(app, out_dir)


if __name__ == "__main__":
    main()
