# NRW: statewide 2020 election-register audit

Checked on 3 October 2026. **NRW is now the active acquisition workstream**, following the user's request to move on from Bavaria. The [Bavaria evidence](bavaria-candidate-and-tenure-register.md) remains available with its unresolved research gates. This project adapts **Florio and Spagnolo's [Female Mayors and Public Procurement](https://doi.org/10.2139/ssrn.7046899)** to Germany; the [literature review](../literature.md) retains the German precedents and measurement lessons.

**All 380 mayoral elections held in the state's scheduled 2020 archive have now been downloaded and checked, supplying 1,349 named candidate records.** This expands the earlier district-municipality runoff pilot to both archive municipality categories and first-round decisions. No procurement effect has been estimated.

## Official universe and complete acquisition

The [official NRW election archive](https://www.wahlergebnisse.nrw/kommunalwahlen/2020/index.shtml) links two final-result exports:

- [District-municipality mayor summary](https://www.wahlergebnisse.nrw/kommunalwahlen/2020/KW20_pers_gemeinden.txt), SHA-256 `1543ef83d84ac017f779c90de70ed69ea720ff70bc527cf894e132d00cc12e36`.
- [City mayors and county executives summary](https://www.wahlergebnisse.nrw/kommunalwahlen/2020/KW20_pers_insgesamt.txt), SHA-256 `20791d1ff493f5b5fd81d9f118104eedc1c58a68b0c08f25787b3651ff20aafe`.

The second export combines different offices. Only entries explicitly labelled `Krfr. Stadt` enter its municipal cohort; **31 county-level entries, including the Städteregion executive, are excluded**. Their election dates and candidates must not enter the mayoral sample.

| Archive category | Municipality entries | Elections held | Explicit no-election entries |
| --- | ---: | ---: | ---: |
| District-municipality export | 373 | 358 | 15 |
| City-mayor category in combined export | 23 | 22 | 1 |
| Total | **396** | **380** | **16** |

These are **archive categories**, not a claim that NRW legally had 23 independent cities in 2020. Aachen is retained in the archive's older city category although its territorial status changed in 2009.

Every held-election entry has a detailed, final-result text file. All **380/380** pass the adapted source checks; there are no unresolved acquisition/format failures in this snapshot. Candidate identity, exact votes and declared winner are preserved. The [382-source manifest](nrw-2020-source-manifest.csv) publishes only source IDs, URLs, checksums, sizes and retrieval dates: two summaries plus 380 detail files. Raw documents and person-level outputs remain local.

The 16 no-election entries are retained in the universe. Their absence from the candidate dataset is explained by the source's explicit “Es findet keine Wahl statt”, rather than interpreted as missing downloads or no female candidates. Other off-cycle election dates and years remain outside this particular audit.

## Voting structures and reconciliation

| Election structure | Decisions |
| --- | ---: |
| Runoff on 27 September 2020 | 117 |
| First-round decision on 13 September 2020 | 263 |
| Of first-round decisions: exactly two candidates | 97 |
| Of first-round decisions: more than two candidates | 125 |
| Of first-round decisions: one candidate | 41 |
| Conservative two-person decisive pairs | **214** |

The two-person register includes all 117 runoffs and 97 outright two-candidate decisions. It deliberately does not apply a two-person running-variable formula to multi-candidate outright victories. Those would need separately justified eligibility and a running-variable definition.

There is a consequential single-candidate exception: **40 of the 41** files report valid votes exceeding the sole candidate's affirmative votes. For example, [Issum](https://www.wahlergebnisse.nrw/kommunalwahlen/2020/aktuell/txtdateien/b154020kw2000.txt) reports 6,052 valid votes and 5,403 candidate votes. Its published candidate percentage uses **voters**, rather than the competitive-race valid-vote denominator. The parser retains the valid-vote remainder as `first_valid_votes_not_allocated_to_candidates`; it does not create a second candidate or treat this remainder as an opponent. Morsbach is the single-candidate case with no such remainder. All 41 cases stay outside the two-person screen.

For competitive races, all listed first-round candidate votes must sum to reported valid votes. A runoff requires precisely two finalists with reconciled runoff votes. An outright winner must exceed half of valid votes, ties are rejected, and the file's declared winner must agree with exact votes. The former-incumbent comparison block is not parsed as a current candidate or an actual office-start record. Percentages are retained as source values; margins use exact votes.

## GERDA is a useful backbone, with explicit identity exceptions

The pinned GERDA candidate file contains **5,117 NRW candidate records** across five years:

| Year | NRW candidate rows in GERDA |
| --- | ---: |
| 2009 | 1,218 |
| 2014 | 671 |
| 2015 | 524 |
| 2020 | 1,349 |
| 2025 | 1,355 |

The source is pinned at `030c1fb865ec4e6ef94d5dee2039edde081a0f5d`; candidate CSV SHA-256 is `5cf7c8f7695cf17d3001ffe49ba5bb5a8f2800be8426754c1db3143b200fba0e`. Cite Heddesheimer et al. (2025), [GERDA: German Election Database](https://doi.org/10.1038/s41597-025-04811-5), together with this snapshot of the later mayoral extension. Only 2020 has received this full independent official-source audit; the other years' counts describe the acquired compilation.

**All 380 complete candidate vote vectors match GERDA.** Candidate names, dates and winner match throughout **374** elections after Unicode, whitespace and comma-spacing normalization. Six elections contain a name discrepancy:

| Municipality | Official candidate name | GERDA candidate name |
| --- | --- | --- |
| Kalkar | van de Löcht, Marco | Löcht, Marco |
| Viersen | aCampo, Dr. Frank | Campo, Dr. Frank |
| Heinsberg | von Helden, Johannes | Helden, Johannes |
| Datteln | von Gilardi, Claudia Isabel | Gilardi, Claudia Isabel |
| Rheda-Wiedenbrück | von Zons, Sonja | Zons, Sonja |
| Bad Salzuflen | Thomas, Dr. Roland | Roland, Dr. Thomas |

These are exact source comparisons, not proposed automatic repairs or verified person-history merges. The official names remain authoritative in the new register. Name particles are not stripped; surname/given-name swaps are not silently corrected.

**212 of the 214 decisive pairs** have independently matched finalist identities in GERDA. Viersen's unrelated first-round candidate-name discrepancy does not invalidate its two exactly matched finalists; the full-election discrepancy is still recorded. The two unmatched pairs are Heinsberg and Bad Salzuflen. Their official election records remain valid; the unresolved compilation identity prevents copying candidate characteristics from GERDA.

### Geographic identifiers

State export codes have six digits and generally obtain full AGS by prepending `05`. **Aachen is the explicit exception:** archive code `313000` links to GERDA AGS **`05334002`**, not `05313000`. Its municipality name and complete candidate vote vector match. The code records this exception instead of assuming every source code is a contemporary AGS.

This crosswalk is sufficient for this source comparison. It does not settle every historical geographic vintage or establish a procurement-buyer crosswalk. Treat Aachen's archive office category and legal municipal status separately; verify municipality changes before pooling other years.

## Gender labels: follow-up queue rather than registry measurement

All **5,117** NRW gender labels in this GERDA snapshot have `candidate_gender_source = predicted`. Methods comprise `full_de` (4,612), `full_global` (236), `hyphen_first_de` (207), `hyphen_first_global` (5), and `manual` (57). Even the records labelled `manual` retain source `predicted`; that method label does not establish an official sex field. The 2020 state text exports supply names and votes without an explicit candidate gender field.

Do not interpret a source probability such as 0.99 as independently validated historical gender evidence. Neither photographs nor first names supply the missing main measurement. Dated official presentation, explicitly recorded registry fields or other documented evidence need their own provenance, as in the [Bavaria candidate register](bavaria-candidate-and-tenure-register.md#measurement-and-identity-rules).

The 212 identity-matched decisive pairs supply **72 prediction-based mixed-label follow-up leads**. These predictions prioritize source acquisition; they neither confirm mixed-gender eligibility nor establish a treatment effect.

| Inclusive candidate-to-candidate absolute margin | All 214 decisive pairs | Prediction-based mixed-label leads |
| --- | ---: | ---: |
| ≤1 pp | 4 | 2 |
| ≤2 pp | 15 | 5 |
| ≤5 pp | 34 | 9 |
| ≤10 pp | 55 | 17 |

The margin is the absolute difference between the two candidates' votes divided by valid decisive votes, multiplied by 100. It differs by a factor of two from the winner's distance above 50% in a two-candidate race. These bands are descriptive acquisition summaries, not selected RDD bandwidths or a power calculation. Model errors may occur among both mixed-label and same-label pairs; the predicted counts are not bounds on true gender eligibility.

The nine mixed-label acquisition leads within five percentage points are Iserlohn, Velbert, Geilenkirchen, Unna, Viersen, Werdohl, Frechen, Sendenhorst and Weilerswist. The first three have margins of 0.3972, 0.8985 and 1.0914 pp. The earlier [102-district-runoff screen](nrw-margin-screen.md) could not include Geilenkirchen's outright two-candidate victory or city-category runoffs.

## The person panel does not establish actual office dates

GERDA's acquired NRW person panel has **1,522 person-election rows**. Person linkage uses `candidate_name` in 1,512 rows and `candidate_name_variant_link` in 10. All 1,522 `term_start_date` values equal the person's earliest observed election date in that municipality. This is an observed-election construction, not a municipal appointment record.

The pinned [upstream construction code](https://github.com/awiedem/german_election_data/blob/030c1fb865ec4e6ef94d5dee2039edde081a0f5d/code/mayoral_elections/03_mayor_panel.R#L794) assigns `min(election_date)` where a source appointment is absent. Düsseldorf's new 2020 winner, for example, has `term_start_date = 2020-09-13`, despite the decisive runoff occurring on 27 September. Neither value establishes actual office entry. Left-censored incumbents may already have held office before the first observed year.

Do not assign September contracts to a new winner using that field or the annual forward fill. Actual entry, successor entry, resignation, interruptions and procurement decision authority require primary-source evidence. The subsequent [historical legal audit](nrw-term-law.md) specifies election acceptance and predecessor exit as the NRW entry components; no separate appointment is required. This NRW audit establishes **zero complete actual terms** and **zero approved main treatment assignments**.

## Reproduce and inspect

```bash
python src/pilot/nrw_election_register.py --download
python -m unittest discover -s tests -v
```

Run from the repository root with the pinned GERDA candidate CSV and person panel already acquired; the earlier [GERDA audit](gerda-usability-and-bavaria-followup.md#reproduce-and-continue) documents those inputs. Python's standard library suffices. Acquisition uses at most four concurrent requests. Each official detail must match the published source manifest; changed live documents require review rather than an automatic pin update. Without `--download`, the script audits cached inputs and checks their hashes.

Local outputs under `outputs/nrw-election-register/` include the complete municipality universe, named events, full-election and finalist comparisons, prediction follow-up queue, and summary. Raw sources and retrieval metadata live under `data/raw/nrw-2020/`. The [aggregate CSV](nrw-election-register-summary.csv) contains the reported counts. The public repository does not release the full candidate/person records or third-party source files.

The combined suite passes **25 offline tests**, including eight new NRW tests covering county exclusion, explicit no-election entries, Aachen's source code, single-candidate residuals, former-incumbent blocks, missing majorities, name particles and independent finalist matching. The real-source audit independently validates all 380 held-election details and all 380 complete vote vectors against GERDA.

## Subsequent NRW acquisition

The [NRW operational follow-up](nrw-operational-pilot.md) now documents 55 strict municipal TED result notices, four named official title observations, the first mixed-title pair, a source-bounded Geilenkirchen council-head interval, two legacy awarded contracts with dates/counts and one explicit non-award. It preserves the distinction between temporal overlap and procurement responsibility. The statewide register's own measurement flags remain unchanged; the new evidence is a separately sourced supplement.

Expand buyer-alias/beneficiary review, primary candidate evidence, actual office boundaries and full-document outcome recovery across the close-election queue. Missing buyer matches cannot be coded as zero procurement. Count distinct eligible elections only after coverage and measurement checks; then assess precision before preregistering the main analysis. GitHub Pages remains deferred until completion of the research.

The [expanded NRW pilot](nrw-expanded-pilot.md) subsequently completes the original buyer-scope queue and retains 92 municipal notices. Its full-notice audit supplies 49 award/lot-result units with both dates and total tender counts, while preserving five non-awards, two unsupported layouts, nominal prices and party-source candidate presentation separately. These outcomes still represent three electoral clusters.
