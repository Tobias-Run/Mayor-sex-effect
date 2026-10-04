# NRW procedure-specific timing and mayoral term follow-up

Reviewed on **4 October 2026 (UTC)**. This continues the [buyer and phase audit](nrw-buyer-and-phase-audit.md) for the German adaptation of **Florio and Spagnolo (2026), [Female Mayors and Public Procurement](https://doi.org/10.2139/ssrn.7046899)**. The [literature note](../literature.md) retains the German research foundations, including Schild and Baskaran and Hessami. There are no causal estimates or main-study treatment assignments.

**All 123 dated/count observations now have an original-source procedure classification. Of the eight cases without a supported competition date, three are explicitly procedures without a prior call. The remaining five have unresolved competition identity or date.** The inventory remains **237 result notices, 123 observed award-result units across six municipal elections, and 115 supported competition-to-contract pairs**. This step improves measurement and the design specification; it adds no supported competition dates or certified 2020 office-entry dates.

## What the Italian paper actually compares

The primary CEIS PDF was retrieved again from the official university source. Its **793,190 bytes and SHA-256 match the previously reviewed PDF**. The source is now explicitly pinned in the [primary-source manifest](nrw-procedure-term-followup-source-manifest.csv).

The paper distinguishes two outcome populations:

| Primary-paper location | Verified sample or definition | Implication for Germany |
| --- | --- | --- |
| Section 2, printed p. 6 | Open procedures, negotiated procedures with invited bidders, and direct awards are distinct categories | Build a documented country-specific mapping; German source codes are not automatically Italian categories |
| Section 3.1, pp. 7–8 | About 76% of direct awards lack adjudication data, compared with slightly over 40% of open/negotiated procedures | Audit reporting by outcome and procedure; complete award rows can select a different population |
| Table 2, p. 14 | Procedure-choice outcomes include direct awards | Removing all no-call procedures would remove part of the proposed procedure-choice outcome |
| Table 3, p. 15 | Number-of-bidders regressions use the **Open&Negotiated** sample | Define bidder-count eligibility separately from procedure-choice eligibility |
| Section 4, pp. 10–11 | The baseline aggregates procedures published under close-election winners | For German calls, preserve original competition publication; define an explicit timing rule for procedures without a call |

The Italian paper includes direct awards while describing them as contracts assigned without publishing a tender. Its ANAC publication field should therefore **not be assumed to be a prior tender-call date for every procedure type**. This audit does not establish the exact administrative meaning of that field for Italian direct awards. In Germany, substituting the later result-notice publication or contract date would change the exposure definition and needs an explicit argument.

Procedure choice may respond to the election. Restricting bidder analysis to realized competitive procedures creates an outcome-specific selected population. Describe this selection and changes in composition; keep procedure-choice outcomes visible. Such a conditional estimate is not automatically the municipal ITT over all purchases. The [preliminary protocol](../research-protocol.md) now makes these requirements explicit.

## Original-source procedure classifications

The pipeline verifies all **69 retained original result XML notices** and all **63 retained legacy result PDFs**: **132 result notices** with an original procedure classification. Original sources establish the type of every paired observation. The remaining 105 retained indexed notices do not receive an original-source classification in this step.

XML classification uses the primary `cac:TenderingProcess/cbc:ProcedureCode`. Reason codes and reason text remain separate. Legacy classification is restricted to **Section IV.1.1** and checked against the indexed type. The 63 legacy sources contain 48 open, 14 negotiated and one restricted procedure; their previous-competition references remain in the separately audited phase ledger.

| Original XML code | Notices |
| --- | ---: |
| `open` | 43 |
| `neg-w-call` | 9 |
| `neg-wo-call` | 13 |
| `restricted` | 2 |
| `us-free-no-tw` | 2 |
| **Total** | **69** |

Fifty-five XML source codes match the prior index literally. Twelve newly retained notices lack a procedure-type field in their earlier indexed snapshot; original XML supplies it. Two Unna notices, **775139-2023** and **775384-2023**, have original national code `us-free-no-tw` but indexed generic code `oth-single`. Preserve both code values; their equivalence is not assumed from the labels. Neither notice contributes a dated/count observation.

Among the 123 paired observations:

| Source procedure category | Observed units | Supported competition/contract pairs |
| --- | ---: | ---: |
| Open | 98 | 96 |
| Negotiated with prior call | 17 | 14 |
| Restricted | 5 | 5 |
| Negotiated without prior call | 3 | 0 |
| **Total** | **123** | **115** |

The 120 observations outside `neg-wo-call` are a descriptive procedure subset, not an eligible main-analysis sample. German restricted procedures also require an explicit adaptation decision: the Italian bidder table labels its sample Open&Negotiated. Sample membership, analytical units, notice histories, weighting, treatment measurement and actual terms remain unselected.

## Disposition of the eight timing cases

| Result notice | Source finding | Current disposition |
| --- | --- | --- |
| Unna 374488-2024 | `neg-wo-call`; one tender; no primary process-reason text | Separate timing rule needed for a procedure without a prior call |
| Unna 610665-2024 | `neg-wo-call`; one tender; reason code `additional`, describing school IT integration | Separate timing rule needed; do not equate the reason with an independently verified legal exception |
| Unna 657189-2024 | `neg-wo-call`; one tender; reason code `technical`; original text explicitly describes a direct award without competition | Separate timing rule needed; the source cites § 14(4) VgV, without this audit adjudicating legal compliance |
| Geilenkirchen 126957-2024 | Exact same-city project-title candidate 688070-2023, published 13 November 2023; different GUIDs | Identity review; no automatic link or added baseline date |
| Geilenkirchen 196766-2024 | Exact same-city project-title candidate 726123-2023, published 30 November 2023; different GUIDs | Identity review; no automatic link or added baseline date |
| Velbert 17130-2024 | No matching call found in the pinned reference/title searches or complete 2023 municipality queries | Date/identity remains unresolved; search absence does not establish absence of a call |
| Velbert 726107-2024 | Two unlinked competition notices, 485593-2024 and 560607-2024 | Original publication remains under review |
| Velbert 786759-2024 | Two unlinked competition notices, 388784-2024 and 406944-2024 | Original publication remains under review |

Both Geilenkirchen candidate calls are verified in original November 2023 XML, with exact indexed UUID/version and GUID agreement and an aligned sole city buyer. Their titles match the result titles, but **their procedure GUIDs do not**. They may concern a linked procurement history, a restart or another process; title agreement alone cannot choose between these explanations. No stable cross-source identifier has been established. The third discovered KGS Würm call concerns structural engineering and has a different title; it is excluded from these candidate links.

The [candidate-request manifest](nrw-phase-candidate-ted-request-manifest.json) pins five complete public indexed discovery responses: exact internal references (zero results), narrow title searches (three calls), Velbert 2023 competitions (15 notices), all Velbert notice types in that window (35 notices), and a country-filter sensitivity check (the same 15 competitions). The sensitivity check also returns no matching scaffolding call. Results are bounded by the specified queries; they are not universal completeness claims.

## Further official person and term evidence

Three independently accessible municipal sources add [term claims](nrw-term-claim-followup.csv):

| Person and official source | Supported observation | Boundary limitation |
| --- | --- | --- |
| Sabine Anemüller, Viersen's November 2025 farewell publication | Named two-term mayoral history, 2015–2025 | Year boundaries; no exact 2020 renewal date or uninterrupted event-specific term certificate |
| Werner Kolter, Unna's honorary-mayor article | Named predecessor, mayor from 2004 to 2020 | No exact last day in office or first day outside office |
| Dirk Wigant, Unna's council-inauguration article | Oath after reelection on 20 November; accompanying municipal image filenames supply year 2025 | Oath is an event, not proof of legal entry; it cannot date the 2020 term |

The Unna oath's day/month is stated in the article, while its year is corroborated by the municipality's `2025_11_20` image filenames. This provenance is preserved rather than presenting it as a direct legal-entry statement. The regular 1 November council boundary is not substituted for these missing person/event boundaries. No new actual 2020 entry, renewal or predecessor-exit day is assigned.

An independently public Werdohl **official nomination PDF** identifies the two 2020 mayoral candidates, Silvia Voßloh and Andreas Späinghaus, and their occupational presentations. Both identities match the official election finalists after normalizing comma whitespace only; the election file's original `Späinghaus , Andreas` spelling is retained alongside the PDF's `Späinghaus, Andreas`.

The PDF records the committee meeting and signature on **30 July 2020**; its filename contains **14 August 2020**. These dates stay distinct. Section A on PDF page 1 contains the mayoral nominations; council candidates elsewhere are not included. The [derived presentation table](nrw-werdohl-nomination-presentations.csv) retains the named occupational wording without contact details, birth information or residential addresses. It is evidence of a dated official public presentation, **not a registry gender field**. No automated sex/gender or treatment label is assigned from occupation wording.

## Reproduction and remaining work

After reproducing the preceding [buyer/phase audit](nrw-buyer-and-phase-audit.md), run:

```bash
python src/pilot/nrw_procedure_scope.py --download --write-public-tables
python -m unittest discover -s tests
```

The script verifies the original monthly archives and legacy PDFs, the five pinned candidate searches, and all five new primary-source files. Its optional download retrieves independently public primary sources and indexed snapshots only; it does not reacquire protected TED web PDFs. An altered mutable response requires review before changing its pin. Reproduction still depends on the previously archived legacy PDF cohort.

The derived [summary](nrw-procedure-scope-summary.csv), [132 original procedure classifications](nrw-procedure-type-sources.csv), [123 procedure/timing dispositions](nrw-procedure-timing-dispositions.csv), [two conflicting candidates](nrw-phase-conflicting-candidates.csv), term claims and nomination presentations are reproducible. All **118 offline tests pass**, including procedure-code multiplicity, reason/type separation, legacy section scope, no-call timing, conflicting GUIDs, year precision and oath versus entry.

Next work needs explicit timing and outcome rules for no-call procedures, legal/category mapping, resolution of the five competitive-procedure timing cases, the 37 remaining buyer cases and source-supported 2020 term boundaries. Broader independent eligible-election coverage, complete deduplication and a precision assessment remain prerequisites for the main study. GitHub Pages remains deferred until research completion.
