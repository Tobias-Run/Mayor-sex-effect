# Data management and reproducibility

## Storage and publication

Keep raw, interim, and processed research records under `data/`; these files are ignored by Git. Keep generated local results under `outputs/`, also ignored. Preserve original raw files and derive cleaned versions through documented code. Restricted research environments may require different storage arrangements.

Do not commit credentials, confidential records, or personally identifying research datasets. Candidate information being public does not by itself settle redistribution rights. Check provider terms and disclosure requirements before releasing datasets or website assets.

## Provenance

For every source record provider, URL, retrieval date, data vintage, access conditions, license, checksum where useful, geographic and temporal coverage, identifiers, and transformations. Keep a source manifest without restricted record-level content.

## Planned identifiers and linkage

An election register should document municipality identifier and territorial vintage, state, election and round dates, decisive-round eligibility, candidate source information, vote counts and shares, margin, winner, and actual term dates. Do not infer gender from a first name alone; document the source and treatment of uncertain records.

Procurement records require source record and lot identifiers, buyer identity, award-related dates, procedure and outcome definitions, and municipal responsibility. Keep a buyer mapping with match method, supporting evidence, and unresolved ambiguity. Document boundary changes, joint procurement bodies, and municipal companies.

## Reproducible execution

Select and pin the analysis environment when implementation starts. Document acquisition separately from transformations and estimation. Record seeds for simulation, code version, data vintage, and execution commands. If data cannot be distributed, provide permissible code, metadata, and access instructions. Synthetic examples must be visibly labeled and must never be presented as research evidence.
