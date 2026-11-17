# Analytical Questions — DPE-Insight

## 1. Project context

DPE-Insight analyses energy performance certificates (DPEs, France's official certificate system) for existing homes in Seine-Saint-Denis (department 93). The study uses ADEME records for existing homes since July 2021.

The goal is to understand where the most energy-inefficient homes are recorded, which types of homes are most affected, and which characteristics are associated with poor energy performance. The findings should help identify municipalities and housing categories that may deserve priority in energy-renovation programs.

**Geographic scope:** Seine-Saint-Denis (93).

**Main source:** ADEME, Existing homes DPE records since July 2021.

## 2. Working definition of an energy-inefficient home

For this study, an energy-inefficient home is a DPE with an **energy label of F or G**. This definition refers to the energy label, not the greenhouse-gas label, and must be applied consistently across analyses and visualizations.

- **Labels A to E:** not classified as energy-inefficient under this project definition.
- **Labels F and G:** classified as energy-inefficient under this project definition.

Any relevant changes to DPE regulations or rating thresholds must be checked against ADEME documentation and recorded before comparing periods.

## 3. Main question

**Which municipalities and housing categories should the departmental housing service prioritize when directing energy-renovation support in Seine-Saint-Denis?**

## 4. Business questions

### Q1 — Geographic distribution

Where are F/G DPEs concentrated in the department, both by count and as a share of usable DPEs in each municipality?

We will examine two complementary measures:

- The number of F/G DPEs recorded in each municipality.
- The share of usable DPEs in that municipality that are rated F or G.

These measures answer different questions: a municipality can have many F/G diagnoses but a lower F/G share than a municipality with fewer diagnoses. DPE counts must not be treated as counts of unique homes.

### Q2 — Housing type

Does the share of F/G DPEs differ between detached houses and apartments?

The analysis will compare energy-label distributions by building type, with particular attention to the F/G share.

### Q3 — Construction period

How does the share of F/G DPEs vary by housing construction period?

The analysis will compare energy labels across construction periods and examine whether older homes are more frequently rated F or G.

### Q4 — Heating system

How do energy labels differ by primary heating energy?

The analysis will compare heating categories such as fuel oil, direct electric heating, gas, and heat pumps. Any observed association is descriptive and does not establish causation.

### Q5 — Change over time

How have the monthly number of DPEs and the share of F/G DPEs changed since July 2021?

The analysis will examine:

- Monthly DPE counts.
- The distribution of energy labels A to G by month.
- The monthly share of F/G DPEs.

Potential regulatory or methodological changes must be considered when interpreting trends.

## 5. Hypotheses to test

These hypotheses must be tested against the data; their outcomes are not known in advance.

- **H1 — Construction period:** Homes built before 1975 have a higher share of F/G DPEs than homes built from 1975 onward. (Q3)
- **H2 — Housing type:** The share of F/G DPEs differs between detached houses and apartments. (Q2)
- **H3 — Municipality counts and shares:** Municipalities with the highest number of F/G DPEs are not necessarily those with the highest F/G share. (Q1)

For each hypothesis, report whether the results support it, contradict it, or are inconclusive.

## 6. Indicators

- **Number of DPEs:** number of usable DPE records included in the analysis.
- **Number of F/G DPEs:** number of records with an energy label of F or G.
- **F/G share:** number of F/G DPEs divided by all usable DPEs in the group, multiplied by 100.
- **Energy-label distribution:** distribution of DPE records across labels A to G.
- **Geographic distribution:** F/G counts and shares by municipality.
- **Construction period:** DPE counts and F/G shares by construction period.
- **Building type:** comparison of DPE counts and F/G shares for houses and apartments.
- **Primary heating energy:** comparison of DPE counts and F/G shares by heating-energy category.
- **Monthly trend:** DPE counts and F/G shares by month.

**Formula:**

`F/G share (%) = (number of usable DPEs rated F or G / total usable DPEs in the group) × 100`

Comparisons between municipalities may also require a normalized indicator, such as a rate relative to the number of main residences, using a join with an INSEE municipality reference table. The join key, unmatched records, and data quality must be checked and documented.

## 7. Interpretation limits

- The data describe recorded diagnoses and do not necessarily represent the department's full housing stock.
- A home may have more than one DPE; diagnosis counts must not automatically be interpreted as unique-home counts.
- Some variables may be missing. Missingness and any exclusions must be quantified and documented.
- Floor areas and energy-consumption values may contain outliers. Any treatment must be justified and recorded in `docs/anomalies.md`.
- DPE rules, rating thresholds, and methods may change over time; check the ADEME technical documentation before comparing periods.
- An association between a housing characteristic and a poor energy label does not prove causality.
- Changes in recorded DPEs do not by themselves show that the actual housing stock is improving or worsening.

## 8. Study purpose

The analysis should provide a clear, documented picture of energy-inefficient DPEs recorded in Seine-Saint-Denis, their geographic distribution, and the housing characteristics associated with them. The findings are intended to inform the departmental housing service as it considers where to direct renovation support.
