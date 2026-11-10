o# Missing data in `master_data.csv`

One section per variable: how much is missing, where, why, and what (if anything) was done about it.
Counts are from `master_data.csv` (39,538 rows, 17 projects). Variable definitions are in
`master_codebook.xlsx` (source: `codebooks/master_schema.csv`).

Add new variables below as they are reviewed.

## `set`

- **Missing:** 34,342 of 39,538 rows (87%).
- **Filled for:** 17_03 (SuperLab), 20_26 (PsychoPy), 21_28 (OpenSesame). Missing for the other 14 projects.
- **Why:** only these three recorded a set. The other projects recorded a booklet or condition label only.
- **Information lost:** none. Where filled, `set` is identical to `booklet` (Set 1 = booklet 1, Set 2 = booklet 2),
  and `booklet` is filled for every project.
- **Handling:** left as NA on purpose. It was not back-filled from `booklet`, because that would imply the other
  projects recorded a set. Use `booklet` for analysis.
- **Why keep it:** it is a provenance column. In 17_03 it identifies the Set 2 participants, who have 28 rows
  instead of 27 (passage 7 has three probes in that set), and the row-count check in `data_combination.Rmd` uses it.

## `probe_num`

- **Missing:** 2,160 rows (5%), all of 19_32 (E-Prime, 80 participants x 27 rows). Filled (1-7) for the other 16 projects.
- **Why:** the 19_32 processed file (`Feng replication - Level 1.sav`) is sorted by reading time within participant,
  not by trial order, so the order of the probes within a passage was lost. Its `Sen_num` column is labelled "sentence
  number" in the authors' codebook but is neither that nor a reliable probe index: it only takes values 1-7, is 1 on all
  7 rows of passage 1 (whose probes are at sentences 2-30), and varies within a passage only in passages 2, 5, 6, 7
  and 8. Its meaning is unexplained (question for the 19_32 lab). The `.ebs3` experiment files are encrypted, so the
  script cannot be read to check. No raw E-Prime output
  (`.edat3` participant files) is available to rebuild the order.
- **Knock-on effects (19_32 only):**
  - `comprehension_item` is blank, because elsewhere it is built as `passage.probe_num`.
  - `sentence_num` and `sentence_text` are also blank (the file has no sentence information).
  - `comprehension_correct` is still present, because the Level 1 file stores the score on each row, so the
    probe-to-question pairing used for the other projects is not needed.
- **Handling:** left as NA. It cannot be inferred. Reading time cannot give the order, since the file was sorted by it,
  and without the probed sentence there is nothing to rank within a passage.
- **Analysis note:** 19_32 can be used for analyses that do not need probe order (passage, difficulty, booklet,
  reading time, mind-wandering, comprehension score). It cannot be used for anything that depends on position within
  a passage.

## `sentence_num` (and `sentence_text`)

Position (1-based) of the probed sentence within its passage, and its text.

- **Missing in `master_data.csv`:** `sentence_num` is NA for 25,806 of 39,537 rows (65%). `sentence_text` is NA for
  25,537 rows; the difference is the 269 rows in 17_03 that have text but no number.
- **Filled for:** 17_25, 17_28, 19_08, 19_23, 19_41, 20_26 (all rows), 17_03 (1,574 of 1,843 rows) and 19_46 (351 of 3,608 rows).
- **Why it is missing, by group:**

| Group | Projects | Rows | Why |
|---|---|---|---|
| Processed files with no sentence information | 17_32, 18_06, 18_38, 21_28 (OpenSesame), 19_32 (E-Prime), 20_46 (jsPsych) | 13,758 | The processed files keep only reading time and the probe answer. The OpenSesame ones give `passage_sentence_id` (for example `1_3`), but that is passage + probe index, not the sentence position. E-Prime `Sen_num` is not a usable sentence number (see `probe_num`), and jsPsych has no sentence field. |
| Qualtrics | 19_01, 19_42, 19_53 | 8,522 | Wide-format export, one column per page. The sentence text is not in the data file (it is only in the survey definitions). |
| 19_46 short export | 19_46 | 3,257 | 121 of 134 participants have the 7-column logger export, which has no `line` or `line_text`. Only 13 participants (subjects 7-17, 60, 61, 141) have the full 210-column export. See `README.md`; the reason for the logger change is unknown. |
| 17_03 | 17_03 (SuperLab) | 269 | These rows have text but no number. Some start with stray labels (for example "Passage 6 (set 2) Actual 13", "5.", "7.1"), and two have no sentence text at all. |

- **Handling:** every recovery below is a separate column in `master_data_matched.csv`; `sentence_num` in
  `master_data.csv` is unchanged. Scripts: `match_sentences.py`, then `match_qualtrics.py` (run in that order).

| Column | Method | Rows filled | Evidence |
|---|---|---|---|
| `sentence_num_fuzzy` | Fuzzy match of `sentence_text` to the original passage Word files | all rows with text (17_03, 17_25, 17_28, 19_08, 19_23, 19_41, 19_46, 20_26) | Agrees with `sentence_num` for 98-100% of rows in every project except 17_03 (15%: its own numbers do not follow the Word-file order). |
| `sentence_num_rowcount` | 19_46 only: number of sentence rows seen so far in the passage minus 1 (the first row of each passage is a title screen, line 0) | all 3,608 | Reproduces `line` for all 351 probed sentences in the 13 full files; in the short files positions are identical across participants for the same booklet, passage and probe, except subject 144 (see below). |
| `sentence_num_qsf` | 19_01 and 19_53: replay of the page-timer logic of `data_combination.Rmd` (reproduces `read_rt_ms` and `passage` on 100% of rows), then the sentence on that timer's page in the `.qsf`, fuzzy-matched to the Word files. 19_42: copied from 19_53 by booklet x passage x probe, because its survey has the same page structure (the gaps between probed sentences are identical within every passage in both booklets) | all 8,522 | 19_01 and 19_53 agree in all 54 booklet x passage x probe cells, and both agree with 19_08 in all 54. 19_42's booklet is itself an inference (see the `booklet` notes), and its Hungarian pages were not read. |
| `sentence_num_design` | The probed sentence is fixed by booklet x passage x probe_num: all ten projects with observed numbers (every project except 17_03) give the same sentence in all 54 cells. This lookup is applied to every row that has a booklet and probe_num | every row except 19_32 (no `probe_num`) and the 34 third-probe rows of 17_03 Set 2 | Matches all but 6 of 23,936 observed rows (the 6 are 19_46 subject 144). On 17_03 it agrees with the fuzzy match for 93% of rows with a match score above 0.9. For the processed projects it assumes their `probe_num` is correct. |

- **Still without any sentence position:** 19_32 (2,160 rows, no `probe_num`; see above). The 34 rows of 17_03 (Set 2,
  passage 7, third probe) are not in the design lookup because no other project has a third probe there, but their
  text is an exact match to sentence 16 of the easy passage 7, so `sentence_num_fuzzy` = 16 for them.
- **17_03 Set 2, passage 7 (caution):** the first two probes of this passage carry the same sentence text ("After
  pursuing his early career in Italy...", sentence 4) and the same SuperLab number (6), so they cannot be told apart
  from the text. `sentence_num_design` gives them 4 and 16, which is wrong for the second one (the 16 belongs to the
  third probe). For 17_03 use `sentence_num_fuzzy` instead of `sentence_num_design` for these rows; the true sentence of
  the second probe is unknown.
- **Subject 144 (19_46):** has 26 probe rows instead of 27; the first probe of passage 1 is missing. Its sentence
  positions from `sentence_num_rowcount` are right, but its `probe_num` values from that point are shifted by one in
  `master_data.csv`, so `sentence_num_design` is wrong for those rows.
- **19_01 timer problem (found while recovering this):** one respondent has a missing page timer, so the timer the
  master used for their passage 7-8 probes belongs to a neighbouring page (the replay gives a different page than
  the other 60 respondents for 4 probes). Their `read_rt_ms` for those probes is probably the wrong sentence's time.
  Not fixed.
- **Not recoverable:** the sentence text itself for the processed projects, and positions for 19_32.

## `n_probes_in_passage`

- **Missing:** was missing for all 1,820 rows of 20_46 (jsPsych); now filled for every row.
- **Why it was missing:** the other processed files report the count (`num_Probs`, `Num_Probs`), but the jsPsych file
  has no such variable, and `data_combination.Rmd` left it blank.
- **Handling:** counted per participant and passage from the rows present, the same way as for the raw projects.
  All 70 participants give 7, 2, 2, 4, 3, 3, 2, 3 probes in passages 1-8 (26 rows each).
- **Caution:** the design has 4 probes in passage 6 (27 rows per participant), and 20_46 has 3, so one passage 6 probe is
  absent from the file. Which one is unknown: `probe_num` for passage 6 is numbered 1-3 from `QuestionNum`, and there
  is no sentence text. If the missing probe is not the last one, `sentence_num_design` is wrong for the later passage 6
  probes of 20_46. The count therefore reflects the probes in the file, not the design. Ask the 20_46 lab.

## `passage_sentence_id`

- **Missing:** was missing for 29,760 of 39,537 rows (everything except the processed OpenSesame projects 17_32, 18_06,
  18_38 and 21_28). Now missing for 2,160 rows, all of 19_32.
- **What it is:** passage + probe index (`1_3` = passage 1, probe 3). It is **not** a sentence position, although the
  original codebook calls it that. In all 9,778 rows that supplied it, it equals passage + `probe_num`.
- **Handling:** derived as `passage_probe_num` for every row that has a passage and `probe_num`, in one format (21_28
  originally wrote it without the underscore, for example `11`). `data_combination.Rmd` checks the supplied values
  against passage + `probe_num` before replacing them.
- **Still missing:** 19_32, because it has no `probe_num` (see above). The column adds no information beyond `passage`
  and `probe_num`; it is kept as a key.

## `sentence_text`

- **Missing in `master_data.csv`:** 25,537 of 39,537 rows (65%). Filled only for the raw OpenSesame, PsychoPy and
  SuperLab projects (17_03, 17_25, 17_28, 19_08, 19_23, 19_41, 20_26) and 351 rows of 19_46.
- **Why:** the processed files, the Qualtrics data files and the 19_46 short export do not contain the sentence text. See
  `sentence_num` above.
- **Recovery:** `sentence_text_ref` in `master_data_matched.csv` is the sentence at the best available position (given
  by passage, difficulty and sentence position) in the original passage Word files in `replication_materials`. It is the
  clean English text, without the `<br/>` markup in the raw logs. `sentence_text_ref_from` says which column gave the
  position. Order of preference: the project's own `sentence_num` (17_03 uses `sentence_num_fuzzy` instead, when the
  match score is 0.9 or more), then `sentence_num_rowcount`, `sentence_num_qsf` and `sentence_num_design`.
- **Filled for:** 37,377 rows (everything except 19_32). Where the original text exists, the reference sentence
  matches it in 98-100% of rows (100% for 19_08, 19_23, 19_41, 19_46 and 20_26; 99.5% for 17_28; 98% for 17_25).
- **Caveats:**
  - For the processed projects (17_32, 18_06, 18_38, 20_46, 21_28) the text is inferred from `sentence_num_design`, which
    assumes their `probe_num` is correct. It is wrong for 20_46 passage 6 if the missing probe is not the last one, and
    for 19_46 subject 144.
  - 19_42 participants read a Hungarian translation; the reference text is the English original.
  - 17_03 Set 2, passage 7, second probe: the sentence is unknown (the raw text repeats the first probe).
  - The Word files are the replication materials, not necessarily what every lab displayed.
- **Still missing:** 19_32 (2,160 rows), which has no sentence position.

## 17_03 (SuperLab) sentence numbers: what the experiment script shows

- The SuperLab 5 experiment file (`superlab/Completly Revised Mind Wandering Replication Study.sl5`) names every event
  "Passage N (k, sentence text)", with `k` typed by hand. The "Is your mind wandering?" probe screens are events too
  and take a number, so 17_03's `sentence_num` is the sentence's position in the passage **plus the number of probe
  screens before it**. This explains why 17_03's numbers run 1-5 above the other labs' (for example the Hawthorne
  sentence is passage sentence 18 and event 20, with two probe screens before it).
- The labels have typos (events numbered out of order, passage names wrong on a few events, "actual 12" corrections),
  so the conversion was not done from the script. Instead, for each set x passage x 17_03 number, the position was read
  from the rows whose text matches the Word files with a score of 0.9 or more. That mapping is consistent: 21 cells,
  no conflicts. The remaining 17_03 probe cells (low match scores because of truncated or reworded text) have the same
  position in `sentence_num_fuzzy` and `sentence_num_design`, except Set 1 passage 4 (below).
- **Set 1 passage 4:** 17_03's two probed sentences are "Just mountains, craters, cold winds, and dust storms." (own
  number 7) and "It was almost as if scouts for Columbus…" (own number 9). The first is the difficult-version wording,
  although booklet 1 passage 4 should be the easy version, and in the easy Word file the sentence is "All they saw
  were mountains, craters, cold winds, and dust storms." So 17_03's script appears to mix the two wordings in this
  passage, or probes a different sentence than the other labs. `sentence_num_design` (7, 8) assumes the other labs'
  probes; `sentence_num_fuzzy` (6, 7) follows the text. Neither is verified. Ask the 17_03 lab.
- **Set 2 passage 7:** the script labels "After pursuing his early career…" as event 6 and has a probe screen as event 5
  right after it, but the labels around it skip numbers (2, and the third probe's screen is not labelled in the
  same way), so the second probe's sentence could not be read from it. The third probe's text matches sentence 16.

## `comprehension_item` and the question text

- **Missing before:** `comprehension_item` (passage.question, for example `2.1`) was NA for all rows of the processed
  OpenSesame projects (17_32, 18_06, 18_38, 21_28) and E-Prime 19_32: 9,657 rows had a comprehension answer but no item.
- **Handling:** the master pairs question k with probe k, and every supplied item equals passage.`probe_num` (checked on
  all 12 projects that supplied it). `data_combination.Rmd` now derives `comprehension_item` as passage.`probe_num` for every
  row that has a comprehension answer and a `probe_num`. For the processed OpenSesame projects this assumes that row k
  holds question k, as in the original processed files.
- **Still missing (2,409 rows):** 19_32 (2,160 rows, no `probe_num`, so the question cannot be identified), and rows
  where the question was not answered (no `comprehension_correct`): 21_28 121, 19_42 54, 19_01 40, 19_53 18,
  17_25 7, 19_08 4, 19_23 3, 17_28 1, 19_41 1.
- **Question text:** the master has no question text, so `master_data_matched.csv` adds `comprehension_question_ref` (the
  question), `comprehension_options_ref` (options a-e) and `comprehension_key_ref` (keyed answer), looked up from
  `comprehension_item`. The source is the OpenSesame 19_08 logs, which show each of the 36 questions with its options and
  key (`match_comprehension.py`). Filled for all 37,128 rows that have a `comprehension_item`.
- **Checks:** the keyed answer agrees with `correct_key` in `master_comprehension.csv` for 99.95% of 34,118 rows (the 18
  disagreements are all 17_25). The question stems only roughly match the Nelson-Denny Word file (20 of the 36 stems
  score below 0.9), so the replication wording differs from that file in places; the 19_08 text is what participants saw.
- **Caveats:** this is one wording per question. 19_42 participants read a Hungarian translation. The text for the
  processed projects is inferred from the pairing rule, not observed.
- **Not covered:** the master keeps only the 27 comprehension answers that pair with a probe. The other questions
  (36 per participant, all of them in `master_comprehension.csv`) have no item in `master_data.csv`.
