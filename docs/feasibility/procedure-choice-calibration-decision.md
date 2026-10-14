# P3 decision: historical procedure-choice calibration

14 October 2026. Execution of step P3 in the [measurable-progress plan](measurable-progress-plan-2026-10-14.md). The complete availability audit and all ten case dispositions are delivered. **The proposed outcome is not yet validated:** only two original notices were acquired, and no calibration case has original evidence in both periods. A completed disposition is not a passed validation.

## Complete 55-election denominator

The [availability table](procedure-choice-calibration-availability.csv) retains every NRW 2020 election in the fixed frame, independently of candidate presentation and procurement availability. Re-reading the two source-pinned annual OCDS snapshots reconciles all **380 matched compiled processes** and the existing **338 first-document-year records**. There are 31 municipalities with any such record and 24 without; missing source matches do not establish zero procurement. Nineteen have pre/post method-detail metadata, seventeen have pre/post call metadata, and five are already coded mixed-presentation method leads. These are unchanged acquisition opportunities, not newly eligible elections.

| Source-availability measure | 2019 | 2021 |
|---|---:|---:|
| First-document-year compiled processes | 160 | 178 |
| With call metadata | 138 | 170 |
| Award-only metadata | 22 | 8 |
| Explicit no-call category | 4 | 7 |
| No-call process with missing award-date metadata | 0 | 1 |
| No-call process with award date outside source year | 1 | 1 |
| Broad `open` field paired with competitive-negotiation detail | 4 | 1 |

The snapshots are transformed data under the source's stated CC BY-NC-SA 4.0 licence. We publish aggregate/municipality diagnostics and source provenance; full process records, originals, contact and supplier information remain local. Annual file labels, release dates and first-document dates are not interchangeable with procurement decisions.

## Fixed selection and ten explicit dispositions

The [selection ledger](procedure-choice-calibration-selection.csv) applies the exact published SHA256 rule and preserves the negative control. It was pinned before new original inspection. No shortfall amendment or case substitution was needed.

| Stratum | Cases | Usable originals obtained | Current disposition |
|---|---|---:|---|
| Mixed pre/post method leads | Rösrath, Wilnsdorf, Iserlohn, Velbert, Unna | 2, in Rösrath and Velbert | Partial original support; no case original-supported in both periods |
| Supported same-presentation controls | Lüdenscheid, Beckum | 0 | Original access unresolved |
| Unresolved presentation with pre/post metadata | Lünen, Viersen | 0 | Original access unresolved |
| No pre/post method match | Kempen | 0 | No 2019 source match; original access unresolved |

The [case audit](procedure-choice-calibration-cases.csv) records all ten dispositions: attempted sources, usable originals, period-specific support, buyer/method flags, explicit no-call records, duplicate references and unresolved gates. Losing candidates, same-presentation pairs and unmatched elections remain visible. The five mixed leads are one female-presented win/four losses; they are neither five new supported count outcomes nor a usable causal sample.

## What the original notices establish

The [original-check ledger](procedure-choice-calibration-original-checks.csv) supports two bounded findings:

- **Rösrath, notice 47183-2019:** original Section IV.1.1 confirms the detailed open-procedure category; publication was 31 January and dispatch 28 January 2019. Section I names Stadt Rösrath, but its authority-type field describes a national/federal authority, and the contact address is in Düsseldorf. Record the internal scope inconsistency rather than silently treating the authority type as verified municipal scope. An agent/contact address alone neither changes the named buyer nor resolves the inconsistency.
- **Velbert, notice 119630-2021:** original Section IV.1.1 confirms competitive negotiation and a regional/local authority. Publication was 10 March and dispatch 5 March 2021. The transformed **detailed** category agrees. Its broad field is **`selective`**, not `open`; the five broad-open/negotiation combinations elsewhere in the snapshots are a separate unverified-original finding.

These are two accessible examples, not a representative method-accuracy rate. They do not establish complete original procedure/award graphs, all revisions, actual municipal decision dates or common pre/post outcome coverage.

## Timing, no-call procedures and repeated publications

Re-reading the native OCDS fields adds a concrete timing audit: eleven explicit no-call records have ten observed award-date fields, of which two fall outside the annual source year. For example, a Viersen notice first published in January 2019 has a **17 December 2018** award date in the transformed source; an Erftstadt January 2021 notice has **23 December 2020**. Unna's explicit no-call record lacks an award date. These dates remain original-unverified. Award conclusion itself would also be a different event from choosing the procurement method.

Across all 380 matched compiled records, **112 repeated document references** occur within processes, often from separate lot-award blocks. They are collapsed for notice/source checks, not counted as additional procedures. Within the 338 first-document-year records, 97 such repetitions are observed. No exact source URL is observed across multiple compiled OCIDs in this matched extract, but that does not certify that OCDS IDs identify unique municipal procedures or that corrections are complete. Full original linkage and revision reconciliation remain open.

A first-document-year denominator would mix called procedures with award-only records using different phases and reporting lags. An award-only record is not automatically no-call procurement. A call-only denominator would instead omit the very no-call behaviour relevant to the broad negotiated-procedure outcome. Neither denominator can be silently substituted for the other.

## Source budget and access limits

The initial case/source queue is pinned locally. There were **30 total retrieval attempts**, including 26 HTTP 202 responses with no bytes and two inaccessible browsing-tool requests. Two English original representations were successfully retained and checksummed. The official [TED direct-link documentation](https://ted.europa.eu/en/simap/developers-corner-for-reusers) supports the XML/HTML/PDF representations used. Format changes preserved the cases, recorded failures and the thirty-attempt ceiling, prioritizing a source for every available case/period before optional checks. All nineteen available case/period targets were attempted; four optional targets remained unattempted when the budget stopped. No access-control bypass, bulk archive tranche or outreach occurred.

The [retrieval manifest](procedure-choice-calibration-source-manifest.csv) distinguishes attempts from usable original evidence. HTTP success/acceptance, search snippets and third-party reproductions do not count as source validation. Access failures are an acquisition limitation and do not establish that the underlying procedures are invalid. The resulting severe source-access selection precludes extrapolating the two accessible originals to the whole frame.

## Proposed measure and decision

The [dated outcome/population addendum](procedure-choice-prototype-addendum-2026-10-14.md) specifies one proposed measure: competitive-negotiation share among original-supported **advertised** municipal procedures, with explicit numerator, denominator, publication-time rule, separate dispatch/decision dates, common 2019/2021 windows and undefined-denominator handling. This is a conditional measurement proposal, with a narrower target than all municipal procurement. It has not replaced the frozen outcome codebook or expanded the primary family.

**The all-procedure negotiated share fails the present validation gate. The narrower called-procedure proposal also remains unvalidated.** Complete comparable reporting, no-call timing, original graph coverage, buyer-role reconciliation, undefined shares and treatment-induced reporting/selection remain unresolved. No rate, effect or empirical prognostic R-squared is estimated. There is no original-supported pre/post calibration pair, no added mixed-count election and no main-study certification. The current six provisional mixed-count links and P1/P2 scoreboard remain unchanged.

P3 is complete as a bounded calibration attempt with a negative readiness decision. This finding supports proceeding to the planned independent review/precision decision, rather than another unspecified source hunt or a causal launch. Any renewed acquisition must identify a demonstrably workable source route and a new finite batch before starting; access failures alone do not warrant ending the scientific causal claim. GitHub Pages remains deferred until research completion.

## Verification

233 offline tests pass, including selection-order invariance, unmatched-control retention, publication/award-year separation, repeated-source collapsing, scoped original procedure parsing and buyer/country conflicts. The seven public calibration artifacts reproduce byte-for-byte from pinned local inputs; the earlier report, P1/P2 tables and source inputs remain unchanged. Full replay requires the private original/compiled-source bundle and `python src/pilot/procedure_choice_calibration.py` from the repository root. Publication contains no raw originals or process-level dataset.
