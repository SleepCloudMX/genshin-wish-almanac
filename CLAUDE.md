# UP（原神 UP 池记录）

记录原神历届角色活动祈愿与混池（1.0~7.0），并提供简单分析。

## 结构约定

- `data/UP.json`：唯一数据源。每条 = 一个版本阶段（上/中/下）：
  `version`、`phase`、`start`、`end`、`banners[{name, five_star}]`、`four_star[]`、`mixed_banner{name, region, five_star, four_star}|null`
- `index.html`：祈愿星历页面，由 `visualize.py` 生成（勿手改），随仓库提交、经 GitHub Pages 发布（仓库 Settings → Pages → main 根目录）
- `genshin-up/`：Python 脚本（仅标准库），用 conda **ai 环境**运行（`D:\Software\miniconda3\envs\ai\python.exe`，常见库齐全）
  - `export_md.py`：data/UP.json → `output/UP.md`
  - `visualize.py`：data/UP.json → `index.html`（单文件交互可视化页「祈愿星历」，页面模板在 `templates/`）
  - `update.py`：拉取 TeyvatGuide 最新 gacha.json，追加新期次（新混池地区需人工确认；角色名缓存于 `.cache/`）
  - `validate.py`：校验 UP.json 的结构、顺序、星级一致性、混池规则
  - `analysis/`：分析脚本，输出到 `output/<task>/`
- `output/`：脚本产物（已 gitignore），勿手改：`UP.md`、`viz/up-visual.html`、分析结果等
- `docs/ai-output/`：AI 产出文档，**独立 git 仓库**，本仓库已 gitignore

## 常用命令

- 重新生成 UP.md：`python genshin-up/export_md.py` → `output/UP.md`
- 生成可视化页：`python genshin-up/visualize.py` → 根目录 `index.html`（push 后 GitHub Pages 自动更新）
- 更新数据：`python genshin-up/update.py`（复核 git diff 后提交）
- 校验数据：`python genshin-up/validate.py`
- 跑分析：`python genshin-up/analysis/<script>.py`

## 数据口径

- 日期 = 卡池开始日；`phase` 为上/中/下（仅 1.3 有三期）
- 混池：集录祈愿记地区，溯光祈愿无地区记 `null`、**无 UP 四星记 `[]`**（四星池为全量普通池，不算 UP）
- 统计口径：**复刻含混池**（混池也算一次 UP）；同一期同时进普通池与混池时合并计一条；**复刻间隔 = 上个卡池结束日 → 下个卡池开始日（不含两端）**，常驻五星不计入间隔统计（8 人名单见 `genshin-up/common.py` 的 `STANDARD_5`）
- 数据来源：TeyvatGuide 的 gacha.json（GitHub）；混池名单以 bwiki 混池页为准

## 提交约定

- commit message 用英文，Conventional Commits 一行内
