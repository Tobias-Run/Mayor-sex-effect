# Independent candidate coding and selection audit

**Protocol version 1, 5 October 2026. Status: prepared; no independent reviewer assigned or second coding completed.** This implements the supervisory feedback and [early feasibility decision](early-feasibility-decision.md). It is a quality gate before main-study eligibility is frozen. An additional pass by the first coder, a source-hash check or a program validating existing evidence locators is not independent coding.

The measurement is the unchanged [candidate/exposure codebook](candidate-exposure-codebook.md): historically linked public presentation, with administrative fields, identity, temporal linkage and uncertainty kept separate. Study scope and interpretation continue to adapt Florio and Spagnolo (2026) using the cited German precedents.

## Review population and packet

Review **all 16 currently classified pairs**: six mixed and ten same-presentation exclusions. Also review **12 of the 39 unresolved pairs**: four from the eight pairs with one supported candidate, eight from the 31 with neither candidate supported. Include both unresolved pairs within 2 pp first; choose the remaining cases by the reproducible hash ordering in `nrw_early_feasibility.py`. This is a purposive/stratified audit, not a probability sample supporting an unweighted population error rate.

The generator has prepared 28 pairs / 56 candidate forms under **`data/interim/nrw-independent-review/`**. The first-coder mapping/labels are stored separately under **`data/interim/nrw-independent-review-key/`**. Both directories are ignored by Git. Public output is only this protocol, the aggregate preparation status and the [empty template](independent-coding-template.csv). No originals/person-level packet is uploaded or sent to anyone by preparing it.

Each packet contains an opaque case ID, shuffled candidate slots, official names/municipality solely for identity checks, the target event year, the measurement codebook and available pinned primary/discovery originals. It omits the first coder's labels, accepted quotations, votes, margins, winner flag and GERDA predictions. Source filenames, municipal identity and original text can reveal election/office facts; **full blinding is not guaranteed**. The reviewer must disclose prior exposure to the results.

Available sources were found in the first search, which can itself select documentation. Record unsuccessful access and allow an equally budgeted independent search for a genuinely missing original. A neutral source list cannot prove complete candidate documentation.

## Coding and reconciliation

1. A separate reviewer records an independent result for both candidate slots **before receiving the first-coder key**. Use `female`, `male`, `other_explicit`, `unresolved` or `conflicting` only as the codebook supports. Complete identity, source authorship, exact locator/page, 2020 historical linkage, review date and reviewer identity. Names/photos/predictions are not evidence.
2. Preserve the independent form as an immutable dated/hash-pinned file. If further search is needed, allocate the same initial budget per unresolved candidate—up to 10 minutes—and record actual effort and failed routes. Stop at the limit rather than infer a label. Extra time requires a recorded reason and the finite checkpoint reserve, not an indefinite search.
3. Reveal the first-coder key and reconcile disagreements **against original evidence**. Record agreement, changed identity/temporal/authorship decisions, first-versus-second uncertainty and every eligibility-changing discrepancy. Do not resolve by majority vote or favor the label that adds a mixed pair.
4. Use a separate adjudicator or documented unresolved status for a material remaining disagreement. Preserve both initial records and the resolution provenance. A sourced administrative field discovered later is a distinct measure, not a silent replacement for public presentation.
5. Re-run the existing evidence validator after approved annotation changes and regenerate event-level counts. Freeze the sample only after all provisionally included mixed pairs receive independent review/adjudication. Review same-presentation exclusions and sampled unknowns to detect false negatives, not only agreement among included cases.

Report candidate and pair agreement, unresolved/conflicting rates, eligibility-changing disagreements, direction of changes and evidence tiers. With this small selected audit, descriptive agreement and case dispositions matter more than a single kappa value. Agreement statistics do not validate construct measurement, eliminate source selection or establish administrative sex/gender.

## Selection audit beyond coder agreement

Compare classified versus unresolved pairs and linked versus unlinked outcomes using fixed, pre-election or acquisition-provenance variables:

| Dimension | Current availability | Interpretation |
| --- | --- | --- |
| Winner versus loser evidence | Complete original winner identities and all 110 candidate dispositions | 22 winners versus 18 losers supported; paired availability patterns retain winner-only/loser-only cases |
| Exact margins and decisive round | Source-validated official NRW votes | Search prioritization differs across bands; acquisition bands are not chosen analysis bandwidths |
| Acquired non-election official documents | Available from the primary-source manifest | Excludes official vote files; documentation count reflects acquisition effort and relevance varies |
| Candidate incumbency before election | Not harmonized/validated for this screen | Do not infer from a current title or post-election biography alone; keep missing |
| Municipal population/fiscal characteristics before election | Not yet matched as compatible official 2019 covariates | Necessary to assess municipal-size/documentation selection; not substitute post-election values |
| Historical web availability and search effort | Route outcomes, source dates and exact search logs partly available | Report protected/unavailable routes and priority follow-ups; do not treat absence from the web as absence of a characteristic |
| Procurement availability by category/date/municipality | Incomplete pilot inventory | No matching record is not zero procurement; inspect outcome-specific reporting and censoring separately |

The [early selection table](nrw-early-selection-audit.csv) is descriptive. It does not estimate the causal effect of strict evidence standards or establish missing-at-random. Preserve unknown labels; any changed evidence standard would require a new codebook version, construct justification and symmetric application to winners/losers and all eligible cases. Do not relax it to obtain a desired sample size.

No reviewer has been contacted or source packet sent. The independent review requires a separate person's completed record and cannot be reported as finished by preparing these materials.
