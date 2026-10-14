# P4 exposure and independent-review audit — 15 October 2026

The technical audit is complete. Independent second coding is **not complete**: the project owner confirmed that no independent reviewer is available. No replacement by the first coder or an automated check is counted as independent review.

## Independent-review handoff

The unchanged private packet contains **13 pairs, 26 blank candidate forms and 22 verified source copies** (10,554,768 bytes), including all six current provisional links and seven exclusion/unresolved cases. The separate key covers every linked event. The ZIP is 8,577,956 bytes, SHA256 `b4b03d40c0e8ae149dad998258e2af9c0941394a7ac98d43e0d30f6abc688767`. Archive contents match source hashes; the key is excluded. Neither packet nor key is publicly uploaded.

**Assigned pairs: 0; independently completed pairs: 0.** Candidate agreement, observed disagreements and resolved disagreements are **not available**, rather than zero disagreement or perfect agreement. Preparing and checking a packet does not supply a second observation.

Use the existing [independent-coding protocol](current-cohort-independent-coding-protocol.md). The independent person must declare identity, review date and prior exposure; review all thirteen pairs, including exclusions, without the first-coder key; retain unresolved cases under the existing time bound; and return observations with exact source locators. Hash the return before revealing the key. Preserve both original codes and disagreements before adjudication. Report completion separately for the six linked cases and the seven comparison cases. Reassess inclusion patterns and candidate-role agreement before any causal launch. No person was contacted and no packet was sent.

The forms omit first-coder labels, election winner, margin and procurement outcomes. They retain official identities, municipality and target year to permit identity checks. Original documents and public repository summaries can reveal election and office facts; this is limited masking, not guaranteed blinding.

## Election assignment and exposure rules

The estimand remains election of the particular female-presented candidate against the actual opponent, following the proposed adaptation of Florio and Spagnolo (2026) and the [German literature context](../literature.md). It is not an isolated gender effect.

Retain original election assignment through later turnover for an election **intention-to-treat** analysis. Continuous service by the original winner is a separate exposure sensitivity, not an ITT inclusion requirement. Neither assignment nor eligibility may depend on observing a successful award. An office announcement, oath, statutory term, acceptance and actual procurement decision are different events; do not substitute one for another.

The [six-event exposure ledger](readiness-exposure-audit.csv) reconciles **20 original-supported call procedures and 17 tender statistics**. These remain six provisional elections, not twenty independent assignments. Bückeburg has six supported procedures without an observed supported tender statistic; those remain in the call denominator and are not imputed as zero bids. Multiple lot statistics are not independent elections. Complete reporting is unverified for every case.

The fixed diagnostic comparison rule is **Q1 of the first calendar year after the decisive election**, with the original nine-month call-relative result follow-up target. This is a diagnostic audit, not adoption of a new main-study window. NRW 2025 aligns to 2026 Q1. Werdohl's existing 2025 Q1 and Bückeburg's existing calendar 2025 observations are late-term windows, not their respective first-post-election 2021 Q1 and 2022 Q1 windows. Their earlier evidence remains preserved; the six cannot be pooled as comparable first-year exposure.

Keep the source cutoff at **30 September 2026** despite the later audit date. None of the nine supported NRW-2025 root calls has reached its nine-month target at that cutoff. The eleven older calls have reached it, but maturity does not prove reporting completeness. Contracts can be concluded after the call window and still belong to its follow-up; publication date is a reporting-time proxy, not a verified procurement decision date. Actual decision timing and continuous office exposure remain unverified in all six cases.

## Bounded office-source audit

Eight new retrieval attempts under the pre-recorded twelve-attempt cap yield seven originals and one HTTP 403. Each municipality receives at most two attempts. Existing cached point observations are also hash-verified. See the [source manifest](readiness-source-manifest.csv); raw copies, source quotations and person-level annotations remain local.

| Municipality | Additional official evidence | Limit retained |
|---|---|---|
| Neunkirchen-Seelscheid | Municipal report of entry/first workday on 3 November 2025 | Not independently adjudicated legal acceptance or uninterrupted service |
| Herdecke | New office-page request returned 403; existing 30 January 2026 role observation retained | No new entry date; access failure is not absence from office |
| Lüdenscheid | 29 September 2025 municipal reelection report identifies continued incumbent role | Exact renewal boundary unresolved |
| Lünen | Official report states office since 1 November 2025; oath on 6 November | Entry and oath kept separate; no continuous-history inference |
| Bückeburg | Undated current municipal office page | Retrieval-time observation only; cannot establish 2021 entry or continuous 2025 service |
| Werdohl | Official 2020 annual accounts, physical page 111, records administration-head start on 1 November 2020; 9 July 2025 nomination list records office role | Point/start evidence is not a complete exposure history |

The Werdohl annual-account page was visually checked because text extraction interleaves columns. No newly collected office fact is treated as an independent candidate-presentation recoding.

## Completion status

P4's reproducible packet, office-source, call-timing, reporting-maturity and comparable-window audits are finished. Independent second coding and adjudication remain an external dependency. Zero elections are certified for a main study. P5 can nevertheless decide against launching the current design without pretending P4's review gate has passed.

Replay from the repository root, with the pinned local sources available:

```bash
PYTHONPATH=src/pilot python src/pilot/readiness_p4_p5.py
```

The [input manifest](readiness-p4-p5-input-manifest.json) distinguishes prospective protocol pins from additional replay dependencies locked after retrieval. It identifies private reproduction inputs without uploading them. Public users without those local sources can inspect aggregate outputs and run the source-independent validity tests, but cannot reproduce the original-source audit from the public repository alone.
