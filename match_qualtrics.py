"""Recover sentence_num for the Qualtrics projects (19_01, 19_53) by replaying the page-timer logic of
data_combination.Rmd, then looking up the sentence shown on that page in the .qsf survey definition."""
import pandas as pd, numpy as np, json, re, html, difflib, sys
sys.path.insert(0, '.')
D = 'data_materials/'
probes_per_passage = [7, 2, 2, 4, 3, 4, 2, 3]

def qsf_pages(path):
    q = json.load(open(path)); Q = {}; B = []
    for e in q['SurveyElements']:
        if e['Element'] == 'SQ': Q[e['Payload']['QuestionID']] = e['Payload']
        if e['Element'] == 'BL': B = e['Payload'] if isinstance(e['Payload'], list) else list(e['Payload'].values())
    out = {}   # timing tag -> sentence text on the same page
    for b in B:
        pages = [[]]
        for x in b['BlockElements']:
            if x.get('Type') == 'Page Break': pages.append([])
            elif x.get('QuestionID') in Q: pages[-1].append(Q[x['QuestionID']])
        for p in pages:
            tm = [z['DataExportTag'] for z in p if z['QuestionText'].strip() == 'Timing']
            tx = [html.unescape(re.sub(r'<[^>]+>', ' ', z['QuestionText'])) for z in p
                  if z['QuestionText'].strip() != 'Timing' and not re.match(r'\s*(Were|Where) you', html.unescape(z['QuestionText']))]
            tx = [re.sub(r'\s+', ' ', t).strip() for t in tx if t.strip()]
            for t in tm:
                if tx: out[t] = tx[0]
    return out

def read_wide(path, sep=','):
    raw = pd.read_csv(path, header=None, dtype=str, sep=sep, keep_default_na=False, na_values=[''])
    nm = list(raw.iloc[0]); nm = [n if isinstance(n, str) else f'unnamed_{i}' for i, n in enumerate(nm)]
    seen = {}; u = []
    for n in nm:
        k = seen.get(n, 0); u.append(n if k == 0 else f'{n}.{k}'); seen[n] = k + 1
    d = raw.iloc[3:].reset_index(drop=True); d.columns = u
    return d

def replay(ds, path, rt_offset, branch_booklet):
    cb = pd.read_csv(f'{D}codebooks/qualtrics_{ds}_codebook.csv', dtype=str)
    mw_cols = list(cb.variable[cb.mapped_master_name == 'mw_probe'])
    rt_cols = list(cb.variable[cb.mapped_master_name == 'read_rt_ms'])
    d = read_wide(path)
    if 'Status' in d: d = d[d.Status != 'Survey Preview'].reset_index(drop=True)
    pos = {c: i for i, c in enumerate(d.columns)}
    rows = []
    for i, r in d.iterrows():
        ans = lambda cols: [c for c in cols if c in pos and isinstance(r[c], str) and r[c].strip() != '']
        am = ans(mw_cols)
        if not am: continue
        am = am[:sum(probes_per_passage)]; ar = ans(rt_cols)
        arp = [pos[c] for c in ar]
        pas = np.repeat(range(1, 9), probes_per_passage)[:len(am)]
        cnt = {}
        for c, p in zip(am, pas):
            idx = sum(1 for x in arp if x <= pos[c]) - (rt_offset - 1)
            cnt[p] = cnt.get(p, 0) + 1
            rows.append(dict(row=i, passage=int(p), probe_num=cnt[p], timer=ar[idx-1] if idx > 0 else None,
                             rt=float(r[ar[idx-1]]) * 1000 if idx > 0 else np.nan,
                             rid=r['ResponseId'] if 'ResponseId' in d else (r['id'] if isinstance(r.get('id'), str) else f'row{i+1}')))
    return pd.DataFrame(rows)

if __name__ == '__main__':
    # run this file only: it first calls match_sentences.main() (which writes master_data_matched.csv), then adds sentence_num_qsf, sentence_num_design, sentence_text_ref and sentence_text_ref_from
    import match_sentences
    from match_sentences import match
    match_sentences.main()   # rewrites master_data_matched.csv, then the Qualtrics/design columns are added below
    m = pd.read_csv(D + 'master_data_matched.csv', low_memory=False)
    jobs = {'19_01': (D + 'qualtrics/19_01/Replication_Data.csv', 1, D + 'qualtrics/Mind_Wandering_While_Reading_Study.qsf'),
            '19_53': (D + 'qualtrics/19_53/Widman & Herion_Raw Data.csv', 2, D + 'qualtrics/Mind_Wandering_CREP_Study.qsf')}
    cells = {}
    for ds, (path, off, qsf) in jobs.items():
        r = replay(ds, path, off, None); pages = qsf_pages(qsf)
        x = m[m.project == ds].reset_index(drop=True)
        assert len(r) == len(x) and np.allclose(r.rt, x.read_rt_ms, equal_nan=True) and (r.passage == x.passage).all()
        res = [match(x.difficulty[i], int(x.passage[i]), pages[r.timer[i].replace('_Page Submit', '')]) for i in range(len(x))]
        x['num'] = [b for a, b in res]; x['score'] = [a for a, b in res]
        # one respondent in 19_01 has a missing timer, so the replayed timer (and read_rt_ms) is the neighbouring
        # page for passages 7-8. Use the most common sentence for each booklet x passage x probe instead.
        c = x.groupby(['booklet', 'passage', 'probe_num']).agg(num=('num', lambda s: s.mode()[0]), minscore=('score', 'min'),
                                                               n_diff=('num', lambda s: (s != s.mode()[0]).sum()))
        cells[ds] = c
        print(ds, 'cells', len(c), 'respondent-rows off the modal sentence:', int(c.n_diff.sum()))
    cells['19_42'] = cells['19_53']          # same page structure, checked: gaps between probed sentences are identical per branch
    m['sentence_num_qsf'] = pd.NA
    for ds, c in cells.items():
        idx = m.project == ds
        key = pd.MultiIndex.from_frame(m.loc[idx, ['booklet', 'passage', 'probe_num']])
        m.loc[idx, 'sentence_num_qsf'] = c.num.reindex(key).values
    m['sentence_num_qsf'] = m.sentence_num_qsf.astype('Int64')
    # Design lookup: the probed sentence is fixed by booklet x passage x probe_num. Every project with an observed
    # sentence number (all except 17_03, which uses its own numbering) gives the same sentence in all 54 cells, so
    # the lookup is applied to any row with a booklet and probe_num, including the processed projects.
    obs = m[(m.project != '17_03')].assign(best=lambda t: t.sentence_num.fillna(t.sentence_num_rowcount).fillna(t.sentence_num_qsf))
    obs = obs[obs.best.notna()]
    lut = obs.groupby(['booklet', 'passage', 'probe_num']).best.agg(lambda s: s.mode()[0])
    off = obs.best.values != lut.reindex(pd.MultiIndex.from_frame(obs[['booklet', 'passage', 'probe_num']])).values
    print('observed rows off the design lookup:', int(off.sum()), 'of', len(obs), obs[off].groupby('project').size().to_dict())
    key = pd.MultiIndex.from_frame(m[['booklet', 'passage', 'probe_num']])
    m['sentence_num_design'] = pd.array(lut.reindex(key).values, dtype='Int64')
    # Reference text: the sentence at the best available position, taken from the original passage Word files.
    # Order of preference: the project's own number (17_03 uses its own numbering, so its fuzzy match when the score
    # is >= 0.9), the 19_46 row count, the .qsf match, then the design lookup.
    from match_sentences import ref_raw, start
    own = m.sentence_num.where(m.project != '17_03')
    fz = m.sentence_num_fuzzy.where((m.project == '17_03') & (m.sentence_match_score >= 0.9))
    cands = [('sentence_num', own), ('sentence_num_fuzzy', fz), ('sentence_num_rowcount', m.sentence_num_rowcount),
             ('sentence_num_qsf', m.sentence_num_qsf), ('sentence_num_design', m.sentence_num_design)]
    num = pd.Series(np.nan, index=m.index); src = pd.Series(pd.NA, index=m.index, dtype='object')
    for name, col in cands:
        use = num.isna() & col.notna()
        num[use] = col[use].astype(float); src[use] = name
    txt = [ref_raw[r.difficulty][start[r.difficulty][int(r.passage) - 1] + int(n) - 1]
           if pd.notna(n) and pd.notna(r.passage) and pd.notna(r.difficulty) else pd.NA
           for r, n in zip(m.itertuples(), num)]
    m['sentence_text_ref'] = txt; m['sentence_text_ref_from'] = src
    m.to_csv(D + 'master_data_matched.csv', index=False)
    print(m.groupby('project').sentence_num_qsf.apply(lambda s: s.notna().sum())[['19_01', '19_42', '19_53']])
    import match_comprehension, merge_into_master
    match_comprehension.main()
    merge_into_master.main()   # last: writes the merged master_data.csv and master_comprehension.csv
