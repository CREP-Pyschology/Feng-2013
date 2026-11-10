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
