# -*- coding: utf-8 -*-
"""阶段1修复：对 verify 失败的条目，用 arXiv API / Crossref bibliographic 搜索按标题找正确 ID。
命中（期望标题片段匹配）则写入 data/ref_fixes.json，之后 verify_refs.py 会用它覆盖候选。"""
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

def arxiv_search(q, n=6):
    url = ('https://export.arxiv.org/api/query?search_query='
           + urllib.parse.quote(f'ti:"{q}"') + f'&max_results={n}')
    raw = get(url, FETCH / f'search_arxiv_{re.sub(r"[^a-z0-9]+", "_", norm(q))[:60]}.xml')
    out = []
    for m in re.finditer(r'<entry>(.*?)</entry>', raw, re.S):
        e = m.group(1)
        idm = re.search(r'<id>http://arxiv.org/abs/([^v<]+)', e)
        tm = re.search(r'<title>(.*?)</title>', e, re.S)
        if idm and tm:
            out.append(dict(ref=idm.group(1).strip(), title=html.unescape(re.sub(r'\s+', ' ', tm.group(1)).strip())))
    return out

def crossref_search(q, n=6):
    url = ('https://api.crossref.org/works?query.bibliographic='
           + urllib.parse.quote(q) + f'&rows={n}&mailto=check@example.org')
    raw = get(url, FETCH / f'search_crossref_{re.sub(r"[^a-z0-9]+", "_", norm(q))[:60]}.json')
    items = json.loads(raw)['message']['items']
    out = []
    for it in items:
        t = (it.get('title') or [''])[0]
        if t and it.get('DOI'):
            out.append(dict(ref=it['DOI'], title=t))
    return out

# id -> (mode, query, new_expect or None, year or None)
SEARCHES = {
    'krenn2020selfies':      ('arxiv', 'SELFIES a robust representation', None, None),
    'kadurin2017drugan':     ('arxiv', 'druGAN advanced generative adversarial autoencoder', None, None),
    'decao2018mogan':        ('arxiv', 'Molecular generative adversarial networks for de novo drug design', None, None),
    'shi2020graphaf':        ('arxiv', 'GraphAF a flow-based autoregressive model', None, None),
    'zang2020moflow':        ('arxiv', 'MoFlow an invertible flow model for generating molecular graphs', None, None),
    'luo2021graphdf':        ('arxiv', 'GraphDF a discrete flow model for molecular graph generation', None, None),
    'jin2020hier':           ('arxiv', 'Multi-objective molecule generation using interpretable disentangled representations', None, None),
    'bagal2021molgpt':       ('arxiv', 'MolGPT molecular generation using transformers', None, None),
    'ross2022molformer':     ('arxiv', 'Large-scale chemical language representations capture molecular structure', None, None),
    'flamshepherd2023language': ('arxiv', 'Language models can learn complex molecule distributions', None, None),
    'anderson2019cormorant': ('arxiv', 'Cormorant covariant molecular neural networks', None, None),
    'gebauer2019gschnet':    ('arxiv', 'Symmetry-adapted generation of 3d point sets for the targeted discovery of molecules', None, None),
    'peng2022pocket2mol':    ('arxiv', 'Pocket2Mol efficient molecular sampling based on 3d generative models', None, None),
    'ragoza20223d':          ('arxiv', 'Generative models for 3d structure-based drug design', None, None),
    'jing2022torsional':     ('arxiv', 'Torsional diffusion for molecular conformation generation', None, None),
    'guan2023targetdiff':    ('arxiv', '3d equivariant diffusion for target-aware molecule generation', None, None),
    'stark2024dirichlet':    ('arxiv', 'Dirichlet flow matching', None, None),
    'igashov2024efm':        ('arxiv', 'Equivariant flow matching with hybrid probability transport', None, None),
    'krishna2024boltz1':     ('arxiv', 'Boltz-1 democratizing biomolecular state prediction', None, None),
    'passaro2025boltz2':     ('arxiv', 'Boltz-2 towards material and drug discovery', None, None),
    'chai2024chai1':         ('arxiv', 'Chai-1 decoding the molecular interactions of life', None, None),
    'dauparas2022proteinmpnn': ('arxiv', 'Robust deep learning-based protein sequence design using ProteinMPNN', None, None),
    'brown2019guacamol':     ('arxiv', 'GuacaMol benchmarking models for de novo molecular generation', None, None),
    'isert2023posebusters':  ('arxiv', 'PoseBusters AI-based docking methods are not yet ready', None, None),
    'madani2023progen':      ('arxiv', 'Large language models generate functional protein sequences across diverse families', None, None),
    'ingraham2019proteingraph': ('arxiv', 'Generative models for graph-based protein design', None, None),
    'bowman2016latent':      ('arxiv', 'Generating sentences from a continuous space', None, None),
    'bran2024chemcrow':      ('arxiv', 'ChemCrow augmenting large language models with chemistry tools', None, None),
    'jablonka2024gpt4chem':  ('arxiv', 'Leveraging large language models for predictive chemistry', None, None),
    'arus2019smilesenum':    ('arxiv', 'SMILES-based deep generative scaffolds for molecular enumeration', None, None),
    'segler2018rnn':         ('both',  'Generating focused molecule libraries for drug discovery with recurrent neural networks', None, None),
    'zhavoronkov2019ddr1':   ('crossref', 'Deep learning enables rapid identification of potent DDR1 kinase inhibitors', None, None),
    'olivecrona2017reinvent':('crossref', 'Molecular de novo design through deep learning with conditional recurrent neural networks', None, None),
    'schneuing2024diffsbdd': ('crossref', 'Structure-based drug design with equivariant diffusion models', None, None),
    'coley2018scscore':      ('crossref', 'Quantifying the synthetic challenge of proposed molecules', None, None),
    'coley2017retro':        ('crossref', 'Computer-assisted retrosynthesis based on molecular similarity', None, None),
    'genheden2020aizynth':   ('crossref', 'AiZynthFinder a fast robust and flexible open-source software for retrosynthetic planning', None, None),
    'macleod2020selfdriving':('crossref', 'Self-driving laboratory for chemistry and materials science', None, None),
    'mendezlucio2019cgan':   ('crossref', 'De novo generation of hit-like molecules from gene expression signatures using conditional generative adversarial networks', None, None),
    'blaschke2020reinvent2': ('crossref', 'REINVENT 2.0 an AI tool for de novo drug design', 'reinvent 2.0', 2020),
    # 仅期望片段修正（ID 正确）
    'goodfellow2014gan':     ('none', '', 'generative adversarial', None),
    'segler2018mcts':        ('none', '', 'planning chemical syntheses with deep neural networks', None),
}

def main():
    fixes = {}
    for cid, (mode, q, nexp, year) in SEARCHES.items():
        found = None
        if mode in ('arxiv', 'both'):
            for r in arxiv_search(q):
                if norm(q.split()[0]) in norm(r['title']):
                    found = dict(kind='arxiv', ref=r['ref'], expect=nexp or norm(q)[:40], year=year)
                    found['found_title'] = r['title']
                    break
        if not found and mode in ('crossref', 'both'):
            for r in crossref_search(q):
                t = norm(r['title'])
                if norm(q[:40]) in t or t in norm(q):
                    found = dict(kind='doi', ref=r['ref'], expect=nexp or norm(q)[:40], year=year)
                    found['found_title'] = r['title']
                    break
        if found:
            fixes[cid] = found
            print(f'OK    {cid:28s} -> {found["kind"]}:{found["ref"]}  | {found["found_title"][:70]}')
        else:
            print(f'MISS  {cid:28s}  (query: {q[:60]})')
    out = ROOT / 'data' / 'ref_fixes.json'
    old = json.loads(out.read_text(encoding='utf-8')) if out.exists() else {}
    old.update(fixes)
    out.write_text(json.dumps(old, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\nfixes total: {len(old)} (wrote data/ref_fixes.json)')

if __name__ == '__main__':
    main()
