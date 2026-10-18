# Independent candidate-coding assignment

18 October 2026 · Standalone instructions · Unassigned

**For the project owner:** provide this document with the existing neutral local packet only. Do not include the supervisor briefing, manuscript, first-coder key, adjudication records or outcome summaries. The packet has not been sent. This document restates the existing coding rules for the target year printed on each form; it does not revise the codebook or authorize new data collection.

## Purpose and scope

Independently assess the historical public gender presentation of each supplied candidate using explicit evidence. This operational measure is separate from administrative sex/gender. The assignment contains **26 candidate forms in 13 pairs**, identified by neutral case and slot IDs. Complete every form, including cases that remain unresolved. Do not infer the expected classification or try to reproduce another coder's judgement.

Before starting, record your reviewer identity, review date and prior exposure to this project or its classifications. Avoid the public project summaries until your return has been frozen. Sources themselves may reveal office/election facts, so perfect masking is not promised. If you already know a case or have read project results, disclose that exposure; do not conceal it or assume that a neutral filename makes the judgement independent.

## Coding rules

1. **Confirm identity and target context.** Use the supplied official identity, municipality and target election year. A similar name, deputy or different councillor is not the candidate. Document corroboration for abbreviated identities.
2. **Require primary authorship.** Suitable originals include official municipal/state records, candidate-authored material and identifiable party-authored statements concerning their own candidate or directly addressed participant. News, encyclopaedias and search snippets are discovery material, not accepted evidence.
3. **Require explicit personal presentation.** A named personal address such as `Frau`/`Herr`, a clear person-specific pronoun, explicit self-identification or a specifically named feminine candidate/office description can support presentation. Generic masculine office nouns, plural groups, occupations, names, photographs, predictions and family information cannot supply a label.
4. **Require historical linkage to the year on the form.** Contemporaneous election/role/activity evidence can qualify. An earlier nomination explicitly for that election or a later explicit description of that event can qualify; flag retrospective evidence. Current titles, unrelated historical roles and undated pages do not automatically establish presentation at the target election.
5. **Inspect original context.** Record the source file, physical PDF page or HTML section, a short exact locator, date/context and reason the identity, authorship and historical linkage qualify. Distinguish publication date from event date; do not infer dates from search-engine ages.
6. **Retain uncertainty and contradictions.** Use `female`, `male`, `other_explicit`, `conflicting` or `unresolved`. Do not force nonbinary/other or contradictory evidence into a binary label. Missing evidence does not show that two candidates have the same presentation. Record an explicit administrative field separately, preserving its meaning; it must not silently fill the public-presentation field.

## Work and return format

Use the supplied `blank-review-forms.csv`. Preserve the existing case/slot and official-identity fields. Fill the existing columns:

- `independent_presentation`
- `administrative_measure_if_explicit`
- `source_file`, `exact_locator`
- `identity_status`, `primary_authorship`, `historical_target_link`, `event_date`
- `uncertainty_reason`
- `reviewer_identity`, `review_date`, `prior_exposure_disclosed`

Work from the supplied original-source copies. Preserve the existing unresolved-candidate allowance of at most ten minutes of additional checking; log the effort and stop with `unresolved` if the source conditions cannot be met. This packet handoff does not authorize an additional web-acquisition batch. Identify missing sources rather than expanding the assignment silently. Do not calculate treatment margins, seek procurement outcomes or decide study eligibility.

Return all 26 dispositions in a **new versioned copy** of the CSV. Keep the original blank packet intact. Any necessary supplementary note should refer only to neutral case/slot IDs and source locators. Do not send personal birth dates, addresses, telephone numbers or unrelated personal details. Use an agreed private return channel; the project has not selected one, contacted anyone or authorized a public upload.

## Freeze before comparison

The project owner must preserve the returned bytes, record receipt date and compute a SHA-256 hash **before** revealing first-coder labels or the separate key. For example, run `sha256sum returned-review-forms.csv` locally and retain the output with the immutable return. Never regenerate the prepared packet over partial or completed reviewer work.

Only then compare the two original coding sets. Preserve every original code and disagreement. Resolve differences against original sources with a written reason, or retain unresolved status; neither majority vote nor a repeated model run supplies an independent observation. Report completed candidates/pairs, missing returns, explicit unresolved/other/conflicting classifications and missingness separately from agreement. Agreement among comparable completed codes needs a stated denominator; no return means agreement is unavailable, not perfect.

This review does not itself certify legal office entry, reporting coverage, procurement decision timing, causal identification or main-study launch. Any later substantive review should follow the frozen coding return, with prior exposure documented.
