# NRW 2025 Q1 outcome eligibility and linked-sample decision

**Evidence checkpoint: 11 October 2026 UTC. Recommendation: pursue a bounded, explicitly planned election-cohort expansion; do not launch the causal main study from this inventory.** This completes an outcome/scope/timing audit of the existing 37-procedure Q1 inventory and supplies the linked independent-election counts. The project adapts **Florio and Spagnolo (2026)** to Germany; see the [Italian adaptation and German research](../literature.md). The [historical outcome draft](outcome-population-codebook.md) and frozen report remain unchanged.

## Inventory audit

| Object or disposition | Count |
| --- | ---: |
| Original Q1 procedures / municipalities | 37 / 14 |
| Supported sole named municipal contracting parties | 37 |
| Literal open / restricted / negotiated-with-call procedures | 34 / 2 / 1 |
| Procedures without an indexed standard result by 30 September | 13 |
| Original result notices / source-defined lot-result units | 24 / 29 |
| Successful lot results / closed-without-winner lot results | 28 / 1 |
| Successful lot statistics with supported positive total tenders and dates | 28 |
| Distinct contracts in those successful lots | 25 |
| Main-study-certified independent elections | 0 |

Every call's original issue and supported publication date lies in 1 January–31 March 2026 and follows its municipality's September 2025 decisive election. Original-call publication-to-cutoff follow-up ranges from **184 to 264 days**. The same calendar window/cutoff does not imply identical reporting lag or complete ascertainment. Pending or unobserved results remain in the procedure inventory; they do not become cancelled procedures, zero tenders or zero competition outcomes.

The [procedure ledger](nrw-2025-q1-procedure-eligibility.csv) records individual scope, literal category, timing, follow-up and result availability. The [result ledger](nrw-2025-q1-result-eligibility.csv) records source-specific lot identities, total-tender statistics, graph checks, conclusion dates and exclusion reasons. The [original XML manifest](nrw-2025-q1-eligibility-source-manifest.csv) pins every inspected notice and its public national export. The complete [thirty-election linkage inventory](nrw-2025-q1-linked-election-inventory.csv) retains municipalities without matches and every candidate-presentation disposition.

## Contracting party and result-unit rules

Municipal scope is supported by the **actual UBL contracting-party role**, a uniquely matched municipality name/AGS and the original municipal buyer-type code `kommun-beh`. This is an inventory scope check, not a claim that every purchase is observed. Four procedures include procurement-service-provider records. Those organizations do not become additional contracting buyers merely because they are named in the notice. The underlying municipality remains the named contracting party. County, enterprise, joint-buyer or ambiguous roles would remain separately unresolved/outside scope under the draft rules; none was introduced by these checks.

The new cohort audit resolves five flags produced by the earlier single-lot-contract assumption:

| Original result notice | Source structure | Reviewed disposition |
| --- | --- | --- |
| [293249-2026](https://ted.europa.eu/en/notice/-/detail/293249-2026), Lünen | Three separate lot results and tender totals reference one contract containing all three explicitly linked winning tenders | Keep three lot statistics and one contract. |
| [305108-2026](https://ted.europa.eu/en/notice/-/detail/305108-2026), Selm | Two separate lot results reference one contract containing both explicitly linked winning tenders | Keep two lot statistics and one contract. |

For each affected result, the contract's tender references intersect the result's references exactly as needed; every contract tender has a reciprocal result and matching lot. Winner-party and organization references are also checked. An undefined tender, missing reciprocal edge, overlapping result lot or unlinked result-notice collision remains a failure. Contract values are not divided between lots. A source-defined grouped-lot statistic would remain one statistic rather than being multiplied by its lot count.

The earlier strict parser supported **23 dated Q1 lot statistics**. This separate, reviewed graph construction supports **28**, adding the five reconciled units. Earlier inventory/report outputs and the historical parser are preserved. The change does not invent five additional procedures or elections.

Kleve's original [309392-2026](https://ted.europa.eu/en/notice/-/detail/309392-2026) explicitly reports `clos-nw` with one total tender. Its statistic remains visible, but it is **not a successful single-tender award** and is withheld from the successful-result count population. Electronic, SME or other subset statistics do not replace an explicit total; missing, duplicate or invalid totals would stay unresolved. Total tenders are not distinct bidder firms.

## Independent-election linkage and missingness

The currently supported mixed-public-presentation inventory has the following availability. These are first-coder presentation observations and candidate outcome populations, not certified treatment assignments or outcome rates.

| Election | Female-presented finalist | Original Q1 procedures | Supported successful count statistics | Procedures without indexed results |
| --- | --- | ---: | ---: | ---: |
| Königswinter | Won | 1 | 0 | 1 |
| Neunkirchen-Seelscheid | Lost | 4 | 4 | 0 |
| Herdecke | Won | 2 | 2 | 0 |
| Lüdenscheid | Lost | 1 | 1 | 0 |
| Lünen | Won | 2 | 4 | 0 |
| Mülheim an der Ruhr | Lost | 5 | 0 | 5 |
| **Total** | **3 wins / 3 losses** | **15** | **11** | **6** |

The called-procedure inventory therefore has **six known mixed elections, split 3/3**. The successful total-tender inventory has **four known mixed elections, split 2/2**, contributing eleven lot statistics from nine procedures. Königswinter and Mülheim remain in the acquisition frame with undefined competition outcomes. Balanced remaining sides do not remove outcome/reporting selection. The other procedures come from three reviewed same-presentation elections and five elections whose presentation review remains uncompleted. Those records are retained, not silently classified from predictions.

The separate ≤2 pp review still has three confirmed mixed pairs, all female-presented losses. Within that closest subset, supported count outcomes exist for only **two elections**, both on the losing side; Mülheim's five procedures have no indexed result. No new balanced close-cutoff comparison has emerged. A five-pp acquisition band is not an econometric bandwidth or a justification for expanding a bandwidth after seeing outcome availability.

## Office chronology and interpretation

Eight new source-pinned role observations cover the six mixed elections; see the [observation ledger](nrw-2025-q1-office-observations.csv) and [office-source manifest](nrw-2025-q1-office-source-manifest.csv). Lünen's municipality documents the elected winner as mayor on 15 December 2025 and at the 23 January 2026 reception. This adds actual named role/activity evidence beyond the earlier election confirmation and inaccessible council PDF. Königswinter's official retrospective supplies a **November 2025 entry month**, with no fabricated day. Neunkirchen-Seelscheid has a February interview and a March signed municipal statement; Lüdenscheid and Mülheim have named March activities. Herdecke's January event report is authored by its fire service and hosted by the municipality; authorship is kept distinct from the municipal press office.

Point observations do not certify uninterrupted officeholding, acceptance, predecessor exit or exact legal entry. The Neunkirchen-Seelscheid interview's “100 days” description is not converted by date subtraction into an office-entry day. Earlier November 2025 oath/entry evidence remains separate and dated to its original checkpoint. The other eight municipalities with Q1 procedures have no completed office review in this bounded batch.

The proposed fixed-calendar **election ITT** would retain original election assignment through turnover. Continuous original-winner exposure is a different sensitivity population; it must not silently become an exclusion rule for the election ITT. All procedures have supported post-election calendar chronology, but final estimand/window adoption, presentation second coding and the relevant exposure histories remain unfinished. No personal mayoral signature is required for municipal procurement scope.

## Outcome interpretation and precision decision

The nominated **all-category negotiated-procedure share is not yet constructible** from this call-only inventory. Negotiated-without-call procurement and its harmonized cohort-entry rule are absent. The supported literal categories permit a clearly labelled **called-procedure composition audit**; this is a restricted diagnostic, not a silent replacement of the nominated primary measure. The conditional successful-result total-tender population is technically more complete, but it has only four currently supported mixed elections. No primary outcome rate or treatment effect has been estimated.

The planning calculations use independent, equal-variance Gaussian observations and a pooled two-sample t test, two-sided, 80% power. They are **not RDD power**, observed outcome variability, or a universal lower bound on every possible design. Per-test α=.025 is an illustrative conservative allowance for the nominated two-outcome family.

| Candidate availability inventory | Independent elections | MDE at α=.05 | MDE at α=.025 |
| --- | ---: | ---: | ---: |
| Called composition, 3 wins / 3 losses | 6 | 3.07 outcome SD | 3.74 outcome SD |
| Conditional tender count, 2 wins / 2 losses | 4 | 5.65 outcome SD | 8.01 outcome SD |

Under the same illustrative balanced Gaussian model, an effect of **1.0 SD needs 42 elections**, **0.5 SD needs 156**, and **0.25 SD needs 612** at α=.025 and 80% power. These illustrative effect sizes have not been adopted as substantive thresholds, and the counts are not an RDD sample-size requirement. Clustering, discrete margins, kernels, slopes, repeated municipalities and reporting selection require a separate design-specific assessment.

A second planning diagnostic exposes the finite-assignment problem: with fixed balanced treated counts and equally likely complete-randomization allocations, an absolute difference-in-means two-sided permutation test has minimum attainable p-values of **.10 for six cases** and **1/3 for four**. Complementary allocations yield the same absolute statistic. This result applies to that stated local-randomization model/test, not to every RDD estimator or assignment model.

**Decision:** do not prepare the present sample for causal estimation. Prefer a targeted, bounded expansion of the *independent-election frame*, subject to an a priori source/coverage and precision plan. The Italian adaptation and German precedents remain the methodological starting point; this checkpoint supplies no isolated mayoral-gender effect, null-effect result or universal impossibility claim. Existing few-election evidence can support a transparent feasibility report or explicitly descriptive work if expansion fails.

## Reproduction and next milestone

```sh
python src/pilot/nrw_2025_q1_eligibility.py
python -m unittest discover -s tests -q
```

Full replay requires the ignored original public-export snapshots, election/person annotations and office-source bundle. The audit checks export/source hashes, exact XML identity, original roles and office locators. Public manifests disclose provenance, but do not guarantee reconstruction from mutable live URLs. Raw personal annotations and original documents remain local. **184 offline tests pass**; the historical baseline and all 32 frozen report input/output pins remain unchanged. No external reviewer was contacted. GitHub Pages remains deferred.

The next bounded milestone is a **cohort-expansion protocol** before additional extensive case research: specify acceptable effect thresholds/scenarios, candidate election cohorts and common public reporting windows; count potential independent assignments and reporting coverage without filtering on realized procurement outcomes; account for repeated municipalities; and set an explicit stop rule if a realistically verifiable sample cannot approach useful precision. Independent second coding remains required before any main-study go decision. Clarification of the three closest-pair evidence gaps can continue within a capped budget, but does not change this checkpoint's small linked-sample decision.
