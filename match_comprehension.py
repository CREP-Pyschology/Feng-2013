"""Add the comprehension question text to master_data_matched.csv (columns comprehension_question_ref,
comprehension_options_ref, comprehension_key_ref), looked up from comprehension_item (passage.question).
Reference: the OpenSesame 19_08 logs, which show every question with its options and the keyed answer.
Called at the end of match_qualtrics.py."""
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

if __name__ == '__main__':
    main()
