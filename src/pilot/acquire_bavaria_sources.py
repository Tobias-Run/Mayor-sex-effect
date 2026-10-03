"""Retrieve pinned public source copies into ignored local storage.

Run from repo root: python src/pilot/acquire_bavaria_sources.py
Uses only the Python standard library; downloads about 30 MB on a fresh run.
Retrieval does not establish permission to redistribute the source records.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

COMMIT = "030c1fb865ec4e6ef94d5dee2039edde081a0f5d"
ROOT = Path("data/raw/gerda")
BASE = "https://media.githubusercontent.com/media/awiedem/german_election_data/" + COMMIT
SOURCES = [
    ("mayoral_candidates.csv", "/data/mayoral_elections/final/mayoral_candidates.csv",
     "5cf7c8f7695cf17d3001ffe49ba5bb5a8f2800be8426754c1db3143b200fba0e", "retrieval.json"),
    ("bavaria-historical.xlsx", "/data/mayoral_elections/raw/bayern/20251114_Wahlen_seit_1945.xlsx",
     "7ba6aac1381496b3beed2bbd1d0f68209942026b7f9234af8cf1d914c81396a3", "bavaria-historical-retrieval.json"),
]


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    for filename, remote_path, expected, manifest_name in SOURCES:
        path = ROOT / filename
        if path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError(f"Existing {path} differs; preserve it and investigate before replacement")
            # Preserve the original retrieval date when its manifest already exists.
            if (ROOT / manifest_name).exists():
                manifest = json.loads((ROOT / manifest_name).read_text())
                if manifest["sha256"] != expected or manifest["url"] != BASE + remote_path:
                    raise ValueError(f"Existing manifest for {path} disagrees with the pinned source")
                print(f"Verified existing {path}")
                continue
            acquisition = "existing_local_file_verified; original retrieval time unknown"
        else:
            with urlopen(BASE + remote_path, timeout=60) as response:
                data = response.read()
            if hashlib.sha256(data).hexdigest() != expected:
                raise ValueError(f"Downloaded {filename} checksum disagrees with pinned source")
            path.write_bytes(data)
            acquisition = "downloaded"
        metadata = {"commit": COMMIT, "url": BASE + remote_path, "sha256": expected,
                    "bytes": path.stat().st_size, "verified_at_utc": datetime.now(timezone.utc).isoformat(),
                    "acquisition": acquisition,
                    "distribution": "GERDA public source copy; redistribution rights not established"}
        (ROOT / manifest_name).write_text(json.dumps(metadata, indent=2))
        print(f"Verified {path}: {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
