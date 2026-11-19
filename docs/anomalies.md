# Data anomalies — DPE-Insight

Snapshot: `data/raw/dpe_93.csv.gz`, retrieved 2026-11-18, 419,164 DPEs dated 2021-07-01 to 2026-11-11 (SHA-256 in the manifest). Counts below come from `src/cleaning.py` and its report `data/processed/dpe_93_clean_report.json`.

No row is deleted. Each anomaly is either corrected (commune names) or flagged with a `flag_*` column so each analysis can decide whether to exclude it.

## Checks that passed

| Check | Result |
|---|---|
| Duplicate `numero_dpe` | 0 |
| Fully duplicated rows | 0 |
| Records outside department 93 | 0 |
| Missing or unexpected energy label | 0 (all A–G) |
| Missing date, building type, heating energy, INSEE code | 0 |
| Distinct INSEE codes | 40 (the 40 municipalities of the department) |

## Missing values

| Column | Missing | Share | Impact |
|---|---:|---:|---|
| `annee_construction` | 158,604 | 37.8 % | Use `periode_construction` instead (complete). |
| `surface_habitable_logement` | 10,266 | 2.4 % | Almost all are `immeuble` DPEs (10,197 of 10,241 have no surface). |
| `conso_5_usages_par_m2_ep` | 5 | < 0.01 % | The energy label is still present; no impact on F/G shares. |
| `emission_ges_5_usages_par_m2` | 5 | < 0.01 % | Same 5 records. |

## Corrected anomalies

**Municipality names (67 spellings for 40 INSEE codes).** Variants come from upper case (`STAINS`), abbreviations (`ST DENIS`, `ST OUEN`), missing spaces (`LesLilas`) and broken character encoding (`Ã pinay-sur-Seine`, `L'Ã le-Saint-Denis`). Fix: new column `commune` = the most frequent name for each `code_insee_ban`. Always group by `code_insee_ban` or `commune`, never by `nom_commune_ban`.

## Flagged anomalies

| Flag | Rows | Rule | Recommendation |
|---|---:|---|---|
| `flag_annee_incoherente` | 10,891 | `annee_construction` outside the bounds of `periode_construction`, or after the DPE year (e.g. 1664, 2028, or 1900 in period `2013-2021`) | Use `periode_construction` for Q3/H1. |
| `flag_mois_incomplet` | 1,185 | DPEs from the last month of the extraction (2026-11, up to the 11th) | Exclude from monthly series (Q5). |
| `flag_surface_aberrante` | 92 | Home (not `immeuble`) with a floor area under 9 m² or over 500 m² | Exclude from any floor-area analysis. |
| `flag_conso_aberrante` | 56 | Primary energy use over 1,000 kWh/m²/year (max 23,766) | Exclude from consumption averages; the label can stay in F/G shares. |

## Points to keep in mind

- **Energy label vs. consumption.** Since July 2021 the label is the worse of the energy and greenhouse-gas classes, and small homes have adjusted thresholds. Some G labels therefore have a low consumption value (minimum 51 kWh/m²/year). Do not recompute labels from consumption: use `etiquette_dpe` as provided.
- **`immeuble` DPEs (10,241).** These cover a whole building, not one home, and rarely have a floor area. Compare `maison` with `appartement` for Q2, and report `immeuble` separately.
- **Heating energy.** The `Électricité` category mixes direct electric heating and heat pumps. This field alone cannot separate them.
- **Repeated DPEs for one home.** The extraction contains no address, so repeated DPEs for the same home cannot be detected. Counts are DPE counts, not home counts.
