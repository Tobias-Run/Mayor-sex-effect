# Feasibility manuscript v0.2 — 16 October 2026

[Read the manuscript](manuscript.md) · [Download PDF](manuscript.pdf). *From Close Elections to Procurement Outcomes: A Bounded German Feasibility Audit Adapting Florio and Spagnolo (2026).* **Review draft, not a completed or independently validated study.**

This separate synthesis incorporates P1–P5 through 15 October, at evidence commit `aa70a89c31afa33003711fa5688db1ab4fb67e3f`. Procurement observations retain the **30 September 2026** cutoff. The original [v0.1 report](../feasibility-report.md) and its 5 October evidence cutoff remain frozen.

The [input manifest](inputs.json) pins thirteen public artifacts by size and SHA-256. The [fact ledger](facts.json) reconciles 176 bookkeeping events/159 municipalities, six provisional links, twenty procedures, seventeen statistics and zero certified cases. The builder checks procedure/statistic denominators, duplicate event keys and window-alignment counts, then renders the three manuscript tables from public CSVs. No downloads or private files are required.

From the repository root:

```sh
python src/report/build_feasibility_update.py
python -m unittest discover -s tests
pandoc manuscript/feasibility-2026-10-16/manuscript.md --standalone --pdf-engine=xelatex -V geometry:margin=22mm -V fontsize=10pt -V mainfont='DejaVu Serif' -V monofont='DejaVu Sans Mono' -V colorlinks=true -o manuscript/feasibility-2026-10-16/manuscript.pdf
```

Edit the [authored template](manuscript.template.md), then rebuild. The Markdown/accounting builder uses Python's standard library; PDF export additionally needs Pandoc, XeLaTeX and the named fonts. Numerical tests elsewhere in the repository require the existing feasibility dependencies. [Verification](verification.json) records the checks actually performed. PDF byte identity is not promised across builds or software versions.

Source verification, candidate coding and procurement extraction are inherited from pinned audits; this public build does not independently repeat the private original-source audit. [The literature crosswalk](../../docs/feasibility/literature-design-crosswalk.md) preserves edition/access limits. [P1/P2](../../docs/feasibility/measurable-progress-p1-p2-checkpoint.md), [P3](../../docs/feasibility/procedure-choice-calibration-decision.md), [P4](../../docs/feasibility/exposure-and-independent-review-p4.md) and [P5](../../docs/feasibility/precision-and-route-decision-p5.md) contain detailed scope and decisions.

Independent review has **zero completions**, no assigned reviewer and NA agreement/disagreement measures. The current thirteen-pair packet remains private. Substantive review and a completed-report decision are outstanding; this manuscript does not close those gates or deploy GitHub Pages. A causal restart requires the P5 reopening conditions, including a demonstrated joint sample and useful design-specific precision. No new individual-case acquisition is undertaken for this synthesis.
