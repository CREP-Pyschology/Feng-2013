"""Add the comprehension question text to master_data_matched.csv (columns comprehension_question_ref,
comprehension_options_ref, comprehension_key_ref), looked up from comprehension_item (passage.question).
Reference: the OpenSesame 19_08 logs, which show every question with its options and the keyed answer.
add_to_comprehension() adds the same columns to master_comprehension.csv. Both are called from match_qualtrics.py."""
import pandas as pd, glob, re
D = 'data_materials/'

def reference():
    rows = []
    for f in sorted(glob.glob(D + 'open_sesame/19_08/*.csv')):
        d = pd.read_csv(f, low_memory=False, dtype=str)
        if 'comprehension_q' not in d: continue
        rows.append(d[(d.comprehension_q == 'y') & d.correct_response.notna()][['passage', 'line_text', 'correct_response']])
    c = pd.concat(rows)
    c['q'] = c.line_text.str.extract(r'^\s*(\d+)\.')[0]
    c = c.groupby(['passage', 'q']).agg(text=('line_text', lambda s: s.mode()[0]), key=('correct_response', lambda s: s.mode()[0])).reset_index()
    out = {}
    for r in c.itertuples():
        parts = [re.sub(r'\s+', ' ', p).strip() for p in r.text.split('<br/>') if p.strip()]
        stem = re.sub(r'^\d+\.\s*', '', parts[0])
        opts = [p for p in parts[1:] if re.match(r'^[a-e]\.', p)]
        out[f'{r.passage}.{r.q}'] = (stem, ' | '.join(opts), r.key)
    return out

def main():
    m = pd.read_csv(D + 'master_data_matched.csv', low_memory=False, dtype={'comprehension_item': str})
    ref = reference()
    # comprehension_item can be read as "1.1" or, for floats, "1.1"; keep it as text
    get = lambda i, k: ref[i][k] if isinstance(i, str) and i in ref else pd.NA
    m['comprehension_question_ref'] = [get(i, 0) for i in m.comprehension_item]
    m['comprehension_options_ref'] = [get(i, 1) for i in m.comprehension_item]
    m['comprehension_key_ref'] = [get(i, 2) for i in m.comprehension_item]
    m.to_csv(D + 'master_data_matched.csv', index=False)

    return ref

def add_to_comprehension():
    """Add the reference columns to master_comprehension.csv (repeatable: any earlier copies are replaced)."""
    ref = reference()
    get = lambda i, k: ref[i][k] if isinstance(i, str) and i in ref else pd.NA
    c = pd.read_csv(D + 'master_comprehension.csv', low_memory=False)
    c = c.drop(columns=[x for x in c.columns if x.endswith('_ref') or x == 'comprehension_item'])
    item = [f'{int(p)}.{int(q)}' if pd.notna(p) and pd.notna(q) else pd.NA for p, q in zip(c.passage, c.question_num)]
    c['comprehension_item'] = item
    c['comprehension_question_ref'] = [get(i, 0) for i in item]
    c['comprehension_options_ref'] = [get(i, 1) for i in item]
    c['comprehension_key_ref'] = [get(i, 2) for i in item]
    c.to_csv(D + 'master_comprehension.csv', index=False)


if __name__ == '__main__':
    main()
