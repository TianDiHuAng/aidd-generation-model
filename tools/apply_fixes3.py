# -*- coding: utf-8 -*-
"""阶段1最终修复：写入 data/ref_fixes.json（含 kind/ref/expect/year 覆盖与 expect-only 修正）
和 data/ref_drops.json（无法核对的候选，剔除）。ref=None 表示保留原候选的 kind/ref。"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
data = ROOT / 'data'
data.mkdir(exist_ok=True)

FIXES = {
    # --- arXiv ID 修正 ---
    'krenn2020selfies':      dict(kind='arxiv', ref='1905.13741', expect='selfies', year=2019),
    'isert2023posebusters':  dict(kind='arxiv', ref='2308.05777', expect='posebusters', year=2023),
    'shi2020graphaf':        dict(kind='arxiv', ref='2001.09382', expect='graphaf', year=2020),
    'zang2020moflow':        dict(kind='arxiv', ref='2006.10137', expect='moflow', year=2020),
    'luo2021graphdf':        dict(kind='arxiv', ref='2102.01189', expect='graphdf', year=2021),
    'jin2020hier':           dict(kind='arxiv', ref='2002.03244', expect='multi-objective molecule generation', year=2020),
    'ross2022molformer':     dict(kind='arxiv', ref='2106.09553', expect='chemical language representations', year=2021),
    'anderson2019cormorant': dict(kind='arxiv', ref='1906.04015', expect='cormorant', year=2019),
    'gebauer2019gschnet':    dict(kind='arxiv', ref='1906.00957', expect='symmetry-adapted generation of 3d point sets', year=2019),
    'jing2022torsional':     dict(kind='arxiv', ref='2206.01729', expect='torsional diffusion', year=2022),
    'guan2023targetdiff':    dict(kind='arxiv', ref='2303.03543', expect='target-aware molecule generation', year=2023),
    'stark2024dirichlet':    dict(kind='arxiv', ref='2402.05841', expect='dirichlet flow matching', year=2024),
    'igashov2024efm':        dict(kind='arxiv', ref='2312.07168', expect='equivariant flow matching', year=2023),
    # --- bioRxiv（有 DOI，走 Crossref 元数据核对）---
    'krishna2024boltz1':     dict(kind='doi', ref='10.1101/2024.11.19.624167', expect='boltz-1', year=2024),
    'passaro2025boltz2':     dict(kind='doi', ref='10.1101/2025.06.14.659707', expect='boltz-2', year=2025),
    'chai2024chai1':         dict(kind='doi', ref='10.1101/2024.10.10.615955', expect='chai-1', year=2024),
    # --- DOI 修正 ---
    'dauparas2022proteinmpnn': dict(kind='doi', ref='10.1126/science.add2187', expect='proteinmpnn', year=2022),
    'brown2019guacamol':     dict(kind='doi', ref='10.1021/acs.jcim.8b00839', expect='guacamol', year=2019),
    'blaschke2020reinvent2': dict(kind='doi', ref='10.1021/acs.jcim.0c00915', expect='reinvent 2.0', year=2020),
    'genheden2020aizynth':   dict(kind='doi', ref='10.1186/s13321-020-00472-1', expect='aizynthfinder', year=2020),
    'coley2018scscore':      dict(kind='doi', ref='10.1021/acs.jcim.8b00501', expect='scscore', year=2018),
    'olivecrona2017reinvent':dict(kind='doi', ref='10.1186/s13321-017-0235-x', expect='molecular de-novo design through deep reinforcement learning', year=2017),
    'kadurin2017drugan':     dict(kind='doi', ref='10.1021/acs.molpharmaceut.7b00346', expect='dragan', year=2016),
    'mendezlucio2019cgan':   dict(kind='doi', ref='10.1038/s41467-019-13807-w', expect='conditional generative adversarial', year=2019),
    'flamshepherd2023language': dict(kind='doi', ref='10.1038/s41467-022-30839-x', expect='complex molecular distributions', year=2022),
    'zhavoronkov2019ddr1':   dict(kind='doi', ref='10.1038/s41587-019-0224-x', expect='ddr1 kinase inhibitors', year=2019),
    'segler2018rnn':         dict(kind='doi', ref='10.1021/acscentsci.7b00512', expect='generating focused molecule libraries', year=2018),
    'coley2017retro':        dict(kind='doi', ref='10.1021/acscentsci.7b00355', expect='computer-assisted retrosynthesis', year=2017),
    'selfdriving2024sdl':    dict(kind='doi', ref='10.1021/acs.chemrev.4c00055', expect='self-driving laborator', year=2024),
    'bagal2021molgpt':       dict(kind='doi', ref='10.1021/acs.jcim.1c00600', expect='molgpt', year=2021),
    # --- 仅期望片段修正（ID 正确）---
    'goodfellow2014gan':     dict(kind=None, ref=None, expect='generative adversarial', year=2014),
    'segler2018mcts':        dict(kind=None, ref=None, expect='planning chemical syntheses with deep neural networks', year=2018),
}
DROPS = ['arus2019smilesenum', 'decao2018mogan', 'ingraham2019proteingraph', 'macleod2020selfdriving']

(data / 'ref_fixes.json').write_text(json.dumps(FIXES, ensure_ascii=False, indent=1), encoding='utf-8')
(data / 'ref_drops.json').write_text(json.dumps(DROPS, ensure_ascii=False, indent=1), encoding='utf-8')
print('fixes:', len(FIXES), ' drops:', len(DROPS))
