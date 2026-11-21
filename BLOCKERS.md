# BLOCKERS

同一问题连续失败 3 次，记录于此并跳过。空表表示当前无阻塞。

| # | 日期 | 问题 | 失败经过 | 处置 |
|---|---|---|---|---|
| B-1 | 2026-11-21 | git push 失败：github.com:443 连接超时（curl 实测 github http=000、baidu http=200，本机网络正常，属 GitHub 间歇性不可达） | 连续 2 次 push 超时（21s），诊断确认非代码问题 | 提交 b2c1634 已安全保存在本地 main；待网络恢复后 `git push origin main` 即可同步 |
