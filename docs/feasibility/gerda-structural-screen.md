# GERDA structural and gender-provenance screen

Run date: 3 October 2026. This is a conservative feasibility screen of a pinned research compilation. It is not a preregistered sample, an institutional-design validation, or a power analysis. No procurement outcomes or treatment-effect estimates were inspected.

## Source and temporal scope

Source commit: `030c1fb865ec4e6ef94d5dee2039edde081a0f5d`. Candidate CSV checksum: `5cf7c8f7695cf17d3001ffe49ba5bb5a8f2800be8426754c1db3143b200fba0e`. The script checks the local file against the retrieval manifest before screening.

The full file contains 113,345 candidate rows grouped into 49,513 event keys (state, municipality identifier, first-round date, election type). Screening uses **decisive dates from 1 January 2020 through 3 October 2026**. Starting in January rather than October deliberately retains elections whose terms might overlap procurement collection starting in October 2020. Actual procurement overlap and term timing are not yet established.

Later dates in the downloaded snapshot are excluded. A mutable dataset can contain future-dated or subsequently revised material; the pinned snapshot is not evidence that all rows were available at their historical election dates.

## Conservative structural rules

- Include municipal mayor and lord-mayor election types; exclude municipal-association executives and an inconsistent county-office label.
- Exclude records flagged superseded, shared municipality identifier or missing decisive round.
- If a runoff is recorded, use its dated two finalists with exact votes. Do not use first-round vote totals as runoff denominators.
- Otherwise require exactly two candidates, exact votes summing to recorded valid first-round votes, and consistent candidate count metadata.
- Require one declared winner, final ranks 1 and 2, agreement between winner and rank, nonnegative integral votes, no tie, and final share agreement within 0.0001 of vote-derived shares.
- Keep source-reported (`raw`) and predicted gender labels distinct. Unknown values remain unknown. A `raw` label still needs source audit and is not automatically a fully approved observation.

These rules deliberately omit potential eligible multi-candidate first-round victories, percentage-only records, write-in complications and exceptional contests. Counts are for this screen, not the complete population of potentially valid elections. Rounded displayed shares or other denominator conventions can trigger the share check; excluded cases require review rather than automatic treatment as bad source data. No final RDD bandwidth has been chosen.

## Bayern and NRW focus: 2020 election cohort

| Screen result | Bayern | NRW |
| --- | --- | --- |
| Structurally passing two-person decisive contests | 906 | 214 |
| Mixed gender labels, prediction involved | 0 established | 72 |
| Gender unresolved for the pair | 906 | 0 under upstream labels |
| Predicted mixed-label contests within 1 pp | Not established | 2 |
| Predicted mixed-label contests within 2 pp | Not established | 5 |
| Predicted mixed-label contests within 5 pp | Not established | 9 |
| Predicted mixed-label contests within 10 pp | Not established | 17 |

Bayern's zero is **not** evidence of zero mixed-gender elections. Its 2020 candidate data have no gender labels available for complete pairs. Among those 906 structurally passing pairs, 125 are within 5 pp across all unknown gender combinations. That subset is a prioritization lead, not 125 identified mixed-gender races.

NRW's 214 includes structurally passing two-candidate outright first-round contests and runoffs, including independent cities where present in GERDA. It is not the previous 102-event district-municipality runoff audit. Within the earlier 102-event subset, exact runoff votes had already matched the official files 102/102.

For the 2020–2024 window, Bayern has 997 structurally passing pairs with unresolved gender, 140 within 5 pp. NRW remains at 214 pairs under this source/window, including the same 72 predicted mixed-label events. This is source coverage, not proof that NRW held no other elections during 2021–2024.

## All-state audit

The [aggregate CSV](gerda-screen-summary.csv) reports the conservative screen through the cutoff for all 13 states. It should guide source checks, not state inclusion in the main research design. Different electoral rules, nomination formats, historical redaction and incomplete sources make direct count comparisons potentially misleading.

Source and schema checks also exposed an entry with a fractional candidate vote count, a county-office label in the mayoral file, ties, missing counts, and 497 cases failing the share-reconciliation threshold (mostly Thüringen). These are documented screening exclusions, not proof of widespread measurement error. The remaining diagnostic counts are saved in local output. No problematic values were silently rounded or imputed.

## Reproduction and validation

```sh
python src/pilot/gerda_structural_screen.py
```

Prerequisites: Python standard library, the downloaded pinned CSV under `data/raw/gerda/mayoral_candidates.csv`, and its `retrieval.json` manifest. The acquisition commit and checksum are above; the file is available through the pinned GitHub media URL recorded in the manifest. Candidate data and event-level output remain ignored by Git.

The script saves all-state summaries, exclusion reasons and an event screen under `outputs/gerda-screen/`. It was executed successfully. Additional checks compared the Iserlohn exact margin against the independently validated official count and verified rejection of flagged or invalid-winner records. Upstream predicted gender was preserved as prediction in that check.

## Replication-archive follow-up

Requests to Harvard Dataverse's dataset API for DOI `10.7910/DVN/FZWOMK` and the OpenICPSR project page for `10.3886/E114710V1` returned HTTP 403. The archive links exist in earlier documentation/article pages, but their file contents were not inspected in this run. Do not infer that no public replication files exist or claim that they supply Bayern data. The Hessami lead concerns Hessen, which is institutionally and geographically separate from Bayern.

## Next actions

1. Review official evidence for both finalists in the nine NRW 2020 predicted mixed-label events within 5 pp, including actual terms. Broaden to adjacent margins after establishing the verification route; maintain a coverage log to avoid selective silent exclusions.
2. Clarify access to source-recorded historical Bayern candidate gender or a legally permissible linkage. More exact vote extraction alone does not close that gap.
3. Audit source-share failures and omitted contest forms before interpreting the screen as a complete sample.
4. Assess usable procurement follow-up for verified terms; only then assess outcome variation and minimum detectable effects.
