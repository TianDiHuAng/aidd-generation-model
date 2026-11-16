# -*- coding: utf-8 -*-
"""阶段1修复第2轮：短查询 + query.title + 双源回退。结果并入 data/ref_fixes.json。"""
import json, re, sys, time, unicodedata, urllib.request, urllib.parse, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
FETCH = ROOT / 'data' / 'fetch'; FETCH.mkdir(parents=True, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (compatible; bibliography-checker/1.0)'}

def norm(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r'\s+', ' ', s).strip().lower()

def get(url, cache):
    if cache.exists():
        return cache.read_text(encoding='utf-8', errors='replace')
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode('utf-8', errors='replace')
    cache.write_text(raw, encoding='utf-8')
    time.sleep(0.7)
    return raw

def arxiv_search(q, n=8):
    url = ('https://export.arxiv.org/api/query?search_query='
           + urllib.parse.quote(q) + f'&max_results={n}')
    raw = get(url, FETCH / f'search2_arxiv_{re.sub(r"[^a-z0-9]+", "_", norm(q))[:60]}.xml')
    out = []
    for m in re.finditer(r'<entry>(.*?)</entry>', raw, re.S):
        e = m.group(1)
        idm = re.search(r'<id>http://arxiv.org/abs/([^v<]+)', e)
        tm = re.search(r'<title>(.*?)</title>', e, re.S)
        pm = re.search(r'<published>(\d{4})', e)
        if idm and tm:
            out.append(dict(ref=idm.group(1).strip(),
                            title=html.unescape(re.sub(r'\s+', ' ', tm.group(1)).strip()),
                            year=int(pm.group(1)) if pm else 0))
    return out

def crossref_title(q, n=8):
    url = ('https://api.crossref.org/works?query.title='
           + urllib.parse.quote(q) + f'&rows={n}&mailto=check@example.org')
    raw = get(url, FETCH / f'search2_crossref_{re.sub(r"[^a-z0-9]+", "_", norm(q))[:60]}.json')
    out = []
    for it in json.loads(raw)['message']['items']:
        t = (it.get('title') or [''])[0]
        y = 0
        for k in ('published-print', 'published-online', 'issued'):
            dp = it.get(k, {}).get('date-parts', [[None]])
            if dp and dp[0] and dp[0][0]:
                y = dp[0][0]; break
        if t and it.get('DOI'):
            out.append(dict(ref=it['DOI'], title=t, year=y))
    return out

def token_overlap(qt, tt):
    qs = set(w for w in norm(qt).split() if len(w) > 2)
    ts = set(norm(tt).split())
    return len(qs & ts) / max(1, len(qs))

# id -> (query, mode, expect_fragment, want_year or None)
SEARCHES = {
    'krenn2020selfies':        ('ti:"SELFIES"', 'arxiv_both', 'selfies', 2020),
    'kadurin2017drugan':       ('druGAN generative adversarial autoencoder molecules', 'crossref_both', 'dragan', None),
    'decao2018mogan':          ('ti:"Molecular generative adversarial networks"', 'arxiv_both', 'generative adversarial networks', None),
    'jin2020hier':             ('ti:"Multi-objective molecule generation"', 'arxiv_both', 'multi-objective molecule generation', None),
    'bagal2021molgpt':         ('ti:"MolGPT"', 'arxiv_both', 'molgpt', None),
    'flamshepherd2023language':('ti:"Language models can learn complex molecule distributions"', 'arxiv_both', 'complex molecule distributions', None),
    'krishna2024boltz1':       ('ti:"Boltz-1"', 'arxiv_both', 'boltz-1', None),
    'passaro2025boltz2':       ('ti:"Boltz-2"', 'arxiv_both', 'boltz-2', None),
    'chai2024chai1':           ('ti:"Chai-1"', 'arxiv_both', 'chai-1', None),
    'dauparas2022proteinmpnn': ('ti:"ProteinMPNN"', 'arxiv_both', 'proteinmpnn', None),
    'brown2019guacamol':       ('GuacaMol benchmarking models de novo molecular generation', 'crossref_both', 'guacamol', 2019),
    'isert2023posebusters':    ('ti:"PoseBusters"', 'arxiv_both', 'posebusters', None),
    'madani2023progen':        ('ti:"Large language models generate functional protein sequences"', 'arxiv_both', 'functional protein sequences', None),
    'ingraham2019proteingraph':('ti:"Generative models for graph-based protein design"', 'arxiv_both', 'graph-based protein design', None),
    'jablonka2024gpt4chem':    ('ti:"Leveraging large language models for predictive chemistry"', 'arxiv_both', 'predictive chemistry', None),
    'schneuing2024diffsbdd':   ('Structure-based drug design with equivariant diffusion models', 'crossref_both', 'equivariant diffusion', None),
    'coley2018scscore':        ('Quantifying synthetic challenge proposed molecules', 'crossref_both', 'synthetic', None),
    'genheden2020aizynth':     ('AiZynthFinder fast robust flexible open source retrosynthetic planning', 'crossref_both', 'aizynthfinder', 2020),
    'macleod2020selfdriving':  ('Self-driving laboratory for chemistry and materials science', 'crossref_both', 'self-driving laboratory', 2020),
    'blaschke2020reinvent2':   ('REINVENT 2.0 AI tool de novo drug design', 'crossref_both', 'reinvent 2.0', 2020),
    'olivecrona2017reinvent':  ('Molecular de novo design through deep learning conditional recurrent neural networks', 'crossref_both', 'molecular de novo design', None),
    'zhavoronkov2019ddr1':     ('Deep learning enables rapid identification of potent DDR1 kinase inhibitors', 'crossref_both', 'ddr1 kinase inhibitors', None),
    # 仅期望片段修正（ID 正确，无需搜索）
    'goodfellow2014gan':       (None, 'none', 'generative adversarial', None),
    'segler2018mcts':          (None, 'none', 'planning chemical syntheses with deep neural networks', None),
}

def main():
    path = ROOT / 'data' / 'ref_fixes.json'
    fixes = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    for cid, (q, mode, expect, year) in SEARCHES.items():
        found = None
        if mode != 'none':
            cands = []
            if mode in ('arxiv', 'arxiv_both'):
                cands += [dict(kind='arxiv', **r) for r in arxiv_search(f'ti:"{q}"' if q.startswith('ti:') is False else q)]
            if mode in ('crossref', 'arxiv_both', 'crossref_both') and not cands:
                cands += [dict(kind='doi', **r) for r in crossref_title(q)]
            for c in cands:
                if expect in norm(c['title']) and token_overlap(q.replace('ti:', '').strip('"'), c['title']) >= 0.55:
                    if year and c['year'] and abs(c['year'] - year) > 1:
                        continue
                    found = dict(kind=c['kind'], ref=c['ref'], expect=expect, year=year)
                    found['found_title'] = c['title']; found['found_year'] = c['year']
                    break
        else:
            found = dict(kind=None, ref=None, expect=expect, year=year, found_title='(expect-only fix)')
        if found:
            fixes[cid] = found
            print(f'OK    {cid:28s} -> {found["kind"]}:{found["ref"]}  y={found["found_year"]}  | {found["found_title"][:68]}')
        else:
            print(f'MISS  {cid:28s}  (q={q})')
    path.write_text(json.dumps(fixes, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\nfixes total: {len(fixes)}')

if __name__ == '__main__':
    main()
