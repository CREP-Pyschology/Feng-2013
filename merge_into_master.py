"""Merge the recovered sentence and comprehension information into data_materials/master_data.csv and
master_comprehension.csv. Called at the end of match_qualtrics.py (do not run it on its own).

master_data.csv keeps every observed value and gains provenance columns:
  sentence_num_raw      sentence_num exactly as exported (17_03 numbers probe screens too, so it is not a position)
  sentence_num          sentence position in the passage, coalesced; observed values first
  sentence_num_source   observed | rowcount | qsf | qsf_copy_19_53 | text_match | design
  sentence_text         observed text, else the passage-file text for the recovered position
  sentence_text_source  observed | reference
  comprehension_question_ref / _options_ref / _key_ref   from the OpenSesame 19_08 logs
The merge is repeatable: when master_data.csv already has the added columns, observed values are restored first.
The intermediate recovery columns stay in master_data_matched.csv."""
import pandas as pd, numpy as np
D = 'data_materials/'
ADDED = ['sentence_num_raw', 'sentence_num_source', 'sentence_text_source', 'comprehension_question_ref',
         'comprehension_options_ref', 'comprehension_key_ref']

def restore_observed(d):
    """Undo an earlier merge: back to the values observed in the source files."""
    if 'sentence_num_raw' in d:
        d['sentence_num'] = d.sentence_num_raw
        d.loc[d.sentence_text_source != 'observed', 'sentence_text'] = pd.NA
    return d.drop(columns=[c for c in ADDED if c in d])

def main():
    m = pd.read_csv(D + 'master_data_matched.csv', low_memory=False, dtype={'comprehension_item': str, 'passage_sentence_id': str})
    obs = restore_observed(pd.read_csv(D + 'master_data.csv', low_memory=False, dtype={'comprehension_item': str, 'passage_sentence_id': str}))
    assert len(m) == len(obs)
    has_text = m.sentence_text.notna()
    is03 = m.project == '17_03'

    # 17_03: the number it exports counts probe screens, so the position comes from the text match (score >= 0.9),
    # or from the design lookup when that agrees with the fuzzy match. Two cells are left blank: Set 1 passage 4 and
    # Set 2 passage 6 probes 3-4 where the two disagree, and Set 2 passage 7 probe 2 (repeated text).
    fz_ok = is03 & (m.sentence_match_score >= 0.9)
    des_ok = is03 & ~fz_ok & (m.sentence_num_design == m.sentence_num_fuzzy)
    blank03 = is03 & (m.set == 2) & (m.passage == 7) & (m.probe_num == 2)
    p03 = pd.Series(np.nan, index=m.index)
    p03[fz_ok] = m.sentence_num_fuzzy[fz_ok]; p03[des_ok] = m.sentence_num_design[des_ok]; p03[blank03] = np.nan
    s03 = pd.Series(pd.NA, index=m.index, dtype='object'); s03[fz_ok & ~blank03] = 'text_match'; s03[des_ok & ~blank03] = 'design'

    cands = [('observed', m.sentence_num.where(~is03)), ('text_match_03', p03), ('rowcount', m.sentence_num_rowcount),
             ('qsf', m.sentence_num_qsf), ('design', m.sentence_num_design.where(~is03))]
    num = pd.Series(np.nan, index=m.index); src = pd.Series(pd.NA, index=m.index, dtype='object')
    for name, col in cands:
        use = num.isna() & col.notna()
        num[use] = col[use].astype(float)
        src[use] = name
    src = src.replace({'text_match_03': np.nan}).where(src != 'text_match_03', s03)
    src[(src == 'qsf') & (m.project == '19_42')] = 'qsf_copy_19_53'
    # the 17_03 source labels from s03 (text_match / design) replace the placeholder
    src[is03 & num.notna()] = s03[is03 & num.notna()]

    out = obs.copy()
    out['sentence_num_raw'] = out.sentence_num
    out['sentence_num'] = pd.array(num.values, dtype='Int64')
    out['sentence_num_source'] = src.where(src.notna(), pd.NA)

    # text: observed first, else the passage-file text for the position used
    from match_sentences import ref_raw, start
    ref_txt = [ref_raw[r.difficulty][start[r.difficulty][int(r.passage) - 1] + int(n) - 1]
               if pd.notna(n) and pd.notna(r.passage) and pd.notna(r.difficulty) else pd.NA
               for r, n in zip(m.itertuples(), num)]
    out['sentence_text_source'] = np.where(out.sentence_text.notna(), 'observed', np.where(pd.Series(ref_txt).notna(), 'reference', None))
    out['sentence_text'] = out.sentence_text.where(out.sentence_text.notna(), pd.Series(ref_txt))
    for c in ['comprehension_question_ref', 'comprehension_options_ref', 'comprehension_key_ref']:
        out[c] = m[c].values

    cols = list(obs.columns)
    def after(col, new):
        cols.insert(cols.index(col) + 1, new)
    after('sentence_num', 'sentence_num_raw'); after('sentence_num_raw', 'sentence_num_source')
    after('sentence_text', 'sentence_text_source')
    after('comprehension_item', 'comprehension_question_ref'); after('comprehension_question_ref', 'comprehension_options_ref')
    after('comprehension_options_ref', 'comprehension_key_ref')
    out[cols].to_csv(D + 'master_data.csv', index=False)

    # every scored comprehension answer: the same reference columns
    import match_comprehension
    match_comprehension.add_to_comprehension()
    return out[cols]
