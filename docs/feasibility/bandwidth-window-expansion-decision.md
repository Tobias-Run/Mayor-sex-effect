# Decision memo: wider acquisition band and longer older-cohort window

11 October 2026. The project owner authorized the recommended revisions before this execution. **Expand acquisition to a 10 percentage-point absolute finalist vote gap, preserve the 2/5 pp strata, and extend the older cohorts to twelve complete calendar months.** This increases the active frame from **58 to 114 different municipalities**, with all 114 identity/vote checks supported by their official sources. Niedersachsen sources explicitly remain provisional state returns. The revised frame is not an eligible causal sample.

The wider national structural screen contains **654 election events in 629 municipalities**, versus 326 events/319 municipalities within 5 pp. Twenty-five municipalities recur and are shared clusters. Both finalist names are available for 258 events; 396 remain incomplete in this source. The pinned GERDA screen is a research inventory, not a national census or a verified mixed-pair population.

## What was changed, and why

| Parameter | Previous checkpoint | Authorized revision | Expected benefit | Cost and safeguard |
|---|---|---|---|---|
| Acquisition vote gap | ≤5 pp | ≤10 pp, with nested ≤2/≤5 and exclusive margin strata retained | More independent election opportunities | Larger gaps can increase confounding and RDD sensitivity. Ten pp is an acquisition ceiling, not an adopted causal bandwidth. No significance-driven bandwidth choice. |
| Older-cohort call window | Q1 2025 | Full January–December 2025 for Niedersachsen 2021 and Brandenburg 2024 | More municipalities with potentially linkable procurement | Changes seasonality, election age and exposure. Cohorts remain separate; legal entry, turnover and original chronology still require audit. |
| Younger-cohort window | Q1 2026 | Retained for NRW 2025 and Brandenburg 2025 | Preserves their existing observed period | Full 2026 is not yet observed. A partial year is not treated as a complete year or pooled with the older annual windows. |
| New-window result follow-up | Earlier Q1 analyses have their own frozen cutoffs | Target nine calendar months after each verified original call; administrative cutoff 30 September 2026 | Gives procedures equal intended follow-up rather than letting early calls have more time | Young Q1 2026 calls are immature under this new rule. Keep censoring visible; do not overwrite the earlier audits or drop immature cases. |
| Evidence and linkage quality | Actual municipal buyer, original chronology, presentation evidence and independent coding required | Retained | Protects the interpretation of additional cases | No name/occupation inference, no invented procedure IDs, no automatic conversion of notices into independent purchases. |

The twelve-month period is the **first full calendar year after Brandenburg's 2024 elections**, but a **separate late-term calendar year after Niedersachsen's 2021 elections**. Neither is automatically the first twelve months after legal entry. Their different election ages need substantive justification before any eventual pooling.

## Executed election expansion

| Cohort | ≤2 pp | ≤5 pp | ≤10 pp | Added beyond the previous 5 pp frame |
|---|---:|---:|---:|---:|
| NRW 2025 | 14 | 30 | 65 | 35 |
| Niedersachsen 2021 | 7 | 18 | 36 | 18 |
| Brandenburg 2024 | 1 | 5 | 5 | 0 |
| Brandenburg 2025 | 2 | 5 | 8 | 3 |
| **Active total** | **24** | **58** | **114** | **56** |

NRW's official statewide detail sources were rehashed and reparsed. The existing Niedersachsen PDFs support all 36 pairs, including the explicit Oberbürgermeister office label. Three new Brandenburg result pages support the Nauen, Jüterbog and Templin pairs. Selection does not use candidate presentation, winner gender or procurement availability. Missing-name cases remain visible in the [national inventory](national-10pp-election-inventory.csv); unresolved presentation is not a reason to drop an active event.

## Separate the gains from band and window

All comparisons below use the **same fifteen verified source archives, alias rules and source-publication-date filters** in this replay. They compare acquisition opportunities, not certified outcomes or earlier TED-only counts.

| Acquisition band and call window | Municipal elections with at least one exact standard-call metadata match |
|---|---:|
| ≤5 pp, Q1 in each cohort | 28 |
| ≤10 pp, Q1 in each cohort | 54 |
| ≤10 pp, full 2025 for older cohorts and Q1 2026 for younger cohorts | **61** |

The wider band adds **26** matched municipalities when the quarter is held fixed. The annual window then adds **seven** more: six in Niedersachsen and one in Brandenburg 2024. This decomposition follows band expansion first; the contributions overlap if the changes are applied in the opposite order. Within Niedersachsen's original 5 pp frame alone, the annual window increases matched municipalities from six to eleven. Read the [full 2/5/10 pp and Q1/annual decomposition](parameter-gain-decomposition.csv) rather than treating every additional notice as a new election.

| Cohort | Active elections | Elections with standard-call metadata | Standard-call notice/version records | Records without procedure IDs |
|---|---:|---:|---:|---:|
| Brandenburg 2024 | 5 | 4 | 20 | 17 |
| Brandenburg 2025 | 8 | 4 | 9 | 5 |
| NRW 2025 | 65 | 32 | 192 | 110 |
| Niedersachsen 2021 | 36 | 21 | 276 | 171 |
| **Total** | **114** | **61** | **497** | **303** |

These are **notice/version records**, including possible corrections. Neither the 497 records nor the observed distinct procedure IDs is a count of verified independent purchases. Fifty-three elections remain without exact standard-call matches; this means unknown source coverage, not zero procurement. Original calls, role/jurisdiction, correction graphs, linked results and candidate/tenure measurement remain to be checked.

## Source and follow-up controls

Nine April–December 2025 monthly CSV archives were acquired, while all six earlier Q1 2025/2026 sources were reused. All fifteen source-file hashes verify. The new compressed procurement sources total **152,394,595 bytes**; the combined tracked NRW/Brandenburg/new bundle totals **1,027,231,657 bytes**, below the pinned 1 GiB cap. All twelve 2025 and three 2026 source files are present. Monthly-file completeness does not establish complete original-call or result coverage.

The replay inspects 372,959 national rows containing 372,958 unique notice/version keys. One fully identical notice-and-buyer record appears in both September and October exports and is counted once. Conflicting duplicate metadata would stop the replay. There are 2,012 matched records outside their fixed cohort windows, retained in a [separate disposition ledger](relaxed-acquisition-outside-window-notices.csv). An export month can contain a correction whose own publication field belongs to an earlier period; the [calendar clarification](window-discovery-calendar-addendum.md) prevents export membership from substituting for original chronology. The previously source-observed Velten buyer alias is retained.

For the longer-window target, all 296 older-cohort call records have calendar-mature nine-month targets at the September cutoff. All 201 younger-cohort call records have immature targets reaching October–December 2026. **Calendar maturity is not evidence that results have been completely searched or observed**, and metadata targets are provisional until original roots establish the correct publication date. Keep absent outcomes censored/unresolved and report coverage separately. The earlier supported NRW count inventories remain intact under their original audit rules.

## Research decision and next queue

Continue the expanded feasibility route; do not launch a causal estimator from these counts. This phase adds **zero verified mixed-election count outcomes**. The existing four provisional mixed elections with supported tender-count inventories remain four, independent second coding remains open, and there are zero certified main-study elections.

Next verify original calls and domestic IDs for the 61 matched municipalities, prioritizing the newly opened 5–10 pp and annual-window cases while retaining all 114 elections in the source-selection ledger. Review candidate presentation independently of procurement matches, including losing finalists and all unmatched elections. Then assess legal exposure, correction deduplication, result coverage and cohort-specific linked-election precision. The eventual design still identifies electing a particular female-presented finalist relative to her actual opponent, not an isolated gender effect. More notices do not resolve the independent-election precision bottleneck.

The [prospectively pinned protocol](bandwidth-and-window-expansion-protocol.md), [nested counts](bandwidth-expansion-nested-counts.csv), [active ledger](relaxed-acquisition-election-inventory.csv), [call discovery](relaxed-acquisition-national-call-discovery.csv), [official-source manifest](relaxed-acquisition-official-source-manifest.csv), [export manifest](bandwidth-window-export-manifest.json) and [summary](bandwidth-window-expansion-summary.json) support review. Replay with `python src/pilot/bandwidth_window_expansion.py` using the locally cached pinned sources; add `--acquire` only for the bounded acquisition route. The source manifests provide URLs and hashes, but this script is an extension of the existing audits, not a clean-clone downloader. Local verification passes 202 offline tests, reproduces all nine new generated public artifacts byte-for-byte, and preserves 15 baseline pins, 32 frozen-report pins and the eight earlier 5 pp replay artifacts. Original files and candidate working records stay ignored/local. Old 5 pp ledgers and the frozen historical report remain unchanged; no contact or Pages publication occurred.
