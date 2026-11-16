# PROGRESS

无人值守执行记录。规则：每个阶段开始前先读本文件，从上次中断处继续；每阶段结束：更新本文件 → 运行 `python -I tools/check.py` → git commit。

当前日期：2026-11-16（阶段4"近12个月"= 2025-11-16 之后）。

## 状态总览

| 阶段 | 内容 | 状态 |
|---|---|---|
| 0 | 项目初始化（git、PROGRESS/DECISIONS/BLOCKERS） | 🔄 进行中 |
| 1 | 引用库 references.json（≥80 条，verified 逐条核对） | ⬜ 未开始 |
| 2 | tools/check.py（链接 / 7部分 / 引用 / SVG出界） | ⬜ 未开始 |
| 3 | 页面 01–11（只用 verified=true 引用） | ⬜ 未开始 |
| 4 | 页面 12 前沿动态（近12个月、每条带日期链接） | ⬜ 未开始 |
| 5 | 页面 00 总览、13 参考文献库、导航、全站自检、REPORT.md | ⬜ 未开始 |

## 阶段明细

### 阶段0 进行中
- [x] git init（main 分支）
- [x] .gitignore：data/fetch/（抓取缓存）、render/（截图）、__pycache__
- [x] PROGRESS.md / DECISIONS.md / BLOCKERS.md 建立
- [ ] 首次 commit
