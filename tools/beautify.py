# -*- coding: utf-8 -*-
"""全站美化：吸顶胶囊导航（当前页高亮 + 主题按钮入栏）+ 全站视觉细节。
只改 CSS 与导航 DOM，不动正文内容；全部使用现有 CSS 变量，深浅色自动适配。
用法: python -I tools/beautify.py
处理对象：13 个手写页面（13-references.html 由 gen_refs.py 重新生成，样式在本脚本同步）"""

import pathlib, subprocess, sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = pathlib.Path(__file__).resolve().parent.parent

PAGES = ['index.html', '01-sequence.html', '02-latent.html', '03-graph.html',
         '04-transformer.html', '05-3d.html', '06-diffusion.html', '07-flow.html',
         '08-cofold.html', '09-synthesis.html', '10-agents.html', '11-eval.html',
         '12-frontier.html']
LINKS = ['01-sequence.html', '02-latent.html', '03-graph.html', '04-transformer.html',
         '05-3d.html', '06-diffusion.html', '07-flow.html', '08-cofold.html',
         '09-synthesis.html', '10-agents.html', '11-eval.html', '12-frontier.html',
         '13-references.html']
LABELS = ['序列', '隐空间', '图生成', '语言模型', '3D', '扩散',
          '流匹配', '共折叠', '可合成性', '智能体', '评测', '前沿', '文献']

CSS_REPL = [
    ('.nav{max-width:860px;margin:0 auto;padding:16px 20px 0;display:flex;gap:14px;align-items:baseline;flex-wrap:wrap;font:13px/1.6 "Noto Sans SC","PingFang SC",system-ui,sans-serif}\n'
     '.nav .brand{font-weight:700;color:var(--ink);font-size:14px;text-decoration:none}\n'
     '.nav a{color:var(--mute);text-decoration:none}\n'
     '.nav a:hover{color:var(--lig)}',
     '.nav{position:sticky;top:0;z-index:50;background:var(--card);border-bottom:1px solid var(--line);display:flex;gap:6px;align-items:center;flex-wrap:wrap;padding:10px max(20px,calc((100% - 860px)/2));font:13px/1.6 "Noto Sans SC","PingFang SC",system-ui,sans-serif}\n'
     '@supports (backdrop-filter:blur(10px)){.nav{background:color-mix(in srgb,var(--card) 84%,transparent);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}}\n'
     '.nav .brand{display:inline-flex;align-items:center;gap:8px;font-weight:700;color:var(--ink);font-size:15px;text-decoration:none;padding:5px 12px 5px 9px;margin-right:6px;border:1px solid var(--line);border-radius:999px;background:var(--bg)}\n'
     '.nav .brand::before{content:"";width:10px;height:10px;border-radius:3px;background:var(--lig);box-shadow:0 0 0 3px var(--code)}\n'
     '.nav > a{color:var(--mute);text-decoration:none;padding:5px 13px;border-radius:999px;transition:color .15s,background .15s}\n'
     '.nav > a:hover{color:var(--lig);background:var(--code)}\n'
     '.nav > a.on{color:var(--lig);background:var(--code);font-weight:600;box-shadow:inset 0 0 0 1px var(--lig)}'),
    ('.tbtn{position:fixed;top:10px;right:12px;z-index:9;background:var(--card);border:1px solid var(--line);border-radius:50%;width:34px;height:34px;color:var(--ink);font-size:15px;cursor:pointer;line-height:1}',
     '.tbtn{margin-left:auto;flex:0 0 auto;width:34px;height:34px;background:var(--bg);border:1px solid var(--line);border-radius:999px;color:var(--ink);font-size:15px;cursor:pointer;line-height:1;transition:border-color .15s,transform .25s}\n'
     '.tbtn:hover{border-color:var(--lig);transform:rotate(25deg)}'),
    ('.pn{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:64px;padding-top:14px;border-top:1px solid var(--line);font:14px "Noto Sans SC","PingFang SC",system-ui,sans-serif}\n'
     '.pn a{color:var(--lig);text-decoration:none}\n'
     '.pn a:hover{text-decoration:underline}',
     '.pn{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:64px;padding-top:16px;border-top:1px solid var(--line);font:14px "Noto Sans SC","PingFang SC",system-ui,sans-serif}\n'
     '.pn a{color:var(--lig);text-decoration:none;padding:9px 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);transition:border-color .15s,background .15s,transform .15s}\n'
     '.pn a:hover{border-color:var(--lig);background:var(--code);transform:translateY(-1px)}'),
    ('html{scroll-padding-top:env(safe-area-inset-top,0px)}',
     'html{scroll-padding-top:calc(64px + env(safe-area-inset-top,0px))}'),
    ('main{max-width:860px;margin:0 auto;padding:40px 20px 80px}',
     'main{max-width:860px;margin:0 auto;padding:48px 20px 80px}'),
]

POLISH = '''/* 美化补充：交互与细节 */
html{scroll-behavior:smooth}
::selection{background:var(--lig);color:var(--card)}
:focus-visible{outline:2px solid var(--lig);outline-offset:2px;border-radius:4px}
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-thumb{background:var(--line);border-radius:6px}
::-webkit-scrollbar-thumb:hover{background:var(--mute)}
::-webkit-scrollbar-track{background:transparent}
main p a,main li a,main td a,figcaption a,.warn a{text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}
main p a:hover,main li a:hover,main td a:hover,figcaption a:hover,.warn a:hover{color:var(--prot)}
pre{border-left:3px solid var(--lig)}
tr:hover td{background:var(--code)}
figure{transition:box-shadow .2s,border-color .2s}
figure:hover{border-color:var(--mute);box-shadow:0 6px 20px rgba(2,20,30,.08)}
.card{transition:border-color .15s,transform .15s,box-shadow .15s}
.card:hover{border-color:var(--lig);transform:translateY(-2px);box-shadow:0 8px 18px rgba(2,20,30,.1)}
.entry{transition:border-color .15s,background .15s}
.entry:hover{border-left-color:var(--lig);background:var(--card);border-radius:0 12px 12px 0}
.ref{transition:border-color .15s,box-shadow .15s}
.ref:hover{border-color:var(--lig);box-shadow:0 6px 18px rgba(2,20,30,.08)}
'''

NEW_HEADER_TAIL = '<button class="tbtn" id="tbtn" title="切换深浅色" aria-label="切换深浅色">◐</button></header>'
STANDALONE_BTN = '\n<button class="tbtn" id="tbtn" title="切换深浅色" aria-label="切换深浅色">◐</button>'

def new_header(page):
    parts = ['<header class="nav"><a class="brand" href="index.html">分子生成模型演化史</a>']
    for link, label in zip(LINKS, LABELS):
        cls = ' class="on"' if link == page else ''
        parts.append(f'<a{cls} href="{link}">{label}</a>')
    parts.append(NEW_HEADER_TAIL)
    return ''.join(parts)

def process_page(page):
    fp = ROOT / page
    text = fp.read_text(encoding='utf-8')
    miss = []
    for old, new in CSS_REPL:
        if old in text:
            text = text.replace(old, new)
        else:
            miss.append(old.split('{')[0])
    if POLISH.rstrip() not in text:
        idx = text.rfind('</style>')
        text = text[:idx] + POLISH + text[idx:]
    start = text.find('<header class="nav">')
    end = text.find('</header>', start)
    if start != -1 and end != -1:
        text = text[:start] + new_header(page) + text[end + len('</header>'):]
    text = text.replace(STANDALONE_BTN + '\n<script>', '\n<script>')
    text = text.replace(STANDALONE_BTN + '<script>', '<script>')
    fp.write_text(text, encoding='utf-8')
    print(f'  {page:22s} ok' + (f' (CSS 串缺失: {miss})' if miss else ''))

def sync_gen_refs():
    """gen_refs.py 的 CSS/NAV 常量与页面保持一致，然后重新生成 13-references.html"""
    gp = ROOT / 'tools' / 'gen_refs.py'
    g = gp.read_text(encoding='utf-8')
    for old, new in CSS_REPL:
        if old in g:
            g = g.replace(old, new)
        else:
            print(f'  [warn] gen_refs 缺少 CSS 串: {old.split("{")[0]}')
    if POLISH.rstrip() not in g:
        anchor = 'color:var(--prot)}\n\'\'\''
        if anchor in g:
            g = g.replace(anchor, 'color:var(--prot)}\n' + POLISH + '\'\'\'')
        else:
            print('  [warn] gen_refs 未找到 CSS 结尾锚点，POLISH 未插入')
    old_nav_tail = '<a href="13-references.html">13 文献</a></header>'
    new_nav_tail = '<a class="on" href="13-references.html">13 文献</a>' + NEW_HEADER_TAIL
    if old_nav_tail in g:
        g = g.replace(old_nav_tail, new_nav_tail)
    g = g.replace(STANDALONE_BTN + '\n<script>', '\n<script>')
    gp.write_text(g, encoding='utf-8')
    print('  gen_refs.py synced')
    r = subprocess.run([sys.executable, '-I', str(ROOT / 'tools' / 'gen_refs.py')],
                       capture_output=True, text=True)
    print('  ', (r.stdout or r.stderr).strip()[:120])

def main():
    for page in PAGES:
        process_page(page)
    sync_gen_refs()

if __name__ == '__main__':
    main()
