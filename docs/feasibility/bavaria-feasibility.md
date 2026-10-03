# Bavaria: election register audit and access requirements

Assessment: 3 October 2026. Bavaria remains the active state for the German adaptation of **Florio and Spagnolo (2026), [Female Mayors and Public Procurement](https://doi.org/10.2139/ssrn.7046899)**. No procurement effects have been estimated.

**Historical votes have been acquired and audited. Named candidate recovery and a historical municipal procurement pilot are now operational; the mixed-gender sample and study-wide linkage are not complete.** See the [expanded pilot](bavaria-operational-pilot.md). Missing gender labels do not imply no woman–man contests. A power analysis and main-study approval remain premature.

The [GERDA follow-up audit](gerda-usability-and-bavaria-followup.md) adds the person panel, 53 exact links to dated 2026 source gender labels and four historical official-title observations. Gräfelfing now has title evidence for both candidates. These supplementary evidence types remain separate from approved historical treatment labels and complete actual terms.

The subsequent [candidate and tenure register](bavaria-candidate-and-tenure-register.md) expands official title evidence to eight candidates and three mixed-title pairs. Three initial appointments and two source-bounded intervals are documented. Full legacy TED PDFs recover five dated award units within Mühldorf's two existing notices; historical treatment coding, uninterrupted authority and statewide coverage remain open.

## Completed work

- Retrieved, hashed and independently parsed a pinned historical source workbook, preserving source rows and exceptions.
- Built a local municipality-round register for 2014–2024, distinguishing municipal/county offices, nominations, candidate-slot votes, residual votes and first entry into office.
- Validated decisive votes, valid totals, municipal office scope and round labels for all **997** contests in the conservative GERDA two-person screen for **2020–2024**.
- Created an identity-verification queue containing all 997 contests. Gender and actual term dates remain unverified. Margin ordering helps acquisition; it does not define an RDD bandwidth.
- Reviewed Schild, Arnold and Frank–Stadelmann–Torgler for Bavaria data access and measurement lessons.
- Inspected actual municipal ex-post awards in the official Bayern procurement portal and two linked PDFs.

## Historical source

GERDA distributes a copy attributed to the Bavarian State Statistical Office: `20251114_Wahlen_seit_1945.xlsx`, sheet `20251114_bewerberRBZ1-7`, pinned at commit `030c1fb865ec4e6ef94d5dee2039edde081a0f5d`. [Download](https://media.githubusercontent.com/media/awiedem/german_election_data/030c1fb865ec4e6ef94d5dee2039edde081a0f5d/data/mayoral_elections/raw/bayern/20251114_Wahlen_seit_1945.xlsx).

SHA-256: `7ba6aac1381496b3beed2bbd1d0f68209942026b7f9234af8cf1d914c81396a3`; 3,340,463 bytes. This is a third-party copy, not a direct delivery to our project. Agreement with GERDA validates its transformation against the input, not the historical accuracy of every election. Munich, Augsburg and Nuremberg 2020 runoff votes also match the separately inspected municipal archives.

There are **34,824 round rows**, dated 1 April 1945 to 9 November 2025, including county elections and exceptional rounds. **Candidate names and gender are absent from the workbook itself.** Inclusive office titles such as `Bürgermeister*in` are not person-level gender observations. Early records with council-sized electorates require institutional review; they are outside this register window.

| Source-round coverage | 2014–2024 | 2020–2024 |
| --- | ---: | ---: |
| All rounds | 4,937 | 2,530 |
| Classified municipal rounds | 4,754 | 2,434 |
| Classified county rounds | 181 | 95 |
| Office scope unresolved | 2 | 1 |
| Distinct municipal AGS in classified rounds | 2,056 | 2,016 |
| Municipal runoff rows | 608 | 337 |
| Duplicate municipal identifier/date keys | 1 | 1 |

These are rounds, not independent cycles or RDD observations. Off-cycle terms mean some municipalities have no election in 2020–2024; the AGS difference does not automatically indicate missing data. Missing office titles are resolved only by a unique explicit title on the same unit within 60 days. Annulled rounds remain visible.

The `restliche Bewerber` column is a residual beyond separately listed slots, not an identified candidate or invariably the total of all losing candidates. Bodenkirchen 2020 has 2,155 leading votes, individually listed 8, 8, 8 and 5, and residual 311, summing to 2,495 valid votes. Treating that residual as one opponent would create a false margin.

All 2,434 classified municipal rows in 2020–2024 reconcile voters with valid plus invalid ballots where the fields are present. Listed candidate votes reconcile in 1,652 rows; another 781 reconcile after adding the reported residual. Markt Schwaben 2024 cannot be reconciled because a vote cell contains text. Across 2014–2024, 17 rows with a residual fail the arithmetic check and require review. No votes are silently invented or repaired.

## Screen audit and exceptions

The [conservative screen](gerda-structural-screen.md) validates **997/997** events against the source's decisive votes and round structure. Literal nomination text agrees in 995. The two remaining differences are capitalization only: Wallersdorf's `engagierter`/`Engagierter` and Erbendorf's `FREIE WÄHLER`/`Freie Wähler`. Raw text is preserved; these are not evidence of different candidates or changed affiliations.

Two additional exceptions matter for extending coverage:

1. **Seukendorf 2022:** a three-candidate row and a two-person runoff row both carry 10 July 2022. The runoff has 804 versus 781 votes; the first-round date is not established from this workbook. Preserve both rows and obtain the historical municipal notice before correcting the cycle. It is outside the 997 passing events.
2. **Markt Schwaben, 9 June 2024:** source row 1598 contains `Bündnis 90/Die Grünen` in column P, which should hold candidate votes. The parser retains the raw value and records a parse issue.

The 997 screened contests include **52 within 2 pp and 140 within 5 pp**, across unknown gender combinations. These are acquisition priorities, not mixed-gender sample sizes or chosen bandwidths. The 2020-only screen has 906 contests, including 45 within 2 pp and 125 within 5 pp. Validation of passing events does not establish complete coverage of all potentially eligible contest forms.

## Lessons and acquisition routes from German research

**Schild (2013), [Do female mayors make a difference? Evidence from Bavaria](https://hdl.handle.net/10419/81935), Section 3.1:** reports Landesamt data with candidate names, gender, profession, nominations and votes. This establishes previous research use of richer data, not our present access. Its fiscal outcome window and small mixed-gender subset cannot be transplanted to procurement without checking timing and precision.

**Arnold (2018), [Turnout and Closeness: Evidence from 60 Years of Bavarian Mayoral Elections](https://doi.org/10.1111/sjoe.12241), Scandinavian Journal of Economics 120(2): 624–653.** The inspected [2015 DIW working paper 1462](https://www.diw.de/documents/publikationen/73/diw_01.c.499182.de/dp1462.pdf), Section 4, reports Landesamt data with candidate names, gender and profession: 27,015 elections in 2,031 municipalities, 1946–2009, **excluding the 25 independent cities**. Preserve rounds, off-cycle dates and full-time/honorary status. Its historical population differs from ours; its turnout design does not identify female-mayor procurement effects. The Wiley article/supplement routes returned HTTP 403; replication contents remain unverified.

**Frank, Marco, David Stadelmann and Benno Torgler (2023), [Higher turnout increases incumbency advantages: Evidence from mayoral elections](https://doi.org/10.1111/ecpo.12226), Economics & Politics 35: 529–555.** The [published PDF](https://epub.uni-bayreuth.de/id/eprint/7129/1/Economics%20Politics%20-%202022%20-%20Frank%20-%20Higher%20turnout%20increases%20incumbency%20advantages%20Evidence%20from%20mayoral%20elections.pdf) was inspected. Section 4.1 describes 682 elections in 233 municipalities over 2003–2020, using official reports plus municipal/press supplements, limited to municipalities **above 10,000 residents at election time**. Gender is inferred from first names, not an official field. The data availability statement says **“Data available on request from the authors.”** This is a concrete secondary route to identities, subject to reuse conditions, not a state-wide replacement. The paper also documents the postal-only 2020 runoff change and turnout/incumbency implications, which matter for cohort comparability.

The historical reports have now been located in the joint Statistische Bibliothek. Five first-round/runoff reports for 2008, 2014 and 2020 were obtained and parsed: 450 complete named rounds reconcile exactly against the historical workbook. Of the conservative 2020 screen, 95 events now have both candidate identities recovered. The earlier inferred Landesamt URLs returned 404; the verified library route resolves that archive-location gap. Gender fields are still absent from the reports. No provider or author has been contacted.

## Procurement: municipal awards located, analytical fields incomplete

The official [Bayern ex-post page](https://www.vergabe.bayern.de/veroeffentlichungen/vergabeinformationen_ex-post/index.html) embeds a [public RIB stream](https://meinauftrag.rib.de/public/InformationsFrame?filter=604283). Buyers include state offices, counties, municipalities and other entities. Execution location does not identify the municipal buyer.

The [Stadt Freising filter](https://meinauftrag.rib.de/public/InformationsFrame/publisher/U3RhZHQgRnJlaXNpbmc%3D/filter/604283) yields actual city awards. Inspected form-341 PDFs [42612](https://my.vergabe.bayern.de/remote/vergabeinformation.pdf.php?id=42612) and [40362](https://my.vergabe.bayern.de/remote/vergabeinformation.pdf.php?id=40362) identify Stadt Freising, references `65-26-040`/`65-26-014`, works descriptions, locations and selected contractors. Both mark `Freihändige Vergabe`.

| Field | Inspected evidence |
| --- | --- |
| Buyer identity | City name and buyer address; municipality mapping still requires verification |
| Procedure and selected contractor | Present; legal harmonization and contractor identity cleaning required |
| Award value and bid count | Absent from these two forms |
| Complete award date | Absent from these two forms |
| Publication date | Stream shows day/month; full year/date metadata not verified |
| Environmental/social/innovation criteria | Not established |
| Historical 2020–2024 archive and complete municipal coverage | Not established by the inspected pages or search/pagination probes |

The Bayern ex-post portal supports notice discovery, but the inspected form-341 PDFs cannot supply the Italian outcome set. A separate public TED API pilot now supplies historical notices and selected outcome fields for Gauting and Mühldorf; see the [operational pilot](bavaria-operational-pilot.md). Indexed JSON fields can be acquired even while individual XML downloads return empty HTTP 202 responses. Do not infer dates from procurement references, equate publication with award, code missing notices as zero, or pool state/county awards with municipal treatment.

## Bavaria completion gates

| Gate | Status | Evidence still needed |
| --- | --- | --- |
| Historical votes and source-round register | Acquired and audited for the stated windows | Resolve exceptional rows and broader contest eligibility |
| Both finalists' gender | Open | Source-recorded labels or documented permissible recovery; a gender-only supplement is sufficient |
| Actual municipal terms | Open | Starts, ends, reelections and early exits; first-ever entry is insufficient |
| Historical procurement linkage | Two-municipality pilot operational; study coverage open | Actual terms, broader buyer coverage, legacy dates and stable measures |
| Precision/main-study approval | Not ready | Verified mixed-gender contests, follow-up and outcome variation |

The [provider inquiry](bavaria-data-inquiry.md) is prepared with the identified workbook, studies and source exceptions. Applicant details are needed before submission. No email has been sent. A larger-municipality subset or manual reconstruction would need an explicit coverage assessment if source access fails. NRW does not replace these Bayern gates.

## Reproduction

```sh
python src/pilot/acquire_bavaria_sources.py
python src/pilot/gerda_structural_screen.py
python src/pilot/bavaria_historical_register.py
```

Only Python's standard library is required. Downloads are pinned and hash-checked. Local ignored outputs include `rounds.json`, `screen-source-comparison.json`, `summary.json` and `identity-verification-queue.csv` under `outputs/bavaria-register/`. The [aggregate CSV](bavaria-register-summary.csv) is public; third-party records are not redistributed. GitHub Pages remains deferred until research completion.
