# Brandenburg expansion: ten additional official election pairs

**11 October 2026 UTC. The acquisition frame expands from 30 NRW elections to 40 distinct municipalities across three separately retained cohorts. Ten new Brandenburg pairs are verified against original official results. This is a larger acquisition frame, not an increase in the currently supported mixed-election competition-outcome sample.** The project adapts Florio and Spagnolo (2026); see the [Italian adaptation and German research](../literature.md).

The [protocol](cohort-expansion-protocol.md) was source-pinned before new procurement queries. The [national-discovery addendum](cohort-expansion-national-discovery-addendum.md) records the subsequent call-first expansion from TED to the broader German register. The five-percentage-point acquisition rule is unchanged; neither document selects an RDD bandwidth or adopts a causal analysis plan.

## New election frame

The pinned GERDA snapshot supplies 14 structurally screened Brandenburg decisive pairs in 2024 and 28 in 2025. Five per year lie within 5 pp. All ten enter, irrespective of name predictions, winner side or procurement results. The [cross-state/year availability table](cohort-expansion-source-availability.csv) reports complete-pair/name coverage for 2023–2025. It does not certify an official national census. Missing losing-candidate names in other source cohorts remain visible; they are not evidence that the elections did not happen.

| Election cohort | Included municipalities | Candidate procurement window / indexed follow-up |
| --- | --- | --- |
| Brandenburg 2024 | Stahnsdorf, Angermünde, Lychen, Kremmen, Schöneiche bei Berlin | Q1 2025 / 30 September 2025 |
| Brandenburg 2025 | Teltow, Glienicke/Nordbahn, Velten, Bad Freienwalde (Oder), Kolkwitz | Q1 2026 / 30 September 2026 |

All ten official pages reconcile the municipality, decisive day/round, both full candidate identities, exact votes, valid-vote denominator and committee-declared winner. Kremmen's explicit academic titles are normalized, with no initial/surname-only/fuzzy join. The initially guessed Stahnsdorf URL returned an empty template despite HTTP 200; that negative response remains pinned. The source-linked older page using the eight-digit AGS verifies the actual result. HTTP success alone is insufficient evidence.

The [election acquisition inventory](brandenburg-expansion-election-inventory.csv) retains all ten and their official-source dispositions; the [official source manifest](brandenburg-expansion-official-source-manifest.csv) pins originals. The [combined forty-election ledger](expanded-election-acquisition-frame.csv) retains all thirty NRW observations and the ten new municipalities, with cohort labels. Brandenburg's source uses current geographic codes; source-level geographic vintage and institutional comparability still require assessment before analysis. The two Brandenburg windows remain separate: election months and time since actual office entry differ, so identical Q1 labels do not establish identical exposure ages. There is no pooled effect estimate.

## Broader-register discovery

The two complete capped TED call queries return two notices per year, representing one procedure in Kremmen and one in Velten. The source-observed designation **Stadt Velten - Die Bürgermeisterin** is added explicitly to the municipality's name aliases. This is a reviewed exact alias, not a gender assignment or fuzzy stripping rule. Procedure-GUID follow-up returns four call notices and one result notice across the two procedures.

A sparse TED screen cannot establish absence of municipal procurement. The national discovery therefore inspects **six complete monthly CSV exports**, January–March 2025 and January–March 2026, containing **144,404 notice rows**. The join uses original notice/version keys and actual CSV buyer roles, not named supplier/reviewer organizations. It preserves numeric domestic notice IDs rather than rejecting them as malformed UUIDs. Source UTC timestamps are converted to the German calendar day; national publication dates remain distinct from TED publication dates and original dispatch dates.

| Municipality | National Q1 call notices | Nonmissing distinct procedure IDs | Reviewed original Q1 procedures | Supported dated total-tender lot statistics |
| --- | ---: | ---: | ---: | ---: |
| Kremmen | 2 | 1 | 1 | 0 |
| Angermünde | 2 | 0 | 0 | 0 |
| Schöneiche bei Berlin | 4 | 0 | 0 | 0 |
| Velten | 2 | 1 | 1 | 3 |
| Other six selected municipalities | 0 | 0 | 0 | 0 |

These are source-coverage counts. **Six domestic call notices lack a procedure ID** and remain unresolved metadata discoveries; they do not become six independent purchases. The original root of each of the two GUID-linked procedures is now supported. Missing exact name matches are unknown coverage rather than zero procurement. Metadata alone also does not establish complete contracting authority scope. The national quarter contains one additional matched result record, but result-first records do not create Q1 cohort entries.

See the [national call ledger](brandenburg-expansion-national-call-discovery.csv), [ten-election national coverage ledger](brandenburg-expansion-national-election-coverage.csv), [national summary](brandenburg-expansion-national-summary.json), [six CSV export pins](brandenburg-expansion-national-export-manifest.json) and [TED request/page pins](brandenburg-expansion-ted-request-manifests.json).

## Exact original procedure and result audit

All **five indexed original notices** are matched by exact UUID/version and procedure GUID, with no missing targets. Both procedures have a documented correction root with original issue and TED publication in their fixed Q1, a sole original municipal contracting party and literal `open` category. Kremmen has no indexed standard result through its September 2025 cutoff. It remains in the call cohort with undefined competition outcomes.

Velten's [605468-2026](https://ted.europa.eu/en/notice/-/detail/605468-2026) has three successful source-defined lot results, explicit tender totals **18, 18 and 11**, and conclusion date **10 August 2026**. The reciprocal graph audit supports all three: one contract covers two lots, a second covers the third. These are **three lot statistics, two contracts, one procedure and one election**. No contract value is allocated to lots and no count is interpreted as distinct firms. The audited original competition was issued 17 March and published 18 March 2026; the result was published 2 September. Its chronology is supported within the candidate calendar window.

The [procedure audit](brandenburg-expansion-original-procedure-audit.csv), [result-unit audit](brandenburg-expansion-result-audit.csv), [exact XML/export pins](brandenburg-expansion-xml-source-manifest.csv) and [additional daily-export manifest](brandenburg-expansion-xml-export-manifest.json) document these checks. Seven new daily XML exports plus six monthly CSV exports total **117,362,156 compressed bytes**; with the unchanged NRW bundle, **874,837,062 bytes**, below the fixed combined 1 GiB bound. Some newly retrieved alignment days were not needed after cached originals were identified; all retained acquisitions are disclosed. No new original is silently substituted for a pinned older snapshot.

## Presentation and linked-sample status

The bounded first-coder source batch accepts five person-specific primary observations: both finalists in Kremmen and Teltow, and the elected winner in Velten. Kremmen and Teltow are supported mixed-public-presentation pairs; the female-presented finalist lost in both. Velten's official retrospective documents the elected winner as female-presented and records her first workday on **12 January 2026**, while explicitly corroborating the October 2025 election. It does not certify legal acceptance or uninterrupted officeholding. The losing finalist's qualifying primary presentation evidence remains unresolved after the initial search; no predicted male label is promoted. Seven other election pairs have not completed presentation review in this batch.

**Search-budget deviation:** the Velten opponent received three query batches (five queries, including the initial pair-level query), exceeding the planned two-round cap. No qualifying primary observation was accepted; further search stops in this batch. This deviation is retained in the local search record and public summary.

These are selected first-coder observations, not a full ten-pair presentation audit, administrative gender fields or independent second coding. Evidence is accepted for three winners and two losers; this incomplete pattern must not be read as an estimate of source-selection bias. Read the [source manifest](brandenburg-expansion-presentation-source-manifest.csv) and [linked-election ledger](brandenburg-expansion-linked-election-inventory.csv). Exact quotes/person annotations remain local. Unreviewed cases mean unfinished work, not proof that evidence cannot be found.

**No new supported mixed pair currently has supported tender-count outcomes.** Kremmen is a supported mixed pair with a call but no indexed result; Teltow has no exact call match; Velten has three supported lot statistics but an unresolved opponent presentation. Consequently the previously supported NRW count inventory remains **four elections (2 female-presented wins / 2 losses)**. Main-study-certified elections remain zero. The acquisition frame grew by ten, but reporting, identity linkage and two-finalist measurement still constrain usable independent assignments.

## Precision and stopping decision

The first expansion batch is now closed at its fixed ten-election frame. Even complete recovery of all ten as mixed, linked cases would yield at most fourteen supported count elections when added to the existing four; it cannot reach the prior **42-election illustrative benchmark for a 1 SD effect**. The 0.5/0.25 SD balanced Gaussian scenarios need 156/612 elections under their stated alpha/power assumptions. These remain illustrative planning scenarios, not adopted substantive thresholds or RDD requirements. No new effect or outcome rate is estimated, and a larger acquisition ledger alone does not justify a causal launch.

The next bounded work should resolve the **identifier/source coverage bottleneck**, not harvest more lots from the same few elections: inspect documented domestic procedure references for the six numeric-ID calls; obtain qualifying losing-finalist evidence in Velten within a separately recorded follow-up budget; and compare a fixed broader election frame against plausible register coverage before further large acquisition. Continue presentation review of all ten independently of predictions and procurement hits; retain every unresolved/missing row. A failed route should trigger a descriptive/feasibility scope decision rather than widening the RDD bandwidth to gain cases. Cohort-specific office chronology, institutional pooling justification, meaningful effect thresholds and independent second coding remain gates.

## Reproduction

From the repository root, with the retained ignored source bundles:

```sh
python src/pilot/cohort_expansion.py
python src/pilot/cohort_expansion_national.py
python src/pilot/cohort_expansion_audit.py
python -m unittest discover -s tests -q
```

The first command verifies the pinned protocol, GERDA snapshot, official originals and saved TED pages. The second verifies all six monthly national exports and foreign-key/role joins. The third verifies exact original XMLs, source budgets, graph links and primary presentation locators, retaining all thirty prior NRW rows. Optional `--download` on the first command acquires only missing official/TED sources; it does not overwrite snapshots or automatically recreate the separate national export/person bundles. Public manifests disclose exact URLs and hashes; mutable live sources may no longer reproduce the retained originals.

**193 offline tests pass.** The historical baseline and all 32 frozen report input/output pins are unchanged. All original/person bundles remain ignored/local. No outreach was sent and GitHub Pages remains deferred.
