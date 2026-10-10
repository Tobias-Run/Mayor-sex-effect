# Manuscript and report reproduction

**Version 0.1, 9 October 2026 — draft for review. Evidence frozen on 5 October 2026.** Read the [English report](feasibility-report.md) or [PDF](feasibility-report.pdf): *Can German Municipal Data Support a Female-Mayor Procurement Study? A Bounded Feasibility Audit in NRW and Bavaria.* It prominently attributes the Italian adaptation to Florio and Spagnolo (2026), cites the German precedents and preserves their edition/access limits.

**10 October checkpoint:** the [internal claim/interpretation review](report-quality-review-2026-10-10.md) finds no blocking inconsistency in the inspected frozen artifacts. A portable local reviewer handoff contains 28 cases, 56 blank forms and 96 hash-verified originals, without the first-coder key. The report's ten output hashes remain unchanged. This is preparation and first-coder quality control, not independent review; the current combined suite has 160 passing tests without skips.

The [bounded no-go decision](../docs/feasibility/go-adapt-stop.md) governs the present causal launch. This report contains source and design-feasibility findings, with no procurement-effect estimate or null-effect conclusion. Independent second coding is uncompleted; no reviewer is assigned. Substantive review and an explicit completed-report decision remain open. GitHub Pages stays deferred until research completion.

| Artifact | Purpose |
| --- | --- |
| [Authored template](feasibility-report.template.md) | English prose, references and fact placeholders; edit this rather than the generated report |
| [Input manifest](report-inputs.json) | Byte sizes and SHA-256 hashes for 22 public evidence artifacts, cutoff and evidence commit |
| [Fact ledger](report-facts.json) | Reconciled counts, generated tables and chart values |
| [Sample flow](figures/sample-flow.svg) | Separate state-specific election/procurement intersections; also available as PDF/PNG |
| [Precision benchmark](figures/precision-benchmark.svg) · [chart data](figures/precision-data.csv) | Hypothetical-SD Gaussian planning scenarios, not RDD power or effects; also PDF/PNG |
| [Build checkpoint](report-reproduction-checkpoint.json) | Input checks, output hashes and Python/plot/PDF software versions |
| [Verification record](report-verification.json) | Offline tests, public-input-only rebuild comparison and PDF inspection scope |

From the repository root:

```sh
python -m pip install -r analysis/requirements-report.txt
python src/report/build_feasibility_report.py
python -m unittest discover -s tests
```

The report builder uses public artifacts only, without downloads or person-level files. A changed input fails its pin check and requires an explicit evidence/version review. `--facts-only` generates the fact ledger and Markdown without figures; it is not a full visual reproduction. `--pdf` exports the standalone report and requires Pandoc, XeLaTeX, the TeX `needspace` package and DejaVu fonts. The numerical benchmark's tests additionally require [analysis/requirements-feasibility.txt](../analysis/requirements-feasibility.txt). Optional-dependency skips must be reported rather than described as completed numerical validation.

After a `--pdf` build, run `python src/report/verify_feasibility_report.py` with Poppler installed. It copies only the pinned public inputs and report sources into a temporary directory, rebuilds, compares output bytes, runs the offline suite and checks PDF/table/link integrity. Pass `--visual-reviewed-pages` only for PDF pages actually inspected. The recorded byte-identical comparison uses the same installed software/fonts; it is not a cross-platform guarantee. The checkpoint's check timestamp can differ. The report PDF's content-derived file identifier removes temporary-path variation without changing its objects or offsets.

Reproduction means the report's stated inputs, tables and figures can be regenerated. It does not independently validate every original extraction, resolve data rights, or complete the missing candidate review. Original publications, person annotations and reviewer keys stay local. The original German pitch is in `sources/project/`.
