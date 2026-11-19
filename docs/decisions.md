# Decisions — DPE-Insight

## 2026-11-18 — Data cleaning (`src/cleaning.py`)

Run it after the download:

```bash
python src/cleaning.py
```

Output: `data/processed/dpe_93_clean.csv.gz` (one row per DPE) and `dpe_93_clean_report.json` (row counts, missing values, flags).

| Decision | Reason |
|---|---|
| Keep every row and add `flag_*` columns instead of deleting rows | Exclusions depend on the question: a record with an absurd floor area still has a valid label for F/G shares. Each analysis states which flags it excludes. |
| Usable DPE = any record with a label A–G in department 93 | All 419,164 records meet this condition. |
| `passoire` = energy label F or G (`etiquette_dpe`), not the GHG label | Project definition (see `questions.md`). |
| Municipality name taken from the INSEE code (`commune`) | 67 spellings exist for 40 municipalities. See `anomalies.md`. |
| Use `periode_construction`, not `annee_construction` | The period is complete; the year is missing for 38 % of records and contradicts the period for 10,891. |
| `avant_1975` = periods `avant 1948` and `1948-1974` | H1 threshold: the first French thermal regulation dates from 1974. |
| Heating energy grouped into `energie_chauffage` (gas, heat network, electricity, fuel oil, LPG/propane, wood, other, missing) | Several raw categories have fewer than 20 records. |
| Outlier thresholds: consumption > 1,000 kWh/m²/year; home floor area < 9 m² or > 500 m² | 9 m² is the minimum floor area for a decent home in France. The other thresholds sit well above the 99.9th percentile. |
| The last, incomplete month is flagged (`flag_mois_incomplet`) | Prevents a false drop at the end of monthly series. |

## Open points for the team

- **Hypotheses differ between documents.** `questions.md` has H1 (before/after 1975), H2 (houses vs. apartments) and H3 (municipality count vs. share). The team brief also lists a heating hypothesis (fuel oil / direct electric vs. gas / heat pump) and a trend hypothesis (F/G share decreasing since July 2021). Pick one list and update `questions.md`.
- **Heating hypothesis.** `type_energie_principale_chauffage` does not separate direct electric heating from heat pumps: both are `Électricité`. Testing this as worded requires an extra ADEME field such as the heating generator type, which means changing `download.py` and downloading again.
- **Regulatory changes for Q5.** Check the ADEME documentation for label rule changes during the period, for example the adjusted thresholds for small homes and the change to the electricity conversion factor. They can move F/G shares without any change to the homes themselves.
