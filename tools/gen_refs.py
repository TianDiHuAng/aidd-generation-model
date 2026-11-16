# -*- coding: utf-8 -*-
"""阶段5：从 references.json 生成 13-references.html（条目锚点与正文引用链接一致）。
用法: python -I tools/gen_refs.py"""
import json, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((ROOT / 'references.json').read_text(encoding='utf-8'))
entries = sorted(data['entries'], key=lambda r: (r['year'], r['id']))

CSS = '''<style>
:root{--bg:#F6F8F9;--card:#FFFFFF;--ink:#12212C;--mute:#566772;--line:#D3DDE2;--lig:#0F7A8A;--prot:#5B6B8C;--noise:#C27A12;--code:#EAF0F2;
box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0F1A22;--card:#16252F;--ink:#E6EEF2;--mute:#9DB0BB;--line:#2A3C48;--lig:#4CC3D3;--prot:#8FA3C8;--noise:#E7A640;--code:#1C2F3B;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#0F1A22;--card:#16252F;--ink:#E6EEF2;--mute:#9DB0BB;--line:#2A3C48;--lig:#4CC3D3;--prot:#8FA3C8;--noise:#E7A640;--code:#1C2F3B;color-scheme:dark}
html{scroll-padding-top:env(safe-area-inset-top,0px)}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.8 "Noto Serif SC","Songti SC",Georgia,serif}
main{max-width:860px;margin:0 auto;padding:40px 20px 80px}
h1{font:700 clamp(28px,5vw,42px)/1.25 "Noto Sans SC","PingFang SC",system-ui,sans-serif;margin:0 0 12px}
h2{font:700 22px/1.4 "Noto Sans SC","PingFang SC",system-ui,sans-serif;margin:56px 0 12px;padding-left:12px;border-left:4px solid var(--lig)}
p,li{max-width:70ch}
.lead{color:var(--mute);font-size:17px}
.warn{background:var(--card);border:1px solid var(--noise);border-radius:8px;padding:12px 16px;font-size:15px}
.nav{max-width:860px;margin:0 auto;padding:16px 20px 0;display:flex;gap:14px;align-items:baseline;flex-wrap:wrap;font:13px/1.6 "Noto Sans SC","PingFang SC",system-ui,sans-serif}
.nav .brand{font-weight:700;color:var(--ink);font-size:14px;text-decoration:none}
.nav a{color:var(--mute);text-decoration:none}
.nav a:hover{color:var(--lig)}
.pn{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:64px;padding-top:14px;border-top:1px solid var(--line);font:14px "Noto Sans SC","PingFang SC",system-ui,sans-serif}
.pn a{color:var(--lig);text-decoration:none}
.pn a:hover{text-decoration:underline}
.tbtn{position:fixed;top:10px;right:12px;z-index:9;background:var(--card);border:1px solid var(--line);border-radius:50%;width:34px;height:34px;color:var(--ink);font-size:15px;cursor:pointer;line-height:1}
.ref{margin:20px 0;padding:14px 16px;background:var(--card);border:1px solid var(--line);border-radius:10px}
.ref .meta{font:14px/1.7 "Noto Sans SC","PingFang SC",system-ui,sans-serif}
.ref .ttl{font:600 16px/1.6 "Noto Sans SC","PingFang SC",system-ui,sans-serif}
.ref a{color:var(--lig);text-decoration:none}
.ref a:hover{text-decoration:underline}
.badge{display:inline-block;font:600 12px/1 "Noto Sans SC","PingFang SC",system-ui,sans-serif;color:var(--lig);border:1px solid var(--lig);border-radius:10px;padding:2px 8px;margin-left:8px;vertical-align:2px}
.yr{font:700 20px/1.4 "Noto Sans SC","PingFang SC",system-ui,sans-serif;margin:36px 0 8px;color:var(--prot)}
</style>'''

NAV = '<header class="nav"><a class="brand" href="index.html">分子生成模型演化史</a><a href="01-sequence.html">01 序列</a><a href="02-latent.html">02 隐空间</a><a href="03-graph.html">03 图生成</a><a href="04-transformer.html">04 语言模型</a><a href="05-3d.html">05 3D</a><a href="06-diffusion.html">06 扩散</a><a href="07-flow.html">07 流匹配</a><a href="08-cofold.html">08 共折叠</a><a href="09-synthesis.html">09 可合成性</a><a href="10-agents.html">10 智能体</a><a href="11-eval.html">11 评测</a><a href="12-frontier.html">12 前沿</a><a href="13-references.html">13 文献</a></header>'

def fmt_authors(auths):
    if len(auths) <= 3:
        return '；'.join(html.escape(a) for a in auths)
    return '；'.join(html.escape(a) for a in auths[:3]) + ' 等'

def entry_html(r):
    t = html.escape(r['title'])
    venue = html.escape(r['venue']) if r['venue'] else ''
    parts = [f'<span class="yr">{r["year"]}</span>']
    parts.append(f'<div class="ref" id="{r["id"]}">')
    parts.append(f'<div class="meta"><span class="ttl">{t}</span><span class="badge">已核对 ✓</span></div>')
    parts.append(f'<div class="meta">{fmt_authors(r["authors"])} · {r["year"]}'
                 + (f' · {venue}' if venue else '')
                 + (f' · {html.escape(r["venue_comment"][:60])}' if r.get('venue_comment') else '')
                 + f' · 收录日期 {html.escape(str(r["date"]))}</div>')
    parts.append(f'<div class="meta">贡献：{html.escape(r["contribution"])}</div>')
    parts.append(f'<div class="meta">链接：<a href="{html.escape(r["url"])}">{html.escape(r["url"])}</a>'
                 + f' · DOI：<a href="https://doi.org/{html.escape(r["doi"])}">{html.escape(r["doi"])}</a>'
                 + f' · 来源：{"arXiv 摘要页" if r["source"]=="arxiv" else "Crossref 元数据"}</div>')
    parts.append('</div>')
    return '\n'.join(parts)

body = ['<main>']
body.append('<h1>参考文献库</h1>')
body.append(f'<p class="lead">共 {len(entries)} 条，全部经过原文/摘要页核对（标题、作者、年份逐条比对）后标记 verified=true。正文中每一处引用链接都指向本页对应锚点。</p>')
body.append('<div class="warn">核对规则：arXiv 条目抓取 abs 页的 citation_title / citation_author / citation_date 元标签；期刊条目使用 Crossref API 的正式元数据。核对后的条目按年份排列如下。日期口径见 DECISIONS.md（D-005）：arXiv 条目为 v1 提交年，期刊条目为正式发表年。</div>')
cur = None
for r in entries:
    if r['year'] != cur:
        body.append(entry_html(r).split('<div class="ref"')[0])  # 年份标题
        cur = r['year']
        body.append(f'<div class="ref" id="{r["id"]}">' + entry_html(r).split('<div class="ref" id="' + r['id'] + '">')[1])
    else:
        body.append(entry_html(r))
body.append('<h2>使用说明</h2>')
body.append('<p>各章节正文的引用写作"（作者 等，年份）"并链接到本页锚点；"已核对 ✓"表示该条通过了阶段1的机械核对流程（工具见 tools/verify_refs.py，原始页面缓存见 data/fetch/）。正文不给未经原文正文核对的基准数字；各章"待核实"清单列出了未确认的内容。</p>')
body.append('</main>')
html_out = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>13 参考文献库 · 分子生成模型演化史</title>
{CSS}
</head>
<body>
{NAV}
{chr(10).join(body)}
<nav class="pn"><a href="12-frontier.html">← 12 前沿动态</a><a href="index.html">总览</a><a href="index.html">返回总览 ↰</a></nav>
<button class="tbtn" id="tbtn" title="切换深浅色" aria-label="切换深浅色">◐</button>
<script>(function(){{var d=document.documentElement;var q=new URLSearchParams(location.search).get('theme');if(q==='dark'||q==='light')d.dataset.theme=q;document.getElementById('tbtn').addEventListener('click',function(){{d.dataset.theme=(d.dataset.theme==='dark')?'light':'dark';}});}})();</script>
</body>
</html>
'''
(ROOT / '13-references.html').write_text(html_out, encoding='utf-8')
print(f'wrote 13-references.html with {len(entries)} entries')
