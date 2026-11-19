# Anomaly log — DPE-Insight

**Snapshot:** `data/raw/dpe_93.csv.gz`, retrieved on 2026-11-18 from the ADEME API (SHA-256 in `dpe_93_manifest.json`). It holds 419,164 DPEs dated 2021-07-01 to 2026-11-11.

**Source of the counts:** `src/cleaning.py` and its report `data/processed/dpe_93_clean_report.json`. Shares are given out of 419,164 rows.

**General rule:** no row is deleted. Each anomaly is either corrected in a new column (the raw column is kept) or flagged in a `flag_*` column. Each analysis states which flags it excludes.

## Summary of the minimum checks

| Check (specification, section 8) | Result | Entries |
|---|---|---|
| 1. Exact and functional duplicates | 0 duplicate `numero_dpe`, 0 duplicate rows; functional duplicates cannot be detected | ANO-10 |
| 2. Missing values, including disguised ones | 4 columns with missing values; 2 disguised codes | ANO-02, ANO-04, ANO-07, ANO-08 |
| 3. Inconsistent types | Dates parsed with no error; INSEE codes read as text (leading zero kept); municipality names corrected | ANO-01 |
| 4. Out-of-range values or outliers | Business thresholds on year, floor area and consumption | ANO-03, ANO-05, ANO-06, ANO-11 |
| 5. Series breaks | 2 regulatory changes during the period | ANO-12, ANO-13 |
| 6. Coverage | Partial first and last months; municipalities with few DPEs | ANO-14 |
| Other | Building-level DPEs; mixed heating category | ANO-09, ANO-15 |

---

### ANO-01 — Several spellings for one municipality

- **Column(s):** `nom_commune_ban`
- **Description:** 67 spellings for 40 INSEE codes. Examples: `STAINS`, `ST DENIS`, `LesLilas`, `Ã pinay-sur-Seine`, `L'Ã le-Saint-Denis`.
- **Extent:** 1,655 rows (0.39 %), including 322 with broken encoding.
- **Probable cause:** free-text entry by the diagnostician and a character-encoding error.
- **Treatment:** **corrected**. The new column `commune` holds the most frequent name for each `code_insee_ban`. The INSEE code is reliable (40 codes, all in department 93).
- **Impact:** without the fix, municipality counts (Q1) would be split across several lines. Always group by `code_insee_ban` or `commune`.

### ANO-02 — Construction year often missing

- **Column(s):** `annee_construction`
- **Description:** empty value.
- **Extent:** 158,604 rows (37.84 %).
- **Probable cause:** optional field; the diagnostician often enters only the period.
- **Treatment:** **kept**. Analyses use `periode_construction`, which is always filled in.
- **Impact:** Q3 and H1 rely on the period. No analysis by exact year.

### ANO-03 — Construction year inconsistent with the period

- **Column(s):** `annee_construction`, `periode_construction`
- **Description:** year outside the bounds of the period, or after the DPE date. Examples: 1664 (6 rows before 1700), 2028, 1900 in period `2013-2021`.
- **Extent:** 10,891 rows (2.60 %).
- **Probable cause:** entry error, or a default value.
- **Treatment:** **flagged** (`flag_annee_incoherente`). The period is kept as the reference.
- **Impact:** none on Q3/H1, which use the period.

### ANO-04 — Floor area missing

- **Column(s):** `surface_habitable_logement`
- **Description:** empty value.
- **Extent:** 10,266 rows (2.45 %). Of these, 10,197 are `immeuble` DPEs (see ANO-09) and 69 are homes.
- **Probable cause:** a building-level DPE has no single home floor area.
- **Treatment:** **kept**, no imputation.
- **Impact:** only floor-area analyses (ANO-12, small homes); no impact on F/G shares.

### ANO-05 — Outlier floor areas

- **Column(s):** `surface_habitable_logement`
- **Description:** home under 9 m² or over 500 m² (minimum 3 m², maximum 6,284 m² for an apartment).
- **Extent:** 92 rows (0.02 %).
- **Probable cause:** entry error (unit or extra digit), or a whole building entered as one home.
- **Treatment:** **flagged** (`flag_surface_aberrante`). Business threshold: 9 m² is the minimum floor area of a decent home in France; 500 m² is well above the 99.9th percentile (252 m²). `immeuble` DPEs are not checked.
- **Impact:** exclude from floor-area analyses. The label stays usable for F/G shares.

### ANO-06 — Outlier energy consumption

- **Column(s):** `conso_5_usages_par_m2_ep`
- **Description:** primary energy use over 1,000 kWh/m²/year (maximum 23,766).
- **Extent:** 56 rows (0.01 %).
- **Probable cause:** entry error, or a floor area that is too small in the calculation.
- **Treatment:** **flagged** (`flag_conso_aberrante`). The threshold is well above the 99.9th percentile (798 kWh/m²/year).
- **Impact:** exclude from consumption averages. Use the median, which is robust to these values.

### ANO-07 — Consumption and emissions missing

- **Column(s):** `conso_5_usages_par_m2_ep`, `emission_ges_5_usages_par_m2`
- **Description:** empty value in both columns, for the same records.
- **Extent:** 5 rows (< 0.01 %).
- **Probable cause:** incomplete record sent to ADEME.
- **Treatment:** **kept**. The energy label is present.
- **Impact:** negligible.

### ANO-08 — Disguised missing values

- **Column(s):** `type_energie_principale_chauffage`, `emission_ges_5_usages_par_m2`
- **Description:** heating energy `Non affecté` (11 rows); emissions equal to 0 (3 rows). No empty strings or `-1` codes were found in other columns.
- **Extent:** 14 rows (< 0.01 %).
- **Probable cause:** a default value instead of a real entry.
- **Treatment:** `Non affecté` is grouped as `Non renseigné` in `energie_chauffage`; zero emissions are kept.
- **Impact:** negligible. The `Non renseigné` category is too small to interpret.

### ANO-09 — Building-level DPEs (`immeuble`)

- **Column(s):** `type_batiment`
- **Description:** DPE covering a whole building, not one home.
- **Extent:** 10,241 rows (2.44 %).
- **Probable cause:** a different kind of diagnosis, published in the same dataset.
- **Treatment:** **kept**.
- **Impact:** Q2 and H2 compare `maison` with `appartement`. `immeuble` is reported separately and never added to home counts.

### ANO-10 — Functional duplicates (several DPEs for one home)

- **Column(s):** none available
- **Description:** a home may be diagnosed again (new sale, rental, correction).
- **Extent:** unknown. The extract has no address or home identifier, by choice (personal data).
- **Probable cause:** how the DPE system works.
- **Treatment:** **not treated, documented**.
- **Impact:** every count is a number of **DPEs**, not of homes. Stated in the README and dashboard limits.

### ANO-11 — G label with low consumption

- **Column(s):** `etiquette_dpe`, `conso_5_usages_par_m2_ep`
- **Description:** some G labels have consumption below the usual G threshold. Example: 51 kWh/m²/year.
- **Extent:** 122 G labels at or below 330 kWh/m²/year (0.03 %).
- **Probable cause:** since July 2021, the label is the worse of the energy and greenhouse-gas classes. We checked that no energy label is better than its GHG label. Small homes also have adjusted thresholds (ANO-12).
- **Treatment:** **kept**. The label is never recomputed from consumption.
- **Impact:** none. The project definition relies on `etiquette_dpe`.

### ANO-12 — Series break: small-home thresholds (July 2024)

- **Column(s):** `etiquette_dpe`, `date_etablissement_dpe`, `surface_habitable_logement`
- **Description:** the F/G share of homes under 40 m² falls from 16.2 % (July 2021–June 2024) to 12.7 % (July 2024–December 2025). Over the same periods, homes of 40 m² or more go from 8.8 % to 7.5 %.
- **Extent:** 85,892 DPEs under 40 m² (20.49 %).
- **Probable cause:** label thresholds for small homes were adjusted from 1 July 2024. To confirm in the ADEME documentation.
- **Treatment:** **documented**. Q5 marks this date on time charts.
- **Impact:** part of the F/G decrease after July 2024 may come from the rule change, not from renovations. Interpret the trend in H4 with caution.

### ANO-13 — Series break: electricity conversion factor (January 2026)

- **Column(s):** `etiquette_dpe`, `conso_5_usages_par_m2_ep`, `date_etablissement_dpe`
- **Description:** the primary energy factor for electricity was lowered at the start of 2026. In the data, the F/G share of electrically heated homes goes from 13.3 % (before 2026) to 14.3 % (2026).
- **Extent:** 15,566 electrically heated DPEs dated 2026.
- **Probable cause:** regulatory change. To confirm in the ADEME documentation. Its expected effect (better labels for electric homes) does not show in the raw numbers, so other factors may be involved (which homes get diagnosed).
- **Treatment:** **documented**. Q4 and Q5 compare the periods before and after 2026 separately.
- **Impact:** comparisons of electric homes across 2026 are not fully comparable.

### ANO-14 — Partial coverage at the start and end of the period, and small municipalities

- **Column(s):** `date_etablissement_dpe`, `code_insee_ban`
- **Description:** July 2021 has 868 DPEs and August 2021 has 763, against a median of 6,297 per month. November 2026 stops on the 11th. Three municipalities have fewer than 2,000 DPEs (Coubron 715, Gournay-sur-Marne 1,122, Vaujours 1,649).
- **Extent:** 1,185 rows in the incomplete month (0.28 %).
- **Probable cause:** gradual start of the new DPE in July 2021; extraction date; municipality size.
- **Treatment:** the last month is **flagged** (`flag_mois_incomplet`). The first months are kept but commented on.
- **Impact:** exclude the last month from monthly series (Q5). Show counts next to F/G shares for small municipalities (Q1).

### ANO-15 — The `Électricité` category mixes heating systems

- **Column(s):** `type_energie_principale_chauffage`
- **Description:** `Électricité` covers both direct electric heating and heat pumps.
- **Extent:** 103,026 rows (24.58 %) in `energie_chauffage = Électricité`.
- **Probable cause:** this field describes the energy, not the heating equipment.
- **Treatment:** **documented**. Heating energies are grouped in `energie_chauffage`.
- **Impact:** a hypothesis comparing direct electric heating with heat pumps cannot be tested with this field. Compare by energy: fuel oil, electricity, gas, heat network.

## Interpretation limits (not anomalies)

- **DPEs are not a representative sample of the housing stock.** They are mostly carried out for sales and rentals.
- **An association between a characteristic and a poor label does not prove causation.**
- **Fewer F/G DPEs over time does not prove the housing stock is improving.** See ANO-12 and ANO-13.
