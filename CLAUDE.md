# UP（原神 UP 池记录）

记录原神历届角色活动祈愿与混池（1.0~7.0），并提供简单分析。

## 结构约定

- `data/UP.json`：唯一数据源。每条 = 一个版本阶段（上/中/下）：
  `version`、`phase`、`start`、`end`、`banners[{name, five_star}]`、`four_star[]`、`mixed_banner{name, region, five_star, four_star}|null`
- `UP.md`：由脚本生成，**勿手改**。改完数据跑 `python genshin-up/export_md.py`
- `genshin-up/`：Python 脚本（仅标准库）
  - `export_md.py`：data/UP.json → UP.md
  - `analysis/`：分析脚本，输出到 `output/<task>/`
- `output/`：脚本产物（已 gitignore）
- `docs/ai-output/`：AI 产出文档，**独立 git 仓库**，本仓库已 gitignore

## 常用命令

- 重新生成 UP.md：`python genshin-up/export_md.py`
- 跑分析：`python genshin-up/analysis/<script>.py`

## 数据口径

- 日期 = 卡池开始日；`phase` 为上/中/下（仅 1.3 有三期）
- 混池：集录祈愿记地区，溯光祈愿无地区记 `null`、**无 UP 四星记 `[]`**（四星池为全量普通池，不算 UP）
- 数据来源：TeyvatGuide 的 gacha.json（GitHub）；混池名单以 bwiki 混池页为准

## 提交约定

- commit message 用英文，Conventional Commits 一行内
