# GERDA usability and further Bavaria evidence

Audit: 3 October 2026. GERDA is our operational election backbone for the German adaptation of Florio and Spagnolo. It substantially reduces acquisition work, but the public Bavarian files do not supply complete historical candidate gender and actual tenure measures.

**Subsequent archive expansion:** the [candidate and tenure register](bavaria-candidate-and-tenure-register.md) increases the four initial official-title observations documented below to eight, with three mixed-title pairs. It adds actual appointment/role-end evidence and full legacy TED fields. GERDA's 2026 labels remain dated leads; they are not automatically transferred to 2020.

## What GERDA supplies

[GERDA](https://www.german-elections.com/) is a research compilation of state-specific election sources. Its inspected mayoral extension covers 13 states, with election-round, candidate-cycle, person-election and annual files, including versions harmonized to 2021 boundaries. It is not a federal register of all mayoral candidates.

Cite Heddesheimer, Vincent, Hanno Hilbig, Florian Sichart and Andreas Wiedemann (2025), *GERDA: German Election Database*, Scientific Data 12: 618, [doi:10.1038/s41597-025-04811-5](https://doi.org/10.1038/s41597-025-04811-5), together with the repository snapshot for the later mayoral extension. The [upstream main commit](https://github.com/awiedem/german_election_data/commit/030c1fb865ec4e6ef94d5dee2039edde081a0f5d), checked today, is still our pinned `030c1fb865ec4e6ef94d5dee2039edde081a0f5d`. No newer release resolving the Bavarian gaps was found.

Counts below come from actual downloaded CSVs; some upstream README coverage descriptions are older.

| File / subset | Observations | Audit result |
| --- | ---: | --- |
| Candidate-cycle CSV, all 13 states | 113,345 | Votes, rounds, nominations and characteristics with provenance |
| Bavarian candidate-cycle rows, all years | 68,929 | 1,915 names and gender labels; all these labels belong to 2026 |
| Bavarian candidate-cycle rows, 2020–2024 | 4,574 | No candidate names or gender labels |
| Person-election panel, all states | 45,368 | Compiled person identifiers across elections |
| Bavarian person-election rows | 32,233 | All use `first_amtsantritt`; all gender fields are empty |

The 1,915 source-recorded Bavarian labels comprise 1,671 `m` and 244 `w`. They concern named 2026 candidates, principally elected officeholders, and do not establish both candidates' historical labels. The candidate CSV SHA-256 is `5cf7c8f7695cf17d3001ffe49ba5bb5a8f2800be8426754c1db3143b200fba0e`. The newly acquired person panel has 8,143,803 bytes and SHA-256 `2ebbe16114981cd9fdf19e5e6922e5da9d76e70e75b6e86d6f2a2bad3a2fb2aa`.

GERDA already supplies **997 conservatively screened two-person decisions for Bavaria in 2020–2024**, whose decisive votes match the historical workbook. It provides dates, runoff structure, votes and descriptive margins. The [structural screen](gerda-structural-screen.md) documents restrictions and source flags. Official candidate-name recovery and municipal TED linkage build on these events.

The person panel helps investigate reelections and mayoral changes. Boundary crosswalks can support linkage, but election-time municipalities and procurement buyers still require explicit identification.

### First entry is not a renewed term's start

In Bavaria, `term_start_date` means a person's **first** entry into office, copied across reelections. Gauting's 2020 row has `2014-05-01`, not the renewed 2020 term's start. Person IDs are generated from municipality and first-entry date, rather than verified biographical identity. The acquired panel contains no exact `term_end_date` field.

The [annual-panel code](https://github.com/awiedem/german_election_data/blob/030c1fb865ec4e6ef94d5dee2039edde081a0f5d/code/mayoral_elections/03_mayor_panel.R#L1178) forward-fills from election year to the year before the next election, extending open spells to the maximum election year. This was checked in code; the annual CSV was not acquired. Calendar-year assignment can put a new winner in January despite entry into office in May. Contract dates need supplementary appointment, departure and interruption evidence.

### Gender provenance and reuse

Some other states' gender labels are predicted from names. The existing NRW screen has 143 mixed-label structural pairs for 2020 through the cutoff, all involving prediction. Preserve source, method and year; these are leads rather than automatic sample approval. Name-classification confidence scores are not independently calibrated probabilities for every candidate.

The inspected [root LICENSE](https://github.com/awiedem/german_election_data/blob/030c1fb865ec4e6ef94d5dee2039edde081a0f5d/LICENSE) grants CC BY 4.0 for covered **federal election datasets** and explicitly does not establish the license of candidate/mayoral or other third-party data. The R package's software license does not resolve data reuse. Our original code, citations and aggregates are published; downloaded candidate/person records remain local. No restricted data were acquired.

## Further candidate evidence

### 53 exact matches to dated 2026 labels

Complete candidate name plus municipality matches uniquely to a source-recorded 2026 GERDA gender row for **53 candidate observations across 53 of the 95 named 2020 events**. Seven belong to contests within five percentage points. Labels comprise 49 `m` and four `w`.

Only explicit academic titles, case, whitespace and Unicode composition are normalized. There is no first-name expansion, substring or fuzzy matching. These are identity/gender follow-up leads. A 2026 officeholder does not establish both 2020 candidates' labels; homonyms, name changes and historical measurement require review. **No historical treatment labels are promoted from these matches.** The reproducible person-level queue remains local.

### Dated municipal publications

Four official-title observations now link to verified 2020 candidates. Gendered presentation remains separate from an explicit registry gender field.

| Candidate | Official source and evidence |
| --- | --- |
| Uta Wüst, Gräfelfing | [Bürgerjournal 02/2019](https://www.graefelfing.de/fileadmin/user_upload/Rathaus_Buergerservice/Publikationen_Filme_Bilder/Buergerjournal/Buergerjournal-Graefelfing-2019-2.pdf), PDF page 2: `Ihre Uta Wüst`, `Erste Bürgermeisterin` |
| Peter Köstler, Gräfelfing | [Bürgerjournal 01/2020](https://www.graefelfing.de/fileadmin/user_upload/Rathaus_Buergerservice/Publikationen_Filme_Bilder/Buergerjournal/Buergerjournal-Graefelfing-2020-1.pdf), PDF page 2: `Peter Köstler, Erster Bürgermeister` |
| Dr. Brigitte Kössinger, Gauting | [Amtsblatt 14/2020, 1 April](https://www.gauting.de/fileadmin/gauting-online/Dateien/2_Amtsblatt_PDF/2020/Amtsblatt_14_2020.pdf), PDF page 1: `Erste Bürgermeisterin` |
| Helmut Fichtner, Mainburg | [Official annual report 2020/21, June 2021](https://daten2.verwaltungsportal.de/dateien/seitengenerator/c568c489c994bfcc54bf0c71ac81b1e224346/kurzbericht_2020_21.pdf), PDF page 1: `Erster Bürgermeister`; page 4 identifies `Herr Helmut Fichtner` as elected on 29 March 2020 |

Gräfelfing has **both candidates' gendered official titles documented**, with distinct source years and a 2.046-percentage-point decisive margin. This supports measurement review for a possible woman–man contest. Title-based measurement, identity continuity and complete actual terms remain review questions; no main-study treatment is promoted. The 2020 journal also documents the constituting council meeting on 5 May. A council meeting date is not silently converted into a mayoral appointment date.

Gauting's image-based Amtsblatt page 2 was rendered and visually checked. Its heading explicitly says **preliminary result**. It names `Kössinger, Brigitte, Dr.` (5,412 votes) and `Knape, Hans Wilhelm` (5,304); valid votes 10,716, invalid 80, voters 10,796. These agree with the historical workbook and named report. The election-source name is confirmed, while the council archive's `Johannes Wilhelm Knape` variant remains unresolved. Its occupational label is not converted into gender evidence.

The mutable Mühldorf homepage mentions successor Claudia Hungerhuber but also retains an older Michael Hetzl welcome text. Current pages alone therefore cannot reconstruct historical mayoral spells. Search-engine snippets were not used as evidence.

## Reproduce and continue

After the [operational pilot prerequisites](bavaria-operational-pilot.md#reproduction-and-outputs), run:

```bash
python src/pilot/gerda_usability_audit.py --download
python src/pilot/bavaria_official_title_evidence.py --download
```

Omit `--download` for existing files. Both scripts verify pinned hashes; PDF extraction needs Poppler's `pdftotext`. Source and person-level outputs stay in ignored local directories. Public counts are in [gerda-usability-summary.csv](gerda-usability-summary.csv).

Continue with these dated leads and the remaining close-election candidates, prioritizing municipal gazettes, official archived council records and documented departures. Establish both candidates' historical measurement and the winner's actual appointment spell before main-study assignment and estimation. Bavaria remains ahead of NRW; GitHub Pages remains deferred.
