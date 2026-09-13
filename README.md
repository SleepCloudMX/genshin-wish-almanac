# genshin-wish-almanac · 祈愿星历

Genshin Impact wish/banner history & analysis. 原神历届卡池（角色活动祈愿 + 混池）数据与工具：1.0 ~ 7.0 共 105 期，含复刻统计、间隔分布与交互式时间线。

**在线查看：[https://sleepcloudmx.github.io/genshin-wish-almanac/](https://sleepcloudmx.github.io/genshin-wish-almanac/)**

## 内容

- `index.html` — 「祈愿星历」交互页面（由 `genshin-up/visualize.py` 生成）
  - **时间线**：每个角色一行的 UP 点阵（金=五星、银=四星、紫环=混池）；悬停角色名看历次 UP 明细，点击复制
  - **版本节奏**：每版本的 UP 构成（新角色/复刻 × 五星/四星），✦ 标记有混池的版本
  - **复刻间隔**：平均 / 最短 / 最长 / 未复刻 / 首复 五种排行（可切换排序；御三家缺省隐藏，可一键显示）
  - **分布**：五星/四星 × 逐次/平均 的间隔直方图（21 天/箱），点击柱形查看明细；可切换「年代趋势」箱线图（按复刻/按首发年份，悬浮任意样本点看明细）
- `data/UP.json` — 唯一数据源：版本、阶段、起止日期、五星、四星、混池（名称/地区/五星/四星）
- `genshin-up/` — Python 脚本（仅标准库）
  - `visualize.py` 生成页面 · `export_md.py` 导出 Markdown 表 · `update.py` 增量更新数据 · `validate.py` 数据校验
  - `analysis/` 分析脚本（首发时间表、各版本新角色、复刻统计、间隔分布图）

## 统计口径

- 复刻含混池（同一期同时进普通池与混池按一次计）
- 常驻五星 8 名（迪卢克、琴、莫娜、七七、刻晴、提纳里、迪希雅、梦见月瑞希）不计入复刻间隔统计
- 复刻间隔 = 上个卡池结束日 → 下个卡池开始日之间、不含两端的天数
- 首复 = 首个复刻间隔；御三家（安柏、凯亚、丽莎）开服即得、无首发，榜单中缺省隐藏（可切换显示）
- 部分期次为人工补充（如跨地区、无 UP 四星的溯光祈愿「辉天的星告」）

## 使用

需要 Python 3，无第三方依赖：

```bash
python genshin-up/visualize.py    # data/UP.json → index.html
python genshin-up/update.py       # 从上游拉取最新卡池数据，增量并入 UP.json
python genshin-up/validate.py     # 校验 UP.json 结构与规则
python genshin-up/export_md.py    # 导出 Markdown 表格到 output/UP.md
```

## 数据来源与致谢

- 卡池排期与角色名：[BTMuli/TeyvatGuide](https://github.com/BTMuli/TeyvatGuide)
- 混池（集录祈愿）名单：bwiki 原神 WIKI
- 游戏内容与角色名称版权归米哈游（miHoYo）所有；本项目为个人非商业项目
