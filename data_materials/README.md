# data_materials

Materials, raw data, and harmonised outputs for the CREP replication of Feng, D'Mello & Graesser (2013)
(mind wandering while reading easy vs. difficult passages). Each lab ran the study in different software,
so the folders are organised by software, then by project (`yy_nn` folder).

## Contents

| Path | What it is |
|---|---|
| `e_prime/`, `jsPsych/`, `open_sesame/`, `psychopy/`, `qualtrics/`, `superlab/` | Experiment files, materials and data for each software; data live in project subfolders |
| `replication_materials/` | Nelson-Denny passages (easy and difficult) with questions |
| `codebooks/` | One codebook CSV per dataset, `master_schema.csv` (harmonised names), `master_codebook_long.csv` |
| `master_codebook.xlsx` | Combined codebook: schema, master-name x dataset crosswalk, all variables, items to review |
| `master_data.csv` | All datasets harmonised to one row per probed sentence |
| `superlab/superlab_answer_key.csv` | Comprehension answer key for SuperLab (not stored by SuperLab; see below) |
| `data_combination.xlsx` | Earlier hand-made codebook draft, superseded by the files above |

Regenerate with `make_codebooks.R` (profiles the data into the codebook CSVs, keeping hand-edited
descriptions) and then `data_combination.Rmd` (builds `master_codebook.xlsx` and `master_data.csv`).

## Datasets

| Project | Software | Type | Participants | Notes |
|---|---|---|---|---|
| 17_03 | SuperLab | raw | 67 | `.sav` per participant; see SuperLab section |
| 17_25 | OpenSesame | raw | 82 | CSV per participant |
| 17_28 | OpenSesame | raw | 24 | CSV per participant |
| 17_32 | OpenSesame | processed | 93 | |
| 18_06 | OpenSesame | processed | 96 | `RTNoOut_Zub` is entirely empty |
| 18_38 | OpenSesame | processed | 137 | German; has gender, age, native language |
| 19_08 | OpenSesame | raw | 81 | |
| 19_23 | OpenSesame | raw | 91 | |
| 19_32 | E-Prime | processed | 80 | Level 1 = trials, Level 2 = test anxiety |
| 19_41 | OpenSesame | raw | 73 | `Masterdata.csv`: raw logs already stacked, with an added `Subject` column |
| 19_46 | OpenSesame | raw | 134 | Mixed export formats (see below) |
| 20_26 | PsychoPy | raw | 88 | `Set1` and `Set2` folders |
| 20_46 | jsPsych | processed | 70 | Has gender and questionnaire composites |
| 21_28 | OpenSesame | processed | 45 | Seven passages only; 21-23 rows per participant |
| 19_01 | Qualtrics | raw (wide) | 145 | Sentence pages are not timed; only the probed sentences are |
| 19_42 | Qualtrics | raw (wide) | 148 | Hungarian; booklet inferred (see Qualtrics) |
| 19_53 | Qualtrics | raw (wide) | 67 | Also has passage interest ratings |

## The master data: what one row is

`master_data.csv` has one row per **probed sentence** for all 17 projects, in milliseconds. A complete participant has **27 rows**: 7, 2, 2, 4, 3,
4, 2, 3 probes in passages 1-8. This is the shape of the already-processed datasets, and the raw logs contain
exactly those 27 probes. A row holds the (untreated) reading time of the probed sentence, the mind-wandering answer
(`mw_probe`, 0/1), and comprehension question *k* of the passage paired with probe *k* (questions beyond the
number of probes are dropped; this pairing is how the processed files are built, and jsPsych's `QuestionNum`
1.1, 1.2, ... confirms it).

Exceptions to the 27 rows:

- jsPsych (20_46): 26 rows per participant.
- 21_28: 21-23 rows (seven passages).
- SuperLab Set 2: 28 rows (passage 7 has three probes instead of two). All 67 SuperLab files match this exactly.
- Qualtrics partial respondents (answered some but not all probes): 28 in 19_01, 22 in 19_42, 13 in 19_53.
- Partial sessions, kept as is: 17_25 subject 3006 (7 rows), 17_28 subject 21 (10), 19_08 subject 12 (22),
  19_41 subject 18 (22), 19_46 subject 91 (18) and 144 (26).

## Known issues and decisions

### All datasets

- **Booklet:** 1 = odd passages difficult, even easy; 2 = the reverse. Where a dataset has no booklet field it is
  derived from passage difficulty (PsychoPy), from the SuperLab block name, or checked against the data (jsPsych
  `part_condition` cond1/cond2 matches booklet 1/2 exactly).
- **Set vs. booklet:** in PsychoPy and SuperLab, Set 1 is booklet 1 and Set 2 is booklet 2. Each participant read all
  eight passages from one set; the Set 2 odd passages use the easy wording (verified against
  `replication_materials/Easy Passages.docx` and `Difficult Passages.docx`).
- **Difficulty coding:** source labels vary (`Diff.`, `Diff`, `Hard`, `Difficult`, `Easy`) and are recoded to
  Easy/Difficult and 1 = Difficult, 2 = Easy. E-Prime's `Difficult` column is a 0/1 dummy and is not used for this.
- **Units:** reading times are milliseconds in the master. PsychoPy logs and Qualtrics page timers are in
  seconds and are converted (x1000) in the master.
- **Reading times are the original, untreated values only.** Outlier treatment is decided once on the full
  combined data, so the cleaned columns in the source files are not carried into `master_data.csv`, and neither are
  the splits built from them (`Com_Score_HiLo`, `RTnoOut_HiLo`). Recompute them from `read_rt_ms`. Naming
  convention in the sources: `...out` / `...NoOut` / `...noOutliers` = outliers removed; `RT_wind` = winsorized;
  `_Zub` / `_Z` = z-score of the cleaned value. Files with a cleaned column: E-Prime 19_32 `RT_out`, OpenSesame
  17_32 `RTnoOut`, 18_06 and 18_38 `RTNoOut`, 21_28 `RT_noOutliers`, jsPsych 20_46 `RT_wind`. Only 17_32 has missing
  values in its cleaned column; the others have none, which does not fit "removed" and is worth checking if you
  ever need to reproduce the original cleaning.
- **Participant ids** are not unique across projects (combine with `project`). Within a project, ids reused
  across files are suffixed with the file name: 17_25 `5008` (`subject-5008.csv`, `subject-5009.csv`), 19_46 `38`
  and `141` (`subject-38b.csv`, `subject-141b.csv`). These are separate sessions with different data.
- **Descriptions are drafts.** Codebook descriptions were drafted from the earlier xlsx, the data values and the
  software's conventions, not from the original authors' documentation. Rows needing a human check have
  `verify`, `inferred` or `unverified` in `source_notes` (listed in the `to_review` sheet of `master_codebook.xlsx`).

### OpenSesame

- Raw files are **event logs**: sentence rows (`response == "space"`), probe rows (`response` is y/n), comprehension
  rows (`response` a-e, `correct` 0/1). A probe belongs to the sentence row directly before it. Many columns
  (`count_*`, `time_*`, `response_*`, `correct_*`, `live_row_*`) are carried forward from earlier items and are not
  per-row values.
- `time_passage_response` is an **absolute timestamp**, not a reaction time. The reading time is `response_time` on
  the sentence row (equivalently `response_time_passage_response`).
- **Mixed export formats within a folder.** 19_46 has 116 files with only 7 columns (no `subject_nr`, `line`,
  `line_text`, `condition`) next to 13 files with 210 columns. For the short files the participant id comes from the
  file name and the difficulty from `Condition_Num`. 17_25 has one empty file (`subject-1018.csv`), which is skipped.
  The folder contains three export formats, which line up with participant number (so presumably the order they
  were run): subjects 1-6 have 8 columns (the 7 below plus `total_response_time`); subjects 7-17 have the full 210
  columns; subjects 18-153 have 7 columns (`Condition_Num`, `booklet`, `correct`, `correct_response`, `passage`,
  `response`, `response_time`). Three full-format files appear later (60, 61, 141), which may have been run on another
  machine or an older copy of the experiment. The content is the same in all three: a complete session is 180 rows
  (117 sentence, 27 probe, 36 comprehension rows). Nothing stored with the data explains why the logger changed:
  `open_sesame/FengReplication.osexp` has `auto_log yes` (logs every variable), which matches only the full files.
  Ask the 19_46 lab if you need the reason.
- 17_32 `num_Probs` is inconsistent (ten participants have 7 for every passage); the master carries it through as
  reported for processed data and counts probes for raw data.
- 18_38 is in German: `Gender` is translated (männlich/weiblich/divers). `Muttersprache` is native language (coded
  1 = 120 participants, 2 = 17; 1 is probably German, not documented) and `Sorgfalt` is a care/carefulness rating
  (1-4, direction not documented). `Muttersprache` is mapped to `native_language`; `Sorgfalt` has no master variable.
- 21_28: `MW_mean` and `correct_mean` are named like means but contain 0/1 values. `correct_mean` is about 12% missing.

### PsychoPy

- One row per sentence; for probed sentences the probe answer is in the same row (`probe_resp.keys`).
- Reading times are in seconds. No booklet field (derived from difficulty). `condition` has `Diff` and `Diff.` variants.

### SuperLab

SuperLab keeps the file structure of the export but several column headers do not match their contents:

| Column | What it actually holds |
|---|---|
| `Participant_A` | Participant label typed at the start (for example `MW #12`, inconsistent case); the number is the id |
| `Participant_B` | 1 or 2, agrees with `Block` (see below) |
| `Block` | `Condition 1 test` / `Condition 2` = booklet / set 1 / 2 |
| `Participant` | The response given: `space`, `Yes - press y`, `No - press n`, or a letter a-e |
| `PressedOr` | The key actually pressed; blank for space |
| `Correct` | Always `Pressed`; not a correctness flag |
| `Error` | The allowed response keys for the event; not an error flag |
| `Reaction` | Validity code, see below |
| `V12` | **Reaction time in ms**, in an unnamed column (`V13`, `V14` are empty) |

- **`Reaction` codes:** `C` = a valid key for that event; `E` = a wrong key (for example y/n on a sentence screen);
  `SC` = a valid key pressed after one or more wrong keys on the same event (all 60 `SC` rows follow an `E` on the same
  event; read as "self-corrected"). None of these is comprehension accuracy: no correct answer was defined in SuperLab.
- **Answer key:** the `.sl5` has the question text and response keys a-e but no correct answer, and the export has no
  accuracy field. `superlab_answer_key.csv` was built by matching each question's text to the same question in the
  OpenSesame and PsychoPy logs, which store the keyed answer (72 question events, option order and wording identical).
  Two questions (passage 4 question 4 and passage 8 question 4) had a minority key in one 17_25 file; the majority key
  was used. Resulting accuracy is 56.8%, against 55.0% (OpenSesame) and 58.2% (PsychoPy). Two question events have
  garbled names in the data (`S.2:5:3  This passage is mainly about 5.1:3`, `S.2:5 Question 5.1:4`) and were mapped by text.
- **Reshape rules** (needed because event names carry typos and the `Trial` column mislabels some passages):
  passage and set come from the comprehension block that follows each sentence; the sentence read is the closest
  earlier `space` row that is not a probe prompt or intro screen; a probe is a y/n answer with `Reaction` `C`/`SC` that
  is not on an intro screen. A y/n press on a sentence screen (`E`) and y/n presses on the "Passage N.2 Intro" screen
  are stray keys, not probes. Before these rules many files had extra probes (up to 36 rows for one participant); now every file has the expected count.
- **Data quality, not fixed:** 142 reading times are under one second, concentrated in seven participants who
  appear to have pressed through quickly (Sub17, 18, 19, 35, 38, 60, 61). A few reading times are extreme (three over
  200 s, maximum about 1 hour) because raw times are not outlier-treated. Sentence numbers are missing for 269 rows
  where the event name does not contain `(n,`.
- **Event text is truncated** by the export (`...`), so `sentence_text` is partial for SuperLab.

### E-Prime and jsPsych

- E-Prime `RT_out` follows the "out = outliers removed" convention but has no missing values; `Test_Anx` (Level 2) is joined by
  `Subject`.
- jsPsych has 26 probes per participant. Chronotype factor scores and centred variables (`*C`, `ImplicitWP_C`,
  `MindwanderTheoryC`) are derived and not mapped; the composites are.

### Qualtrics

- Wide format: one respondent per row, with a column per sentence page, probe and question (about 360 to 1,540
  columns). Rows 1-3 of each file are headers (variable name, question text, ImportId); rows from 4 are responses.
  Survey definitions are in `qualtrics/*.qsf`: `Mind_Wandering_While_Reading_Study.qsf` is the 19_01 survey and
  `Mind_Wandering_CREP_Study.qsf` the 19_53 survey. **19_42 has no matching `.qsf`** (it is a translated copy
  whose question numbers differ).
- **Reshape** (see `data_combination.Rmd`): a respondent's answered probe columns are split into passages with the
  design counts 7, 2, 2, 4, 3, 4, 2, 3 (this agrees with the 19_53 survey file for 93% of probes; the survey file
  itself has some odd block assignments). Complete respondents have 27 probes and 36 comprehension answers; 117
  (19_01), 126 (19_42) and 54 (19_53) are complete. Survey previews (6 rows in 19_42) are dropped. There is no
  participant number, so `subject_id` is `ResponseId` (19_42, 19_53) or `id` / row number (19_01).
- **Reading time** is the `Q#_Page Submit` timer in seconds, converted to ms. In 19_42 and 19_53 every page has a
  timer *including the probe page* (time spent answering), so the probed sentence's time is the timer **before** the
  probe page's. In 19_01 only the sentence pages are timed, so it is the last timer before the probe.
- **Probe answers** are text: Yes/No, or Igen/Nem in Hungarian.
- **Comprehension** is scored here against `superlab/superlab_answer_key.csv`. 19_42 stores the option letter
  ("e. ..."); 19_01 and 19_53 store only the option text, which is matched to the closest option (within 25% edit
  distance) of that question, taken from the OpenSesame logs. Unmatched answers are `NA`.
- **Booklet** is the survey branch the respondent was in (their first answered probe column). For 19_01 (`Q12` =
  booklet 1, `Q227` = booklet 2) and 19_53 (`Q227` = booklet 1, `Q11` = booklet 2) it comes from the `.qsf`.
  **For 19_42 it is an inference:** the two branches (`Q13`, `Q376`) were matched to 19_53 by total sentence pages
  (the branch with more pages has the longer easy versions of the odd passages, i.e. booklet 2): 19_53 differs by 20
  pages between booklets and 19_42 by 19. Per-passage accuracy could not confirm this (too noisy). If you can get
  the Hungarian survey export, replace this with the real mapping.
- 19_53 has a per-passage interest rating (`Q740_*`) which is not in the master (no master variable).

## Open questions

- Value coding of 18_38 `Muttersprache` (is 1 German?) and the direction of the `Sorgfalt` scale.
- Whether the seven fast-responding SuperLab participants, and the partial sessions, should be excluded.
- 19_42 booklet mapping (inferred, see Qualtrics); Hungarian survey export or `.qsf` would settle it.

