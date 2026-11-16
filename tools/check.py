# -*- coding: utf-8 -*-
"""全站自检脚本（阶段2 起，每个阶段都必须通过）。
用法: python -I tools/check.py [--file <单个页面>]

检查项：
  A. 页面清单完整（14 个页面文件）
  B. 内部链接：相对链接的文件存在；13-references.html#id 的 id 存在于 references.json 且 verified=true
  C. 模型家族页 01-11 必含 7 个固定部分（h2）：核心思想/架构图/数学形式/代表工作/优点局限与常见陷阱/与上一页下一页的衔接/待核实
  D. 引用核实：所有引用链接指向 verified=true 的条目；正文（<a> 标签之外）不得出现"（……等，20XX）"式未加链接的引文
  E. SVG：所有静态几何元素不超出 viewBox（含 path 绝对/相对命令、text 宽度估算、g 平移变换）
  F. 页面 12 的引用条目 date 必须在近 12 个月内（≥ 2025-11-16）
  G. references.json 字段完整性
  H. 每页含站点统一 CSS 变量（浅色 :root 与深色覆盖）与 lang/viewport/title
退出码 0=全部通过，1=有错误。"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
CUTOFF_12M = '2025-11-16'   # 阶段4口径：近 12 个月

PAGES = ['index.html', '01-sequence.html', '02-latent.html', '03-graph.html',
         '04-transformer.html', '05-3d.html', '06-diffusion.html', '07-flow.html',
         '08-cofold.html', '09-synthesis.html', '10-agents.html', '11-eval.html',
         '12-frontier.html', '13-references.html']
FAMILY_PAGES = PAGES[1:12]          # 01-11 需要固定 7 部分
ORDER = PAGES                        # 导航顺序 index(00) -> 13

SECTIONS = [
    ('核心思想', lambda h: '核心思想' in h),
    ('架构图', lambda h: '架构图' in h or '架构' in h),
    ('数学形式', lambda h: '数学' in h),
    ('代表工作表', lambda h: '代表工作' in h),
    ('优点、局限与常见陷阱', lambda h: '优点' in h and '局限' in h and '陷阱' in h),
    ('与上一页、下一页的衔接', lambda h: '衔接' in h),
    ('待核实', lambda h: '待核实' in h),
]
CSS_VARS_LIGHT = ['--bg:', '--card:', '--ink:', '--mute:', '--line:', '--lig:', '--prot:', '--noise:', '--code:']

errors, warnings = [], []

def err(msg):
    errors.append(msg)

def warn(msg):
    warnings.append(msg)

def load_refs():
    data = json.loads((ROOT / 'references.json').read_text(encoding='utf-8'))
    refs = {}
    for r in data.get('entries', []):
        for k in ('id', 'title', 'authors', 'year', 'date', 'venue', 'url', 'doi', 'contribution', 'verified'):
            if k not in r:
                err(f'[G] references.json 条目缺字段 {k}: {r.get("id", "?")}')
        if not r.get('authors'):
            err(f'[G] {r.get("id")}: authors 为空')
        if not r.get('verified'):
            err(f'[G] {r.get("id")}: verified 不为 true（不允许保留未核实条目）')
        d = str(r.get('date', ''))
        if not re.match(r'^(19|20)\d{2}(-\d{2}(-\d{2})?)?$', d):
            err(f'[G] {r.get("id")}: date 格式异常 {d!r}')
        refs[r['id']] = r
    return refs

def strip_comments(html):
    return re.sub(r'<!--.*?-->', '', html, flags=re.S)

def get_h2s(html):
    out = []
    for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', html, re.S):
        out.append(re.sub(r'<[^>]+>', '', m.group(1)).strip())
    return out

def svg_elements(svg):
    """yield (tag, attrs_dict) 跳过 defs 内部元素"""
    depth_defs = 0
    for m in re.finditer(r'<(/?)([a-zA-Z]+)([^>]*?)(/?)>', svg, re.S):
        close, tag, attrs, selfclose = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        if close:
            if tag == 'defs' and depth_defs > 0:
                depth_defs -= 1
            continue
        a = dict(re.findall(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"', attrs))
        if tag == 'defs':
            depth_defs += 1
            continue
        if depth_defs > 0:
            continue
        yield tag, a, selfclose == '/'

def parse_translate(s):
    tx, ty = 0.0, 0.0
    for name, args in re.findall(r'(translate|scale|matrix)\(([^)]*)\)', s or ''):
        v = [float(x) for x in re.split(r'[ ,]+', args.strip()) if x]
        if name == 'translate':
            tx += v[0]; ty += v[1] if len(v) > 1 else 0
        elif name == 'scale':
            tx *= v[0]; ty *= v[1] if len(v) > 1 else v[0]
        else:
            err(f'[E] SVG 使用了未支持的 transform: matrix（请改用 translate）')
    return tx, ty

def _path_points(d):
    pts = []
    i = 0
    x = y = sx = sy = 0.0
    cmd = None
    while i < len(d):
        m = re.match(r'\s*([A-Za-z])', d[i:])
        if m:
            cmd = m.group(1)
            i += 1
            continue
        m = re.match(r'\s*(-?\d*\.?\d+(?:e[-+]?\d+)?)', d[i:])
        if not m:
            i += 1
            continue
        def read():
            nonlocal i
            mm = re.match(r'\s*,?\s*(-?\d*\.?\d+(?:e[-+]?\d+)?)', d[i:])
            if not mm:
                raise ValueError(f'path 解析失败于位置 {i}: {d[max(0, i - 10):i + 10]!r}')
            i += mm.end()
            return float(mm.group(1))
        rel = cmd.islower()
        C = cmd.upper()
        if C == 'M':
            nx, ny = read(), read()
            if rel: x += nx; y += ny
            else: x, y = nx, ny
            sx, sy = x, y
            pts.append((x, y))
            cmd = 'm' if cmd == 'M' else 'M'
            cmd = 'L' if C == 'M' and not rel else 'l'
        elif C == 'L':
            nx, ny = read(), read()
            if rel: x += nx; y += ny
            else: x, y = nx, ny
            pts.append((x, y))
        elif C == 'H':
            nx = read()
            x = x + nx if rel else nx
            pts.append((x, y))
        elif C == 'V':
            ny = read()
            y = y + ny if rel else ny
            pts.append((x, y))
        elif C in 'CSQT':
            n_read = {'C': 6, 'S': 4, 'Q': 4, 'T': 2}[C]
            vals = [read() for _ in range(n_read)]
            if rel:
                vals = [vals[j] + (x if j % 2 == 0 else y) for j in range(n_read)]
            pts += [(vals[j], vals[j + 1]) for j in range(0, n_read, 2)]
            x, y = vals[-2], vals[-1]
        elif C == 'A':
            vals = [read() for _ in range(7)]
            pts.append((vals[5], vals[6]))
            x, y = vals[5], vals[6]
        elif C == 'Z':
            x, y = sx, sy
            pts.append((x, y))
            cmd = 'L'
            # Z 后续若跟数字，按 L 处理
        else:
            i += 1
    return pts

def text_width_est(t):
    w = 0.0
    for ch in t:
        w += 13.0 if ord(ch) > 0x2E80 else 7.2
    return w

def check_svg(name, idx, svg):
    vb = re.search(r'viewBox\s*=\s*"([-\d.\s]+)"', svg)
    if not vb:
        err(f'{name}: 第{idx}个 svg 缺少 viewBox'); return
    vw = [float(v) for v in vb.group(1).split()]
    minx, miny, w, h = vw
    tol = 2.5
    lo_x, hi_x = minx - tol, minx + w + tol
    lo_y, hi_y = miny - tol, miny + h + tol
    n_elem = 0
    tx, ty = 0.0, 0.0
    for tag, a, selfclose in svg_elements(svg):
        if tag == 'g':
            if selfclose: tx, ty = 0.0, 0.0
            else: tx, ty = parse_translate(a.get('transform', ''))
        n_elem += 1
        def span(cx, cy):
            return cx + tx, cy + ty
        if tag == 'rect':
            x, y = span(float(a.get('x', 0)), float(a.get('y', 0)))
            rw, rh = float(a.get('width', 0)), float(a.get('height', 0))
            if x < lo_x - 0 or y < lo_y or x + rw > hi_x or y + rh > hi_y:
                err(f'{name}: 第{idx}个 svg rect 超界 ({x},{y},{rw}x{rh}) viewBox={w}x{h}')
        elif tag == 'circle':
            cx, cy = span(float(a.get('cx', 0)), float(a.get('cy', 0)))
            r = float(a.get('r', 0))
            if cx - r < lo_x or cx + r > hi_x or cy - r < lo_y or cy + r > hi_y:
                err(f'{name}: 第{idx}个 svg circle 超界 ({cx},{cy},r={r}) viewBox={w}x{h}')
        elif tag == 'line':
            x1, y1 = span(float(a.get('x1', 0)), float(a.get('y1', 0)))
            x2, y2 = span(float(a.get('x2', 0)), float(a.get('y2', 0)))
            if min(x1, x2) < lo_x or max(x1, x2) > hi_x or min(y1, y2) < lo_y or max(y1, y2) > hi_y:
                err(f'{name}: 第{idx}个 svg line 超界 ({x1},{y1})-({x2},{y2}) viewBox={w}x{h}')
        elif tag == 'path':
            pts = _path_points(a.get('d', ''))
            for (px, py) in pts:
                jx, jy = span(px, py)
                if jx < lo_x or jx > hi_x or jy < lo_y or jy > hi_y:
                    err(f'{name}: 第{idx}个 svg path 点 ({jx},{jy}) 超出 viewBox {w}x{h}')
                    break
    # text 单独提取（需要文本内容估宽）
    for m in re.finditer(r'<text([^>]*)>(.*?)</text>', svg, re.S):
        attrs = m.group(1)
        content = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        a = dict(re.findall(r'([a-zA-Z-]+)\s*=\s*"([^"]*)"', attrs))
        mx, my = parse_translate(a.get('transform', ''))
        x = float(a.get('x', 0)) + mx
        y = float(a.get('y', 0)) + my
        w_est = text_width_est(content)
        anchor = a.get('text-anchor', 'start')
        if anchor == 'middle':
            x0, x1 = x - w_est / 2, x + w_est / 2
        elif anchor == 'end':
            x0, x1 = x - w_est, x
        else:
            x0, x1 = x, x + w_est
        slack = 6.0
        if x0 < lo_x - slack or x1 > hi_x + slack or y < lo_y or y > hi_y:
            err(f'{name}: 第{idx}个 svg text 可能超界/溢出: "{content[:24]}" x∈[{x0:.0f},{x1:.0f}] y={y:.0f} viewBox={w:.0f}x{h:.0f}')
    return n_elem

CITATION_RE = re.compile(r'[（(][^（）()<>]{0,60}?(?:等|et al\.?)[，,][^（）()<>]{0,12}?(?:19|20)\d{2}[a-z]?[^（）()<>]{0,6}[）)]')

def check_page(name, html, refs):
    html_nc = strip_comments(html)
    # B/C/D/H 通用
    hrefs = re.findall(r'<a\s[^>]*href="([^"]+)"', html_nc)
    for h in hrefs:
        if h.startswith(('http://', 'https://', 'mailto:')):
            continue
        frag = ''
        if '#' in h:
            h_file, frag = h.split('#', 1)
        else:
            h_file = h
        if h_file == '':
            # 页内锚点
            if f'id="{frag}"' not in html_nc:
                err(f'{name}: 页内锚点 #{frag} 无对应 id')
            continue
        f = ROOT / h_file
        if not f.exists():
            err(f'{name}: 内部链接指向不存在的文件 {h}')
            continue
        if h_file == '13-references.html' and frag:
            if frag not in refs:
                err(f'{name}: 引用链接 13-references.html#{frag} 不在 references.json')
            elif not refs[frag].get('verified'):
                err(f'{name}: 引用 {frag} 的 verified 不为 true')
    # D: 未加链接的引文
    text_wo_a = re.sub(r'<a\s[^>]*>.*?</a>', '', html_nc, flags=re.S)
    text_wo_a = re.sub(r'<[^>]+>', ' ', text_wo_a)
    for m in CITATION_RE.finditer(text_wo_a):
        err(f'{name}: 未加引用链接的引文模式: {m.group(0)}（应改为 <a href="13-references.html#id">…</a>）')
    # C: 7 部分
    h2s = get_h2s(html_nc)
    if name not in ('index.html', '12-frontier.html', '13-references.html'):
        for sec, test in SECTIONS:
            if not any(test(h) for h in h2s):
                err(f'{name}: 缺少固定部分「{sec}」')
    # E: SVG
    svg_count = 0
    for i, m in enumerate(re.finditer(r'<svg[^>]*>.*?</svg>', html_nc, re.S), 1):
        svg_count += 1
        check_svg(name, i, m.group(0))
    # F: 页面 12 引用条目日期
    if name == '12-frontier.html':
        for h in hrefs:
            if h.startswith('13-references.html#'):
                rid = h.split('#', 1)[1]
                if rid in refs:
                    d = str(refs[rid].get('date', ''))
                    if d and d[:10] < CUTOFF_12M and len(d) >= 10:
                        err(f'{name}: 引用 {rid} 的 date={d} 早于 {CUTOFF_12M}（近12个月限制）')
                    elif d and len(d) < 10:
                        err(f'{name}: 引用 {rid} 的 date={d} 不够精确，无法判断是否在近12个月内')
        if svg_count == 0:
            warn(f'{name}: 无 SVG（12 页允许但建议有）')
    # H: 样式与元信息
    if '<style>' not in html_nc:
        err(f'{name}: 缺少 <style>（每页内嵌统一样式）')
    for v in CSS_VARS_LIGHT:
        if v not in html_nc:
            err(f'{name}: 缺少 CSS 变量 {v}')
    if 'prefers-color-scheme' not in html_nc:
        err(f'{name}: 缺少深色模式（prefers-color-scheme）')
    if 'data-theme="dark"' not in html_nc:
        err(f'{name}: 缺少 data-theme="dark" 手动深色覆盖')
    if 'lang="zh-CN"' not in html_nc:
        err(f'{name}: <html> 缺少 lang="zh-CN"')
    if 'name="viewport"' not in html_nc:
        err(f'{name}: 缺少 viewport meta')
    if '<title>' not in html_nc:
        err(f'{name}: 缺少 <title>')
    return svg_count, len([h for h in hrefs if h.startswith('13-references.html#')])

def main():
    single = None
    if '--file' in sys.argv:
        single = sys.argv[sys.argv.index('--file') + 1]
    refs = load_refs()
    print(f'references.json: {len(refs)} 条, verified 全 true' if all(r['verified'] for r in refs.values()) else 'references.json: 存在未核实条目!')
    pages = [single] if single else PAGES
    total_svg = total_cites = 0
    missing = [p for p in pages if not (ROOT / p).exists()]
    for p in missing:
        err(f'[A] 缺少页面文件: {p}')
    for p in pages:
        fp = ROOT / p
        if not fp.exists():
            continue
        html = fp.read_text(encoding='utf-8')
        ns, nc = check_page(p, html, refs)
        total_svg += ns; total_cites += nc
        print(f'  {p:22s} svg={ns:2d} 引用链接={nc:2d}')
    if not single:
        # 导航链完整性：01-12 每页应含上一页/下一页链接
        idx = {p: i for i, p in enumerate(ORDER)}
        for p in ORDER[1:13]:
            fp = ROOT / p
            if not fp.exists():
                continue
            html = fp.read_text(encoding='utf-8')
            i = idx[p]
            prevp, nextp = ORDER[i - 1], ORDER[i + 1]
            if prevp not in html and prevp.split('-')[0] not in ('13',):
                pass  # 上一页链接可能在导航里以其它形式出现，下面统一检查
            if f'href="{prevp}"' not in html:
                err(f'[导航] {p}: 缺少上一页链接 {prevp}')
            if f'href="{nextp}"' not in html:
                err(f'[导航] {p}: 缺少下一页链接 {nextp}')
        for p in ORDER[1:]:
            fp = ROOT / p
            if fp.exists() and f'href="index.html"' not in fp.read_text(encoding='utf-8'):
                err(f'[导航] {p}: 缺少返回总览 index.html 的链接')
    print(f'\n汇总: 页面 {len([p for p in pages if (ROOT / p).exists()])}, SVG {total_svg}, 引用链接 {total_cites}')
    if warnings:
        print('\n警告:')
        for w in warnings: print('  [W]', w)
    if errors:
        print(f'\n错误 {len(errors)} 条:')
        for e in errors: print('  [E]', e)
        sys.exit(1)
    print('\n全部检查通过 ✓')

if __name__ == '__main__':
    main()
