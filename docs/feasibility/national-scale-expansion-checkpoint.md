# Broader national frame and Niedersachsen 2021 checkpoint

11 October 2026. **The active acquisition frame grows from 40 to 58 different municipalities**, adding all 18 qualifying Niedersachsen 2021 municipal pairs within the unchanged 5 percentage-point final-vote margin. This expands the work queue, not a certified causal sample. The existing four provisional NRW mixed elections with supported count inventories remain four; this phase adds no supported mixed-election outcome and estimates no causal effect.

## National scale and candidate coverage

The pinned GERDA release provides 2,536 reconciled complete decisive municipal pairs in 2018–2025, including **326 close election events in 319 municipalities** across eleven states. Seven municipalities recur: their elections cannot be counted as independent municipality clusters. Of the 326 events, 127 have both finalist names in the source and 199 do not. These counts reflect this release and conservative structural screen, not a census of German elections or a verified mixed-pair sample. Names, predicted presentation and procurement matches do not select events.

The [national inventory](national-close-election-inventory.csv) retains missing-name cases. The [state/year matrix](national-state-year-expansion-matrix.csv) makes the coverage tradeoff inspectable. Bavaria 2020 supplies 125 close structural leads but no complete named finalist pair in this release; previously recovered local Bavarian names have not been silently merged into this screen. Niedersachsen 2021 supplies eighteen complete named pairs and therefore a practical new acquisition cohort. Treat source completeness as a selection mechanism to assess, rather than dropping poorly documented states without accounting for them.

## Eighteen new state-source checks

Both Landeswahlleitung PDFs agree with the GERDA identities, finalist votes, valid totals and declared winners for all eighteen selected pairs. The PDFs are headed **Vorläufiges Ergebnis** and report municipality-transmitted returns, with a printed update of 13 October 2021. These checks establish agreement with the state source, not final legal election certification, administrative sex/gender or uninterrupted mayoral exposure. The [verification ledger](niedersachsen-2021-official-verification.csv) gives each PDF page and checksum. Finalist details remain in the ignored local work bundle.

## Separate late-term procurement window

This cohort reuses all three pinned national monthly exports for **January–March 2025**, inspecting 74,177 notice/version rows without additional procurement downloads. This is a late-term availability window for a 2021 election. NRW 2025 and Brandenburg 2024/2025 retain their respective following-year quarters. No first-post-election interpretation or pooled estimate is asserted.

Actual sole buyer roles, exact municipal names, country and municipal legal-type checks find **22 standard call notices across six municipalities**:

| Municipality | Standard call notices | Distinct nonmissing procedure IDs |
|---|---:|---:|
| Bad Fallingbostel | 1 | 1 |
| Löningen | 2 | 0 |
| Burgwedel | 5 | 1 |
| Isernhagen | 9 | 1 |
| Wennigsen (Deister) | 1 | 0 |
| Alfeld (Leine) | 4 | 0 |

Eighteen of the 22 notices have numeric domestic identifiers and no procedure ID; four UUID notices carry three distinct procedure IDs. Neither number is a count of verified independent purchases. Two matched result notices and three design-contest calls do not create additional standard procurement-call cohort members. Original roots, correction graphs, buyer jurisdiction and linked outcomes remain unverified. Twelve municipalities lack exact standard call matches in this fixed quarter; that means unknown source coverage, not zero procurement.

The inherited Bavarian routine initially left Niedersachsen's literal `, Stadt` suffix attached to city names. The separately pinned [normalization addendum](niedersachsen-name-normalization-addendum.md) documents its correction for every selected municipality before the corrected replay. It changes only source-format normalization, preserving the roster, quarter and exact-match safeguards. This matters because apparent source absence can arise from a parser convention.

## Next bounded research step

1. Recover original calls for all six matched municipalities, retaining numeric domestic-ID cases rather than only easy UUID matches. Establish deduplicated procedures and source coverage before choosing any outcome denominator.
2. Review historical presentation for all eighteen pairs independently of procurement matches, recording unsupported losing finalists and later turnover. Candidate names or occupations do not become labels. Independent second coding is still required.
3. Audit the three known procedure IDs and any recovered domestic roots against the fixed Q1 window; retain absent results as unresolved. Separate election assignment from contemporary office-holder status.
4. Reassess precision using linked **independent elections**, with this late-term cohort kept separate until institutional comparability, election age and a substantive common estimand justify pooling. More notices alone do not improve the independent-election sample size.

The [combined acquisition ledger](broader-election-acquisition-frame.csv) contains 58 municipalities; the [new linked inventory](niedersachsen-2021-linked-acquisition-inventory.csv) retains all eighteen including unmatched cases. The [summary](national-scale-expansion-summary.json), [source manifest](niedersachsen-2021-source-manifest.json), [protocol](national-scale-expansion-protocol.md) and replay script `python src/pilot/national_scale_expansion.py` make this phase reviewable. Source ZIPs, PDFs and person-level working records stay local. The frozen historical report remains unchanged; there are zero certified main-study elections and GitHub Pages remains deferred.
