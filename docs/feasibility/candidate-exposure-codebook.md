# Candidate and exposure evidence codebook — version 1

Adopted on **5 October 2026**, before the new close-pair evidence screen. This implements FP03 of the [detailed plan](detailed-research-plan.md). It is a feasibility measurement specification, not a preregistration or authorization to estimate causal effects. The project adapts Florio and Spagnolo (2026); German electoral and measurement precedents are documented in the [literature note](../literature.md).

## Measurement and interpretation

Maintain two separate fields: **administratively recorded sex/gender**, when an explicit source field exists, and **documented public gender presentation linked to the 2020 election**. Public presentation is an operational research measure, not a biological-sex or registry-field claim. No source value fills the other field automatically. This screen can establish public-presentation pairs while registry measurement remains unavailable. The final study's interpretation and use of this measure must be explicit in the estimand specification and feasibility decision.

Use `female`, `male`, `other_explicit`, `conflicting`, or `unresolved` only when the evidence warrants that state. Do not force an explicitly different or conflicting presentation into a binary category. Names, photographs, occupations, GERDA predictions/probabilities and knowledge about a person's family do not supply the measure.

## Identity and source rules

1. Preserve the official decisive finalists' names, nomination, municipality, round and exact votes. Unicode/comma/whitespace normalization may support matching; surname particles, given-name swaps and abbreviated identities require documented corroboration. A deputy or similarly named councillor must not replace a finalist.
2. Use named **primary sources**: official municipal/state documents, election or council records, candidate-authored material and identifiable party-authored statements about their own campaign or directly addressed participants. News and encyclopaedias can identify leads but do not pass the primary-source rule. Primary authorship is recorded separately from political impartiality.
3. An explicit named `Frau`/`Herr`, gender-specific self-identification or unambiguous person-specific pronoun can establish public presentation. A specifically named `Bürgermeisterin`/`Bürgermeisterkandidatin`/`Bewerberin` is explicit feminine presentation; an explicit personal description such as `CDU-Mann` can establish masculine presentation. Generic masculine office/candidate labels, plural groups, occupational suffixes and boilerplate greetings do not establish male presentation on their own. Record enough local context to distinguish a personal statement from grammatical agreement with an office noun.
4. Accept historical linkage only when the source's substantive context explicitly concerns the **2020 candidacy, election, contemporaneous role or named 2020 activity**. A 2019 nomination explicitly for the 2020 election qualifies. A later source explicitly describing the named 2020 event can qualify as retrospective evidence and must carry that flag. Current pages, an unrelated 2017 role or a 2024 title do not automatically establish 2020 presentation or justify interpolation.
5. Inspect the original accessible page/PDF, not only a search snippet. Pin URL, provider, retrieval time, bytes/checksum, publication/document/event date with precision, page or section and a short exact locator. Visible page dates and named event dates are distinct; search-engine publication ages are not source dates. Keep unverifiable/undated content explicit.
6. Review relevant existing sources before fetching more. Retain all reviewed contradictions. A candidate is classified only if accepted evidence agrees; conflicting evidence remains conflicting pending review. Lack of accepted evidence is unresolved, never proof that the two finalists share a gender.

| Evidence tier | Meaning | Can support the 2020 presentation screen? |
| --- | --- | --- |
| A | Explicit administrative sex/gender field with suitable identity and historical provenance | Yes, with original field semantics retained; registry and presentation fields remain distinct |
| B | Official primary document explicitly presenting the named candidate in the 2020 event/role context | Yes, as public presentation |
| C | Candidate/party primary statement explicitly presenting the named candidate in the 2020 context | Yes, as public presentation; source authorship is a visible sensitivity dimension |
| D | Current/undated or unrelated historical primary presentation | Corroboration/discovery only; no 2020 assignment |
| E | Predicted, secondary-only, generic-title, occupation-only, inaccessible or ambiguous evidence | No; record the precise reason |

An archival URL or dated meeting header is evidence of document context, not proof that a live page has never changed. Retain this limitation and cached original bytes. Do not record birth dates, home addresses, telephone numbers or other irrelevant personal details in derived public artifacts.

## Pair status and running variable

The acquisition universe is all **55 official decisive two-person pairs within an inclusive 10 percentage-point absolute candidate-to-candidate margin**, ordered by exact margin. Begin with the **15 within 2 pp**. Include all predicted-label combinations. These cutoffs prioritize acquisition; they do not choose an econometric bandwidth. Do not consult procurement outcomes to select candidate evidence.

For each finalist, retain an independently sourced disposition. Pair status is `mixed_public_presentation`, `same_public_presentation`, `unresolved`, or `conflicting_or_other`. Both historical presentation fields must be supported before assigning a mixed or same status. Keep administrative-field pair status separate. Main-study treatment and exposure eligibility stay pending.

For a supported mixed presentation pair, calculate the exploratory **signed candidate-to-candidate margin** as `(female-presented votes - male-presented votes) / valid decisive votes * 100`, and record which candidate won. Use exact runoff votes where there is a runoff, otherwise exact two-candidate first-round votes. Verify the two counts sum to the official valid-vote denominator and the winner agrees. Do not use rounded percentages, the distance above 50%, or a male-male/female-female formula. Unresolved pairs have no signed gender margin or assigned female-win flag.

Report all 55 dispositions, the first 15 separately, evidence tier and source-date limitations, and the number of mixed pairs/female wins/female losses by descriptive margin. Public presentation counts are not certified registry-sex counts, approved main-study eligibility or a power calculation.

## Exposure and office-date rules

Store official election dates independently of actual head-role intervals, initial/renewal terms, successor entry, early exit and interruptions. Formal NRW entry involves acceptance and predecessor exit; no separate appointment is required. Council calendars, oath, first workday, first observed election and GERDA's constructed panel dates are distinct evidence types; see the [historical legal audit](nrw-term-law.md).

Prefer named official histories or event records with explicit dates. Represent year-only intervals and ambiguous entry/exit as bounds, preserving date precision and contradictions rather than filling a specific day. Earlier uncertainty can be immaterial to a later observation window only when relevant later continuity/turnover is independently supported. A deputy record's end date is not the full-time mayor's tenure end. Current-office pages cannot certify an uninterrupted historical term.

The upcoming FP04 window/estimand specification must distinguish fixed-window election ITT, retaining original assignment through turnover, from outcomes during the original winner's officeholding. This candidate screen does not choose that estimand or certify procurement exposure. Personal mayoral signatures are not an eligibility requirement for municipal procurement.

## Audit records and closure

Local candidate records use event/candidate identifiers, official name, reviewed source IDs, registry value/provenance, historical presentation, tier, short locator, date context, reviewer disposition and reason. Public summaries expose event-level statuses and source manifests; raw/derived person datasets remain local under the [data policy](../data-management.md).

FP03 closes when this rule set, fields and uncertainty handling are documented. FP05 closes when all 55 pairs have a recorded evidence-review disposition with source or failed-search provenance, not when all candidates are successfully classified. Distinguish a fully verified pair from an unresolved pair whose review is complete. Revisions to these rules receive a version/date and decision-log entry; recompute the whole screen after a substantive rule change.
