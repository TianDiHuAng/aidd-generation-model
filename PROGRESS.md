# PROGRESS

无人值守执行记录。规则：每个阶段开始前先读本文件，从上次中断处继续；每阶段结束：更新本文件 → 运行 `python -I tools/check.py` → git commit。

当前日期：2026-11-16（阶段4"近12个月"= 2025-11-16 之后）。

## 状态总览

| 阶段 | 内容 | 状态 |
|---|---|---|
| 0 | 项目初始化（git、PROGRESS/DECISIONS/BLOCKERS） | ✅ 完成 |
| 1 | 引用库 references.json（≥80 条，verified 逐条核对） | ✅ 完成（95 条 verified=true） |
| 2 | tools/check.py（链接 / 7部分 / 引用 / SVG出界） | ✅ 完成 |
| 3 | 页面 01–11（只用 verified=true 引用） | 🔄 进行中 |
| 4 | 页面 12 前沿动态（近12个月、每条带日期链接） | ⬜ 未开始 |
| 5 | 页面 00 总览、13 参考文献库、导航、全站自检、REPORT.md | ⬜ 未开始 |

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
