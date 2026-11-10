"""Fuzzy-match sentence_text in data_materials/master_data.csv to the sentence position (1-based) within its
passage, using the original passage text in replication_materials/{Easy,Difficult} Passages.docx.
Writes data_materials/master_data_matched.csv with extra columns sentence_num_fuzzy, sentence_match_score and (19_46 only) sentence_num_rowcount.
The Word files have no passage breaks, so each passage's first sentence was calibrated from rows that
already have an exact text match + sentence_num (offsets below)."""
import pandas as pd, zipfile, re, html, difflib
D = 'data_materials/'
def norm(s):
    s = html.unescape(str(s)); s = re.sub(r'<[^>]+>', ' ', s)
    for a, b in {'’': "'", '‘': "'", '“': '"', '”': '"', '–': '-', '—': '-'}.items(): s = s.replace(a, b)
    return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()
def clean(s):  # strip stray labels found in the SuperLab (17_03) text, e.g. "Passage 6 (set 2) Actual 13", "5.", "7.1"
    s = re.sub(r'^\s*Passage\s*\d+\s*(\(set \d\))?\s*(actual\s*\d+)?[.:]?', '', str(s), flags=re.I)
    s = re.sub(r'^\s*\(?\d+(\.\d+)?[.)]?\s+(?=[A-Z])', '', s)
    return s
def docx(f):
    x = zipfile.ZipFile(f).read('word/document.xml').decode()
    t = [html.unescape(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p))) for p in re.findall(r'<w:p[ >].*?</w:p>', x, re.S)]
    return [re.sub(r'\s+', ' ', s).strip() for s in t if s.strip()]
ref_raw = {k: docx(f'{D}replication_materials/{k} Passages.docx') for k in ['Easy', 'Difficult']}
ref = {k: [norm(s) for s in v] for k, v in ref_raw.items()}
start = {'Difficult': [0, 30, 42, 51, 64, 73, 86, 96], 'Easy': [0, 39, 51, 62, 75, 89, 104, 120]}
cache = {}
def match(df, p, t):
    key = (df, p, t)
    if key not in cache:
        n = norm(clean(t)); a = start[df][p-1]; b = start[df][p] if p < 8 else len(ref[df])
        best = (0, None)
        for i in range(a, b):
            r = difflib.SequenceMatcher(None, n, ref[df][i]).ratio()
            if r > best[0]: best = (r, i - a + 1)
        cache[key] = best
    return cache[key]
def main():
    import merge_into_master
    d = merge_into_master.restore_observed(pd.read_csv(D + 'master_data.csv', low_memory=False))   # observed values only (repeatable)
    has = d.sentence_text.notna() & d.passage.notna() & d.difficulty.notna()
    res = [match(r.difficulty, int(r.passage), r.sentence_text) for r in d[has].itertuples()]
    d['sentence_num_fuzzy'] = pd.NA; d['sentence_match_score'] = pd.NA
    d.loc[has, 'sentence_num_fuzzy'] = [r[1] for r in res]
    d.loc[has, 'sentence_match_score'] = [round(r[0], 3) for r in res]
    d['sentence_num_fuzzy'] = d.sentence_num_fuzzy.astype('Int64')

    # --- 19_46: sentence position rebuilt by counting rows in the raw logs -------------------------------------
    # 121 of 134 participants have a 7-column export with no `line`. In the 13 full files `line` equals the number of
    # "space" (sentence) rows seen so far in the passage minus 1 (the first space row is a title screen, line 0);
    # this rule reproduces `line` for all 351 probed sentences there, so it is applied to every file. A probe (y/n)
    # belongs to the sentence row before it; probes are numbered within passage in the same way as data_combination.Rmd.
    import glob, os
    rows = []
    for f in sorted(glob.glob(D + 'open_sesame/19_46/*.csv')):
        g = pd.read_csv(f, low_memory=False, usecols=lambda c: c in ('response', 'passage'))
        g['passage'] = pd.to_numeric(g.passage, errors='coerce')
        sp = (g.response == 'space') & g.passage.notna()
        pos = sp.groupby(g.passage).cumsum() - 1
        cnt = {}
        for i in g.index[g.response.isin(['y', 'n']) & g.passage.notna()]:
            j = g.index[:i][sp[:i]].max(); p = int(g.passage[j]); cnt[p] = cnt.get(p, 0) + 1
            rows.append((os.path.basename(f), p, cnt[p], int(pos[j])))
    rc = pd.DataFrame(rows, columns=['source_file', 'passage', 'probe_num', 'sentence_num_rowcount'])
    rc['project'] = '19_46'
    d = d.merge(rc, on=['project', 'source_file', 'passage', 'probe_num'], how='left')
    d['sentence_num_rowcount'] = d.sentence_num_rowcount.astype('Int64')
    d.to_csv(D + 'master_data_matched.csv', index=False)


if __name__ == '__main__':
    main()
