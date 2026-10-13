# Builds / refreshes one codebook CSV per dataset in data_materials/codebooks/.
#
# Auto-filled on every run: variable, type, example_values, n_unique, pct_missing
# Hand-edited (preserved on re-run): description, mapped_master_name, source_notes
# Only prefilled on first run: description (SPSS labels / Qualtrics question text)

library(tidyverse)
library(data.table)
library(haven)
library(readxl)

root <- "data_materials"
out_dir <- file.path(root, "codebooks")
dir.create(out_dir, showWarnings = FALSE)

# ---- readers ---------------------------------------------------------------
# each reader returns list(data = tibble (all character), labels = named chr or NULL)

read_all_chr <- function(x) mutate(x, across(everything(), ~ as.character(as_factor_safe(.x))))
as_factor_safe <- function(x) if (inherits(x, "haven_labelled")) unclass(x) else x

read_csv_chr <- function(f) {
  as_tibble(fread(f, colClasses = "character", encoding = "UTF-8", na.strings = c("", "NA")))
}

read_spss_chr <- function(f) {
  x <- haven::read_sav(f)
  lab <- map_chr(x, ~ attr(.x, "label") %||% NA_character_)
  list(data = read_all_chr(x), labels = lab)
}

read_xlsx_chr <- function(f, sheet = 1) {
  read_excel(f, sheet = sheet, col_types = "text")
}

read_qualtrics <- function(f) {
  # rows: 1 = variable name, 2 = question text, 3 = ImportId JSON, 4+ = responses
  # (read whole file at once; question text contains embedded newlines)
  raw <- fread(f, header = FALSE, colClasses = "character", encoding = "UTF-8",
               na.strings = c("", "NA"), fill = TRUE)
  nm <- as.character(unlist(raw[1]))
  nm[is.na(nm) | nm == ""] <- paste0("unnamed_col_", which(is.na(nm) | nm == ""))
  nm <- make.unique(nm)
  q <- str_squish(as.character(unlist(raw[2])))
  dat <- raw[-(1:3)]
  setnames(dat, nm)
  list(data = as_tibble(dat), labels = setNames(q, nm))
}

# read every file matching pattern in a folder; stack; track which vars occur in which files
read_folder <- function(dir, pattern, reader) {
  files <- list.files(dir, pattern = pattern, full.names = TRUE, ignore.case = TRUE)
  parts <- map(files, reader)
  dfs <- map(parts, ~ if (is.data.frame(.x)) .x else .x$data)
  list(data = bind_rows(dfs),
       n_files = length(files),
       present = table(unlist(map(dfs, names))),
       labels = NULL)
}

# ---- dataset registry ------------------------------------------------------
sl <- function(...) file.path(root, ...)

datasets <- list(
  eprime_19_32_level1 = \(){ r <- read_spss_chr(sl("e_prime/19_32/Feng replication - Level 1.sav")); c(r, n_files = 1) },
  eprime_19_32_level2 = \(){ r <- read_spss_chr(sl("e_prime/19_32/Feng replication - Level 2.sav")); c(r, n_files = 1) },
  jspsych_20_46 = \() list(data = read_csv_chr(sl("jsPsych/20_46/FengReplicationResults_Dec2020.csv")), n_files = 1),
  opensesame_17_25 = \() read_folder(sl("open_sesame/17_25"), "\\.csv$", read_csv_chr),
  opensesame_17_28 = \() read_folder(sl("open_sesame/17_28"), "\\.csv$", read_csv_chr),
  opensesame_17_32 = \() list(data = read_csv_chr(sl("open_sesame/17_32/FENG.MASTER.R.csv")), n_files = 1),
  opensesame_18_06 = \() list(data = read_xlsx_chr(sl("open_sesame/18_06/Feng.Data.xlsx")), n_files = 1),
  opensesame_18_38 = \() list(data = read_xlsx_chr(sl("open_sesame/18_38/Feng replication_Data.xlsx")), n_files = 1),
  opensesame_19_08 = \() read_folder(sl("open_sesame/19_08"), "\\.csv$", read_csv_chr),
  opensesame_19_23 = \() read_folder(sl("open_sesame/19_23"), "\\.csv$", read_csv_chr),
  opensesame_19_41 = \() list(data = read_csv_chr(sl("open_sesame/19_41/Masterdata.csv")), n_files = 1),
  opensesame_19_46 = \() read_folder(sl("open_sesame/19_46"), "\\.csv$", read_csv_chr),
  opensesame_21_28 = \() list(data = read_csv_chr(sl("open_sesame/21_28/FengDatasetUpdated.csv")), n_files = 1),
  psychopy_20_26_set1 = \() read_folder(sl("psychopy/20_26/Set1"), "\\.csv$", read_csv_chr),
  psychopy_20_26_set2 = \() read_folder(sl("psychopy/20_26/Set2"), "\\.csv$", read_csv_chr),
  superlab_17_03 = \() read_folder(sl("superlab/17_03"), "\\.sav$", \(f) read_spss_chr(f)$data),
  qualtrics_19_01 = \() c(read_qualtrics(sl("qualtrics/19_01/Replication_Data.csv")), n_files = 1),
  qualtrics_19_42 = \() c(read_qualtrics(sl("qualtrics/19_42/feng_data.txt")), n_files = 1),
  qualtrics_19_53 = \() c(read_qualtrics(sl("qualtrics/19_53/Widman & Herion_Raw Data.csv")), n_files = 1)
)

# ---- profiling -------------------------------------------------------------
describe_values <- function(x, n_show = 4, width = 40) {
  v <- x[!is.na(x)]
  if (length(v) == 0) return(NA_character_)
  num <- suppressWarnings(as.numeric(v))
  if (!anyNA(num) && n_distinct(v) > n_show) {
    return(sprintf("range %s to %s", format(min(num), digits = 6), format(max(num), digits = 6)))
  }
  tab <- sort(table(v), decreasing = TRUE)
  top <- names(tab)[seq_len(min(n_show, length(tab)))]
  paste(str_trunc(str_squish(top), width), collapse = " | ")
}

infer_type <- function(x) {
  v <- x[!is.na(x)]
  if (length(v) == 0) return("empty")
  if (all(v %in% c("TRUE", "FALSE", "True", "False"))) return("logical")
  num <- suppressWarnings(as.numeric(v))
  if (!anyNA(num)) return(if (all(num == round(num))) "integer" else "numeric")
  if (n_distinct(v) <= 10) "categorical (text)" else "text"
}

profile <- function(res) {
  d <- res$data
  tibble(
    variable = names(d),
    type = map_chr(d, infer_type),
    example_values = map_chr(d, describe_values),
    n_unique = map_int(d, ~ n_distinct(.x, na.rm = TRUE)),
    pct_missing = round(100 * map_dbl(d, ~ mean(is.na(.x))), 1)
  ) |>
    mutate(file_coverage = if (!is.null(res$present) && res$n_files > 1)
      as.integer(res$present[variable]) else NA_integer_,
      n_files = res$n_files,
      label_prefill = if (!is.null(res$labels)) unname(res$labels[variable]) else NA_character_)
}

# ---- write, preserving hand edits -------------------------------------------
for (nm in names(datasets)) {
  message("Profiling ", nm)
  res <- datasets[[nm]]()
  prof <- profile(res)
  path <- file.path(out_dir, paste0(nm, "_codebook.csv"))

  old <- if (file.exists(path)) read_csv(path, col_types = cols(.default = "c")) else NULL

  cb <- prof |>
    mutate(description = label_prefill,
           mapped_master_name = NA_character_,
           source_notes = ifelse(!is.na(file_coverage) & file_coverage < n_files,
                                 sprintf("auto: present in %d of %d files", file_coverage, n_files),
                                 NA_character_))
  if (!is.null(old)) {
    keep <- old |> select(variable, description, mapped_master_name, source_notes)
    cb <- cb |> select(-description, -mapped_master_name, -source_notes) |>
      left_join(keep, by = "variable")
  }
  cb |>
    transmute(dataset = nm, variable, description, type, example_values, n_unique,
              pct_missing, mapped_master_name, source_notes) |>
    write_csv(path, na = "")
}
message("Done. Codebooks in ", out_dir)
