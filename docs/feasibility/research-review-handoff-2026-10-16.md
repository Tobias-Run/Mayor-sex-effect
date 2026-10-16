# Review and completion handoff — 16 October 2026

The active contribution is the [English feasibility manuscript v0.2](../../manuscript/feasibility-2026-10-16/manuscript.md), supported by the [28-claim internal audit](manuscript-v02-claim-review-2026-10-16.md), [Hesse access/rights assessment](hesse-replication-audit-2026-10-16.md) and [selection diagnostics](selection-and-attrition-2026-10-16.md). This handoff records actual status, rather than accepting the report on the owner's behalf.

| Task | Status and evidence | Completion requirement |
| --- | --- | --- |
| Internal source/claim accounting | Complete within the 28-claim scope; no numerical correction found | New evidence requires a dated correction/version record |
| Public reproduction | Fresh public clone rebuilds Markdown, facts and selection tables identically; offline tests run without originals | Preserve source pins and distinguish private-only tests |
| Automated public checks | Read-only GitHub workflow added; verify its actual run separately | A green workflow validates software/accounting, not identification or original coding |
| Independent coding | Open; no reviewer assigned or coding returned | Review current thirteen-pair packet; freeze return before key release; retain prior-exposure declarations and disagreements |
| Substantive research review | Open | Assess estimand, institutional transfer, source population, selection interpretation and precision limits; record limitations and revisions |
| Completed-report decision | Open | Explicitly accept/revise the feasibility contribution after review; do not infer acceptance from a build or passing tests |
| GitHub Pages companion | Deferred | Only after research completion; reproduce feasibility findings without exposing private originals or implying causal estimates |
| Causal main-study reopening | No launch under audited protocols | All P5 gates: complete source-pinned cohort, demonstrated joint yield, validated population/windows/coverage, independent review and useful design-specific precision |

The independent-coding packet and first-coder key remain separate, ignored local records. The public repository supplies the [current-cohort protocol](current-cohort-independent-coding-protocol.md), not those private files. Review all six provisional links and the seven selected controls; this is not a random full-frame error-rate audit. Candidate names/administrative fields from a newly accessible archive must not silently overwrite historical public-presentation coding.

The Hesse archive has identifiable files but unresolved payload access and custom-license conditions. This is a conditional source lead, not an instruction to contact authors, create an account, accept restricted terms, publish original data or restart case-by-case collection. The existing latest-election workbook supplies no verified opponent fields. No new reviewer recruitment or outreach has been undertaken.

## Public verification

```sh
python -m pip install -r analysis/requirements-feasibility.txt
python src/report/verify_public_checkpoints.py
python src/report/build_feasibility_update.py
python src/report/audit_feasibility_selection.py
python -m unittest discover -s tests -v
```

The [workflow](../../.github/workflows/public-research-checks.yml) uses Python 3.12 and pinned numerical package versions, read-only repository permissions and no deployment step. It checks published pins, deterministic text/accounting outputs and the offline suite. The private-packet test is expected to skip in a clean public clone; local execution with the packet can run it. PDF byte hashes are verified, but the workflow does not render a new PDF or certify typography across software environments. It does not redownload mutable websites or validate original data rights.

The standalone v0.1 report and v0.2 manuscript retain their published inputs and procurement cutoff. No extra observations, treatment effects or independently certified main-study cases are claimed by this handoff.
