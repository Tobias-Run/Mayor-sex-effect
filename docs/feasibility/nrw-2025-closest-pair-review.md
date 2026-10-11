# NRW 2025 closest-pair primary-evidence review

Evidence checkpoint: **11 October 2026 UTC**. This completes a bounded first-coder review of the eleven previously unreviewed pairs in the fourteen-election, inclusive ≤2 percentage-point queue. It adapts the measurement rules used in the German feasibility work, as part of the adaptation of Florio and Spagnolo (2026). See the [literature and German precedents](../literature.md) and [2025 measurement addendum](nrw-2025-measurement-addendum.md).

## Result and decision

| Disposition across all fourteen elections | Elections |
| --- | ---: |
| Supported mixed public presentation | 3 |
| Supported same public presentation (all male–male) | 8 |
| Review completed; presentation unresolved for one finalist | 3 |
| Independently second-coded / main-study certified | 0 / 0 |

The three supported mixed pairs are Mülheim an der Ruhr, Lüdenscheid and Neunkirchen-Seelscheid. **All three female-presented candidates lost.** The new batch supports nineteen of twenty-two finalist observations; it adds no confirmed mixed pair. Eight pairs are supported as same presentation: Siegen, Hamminkeln, Overath, Bergisch Gladbach, Engelskirchen, Selm, Unna and Altenbeken. No administrative sex/gender field has been verified.

**Do not launch a causal study at the ≤2 pp cutoff.** The currently supported mixed sample has no female-presented win and therefore no observed win-versus-loss contrast. Even if all three unresolved pairs were mixed, this fixed election frame could contain at most six mixed pairs. Conditional on the accepted winner observations, at most one additional female-presented win could arise, in Emmerich. These are logical bounds on this frame, not classifications of missing finalists, an econometric bandwidth choice or a universal claim about other cohorts.

## Unresolved searches and selection risk

| Election | Accepted winner observation | Remaining limitation |
| --- | --- | --- |
| Datteln | Male presentation in a named municipal June 2025 activity | Finalist identified in the official recount and September CDU campaign pages; generic candidate labels and impersonal pronouns do not establish the other finalist's presentation. |
| Willebadessen | Male presentation in the municipal report of the September 2025 council farewell | UWG homepage, about and press pages were inspected. Accessible text names the candidacy; newspaper reproductions remain secondary. No accepted person-specific presentation locator was obtained. |
| Emmerich am Rhein | Female presentation in the CDU's explicitly dated 2025 campaign statement | An attempted SPD-domain homepage route returned HTTP 403; authorship/content could not be inspected. Newspaper reports and indexed advertisement leads cannot substitute for a retained primary original; occupational suffixes do not suffice. |

The attempted searches used each finalist's official name, municipality, election year and municipal/party routes. Exact surname and abbreviated given-name variants were inspected only within the same jurisdiction and election; no global fuzzy merge was used. The [event audit](nrw-2025-closest-pair-evidence-review.csv) records both dispositions and the precise unresolved reasons. The [source manifest](nrw-2025-closest-review-source-manifest.csv) pins accepted originals and inspected discovery/rejected originals. One attempted candidate domain returned placeholder content; it supplies no evidence. Failed retrieval is recorded in the [summary](nrw-2025-closest-review-summary.json), without bypassing the access restriction.

Accepted evidence covers **14/14 winners and 11/14 losers**. All remaining missing observations concern losing finalists. This is an observable documentation asymmetry and a reason to retain the entire fourteen-election frame, report unresolved dispositions and require independent second coding. It does not establish the magnitude or direction of selection bias. Party authorship remains a sensitivity dimension, including the Altenbeken CDU response directly addressing its opponent's campaign flyer. No second independent coding has taken place; automated source/hash checks are not a second coder.

## Procurement linkage and precision

The three confirmed mixed cases have **ten original Q1 competition procedures** in the independent call roster: Mülheim five, Lüdenscheid one and Neunkirchen-Seelscheid four. These remain only a procurement-availability inventory; jurisdiction, outcome-specific eligibility, office/exposure and comparable-window certification are unfinished. Ten procedures provide **three elections**, not ten independent assignments.

Each of the three unresolved elections currently has zero original Q1 procedures in the fixed roster. Resolving presentation alone would therefore not add a linked female-win case to this inventory. Zero matching calls means unknown or absent coverage in this particular query, not zero procurement or a direct-award classification. The wider ≤5 pp roster continues to contain 37 original Q1 procedures; thirteen have no indexed standard result by the unchanged September cutoff. Those cases remain in the roster.

The wider first-coder mixed inventory still contains six elections, three wins and three losses. The earlier equal-variance, independent-election Gaussian planning benchmark for six cases split 3/3 is about **3.07 outcome standard deviations** at two-sided 5% significance and 80% power. This is not RDD power, observed outcome variability or a justification for choosing 5 pp after seeing labels. The ≤2 pp inventory does not support that balanced calculation. Precision must be reassessed before extensive additional outcome collection or main-study launch.

## Evidence handling and reproduction

Source dates and context are retained separately from retrieval timestamps. The 2024 Engelskirchen nomination explicitly addresses autumn 2025. Undated campaign pages in Hamminkeln, Selm and the Bergisch Gladbach CDU council-candidate statement explicitly identify the 2025 election context. Retrospective municipal reports explicitly identify the relevant 2025 event; current office titles alone do not establish historical presentation or continuous officeholding. Live pages can have changed since the election; retained originals establish what was inspected at this checkpoint.

Datteln's municipal recount confirms a final five-vote lead, reversing the initially reported winner; the official state counts remain 5,855 versus 5,850. Siegen's official committee confirms seven votes, 14,687 versus 14,680. Engelskirchen is a two-candidate first-round decision, not a runoff. Full official state identities remain in ignored local records. Shortened primary-source names in Overath and Engelskirchen are corroborated by jurisdiction, nomination, named election and role. The Altenbeken municipality uses an additional middle-name variant; it does not change the state-register identity or certify the disposition of any election challenge.

The verifier reparses the fourteen pinned official state originals, checks original source bytes/hashes and exact presentation locators, and retains all fourteen reviewed elections independently of prediction labels and procurement coverage. The pair validator now distinguishes complete same-presentation pairs from unresolved and conflicting/other pairs; it assigns no signed gender margin to them. The call-roster script preserves the updated review dispositions when rerun.

```sh
python src/pilot/nrw_2025_closest_review.py
python -m unittest discover -s tests -q
```

Full replay requires the ignored local original-source and annotation bundle. Public source pins permit provenance inspection but do not promise reconstruction from mutable live URLs alone. Public files contain event-level summaries; raw originals and person annotations remain local. The frozen historical report and its inputs/outputs are unchanged. GitHub Pages remains deferred.

## Next bounded milestone

Complete outcome-specific, buyer-jurisdiction and exposure eligibility for the existing 37-procedure inventory while retaining missing results. Then produce a cohort-level feasibility decision using linked independent elections and precision, with independent second coding explicitly still required. Any extension to additional cohorts or a wider election scope needs a stated acquisition rationale and a fresh precision assessment; this review does not authorize a causal launch.
