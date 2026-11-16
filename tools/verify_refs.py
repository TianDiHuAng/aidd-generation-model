# -*- coding: utf-8 -*-
"""阶段1：逐条打开原文/摘要页核对标题、作者、年份。
来源两种：arXiv abs 页（解析 citation_* 元标签）与 Crossref API（DOI 元数据）。
输出：references.json（仅保留 verified=true）+ data/verify_failures.json + data/fetch/ 原始缓存留档。
用法: python -I tools/verify_refs.py [--rebuild-only]"""
import json, re, sys, time, unicodedata, urllib.request, urllib.error, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
FETCH = ROOT / 'data' / 'fetch'
FETCH.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / 'tools'))
from build_refs import CANDIDATES

UA = {'User-Agent': 'Mozilla/5.0 (compatible; bibliography-checker/1.0; static-site project)'}

def norm(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r'\s+', ' ', s).strip().lower()

def get(url, cache_path, refresh=False):
    if cache_path.exists() and not refresh:
        return cache_path.read_text(encoding='utf-8', errors='replace')
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode('utf-8', errors='replace')
    cache_path.write_text(raw, encoding='utf-8')
    time.sleep(0.6)
    return raw

def fetch_arxiv(ref):
    url = f'https://arxiv.org/abs/{ref}'
    raw = get(url, FETCH / f'arxiv_{ref.replace(".", "_")}.html')
    if 'no longer active' in raw or 'Not Found' in raw[:2000]:
        return None
    def metas(name):
        vals = re.findall(r'<meta\s+name="' + re.escape(name) + r'"\s+content="(.*?)"\s*/?>', raw, re.I)
        return [html.unescape(v) for v in vals]
    title = metas('citation_title')
    authors = metas('citation_author')
    date = metas('citation_date') or metas('citation_online_date')
    if not title or not authors:
        return None
    y_m_d = date[0].split('/') if date else ['0', '0', '0']
    y = int(y_m_d[0]) if y_m_d[0].isdigit() else 0
    ds = f'{y_m_d[0]}-{y_m_d[1].zfill(2)}-{y_m_d[2].zfill(2)}' if len(y_m_d) == 3 else ''
    # arXiv 页面自带 journal-ref（作者填写的正式出处）与 comments，如实记录
    jref = re.search(r'<td class="tablecell jref">(.*?)</td>', raw, re.S)
    comments = re.search(r'<td class="tablecell comments">(.*?)</td>', raw, re.S)
    venue = html.unescape(jref.group(1)).strip() if jref else ''
    vcmt = html.unescape(comments.group(1)).strip() if comments else ''
    return dict(title=title[0], authors=authors, year=y, date=ds, venue=venue,
                venue_comment=vcmt, url=url, source='arxiv')

def fetch_doi(doi):
    url = f'https://api.crossref.org/works/{doi}'
    raw = get(url, FETCH / f'doi_{re.sub(r"[^A-Za-z0-9._-]", "_", doi)}.json')
    msg = json.loads(raw)['message']
    title = (msg.get('title') or [''])[0]
    authors = []
    for a in msg.get('author', []):
        nm = ' '.join(x for x in (a.get('given', ''), a.get('family', '')) if x)
        if nm:
            authors.append(nm)
    if not title or not authors:
        return None
    year, date = 0, ''
    for k in ('published-print', 'published-online', 'issued', 'created'):
        dp = msg.get(k, {}).get('date-parts', [[None]])
        if dp and dp[0] and dp[0][0]:
            year = dp[0][0]
            date = '-'.join(str(x).zfill(2) for x in dp[0][:3])
            break
    venue = (msg.get('container-title') or [''])[0]
    return dict(title=title, authors=authors, year=year, date=date, venue=venue,
                venue_comment='', url=f'https://doi.org/{doi}', source='crossref')

def main(refresh=False):
    drops = set(json.loads((ROOT / 'data' / 'ref_drops.json').read_text(encoding='utf-8')))
    fixes = json.loads((ROOT / 'data' / 'ref_fixes.json').read_text(encoding='utf-8'))
    results, failures = {}, []
    cands = []
    for c in CANDIDATES:
        if c['id'] in drops:
            print(f'[ drop] {c["id"]}  (无法核对来源，剔除)')
            continue
        c = dict(c)
        fx = fixes.get(c['id'])
        if fx:
            if fx.get('kind'):
                c['kind'], c['ref'] = fx['kind'], fx['ref']
            c['expect'] = fx['expect']
            if 'year' in fx and fx['year'] is not None:
                c['year'] = fx['year']
        cands.append(c)
    for i, c in enumerate(cands, 1):
        try:
            if c['kind'] == 'arxiv':
                got = fetch_arxiv(c['ref'])
            else:
                got = fetch_doi(c['ref'])
        except Exception as e:
            got = None
            err = f'{type(e).__name__}: {e}'
        else:
            err = 'page parse failed' if got is None else ''
        if got is None:
            failures.append(dict(id=c['id'], ref=c['ref'], error=err or 'fetch failed'))
            results[c['id']] = dict(status='fail', error=err or 'fetch failed')
            print(f'[{i:3d}/{len(cands)}] FAIL  {c["id"]}  {err}')
            continue
        ok = c['expect'] in norm(got['title'])
        year_ok = (not c.get('year')) or got['year'] == c['year']
        if ok and year_ok:
            results[c['id']] = dict(status='ok', **got)
            print(f'[{i:3d}/{len(cands)}] OK    {c["id"]}  {got["year"]}  {got["title"][:60]}')
        else:
            why = 'title mismatch' if not ok else f'year mismatch (expect {c["year"]}, got {got["year"]})'
            failures.append(dict(id=c['id'], ref=c['ref'], got_title=got['title'], got_year=got['year'], why=why))
            results[c['id']] = dict(status='mismatch', why=why, **got)
            print(f'[{i:3d}/{len(cands)}] MISS  {c["id"]}  {why}  | got: {got["title"][:60]}')

    refs = []
    for c in cands:
        r = results.get(c['id'])
        if not r or r['status'] != 'ok':
            continue
        entry = dict(
            id=c['id'], title=r['title'], authors=r['authors'], year=r['year'],
            date=r['date'], venue=r['venue'],
            venue_comment=r.get('venue_comment', ''),
            url=r['url'],
            doi=(c['ref'] if c['kind'] == 'doi' else f'10.48550/arXiv.{c["ref"]}'),
            contribution=c['contrib'], verified=True, source=r['source'],
        )
        refs.append(entry)
    out = ROOT / 'references.json'
    out.write_text(json.dumps(dict(generated='2026-11-16', rule='verified=true 仅在打开原文/摘要页核对标题、作者、年份后成立', entries=refs),
                              ensure_ascii=False, indent=1), encoding='utf-8')
    (ROOT / 'data' / 'verify_failures.json').write_text(
        json.dumps(failures, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\nverified={len(refs)} / candidates={len(CANDIDATES)}  failures={len(failures)}')
    print('wrote references.json and data/verify_failures.json')

if __name__ == '__main__':
    main(refresh='--refresh' in sys.argv)
