# PROGRESS

无人值守执行记录。规则：每个阶段开始前先读本文件，从上次中断处继续；每阶段结束：更新本文件 → 运行 `python -I tools/check.py` → git commit。

当前日期：2026-11-16（阶段4"近12个月"= 2025-11-16 之后）。

## 状态总览

| 阶段 | 内容 | 状态 |
|---|---|---|
| 0 | 项目初始化（git、PROGRESS/DECISIONS/BLOCKERS） | ✅ 完成 |
| 1 | 引用库 references.json（≥80 条，verified 逐条核对） | ✅ 完成（95 条 verified=true） |
| 2 | tools/check.py（链接 / 7部分 / 引用 / SVG出界） | ✅ 完成 |
| 3 | 页面 01–11（只用 verified=true 引用） | ✅ 完成（11/11 通过 check + 截图自检） |
| 4 | 页面 12 前沿动态（近12个月、每条带日期链接） | ✅ 完成（14 条，全部经 arXiv 元数据核对日期） |
| 5 | 页面 00 总览、13 参考文献库、导航、全站自检、REPORT.md | ✅ 完成 |

## 阶段明细

### 阶段0 ✅
- [x] git init（main 分支）
- [x] .gitignore：data/fetch/（抓取缓存）、render/（截图）、__pycache__
- [x] PROGRESS.md / DECISIONS.md / BLOCKERS.md 建立
- [x] 首次 commit

### 阶段1 ✅（2026-11-16）
- 候选 100 条；剔除 5 条无法核对来源（arus2019smilesenum、decao2018mogan、ingraham2019proteingraph、macleod2020selfdriving、bjerrum2018smilesaug）
- 最终 **95 条 verified=true，失败 0**；arXiv abs 页 58 条 + Crossref 元数据 37 条
- 修复过程（三轮搜索+人工复核）全部留档：data/ref_fixes.json、data/ref_drops.json、data/id_renames.json、data/verify_failures.json（空）、data/fetch/ 原始缓存
- 关键修正：REINVENT 原文=J Cheminform "Molecular de-novo design through deep reinforcement learning"；MolGPT=JCIM（print 2022）；druGAN=Mol Pharm 2017；Boltz-1/2、Chai-1=bioRxiv（有 DOI）；SELFIES=arXiv 1905.13741；PoseBusters=arXiv 2308.05777；SCScore=JCIM 7b00622；ProteinMPNN=Science add2187；AiZynthFinder=J Cheminform 00472-1；Dirichlet FM=2402.05841；MoGAN/Ingraham 2019 无可核对来源，剔除
- id 内嵌年份已统一为与 year 字段一致（19 处改名）
- 追加核对 REINVENT 2.0（JCIM 0c00915）→ 最终 96 条 verified=true

### 阶段3 ✅（2026-11-17）
- 11 页全部写完：01-sequence / 02-latent / 03-graph / 04-transformer / 05-3d / 06-diffusion / 07-flow / 08-cofold / 09-synthesis / 10-agents / 11-eval
- 每页 7 个固定部分齐全；22 张内联 SVG（每页 2 张）；正文不给未核实的基准数字
- 每页写完即跑 check.py；浏览器截图自检浅色模式（深色变量同源，阶段5 全站复核）
- 截图自检修复 3 处：03 页图 3-1 两处文字重叠；05 页图 5-2 底注出画布（删除）；11 页图 11-1/11-2 底注重叠
- check.py 顺手修复：path 解析支持逗号分隔坐标；删除死代码
- commit: 每 1–3 页一次

### 阶段4 ✅（2026-11-17）
- 新增 14 条近 12 个月条目（2025-11-16 之后，arXiv 提交日期逐一核对）→ references.json 共 111 条 verified=true
- 页面 12-frontier：按共折叠/3D 生成与流/SBDD 与 LLM/评测/智能体五组收录，每条带日期、链接与章节关联
- check.py 强制校验该页引用条目 date ≥ 2025-11-16，通过
- 修复：阶段4 重跑 verify 覆盖了 id 改名 → 从 build_refs.py 源头改名并补入 selfdriving2024sdl（Chem Rev 2024），全站重检通过

### 阶段5 ✅（2026-11-17）
- tools/gen_refs.py 从 references.json 生成 13-references.html（111 条、按年份分组、锚点齐全、已核对徽章）
- index.html（00 总览）：2013–2026 时间线 SVG（13 节点、年份口径与文献库一致）+ 里程碑导航表 + 章节卡片 + 方法与口径说明
- 全站导航：每页顶部站点导航 + 上一页/下一页页脚（check.py 校验导航链完整性）
- 全站 check.py 通过：14 页 / 23 SVG / 198 引用链接 / 0 错误
- 全部页面截图自检（浅色 + 深色）：index 时间线、12 页条目列表、13 页文献卡片均正常
- REPORT.md 完成（页数、图数、引用数、58 条待核实汇总）
