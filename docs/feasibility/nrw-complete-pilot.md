# NRW: complete pilot notice coverage and outcome audit

Checked on 4 October 2026 (Europe/Berlin). This extends the [previous follow-up](nrw-pilot-completion.md) within the fixed 2021–2024 publication-window query for Iserlohn, Velbert and Geilenkirchen. It supports the German adaptation of **Florio and Spagnolo's [Female Mayors and Public Procurement](https://doi.org/10.2139/ssrn.7046899)**; the [literature note](../literature.md) documents the German precedents. No treatment effects have been estimated.

**Full PDFs now cover all 92 retained municipal notices.** The audit extracts 112 observed award-result units, of which **106 have both an explicit contract date and a total tender count**. Six notices require further outcome review, eight are explicit non-awards, and one reports an unfinished competition. There are still only **three independent electoral events**, and these units are not a final analytical sample.

## Coverage and counts

The [complete source manifest](nrw-complete-ted-source-manifest.csv) contains **96 pinned PDFs**: the existing 50 plus 46 newly acquired sources. Ninety-two belong to the retained municipal cohort; four were already inspected and excluded during buyer-scope review. The original 115-notice search and its 92 retained / 23 excluded decisions are unchanged. This completes full-text acquisition for that cohort, rather than establishing complete municipal procurement coverage.

| Full-document measure | Count |
| --- | ---: |
| Retained municipal notices with pinned PDFs | **92 / 92** |
| Notices with supported award-result layouts | 77 |
| Explicit non-award notices | 8 |
| Explicit pending competition | 1 |
| Notices requiring outcome review | **6** |
| Observed award-result units | **112** |
| Legacy / eForm units | 88 / 24 |
| Units with an explicit contract date | 109 |
| Units with an explicit total tender count | 108 |
| Units with both fields | **106** |
| One-euro / one-cent award values requiring review | 17 / 1 |
| Notices with conflicting notice-total / award-sum values | **8** |
| Notices with an award lot absent from the lot definitions | 1 |
| Dated Geilenkirchen units inside its documented head-role interval | 17 |
| Independent electoral events | **3** |
| Approved main treatment / procurement-responsibility assignments | **0** |

| Municipality | Retained notices | Observed award units | Units with date and total count |
| --- | ---: | ---: | ---: |
| Iserlohn | 37 | 44 | 44 |
| Velbert | 38 | 50 | 45 |
| Geilenkirchen | 17 | 18 | 17 |
| Total | **92** | **112** | **106** |

The 112 units include the previous 57; the 106 dated/count units include the previous 52. Do not sum these successive totals. One grouped-lot award remains a single observation. Counts describe explicit source sections; procedure duplication, eligibility, source inconsistencies and municipal responsibility still require review.

## Separate valid dates/counts from conflicting prices

Seven additional legacy notices report clear award dates and total tender counts but conflicting notice and award values. The parser now retains those fields separately and marks every affected monetary outcome for review. It never rescales an award to match a notice total or replaces an awarded amount with an estimate.

For example, [151563-2021](https://ted.europa.eu/de/notice/151563-2021/pdf) reports **8 March 2021 and 17 tenders**, a notice total of EUR 200,000.00, and an awarded value of EUR 203,906.52. [587521-2023](https://ted.europa.eu/de/notice/587521-2023/pdf) reports **14 September 2023 and two tenders**, but a winning value of **EUR 0.01** against EUR 560,000.00 in the notice total. The cent value is flagged separately from a missing price. These sources support date/count extraction without establishing valid economic price outcomes.

Explicit numeric lot labels such as `01` in definitions and `1` in award sections are compared after numeric normalization, with original labels preserved. Undefined, overlapping, duplicated or uncovered lots cannot pass the value-mismatch recovery branch. The [previous bid-range and grouped-lot safeguards](nrw-pilot-completion.md) remain in place.

The additional cross-check also flags [194586-2023](https://ted.europa.eu/de/notice/194586-2023/pdf): Section II defines lots 1–3, while Section V explicitly awards lots 1–4. Its four dated/count award sections remain observed source results, but lot 4 has no matching definition and is flagged individually. This case was already among the earlier reviewed notices. Value reconciliation alone does not establish complete lot mapping or criterion linkage.

## Pending results and unresolved winner information

In [424806-2024](https://ted.europa.eu/de/notice/424806-2024/pdf), the result explicitly says **“Ein Wettbewerbsgewinner wurde noch nicht ermittelt, der Wettbewerb ist noch nicht abgeschlossen.”** Its three received tenders are excluded from awarded outcomes. This status stays separate from a closed cancellation and from missing information.

The [review register](nrw-complete-ted-review.csv) records the six unresolved notices, the pending procedure and the separate lot-definition flag:

| Notice(s) | Remaining issue |
| --- | --- |
| 126957-2024 | Two contract-information blocks in one lot, with differently spelled versions of the same firm's name; no assumed merger or two-contract count |
| 373198-2022 | Two declared lots but one unnumbered award section; no allocation of its count across invented lot observations |
| 50377-2024, 51385-2024 | Awarded status, but the displayed bidder is in the **unsuccessful-bidders** section and no winner section is supplied |
| 315323-2024, 406057-2024 | Awarded status and statistics without a winner-information section; contract linkage remains incomplete |

Prices and dates are now read only from the eForm winner-information section. An unsuccessful bidder's zero-value offer cannot become a winning price. Typed total tenders remain distinct from electronic/SME subsets and participation requests. Missing contract dates are not filled from winner-selection dates.

## Legal calendar and next research work

The [historical legal audit](nrw-term-law.md) verifies the 1 November 2020 council-period boundary and the mayoral entry rule. **NRW mayoral office does not require a separate appointment.** Acceptance of the election and predecessor exit determine entry; an oath or the general calendar alone does not prove an individual's start. Of the 112 observed award units, 108 dates fall within the regular council period, one precedes it and three dates are missing. These are calendar comparisons, not authority assignments.

Next, obtain person/event evidence for election acceptance, predecessor exit and renewed terms; audit acting officeholders and delegated or represented purchasing; and establish procedure/contract deduplication. Validate historical presentation measurement, price meaning and environmental/social criteria before extending to further close-election municipalities. TED excludes procurement below reporting thresholds and the current query omits other notice types. More contract rows do not supply more independent elections or resolve the precision gate.

## Reproduction

First reproduce the [statewide register](nrw-statewide-election-register.md#reproduce-and-inspect) and the [expanded buyer-scope pipeline](nrw-expanded-pilot.md#reproduce-the-supplement), including the official role evidence. Then run:

```bash
python src/pilot/nrw_full_ted_awards.py --download \
  --manifest docs/feasibility/nrw-complete-ted-source-manifest.csv \
  --raw-root data/raw/nrw-complete-ted \
  --out outputs/nrw-complete-ted --require-complete-cohort
python src/pilot/nrw_term_law.py --download
python -m unittest discover -s tests -q
```

Omit `--download` to audit cached sources. The original full-notice command retains its earlier manifest/output defaults; the complete cohort uses explicit arguments and a completeness check. Source changes require review before updating pins. All 96 PDF hashes are verified locally, both real-source pipelines complete, and **58 offline tests pass**. The [aggregate summary](nrw-complete-pilot-summary.csv) records the current counts.

Public artifacts contain original code, source manifests, limited cited evidence and aggregate summaries. Raw PDFs/pages, person-level evidence and complete award records remain local and ignored by Git. GitHub Pages remains deferred until the research is complete.
