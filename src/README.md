# Research pipeline

Current election pilots use Python's standard library. The [Bavaria reproduction guide](../docs/feasibility/bavaria-feasibility.md#reproduction) documents pinned acquisition, structural screening and an independent historical-workbook audit. Outputs and source data remain local and ignored by Git.

The [operational Bavaria pilot](../docs/feasibility/bavaria-operational-pilot.md) adds pinned official-report extraction and a historical TED JSON acquisition and municipal buyer-linkage script. It preserves notice, lot and contract fields separately and excludes ongoing competitions from awarded tender-count outcomes. Python's standard library and Poppler's `pdftotext` are sufficient; the source-linkage tests run without downloads.

The historical register preserves nominations and anonymous candidate slots. Candidate names are recovered only from complete exact vote-vector matches; gender and actual terms are not inferred. Broader procurement cleaning and the main analysis remain conditional on measurement, coverage and precision checks.
