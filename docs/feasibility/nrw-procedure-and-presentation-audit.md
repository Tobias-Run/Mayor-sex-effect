# NRW procedure identity, indexed counts and historical presentation

Reviewed on **4 October 2026**. This supplement follows the [six-municipality extension](nrw-extension.md). It improves measurement and duplication checks for the German adaptation of Florio and Spagnolo's Italian study; [German precedents and the adaptation](../literature.md) remain part of the research design. No causal effects or main-study treatment assignments have been produced.

**Later source supplements:** the [national OpenData audit](national-procurement-open-data.md) matches all 57 known UUID/version pairs in original German eForms and corroborates the four indexed totals. The subsequent [buyer and phase audit](nrw-buyer-and-phase-audit.md) expands the inventory to 237 retained results and 123 dated/count observations across six elections. It verifies both explicit previous-competition references in original result XML and all 63 legacy previous-competition references in original PDFs; 115 observations have supported competition-to-contract chronology. The counts below describe this earlier index/PDF stage.

## A complete enriched index snapshot

The public TED Search API was queried for all **225 retained publication numbers**, returning exactly that fixed set with 29 requested fields. The independently accessible API index supplies structured search fields; protected web full notices were not fetched. Its official [OpenAPI specification](https://api.ted.europa.eu/api-v3.yaml) documents 1,830 indexed field aliases. Discovery used that specification; the published pipelines run with Python's standard library and Poppler.

The supplemental snapshot adds notice versions, contract identifiers, contract/tender references and procedure titles. All **13 shared buyer, date, result and identity fields are unchanged** relative to the earlier reviewed snapshots. The [request manifest](nrw-procedure-ted-request-manifest.json) pins this 225-row request plus a separate two-row previous-notice context request. Those two context rows are not additions to the retained procurement inventory.

## Notice histories and identifier collisions

| Check | Finding | Consequence |
| --- | --- | --- |
| Global procedure GUID | Present in 57 notices, representing 56 distinct municipality-scoped GUIDs | One observed multi-notice procedure; 168 notices still lack this identifier |
| Explicit parent version | One linked Viersen pair, with matching city, procedure GUID, parent notice UUID and version | Retain the result history; do not count the two notices as two independent procedures |
| Internal procedure reference | Two repeated-reference groups; one spans two different GUIDs | A local text reference alone does not prove procedure identity |
| Contract reference | Geilenkirchen's contract reference `1` appears in four different procedures | Contract labels need procedure and municipality scope |
| Previous-notice references | Two links point to `cn-standard` competition notices outside the retained result cohort | Competition history is not a duplicate award |
| Legacy full-text header reference | Recovered for 45 of 63 original legacy notices, with no repeated city-scoped reference among those 45 | Useful additional keys; completeness and broader duplication remain unresolved |

Viersen **315657-2024** and **381033-2024** share procedure GUID `12f8c62a-7a83-4ee0-a34a-507106e981bd`. The latter points to the former's exact UUID/version. Their indexed result histories differ: the earlier notice has four open results and two closed non-awards; the later notice has four selected-winner results and two closed non-awards. Keeping only one arbitrary row could erase the award transition. Main-analysis version selection will need a specified rule and full result/contract validation.

Iserlohn **315323-2024** and **424806-2024** share the internal wording “Verhandlungsverfahren - Übermittlung der Beabsichtigung einer Auftragsvergabe” but have different procedure GUIDs. They remain separate. Likewise, Geilenkirchen notices **126957-2024**, **194171-2024**, **196766-2024** and **218390-2024** use contract reference `1` under four different GUIDs. Globally merging that reference would combine unrelated procedures.

The prior references from Geilenkirchen **707371-2023** to **546284-2023**, and Werdohl **253377-2024** to **96667-2024**, were independently checked through indexed fields. Both targets are competition notices. Werdohl's target has the same procedure GUID; the older Geilenkirchen competition has no indexed GUID. Neither previous-notice link is treated as evidence of a duplicate awarded contract.

There are **zero automatic notice or award merges**. The 56 observed GUIDs are not a verified total of distinct procedures for the whole inventory. Missing identifiers and nonrepeated legacy references cannot establish that all remaining notices are unique. Both the original 92-notice full-text cohort and the combined 225-notice acquisition inventory retain their previous sizes.

## Four conservative index-supported total tender counts

The earlier strict index parser required a single statistic. The supplemental audit can also identify a total without assuming that separate flattened arrays have matching positions, but only when:

1. Exactly one lot is defined and returned, and its sole result explicitly selects a winner.
2. Exactly one statistic type is `tenders`; types are unique and the type/value/business-term arrays have matching lengths.
3. Every returned value, including its business-term alias, is the **same finite positive integer**.

Under those conditions, permuting the values cannot change the total associated with `tenders`. Unequal values stay unresolved; the code never zips them to types or distributes them over lots. This is a deliberately narrow index-level measurement rule, not full-notice validation. The repeated alias is a consistency check on the same indexed source, not independent corroboration.

| Municipality | Publication | Total tenders supported by index | Returned statistic values | Contract date |
| --- | --- | ---: | --- | --- |
| Werdohl | 253377-2024 | 4 | 4 total; 4 electronic | Missing |
| Viersen | 557169-2024 | 9 | 9 total; 9 electronic; 9 SME | Missing |
| Viersen | 724046-2024 | 3 | 3 total; 3 electronic; 3 SME | Missing |
| Viersen | 785396-2024 | 3 | 3 total; 3 electronic; 3 SME | Missing |

These four observations are stored separately as `index_supported_single_awarded_lot`, with `fulltext_validated=false`. None has an indexed contract date. They add **zero full-text-validated units and zero new paired date/count observations** to the earlier 106. Other single-lot, multi-lot, unfinished or unequal-statistic records remain outside this narrow rule.

## Award units are concentrated within three elections

The original full-text cohort's 106 units with both dates and tender totals appear in **72 distinct notices**, distributed as follows. These notice counts precede complete procedure/contract deduplication.

| Municipality | Dated/count award-result units | Distinct notices containing them | Independent 2020 election events |
| --- | ---: | ---: | ---: |
| Velbert | 45 | 32 | 1 |
| Geilenkirchen | 17 | 14 | 1 |
| Iserlohn | 44 | 26 | 1 |
| **Total** | **106** | **72** | **3** |

Several lots or award sections within one notice remain separate observed units; equal dates or tender counts alone are not grounds for merging them. Those units also do not create additional independent mayoral elections. The wider acquisition inventory covers eight elections with retained indexed notices, but usable dated outcomes still cover only three. Statistical precision cannot be inferred from the count of 106 rows. Coverage, consistent historical treatment measurement, actual terms and procurement authority remain gates before a power or design decision.

## Four additional party-source presentations

The combined public primary-presentation register now contains **15 observations and seven pairs with both mixed primary presentations**. New observations match exact decisive candidates in the official 2020 state results. Werdohl's original comma whitespace in `Späinghaus , Andreas` is preserved after an explicit normalized-name match.

| Candidate | Primary source and quote | Time retained |
| --- | --- | --- |
| Susanne Stupp, Frechen | SPD letter: “Frau Bürgermeisterin Susanne Stupp” | Letter dated 23 September 2020; article posted 30 September 2020 |
| Carsten Peters, Frechen | SPD article: “Bürgermeisterkandidat Carsten Peters” | Article posted 31 August 2020 |
| Andreas Späinghaus, Werdohl | SPD nomination article: “Andreas Späinghaus zum Bürgermeister-Kandidaten gewählt”; body explicitly refers to nomination on 14 June 2020 | Named event-reference date, rather than a certified article-publication day |
| Silvia Voßloh, Werdohl | SPD *Haushaltsberatung 2017*: “Bürgermeisterin Silvia Voßloh” | October 2017; explicitly **not a 2020 observation** |

Frechen's [Stupp letter](https://spd-frechen.de/2020/09/30/warntafel-auf-der-elisabethstrasse-wieder-aufstellen/) and [Peters article](https://spd-frechen.de/2020/08/31/strassenausbaubeitraege-nicht-mehr-zeitgemaess/) are party-authored primary documents. Addressing a municipal incumbent does not make the letter a municipal official source. Deputy or candidate titles do not supply full-time mayoral authority.

Werdohl's [Späinghaus nomination](https://www.spd-werdohl.de/spd/2020/06/14/andreas-spaeinghaus-zum-buergermeister-kandidaten-gewaehlt/) and [2017 budget report](https://www.spd-werdohl.de/spd/2017/10/16/haushaltsberatung-2017/) name the candidates fully. Surname-only earlier letters were not accepted as exact identity observations. Both selected Werdohl pages display publication-day labels inconsistent with their permalink days. The explicit nomination event and safe historical month are retained instead of inventing exact publication dates. These mixed primary-presentation counts are **not counts of seven validated historical-2020 gender pairs or RDD-eligible elections**.

The [primary source manifest](nrw-procedure-primary-source-manifest.csv) records hashes, byte sizes and retrieval times for four selected articles and the API documentation. Source timing, party authorship and unknown registry gender remain explicit in the local observation register.

## Reproduction and remaining work

After reproducing the earlier [extension](nrw-extension.md) and [complete full-text cohort](nrw-complete-pilot.md), run from the repository root:

```bash
python src/pilot/nrw_procedure_audit.py
python src/pilot/nrw_historical_presentation_followup.py
python -m unittest discover -s tests
```

The procedure script accepts `--download` for the initial enriched/context acquisition only; an existing snapshot is preserved. Downloads must match the reviewed published pins. The presentation script also accepts `--download` and rejects changed source hashes. Mutable sources require review before updating any pin. Raw notices, source articles and person-level outputs remain local and ignored by Git.

Both pipelines run successfully. The combined suite passes **80 offline tests**. New tests protect version-specific identity, city scope, generic reference collisions, unequal flattened statistics, pending/multiple lots, invalid counts, header scope, surname-only identity and distinct letter/event/article dates. The enriched/context snapshots, five new primary/documentation files and the 92 reused original full texts pass hash/byte checks.

Aggregate outputs are [nrw-procedure-audit-summary.csv](nrw-procedure-audit-summary.csv) and [nrw-award-concentration-summary.csv](nrw-award-concentration-summary.csv). Remaining priorities are authorized full-notice access, the 51 pending beneficiary/buyer cases, missing historical finalist evidence, initial/renewed term boundaries, delegation and broader procedure/contract matching. No Pages site has been released; the interactive companion remains deferred until research completion.
