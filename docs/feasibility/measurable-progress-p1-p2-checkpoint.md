# P1/P2 completed audit checkpoint

14 October 2026 UTC. Execution of [the measurable-progress plan](measurable-progress-plan-2026-10-14.md), steps P1 and P2. Completion means that every scoped event has an auditable disposition; it does not mean every eligibility gate passed. The historical report and earlier acquisition tables are preserved.

## P1: Complete cohort-specific scoreboard

The [event scoreboard](eligibility-scoreboard-events.csv) retains **all 169 existing events in 152 municipalities** and adds the **seven separately reviewed Saxony leads**. Combined bookkeeping contains **176 events in 159 municipalities**, with seventeen repeated municipalities/seventeen excess repeat events. These are not 176 eligible elections or 159 independently assigned treatments. The seven events were already in the twenty-event plurality source screen, so the national structural union remains **674 events / 649 municipalities**, not 681.

Every event records official identity/vote status and finality, event-law status, both candidates' presentation, first-coder pair status, current assignment exclusions, original buyer/procedure evidence, observation window, reporting coverage, exposure/intention-to-treat, independent coding and main-study eligibility. Public provenance fields identify the source ledgers. Zero supported evidence records are evidence-availability counts, never zero purchases or zero outcomes. Existing earlier-cohort legal and exposure evidence is not upgraded to event-level certification merely by joining tables.

The [nested cohort/band counts](eligibility-scoreboard-cohort-bands.csv) distinguish 2/5/10 pp acquisition bands, female-presented wins/losses, complete pairs and provisional count links. The [selection diagnostics](eligibility-scoreboard-selection-diagnostics.csv) compare documented winner/loser completion in municipalities with and without original-supported procedures. Missing/unreviewed role evidence remains unresolved; these diagnostics do not establish missing-at-random selection. For example, across the 55 NRW 2020 cases, documented presentation support covers 27 winners and 20 losers. Across the seven Saxon events it covers five winners and two runners-up. Independent review of inclusions and exclusions remains essential.

The [176-event acquisition queue](eligibility-scoreboard-acquisition-queue.csv) is ordered within cohort by exact margin/date/AGS, independently of presentation and procurement outcomes. It identifies the next unresolved gate, without authorizing an unlimited new retrieval wave. Provisional same-presentation exclusions remain distinguishable from unresolved assignments and independently certified exclusions.

**Joint linkage remains six provisional mixed-count elections:** four NRW 2025, one NI 2021 and one NRW 2020. Different source windows remain separate. Independent coding and certified main-study counts both remain zero.

## P2: All seven screened Saxony 2022 elections reviewed

The [complete event audit](saxony-2022-complete-audit.csv) reconciles official final results for **7/7 events**, including every final-round candidate, exact votes, valid-vote totals, ranking and declared winner. Both top-two identities are now available for all seven; the earlier compiled source had complete top-two names for only two. Full candidate names and annotations stay private; the official original sources are linked in the [source manifest](saxony-2022-source-manifest.csv).

The original [historical KomWG version effective 20 February 2022](https://www.revosax.sachsen.de/vorschrift/3818?stichtag=2022-07-03) establishes the second-round highest-vote rule in section 44a for the July 2022 events. This closes the event-date rule check, not legal office entry, election challenges, uninterrupted tenure or causal design certification. No first-round majority election is substituted.

| Municipality | Top-two gap, pp | Runner-up/third gap, pp | First-coder pair disposition | 2024 call notice/version records | 2024 result notice/version records |
|---|---:|---:|---|---:|---:|
| Oelsnitz/Erzgeb. | 8.076 | 22.710 | Unresolved opponent presentation | 19 | 2 |
| Roßwein | 5.041 | 28.856 | Both presentations unresolved; historical URLs redirect | 0 | 0 |
| Elsterberg | 5.851 | 43.969 | Both presentations unresolved under primary-source rule | 0 | 0 |
| Königsbrück | 9.144 | 25.000 | Mixed; female-presented loss | 2 | 0 |
| Reichenbach/O.L. | 5.506 | 28.863 | Feminine winner documented; opponent unresolved | 0 | 0 |
| Neustadt in Sachsen | 3.829 | 28.617 | Winner documented; opponent unresolved | 3 | 0 |
| Dresden | 7.061 | 26.025 | Mixed; female-presented loss | 652 | 166 |

The candidate block completes **14/14 dispositions**, supporting seven historical candidate presentations and **two complete mixed pairs**, with zero female-presented wins/two losses. Five pairs remain unresolved; unresolved does not mean same-presentation. Specifically:

- Königsbrück: personally signed feminine candidacy in the municipal bulletin of 31 May 2022 (physical PDF p4), paired with an explicit named masculine address in the 30 June bulletin (physical PDF p19).
- Dresden: own-party feminine nomination dated 22 January 2022, paired with a personal masculine pronoun in the official 14 July election bulletin (physical PDF p1, middle column). The pronoun's column attribution was visually checked.
- Oelsnitz: a named pronoun in the SPD's own 2022 campaign publication supports the winner; Reichenbach's elected-person table explicitly presents its named winner as feminine; Neustadt's 1 July bulletin supports the named winner in a contemporaneous municipal activity (physical PDF p6), with shortened identity reconciled to the official full name.

These apply the existing primary-source and explicit-person rules to the named 2022 event context; the original 2020 codebook and prior annotations remain unchanged. Names, photos, occupations, generic masculine office nouns and secondary accounts are insufficient. Administrative sex/gender is not established by these observations. No independent second coding is claimed.

All seven are outside 2 pp. Only Neustadt falls within 5 pp, and its pair remains unresolved. Thus neither of the new supported mixed pairs augments the narrow 2/5 pp sample. The margin denominator is **all valid decisive-round votes**. The third contender lies below a hypothetical tied top pair in each observed vector, but this arithmetic check does not certify an RDD: strategic candidacy, support near zero, legal assignment and a defensible multi-candidate estimand still need study. No third-candidate threshold or automatic pooling is adopted.

## Common-window availability and the concrete remaining bottleneck

We replayed the twelve pinned national CSV archives for **calendar 2024**, without new procurement downloads. This is a complete cached-calendar availability diagnostic for all seven events, not an adopted election-relative analysis window. It yields **676 call notice/version records in four municipalities and 168 result notice/version records in two**. No matching record for a municipality proves neither zero procurement nor complete reporting. Calls/results are not purchases, distinct procedures or original outcome counts.

An explicit exact-name addendum repairs the default alias set's omission of **Landeshauptstadt Dresden**, a name documented in the already acquired official municipal bulletin. Before the correction, the seven-event scan found 24 calls; the same seven-event scan after the correction finds 676. No substring matches, utilities or multiple-buyer allocations are admitted. The [procurement source manifest](saxony-2022-procurement-source-manifest.json) records the correction and all twelve archive pins, including the diagnostic's fixed window and cutoff.

The two supported mixed pairs have **654 call records, all without a procedure GUID**. Dresden has 646 distinct call notice identifiers among its 652 versions; Königsbrück has two. Domestic identifiers therefore need a separate original-notice recovery/linkage audit before these pairs can yield supported outcome data. This checkpoint does not silently replace the original graph standard with CSV metadata. Calendar-mature potential follow-up does not prove complete result coverage; missing result records are retained.

Office/exposure and common election-relative window checks remain unresolved. A later Neustadt election surfaced during discovery and reinforces why the entire 2022 term cannot be presumed uninterrupted; it is not certified from a search snippet. Dresden's litigation/office chronology also remains a separate exposure/validity check. No date of legal office entry is inferred from the election date.

## Source budget, verification and decision

There were **28 of at most 30 new source retrieval attempts**, including two public read-only download-form submissions; no person was contacted. The batch stops after every scoped disposition is recorded, leaving two attempts unused. Fourteen discovery-search batches are indexed privately; snippets and secondary material are never accepted as measurement evidence. Redirected Roßwein documents serve unrelated Google content despite HTTP 200 and are rejected. A Dresden campaign PDF was access-denied; one statistical report exceeded the per-document 12 MiB retrieval ceiling and was not retained. Neither supplies evidence. Historical bulletin originals and the candidate-keyed worksheet remain ignored local files; only municipality dispositions, source provenance, code and aggregates are public.

**226 offline tests pass.** The new validity tests reject wrong-event/non-final pages, inconsistent full vote vectors and totals, same-name duplicate joins, country/utility/multi-buyer matches and inferred assignments for unknown opponents. Deterministic replay and frozen report/source preservation are recorded in the local verification receipt. Full candidate replay requires the private, pinned original-source and review bundle.

**Decision:** P1 and P2 are complete as bounded audits. They add two supported historical mixed pairs and close seven official-event and event-date-law checks, but add **zero original-supported mixed-count links and zero certified main-study cases**. Continue to P3's historical procedure-choice calibration, already specified in the plan. Any domestic-ID recovery for the two new pairs must first receive its own finite, source-pinned batch definition. Independent review remains mandatory before a main-study launch. GitHub Pages remains deferred until research completion.
