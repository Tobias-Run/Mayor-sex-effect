# NRW 2025 Q1 call cohort: original-file completion

Evidence checkpoint: 11 October 2026 (UTC). This completes the 28 missing original targets and 16 pending competition graphs from the [10 October audit](nrw-2025-validation-progress.md). The selected election universe, original Q1 query and 30 September result cutoff are unchanged. The project continues the Florio–Spagnolo adaptation and its [German research/design precedents](literature-design-crosswalk.md); no causal outcome is asserted.

## What is now established

All **78 indexed competition/result originals** in the independent call cohort now match exact notice UUID/version and procedure GUID: 51 competitive notices and 27 standard result notices. There are no remaining original targets or unresolved correction graphs in this fixed index. Fifty additional public eForms export dates recover the missing files. Combined retained exports total 224 dates and 757,474,906 bytes, below the existing 1 GiB cap. Source archives remain local and ignored.

| Check | Previous checkpoint | Completed checkpoint |
|---|---:|---:|
| Original XMLs matched | 50 | 78 |
| Missing original targets | 28 | 0 |
| Supported original competition graphs | 25 | 41 |
| Pending original competition graphs | 16 | 0 |
| Procedures with original issue and publication in Q1 | 23 | 37 |

The independently selected roster still contains **41 procedure GUIDs in 15 municipalities**. Four are outside the proposed issue/publication window: one Mülheim root dates to December 2025, one Alsdorf root to October 2025, and one root each in Datteln and Kleve to December 2025. Their later Q1 publications do not create new Q1 procedures. A supported graph establishes one documented root in this checked index, not the earliest-ever publication across every possible notice family.

The corrected Q1 inventory contains **37 procedures**, of which **13 have no indexed standard result through 30 September**. Across the original 41-procedure roster, the corresponding missing-result count remains 14. Missing results mean unresolved or censored observations; they do not establish cancellation, no procurement or zero bids.

In the full 41-procedure roster, original results identify **32 explicitly awarded lot units** and **one explicitly closed-without-winner lot unit**. The latter is the sole lot in Kleve result `309392-2026`; it has an explicit `clos-nw` status. This documented outcome is different from the 14 procedures lacking an indexed result. Twenty-seven result lot units have supported dated total-tender statistics. These are source-availability counts over the full roster, including its four out-of-window procedures, not a Q1 outcome rate or certified analysis denominator. Lot multiplicity, contractual units and chronology still need the nominated outcome's eligibility rules.

## Consequences for the six reviewed election pairs

| Municipality | Original Q1 procedures | Procedures lacking an indexed result in the provisional roster |
|---|---:|---:|
| Königswinter | 1 | 1 |
| Neunkirchen-Seelscheid | 4 | 0 |
| Herdecke | 2 | 0 |
| Lüdenscheid | 1 | 0 |
| Lünen | 2 | 0 |
| Mülheim an der Ruhr | 5 | 6, including one out-of-window procedure |

All six first-coder-supported mixed-presentation municipalities have original Q1 calls. Königswinter and Mülheim must therefore remain in the availability inventory even though the earlier result-first sample omitted them from its Q1 list. They have unresolved results, not assumed zero outcomes. The election-level inventory remains six possible independent cases, three female-presented wins and three losses; it has not become 37 independent treatment assignments.

At ≤2 percentage points the three supported mixed pairs in the reviewed batch are still all female-presented losses. More procedures cannot repair that cutoff imbalance or the small election sample. The earlier conditional precision benchmarks remain relevant, and administrative gender, independent second coding, actual office continuity, delegated buyer jurisdiction and complete outcome populations remain uncertified. The competitive-call cohort also omits procurement without a call, so it cannot establish the full procedure-choice denominator.

## Next bounded work

The [closest-pair review queue](nrw-2025-closest-pair-review-queue.csv) retains all **14 official pairs within 2 pp**, ordered only by exact absolute election margin. Three have supported presentation dispositions from the six-case batch; eleven remain unreviewed in this cohort batch. Procurement matches and predicted gender labels do not determine priority or exclusion. The next candidate task is primary evidence for those eleven pairs, followed by independent coding rather than treating a search prediction as measurement.

In parallel, classify the 37 original Q1 procedures under the outcome/population rules, retaining missing results explicitly and verifying original buyer jurisdiction and office intervals. Any proposed change in the observation window or follow-up cutoff needs a reason independent of the observed outcome pattern. No primary outcome rate, causal coefficient or main-study eligibility is certified at this checkpoint. GitHub Pages remains deferred until research completion.

## Evidence and validation

The updated [cohort summary](nrw-2025-q1-call-summary.json), [procedure roster](nrw-2025-q1-call-procedures.csv) and [municipality matrix](nrw-2025-q1-call-municipalities.csv) expose the checks. The [additional export manifest](nrw-2025-q1-completion-export-manifest.json) pins the fifty new source responses; the original [query/follow-up request pins](nrw-2025-q1-call-request-manifests.json) are unchanged.

With retained local snapshots and the feasibility dependencies installed, run `python src/pilot/nrw_2025_call_roster.py`. This verifies exact originals across all three pinned export batches and enforces unique source files and the combined 1 GiB cap. All **171 offline tests pass**. The historical baseline and frozen report's 22 public input hashes and 10 output hashes remain unchanged. Neither nationwide source archives nor personal coding records are uploaded.
