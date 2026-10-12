# Tested alternatives toward a causal main study

12 October 2026. **Recommendation: prioritize complete multi-candidate plurality cohorts and a historical procedure-choice prototype with a genuine pre-election baseline.** Do not widen the causal bandwidth, pool incompatible windows or replace missing total bids with subcounts. The present six provisional mixed-count elections remain six; zero are main-study certified. The Italian adaptation and German precedents remain the project's starting point in the [literature note](../literature.md).

## What this batch actually tested

| Route | Observed result | Scientific consequence |
| --- | --- | --- |
| Mature calendar-2024 source window | All 91 NRW 2020/NI 2021 pairs retained; 1,560 standard-call metadata records | An additional common calendar window, not common time since election |
| Original 2024 graphs and results | 694 exact originals, 90 missing; 367 supported original-window/buyer procedures in 42 elections; 86 supported tender statistics in 17 elections | More original procurement evidence, but only Bückeburg already has supported mixed assignment and counts in this window; no independent election added to the six-case inventory |
| Historical OCDS bridge | 48,308 compiled processes in 2019 and 57,383 in 2021; strict buyer matches 174/206; 138/170 call-date metadata processes | Genuine source access for pre/post first-full-calendar-year opportunities; compiled/transformed data still need validation |
| Historical total-bid fields | No qualifying total-bid/total-tenderer field in the matched 2019/2021 records | Electronic/SME/foreign subcounts cannot be summed or substituted as total bids |
| Historical procedure-choice fields | 338 processes with first document dates in the target years; 19 municipalities have procedure-detail metadata in both years | A potentially usable alternative outcome route, including five historically supported mixed pairs (one female-presented win/four losses), not five certified causal cases |
| Multi-candidate decisive rounds | 20 fully source-reconciled additional Saxon election events; eight complete top-two names; three within 2 pp and nine within 5 pp | Adds acquisition opportunities without changing the 10 pp gap; plurality legal/design and official/assignment checks remain necessary |
| Candidate completion | Six pairs, seven searches, six new original requests: four acquired/two unavailable; one accepted reinspection | Lüdenscheid 2020 is now supported same-presentation, not a new mixed case; five pairs remain unresolved |
| Prognostic-adjustment sensitivity | At a 0.5 SD target, illustrative balanced totals fall 156→80→42 under assumed R² 0/.50/.75 | Potential efficiency gain only; no empirical R² established and not RDD power |

The complete [2024 call ledger](creative-2024-call-discovery.csv) preserves two cross-municipality records sharing one GUID. The strict auditor initially stopped. The [shared-GUID addendum](creative-2024-shared-guid-addendum.md) withholds that identifier from attribution while retaining both municipalities and every original source snapshot. The complete TED contexts contain 803 notices, of which nineteen belong to the shared GUID; 784 unambiguous context notices are audited. Never infer zero purchases or award outcomes from a withheld/missing record. The source audit uses 291 existing original archives and adds no new XML download.

Read the [original procedure audit](creative-2024-original-procedure-audit.csv), [lot-result audit](creative-2024-original-result-audit.csv), [assignment ledger](creative-2024-assignment-inventory.csv) and [summary](creative-2024-original-audit-summary.json). All 86 supported statistics have calendar-mature nine-month targets; reporting and result-revision completeness are still open. Sixteen more outcome-bearing elections than the one known mixed case do not become treatment assignments by inference.

## 1. Expand the electoral-rule screen, not the assumed randomization window

The original national screen required exactly two candidates in the decisive round. That omits valid second-round **plurality** contests where the winner is the highest-vote candidate among three or more. The separate [opportunity ledger](multi-candidate-plurality-opportunities.csv) reconciles twenty such Saxon events within the same 10 pp acquisition gap. The accounting union grows **654→674 source events**, in **649 municipal clusters**. This is not an officially verified 674-case causal sample. The preliminary diagnostic yielded 22 possible records; full candidate-count/rank/winner/share reconciliation changes that set, and does not retain the three Baden-Württemberg leads under these source checks. It is not a finding that those real elections were invalid.

The inspected original [SächsKomWG §44a, no. 4](https://www.revosax.sachsen.de/vorschrift/3818.14) states: “Im zweiten Wahlgang ist gewählt, wer die höchste Stimmenzahl auf sich vereint; bei Stimmengleichheit entscheidet das Los.” The general rule is verified. Exact historical applicability to each event and official declarations remain uncompleted. In these contests, the signed female-versus-male vote difference must use **all valid decisive-round votes**, and the other candidates' separation from the top two must be assessed. Do not apply this zero-margin rule to multi-candidate first-round **majority** contests, choose a third-candidate gap to rescue precision, or pool electoral regimes automatically. Missing names remain explicit; source/predicted labels are not primary assignments.

**Next executable cohort:** the complete seven-event Saxony 2022 multi-candidate cohort, with official source/identity, election-rule, third-candidate and candidate-presentation checks before outcome-selected inclusion. Dresden municipal-source aliases and other municipal entity names must be verified against original buyer/legal-role data; broad fuzzy matching is not a shortcut. This extends the candidate-specific election contrast, not an isolated gender intervention.

## 2. Prototype procedure choice before promising total-bid outcomes

The [2019/2021 bridge inventory](creative-historical-bridge-inventory.csv) finds call metadata in both years for seventeen municipalities. A broader first-document-year discovery, also retaining award-without-prior-call records, finds procedure-detail metadata in both years for **nineteen** municipalities. The [candidate-opportunity ledger](creative-procedure-choice-assignment-opportunities.csv) contains five first-coder mixed leads: Velbert, Rösrath, Iserlohn, Wilnsdorf and Unna. They have not been independently coded or certified for this source/window. These counts do not augment the current supported tender-count inventory.

The generic OCDS `procurementMethod` is insufficient for the proposed negotiated-share measure: some `pt_competitive_negotiation` records are labelled `open`, others `selective`. Literal method details must be traced to original source codes, including `pt_award_contract_without_call`. All-procedure negotiated share still needs a verified reporting universe and a justified no-call timing rule. A narrower competitive-negotiation measure among published called procedures would change the denominator and policy interpretation, and must be documented as such rather than presented as the Italian measure unchanged. A normalized count of published competition types with a fixed pre-election denominator is another candidate, but requires complete scope/reporting and prior population data before missing records can be treated as zero.

**Recommended first prototype:** reconcile original procedure categories, publication/call dates and entity scope for a fixed first-full-post-election window, using a pre-election reporting frame and retaining municipalities with no post matches. Keep single-tender share conditional on recovering actual totals. Do not select the main sample by having a post-election outcome, declare zero procurement from missing matches, or launch a before/after comparison as causal identification. The close-election assignment/design still supplies the proposed causal comparison; the historical panel is for timing, diagnostics and precision.

The [original historical mapping workbook](https://raw.githubusercontent.com/digiwhist/wp2_documents/a5288121f9d685df000e55f9be7d50dafa681c3c/digiwhist_ocds.xlsx) defines `lot (bidsCount)` and plans a `bids/statistics` mapping with measure `bids`. The inspected matched data instead expose only `electronicBids`, `smeBids` and `foreignBidsFromEU`; recursive field inspection found no nested number-of-tenderers/count field in these matched records. **A conversion loss is possible but unproven**: that historical workbook does not describe the current OCP converter, and the native OpenTender download page returned 403. No protected-page bypass was attempted. The downloaded annual snapshots total **86,235,202 compressed bytes** and remain local, with CC BY-NC-SA 4.0 source metadata. Public artifacts contain audit aggregates, not redistributed transformed process records.

## 3. Use pre-election data for precision, with explicit assumptions

The [twelve prespecified planning scenarios](creative-precision-scenarios.csv) treat R² as hypothetical residual-variance reduction under a balanced, independent, equal-variance Gaussian two-group model. At alpha .025/80% power:

| Target effect in original outcome SD | No prognostic gain | Assumed R²=.50 | Assumed R²=.75 |
| --- | ---: | ---: | ---: |
| 0.25 | 612 | 308 | 156 |
| 0.50 | 156 | 80 | 42 |
| 1.00 | 42 | 22 | 14 |

These are neither RDD requirements nor a go threshold. They omit uncertainty/parameter costs of estimating controls, clustering, kernels/slopes, discrete margins and reporting selection. No empirical prognostic relationship is established by finding baseline records. Use compatible truly pre-treatment outcomes/covariates and assess predictions across independent municipalities, avoiding post-treatment controls and significance-driven specifications. Even an imagined six-election balanced sample with R²=.75 has an MDE around **1.87 SD** at the stated alpha/power; the actual six cases are split across incompatible cohorts and cannot be pooled to claim that benchmark. More contracts or a wider arbitrarily chosen RDD bandwidth cannot supply independent elections.

## Candidate and accounting closure

The [bounded completion dispositions](creative-candidate-completion-dispositions.csv) preserve unavailable sources (404/502), current-only named addresses and generic-role evidence as insufficient for historical assignment. Reinspection of an already pinned 2020 campaign original identifies the personal masculine relative pronoun in a named/signed candidate letter; visual text attribution confirms **Lüdenscheid 2020 as same-presentation**. Names, occupations and photographs were not used as gender evidence. The older candidate worksheets, independent-review packet and six-case inventory remain frozen.

The [source-accounting correction](creative-source-accounting.json) reconciles **320 listed archive entries, 318 distinct SHA256 snapshots**, totaling **2,599,690,693 unique retained compressed bytes** before this historical bridge. Earlier 1.125 GiB statements covered newer acquisition tranches and omitted the pre-existing monthly archive cache; they were not a complete repository-storage ledger. Previous receipts/stops are preserved. This batch adds only the two bounded OCDS archives; the total for these listed unique archives plus them is **2,685,925,895 bytes**. Documentation and unrelated repository files are outside that archive total.

## Decision and reproduction

Continue with the two substantive routes above. Do not launch the main study yet: independent coding, official/administrative candidate measurement, exposure/ITT definition, complete outcome reporting, electoral-rule-specific RDD diagnostics and useful cluster-level precision remain gates. No paper, coding packet or message has been sent to anyone. Pages remains deferred.

With the private pinned source/annotation bundle, from repository root:

```sh
python src/pilot/creative_cached_2024.py
python src/pilot/creative_historical_bridge.py
python src/pilot/creative_precision_scenarios.py
python src/pilot/multi_candidate_plurality_screen.py
python src/pilot/creative_candidate_completion.py
python -m unittest discover -s tests
```

The final candidate command revalidates and refreshes the separate follow-up dispositions after the source audits. Original downloads/search and manual annotations are not reproduced by a fresh public clone alone; live websites can change. The source graphs, discovery ledgers, planning scenarios and manual-evidence validators replay against the pinned local bundle. **219 offline tests pass**; old report/baseline/acquisition artifacts remain unchanged. No original/process/person datasets or causal estimates are published.
