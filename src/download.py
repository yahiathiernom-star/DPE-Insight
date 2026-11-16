"""Download a reproducible, department-level snapshot of ADEME DPE records."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://data.ademe.fr/data-fair/api/v1/datasets/dpe03existant/lines"
DEPARTMENT = "93"
PAGE_SIZE = 10_000
FIELDS = [
    "numero_dpe",
    "date_etablissement_dpe",
    "etiquette_dpe",
    "etiquette_ges",
    "conso_5_usages_par_m2_ep",
    "emission_ges_5_usages_par_m2",
    "surface_habitable_logement",
    "annee_construction",
    "periode_construction",
    "type_batiment",
    "type_energie_principale_chauffage",
    "code_departement_ban",
    "code_insee_ban",
    "nom_commune_ban",
]
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "data" / "raw" / "dpe_93.csv.gz"


def fetch_page(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "DPE-Insight student project"})
    try:
        with urlopen(request, timeout=120) as response:
            return json.load(response)
    except Exception as error:
        # On some local Python installations the system CA bundle is available
        # to curl but not to Python's ssl module. Keep certificate verification
        # enabled by falling back to the system HTTP client.
        if "CERTIFICATE_VERIFY_FAILED" not in str(error):
            raise
        response = subprocess.run(
            ["curl", "--fail", "--silent", "--show-error", "--max-time", "120", url],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(response.stdout)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download(output: Path, limit: int | None = None) -> tuple[int, str]:
    output.parent.mkdir(parents=True, exist_ok=True)
    query = {
        "code_departement_ban_eq": DEPARTMENT,
        "select": ",".join(FIELDS),
        "size": min(limit, PAGE_SIZE) if limit else PAGE_SIZE,
        "count": "exact",
    }
    url = f"{API_URL}?{urlencode(query)}"
    total_expected: int | None = None
    rows_written = 0
    fd, temp_name = tempfile.mkstemp(prefix="dpe_93_", suffix=".csv.gz", dir=output.parent)
    os.close(fd)
    temp_path = Path(temp_name)

    try:
        with gzip.open(temp_path, "wt", encoding="utf-8", newline="") as compressed:
            writer = csv.DictWriter(compressed, fieldnames=FIELDS, extrasaction="ignore")
            writer.writeheader()
            while url and (limit is None or rows_written < limit):
                page = fetch_page(url)
                if total_expected is None:
                    total_expected = page.get("total")
                results = page.get("results", [])
                if not results:
                    break
                if any(str(row.get("code_departement_ban", "")) != DEPARTMENT for row in results):
                    raise ValueError("L’API a renvoyé une ligne hors du département 93.")
                if limit is not None:
                    results = results[: limit - rows_written]
                writer.writerows(results)
                rows_written += len(results)
                print(f"{rows_written:,} lignes récupérées", flush=True)
                url = page.get("next", "") if limit is None or rows_written < limit else ""

        if not rows_written:
            raise RuntimeError("L’API n’a renvoyé aucune ligne pour le département 93.")
        temp_path.replace(output)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    return rows_written, sha256(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Chemin du CSV gzip de sortie")
    parser.add_argument("--limit", type=int, help="Limiter le nombre de lignes (utile pour un essai rapide)")
    args = parser.parse_args()

    if args.limit is not None and args.limit <= 0:
        parser.error("--limit doit être supérieur à zéro")

    rows, digest = download(args.output, args.limit)
    manifest = {
        "source": API_URL,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "department_code": DEPARTMENT,
        "rows": rows,
        "complete_snapshot": args.limit is None,
        "columns": FIELDS,
        "sha256_gzip": digest,
    }
    basename = args.output.name.removesuffix(".csv.gz")
    manifest_path = args.output.with_name(f"{basename}_manifest.json")
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Fichier : {args.output}")
    print(f"Manifest : {manifest_path}")
    print(f"SHA-256 : {digest}")


if __name__ == "__main__":
    main()
