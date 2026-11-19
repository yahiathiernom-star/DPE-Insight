"""Nettoyage de l'extraction ADEME des DPE logements existants du 93.

Principe : aucune ligne n'est supprimée. Les valeurs douteuses sont signalées
par des colonnes ``flag_*`` pour que chaque analyse décide de les exclure ou non.
Les choix sont expliqués dans docs/decisions.md et docs/anomalies.md.

Usage :
    python src/cleaning.py
    python src/cleaning.py --input data/raw/dpe_93_sample.csv.gz --output data/processed/dpe_93_sample_clean.csv.gz
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "raw" / "dpe_93.csv.gz"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "dpe_93_clean.csv.gz"

LABELS = ["A", "B", "C", "D", "E", "F", "G"]
PASSOIRE_LABELS = {"F", "G"}

# Périodes ADEME, dans l'ordre chronologique, avec leurs bornes en années.
PERIODES = {
    "avant 1948": (None, 1947),
    "1948-1974": (1948, 1974),
    "1975-1977": (1975, 1977),
    "1978-1982": (1978, 1982),
    "1983-1988": (1983, 1988),
    "1989-2000": (1989, 2000),
    "2001-2005": (2001, 2005),
    "2006-2012": (2006, 2012),
    "2013-2021": (2013, 2021),
    "après 2021": (2022, None),
}
# H1 : logements construits avant la première réglementation thermique (1974).
PERIODES_AVANT_1975 = {"avant 1948", "1948-1974"}

ENERGIE_GROUPES = {
    "Gaz naturel": "Gaz naturel",
    "Réseau de Chauffage urbain": "Réseau de chaleur",
    "Électricité": "Électricité",
    "Électricité d'origine renouvelable utilisée dans le bâtiment": "Électricité",
    "Fioul domestique": "Fioul",
    "GPL": "GPL / propane",
    "Propane": "GPL / propane",
    "Bois – Bûches": "Bois",
    "Bois – Granulés (pellets) ou briquettes": "Bois",
    "Bois – Plaquettes forestières": "Bois",
    "Bois – Plaquettes d’industrie": "Bois",
    "Charbon": "Autre",
}

# Seuils de valeurs aberrantes (voir docs/anomalies.md).
CONSO_MAX = 1000  # kWh EP/m²/an
SURFACE_MIN = 9  # m², surface minimale d'un logement décent
SURFACE_MAX = 500  # m², pour un logement (hors DPE « immeuble »)

NUMERIC_COLUMNS = [
    "conso_5_usages_par_m2_ep",
    "emission_ges_5_usages_par_m2",
    "surface_habitable_logement",
    "annee_construction",
]


def load_raw(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        dtype={"numero_dpe": str, "code_insee_ban": str, "code_departement_ban": str},
    )


def check_scope(df: pd.DataFrame) -> pd.DataFrame:
    """Vérifie les contraintes qui, si elles cassent, invalident toute l'analyse."""
    if df["numero_dpe"].duplicated().any():
        raise ValueError("Des numéros de DPE sont en double.")
    if (df["code_departement_ban"] != "93").any():
        raise ValueError("Des DPE hors du département 93 sont présents.")
    unknown = set(df["etiquette_dpe"].dropna()) - set(LABELS)
    if unknown:
        raise ValueError(f"Étiquettes DPE inattendues : {sorted(unknown)}")
    return df


def clean_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date_etablissement_dpe"] = pd.to_datetime(df["date_etablissement_dpe"], errors="raise")
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df["annee_construction"] = df["annee_construction"].astype("Int64")
    df["etiquette_dpe"] = pd.Categorical(df["etiquette_dpe"], categories=LABELS, ordered=True)
    df["etiquette_ges"] = pd.Categorical(df["etiquette_ges"], categories=LABELS, ordered=True)
    df["periode_construction"] = pd.Categorical(
        df["periode_construction"], categories=list(PERIODES), ordered=True
    )
    return df


def normalize_communes(df: pd.DataFrame) -> pd.DataFrame:
    """Un seul nom par code INSEE : le libellé le plus fréquent pour ce code.

    Les variantes viennent de majuscules, d'abréviations (« ST DENIS ») et de
    problèmes d'encodage (« Ã pinay-sur-Seine »). Le code INSEE fait foi.
    """
    df = df.copy()
    canonical = df.groupby("code_insee_ban")["nom_commune_ban"].agg(lambda s: s.value_counts().index[0])
    df["commune"] = df["code_insee_ban"].map(canonical)
    return df


def add_analysis_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["passoire"] = df["etiquette_dpe"].isin(PASSOIRE_LABELS)
    df["mois"] = df["date_etablissement_dpe"].dt.to_period("M").astype(str)
    df["annee_dpe"] = df["date_etablissement_dpe"].dt.year
    df["avant_1975"] = df["periode_construction"].isin(PERIODES_AVANT_1975)
    df["energie_chauffage"] = (
        df["type_energie_principale_chauffage"].map(ENERGIE_GROUPES).fillna("Non renseigné")
    )
    return df


def _annee_hors_periode(df: pd.DataFrame) -> pd.Series:
    bounds = df["periode_construction"].astype(str).map(PERIODES)
    low = bounds.map(lambda b: b[0] if isinstance(b, tuple) and b[0] is not None else -10_000)
    high = bounds.map(lambda b: b[1] if isinstance(b, tuple) and b[1] is not None else 10_000)
    year = df["annee_construction"]
    outside = (year < low) | (year > high) | (year > df["annee_dpe"])
    return outside.fillna(False).astype(bool)


def add_quality_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    logement = df["type_batiment"] != "immeuble"
    surface = df["surface_habitable_logement"]

    df["flag_conso_aberrante"] = (df["conso_5_usages_par_m2_ep"] > CONSO_MAX).fillna(False)
    df["flag_surface_aberrante"] = (logement & ((surface < SURFACE_MIN) | (surface > SURFACE_MAX))).fillna(False)
    df["flag_annee_incoherente"] = _annee_hors_periode(df)
    # Le dernier mois de l'extraction n'est pas complet : à exclure des séries mensuelles.
    df["flag_mois_incomplet"] = df["mois"] == df["mois"].max()
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = check_scope(df)
    df = clean_types(df)
    df = normalize_communes(df)
    df = add_analysis_columns(df)
    df = add_quality_flags(df)
    return df


def quality_report(raw: pd.DataFrame, cleaned: pd.DataFrame) -> dict:
    flags = [c for c in cleaned.columns if c.startswith("flag_")]
    return {
        "lignes_brutes": len(raw),
        "lignes_nettoyees": len(cleaned),
        "valeurs_manquantes": {k: int(v) for k, v in cleaned[raw.columns].isna().sum().items() if v},
        "flags": {f: int(cleaned[f].sum()) for f in flags},
        "variantes_noms_communes": int(raw["nom_commune_ban"].nunique() - cleaned["commune"].nunique()),
        "communes": int(cleaned["commune"].nunique()),
        "periode_dpe": [
            cleaned["date_etablissement_dpe"].min().date().isoformat(),
            cleaned["date_etablissement_dpe"].max().date().isoformat(),
        ],
        "part_passoires_pct": round(100 * cleaned["passoire"].mean(), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if not args.input.exists():
        parser.error(f"{args.input} introuvable. Lancez d'abord : python src/download.py")

    raw = load_raw(args.input)
    cleaned = clean(raw)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(args.output, index=False, compression="gzip")
    report = quality_report(raw, cleaned)
    report_path = args.output.with_name(args.output.name.removesuffix(".csv.gz") + "_report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Fichier : {args.output}")
    print(f"Rapport : {report_path}")


if __name__ == "__main__":
    main()
