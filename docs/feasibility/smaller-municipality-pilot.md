# District-municipality pilot: Hallbergmoos and source access

Review date: 3 October 2026. Municipalities were selected for a convenience source probe, not by random sampling. They are district municipalities rather than the independent-city examples examined earlier; a population-based small-municipality stratum has not yet been defined.

## Hallbergmoos: an off-cycle historical election

The municipal website links [first-round results](https://www.hallbergmoos.de/buerger/politik-und-sitzungen/buergermeister/wahlergebnisse-2024) and [runoff results](https://www.hallbergmoos.de/buerger/politik-und-sitzungen/buergermeister/ergebnisse-der-buergermeister-stichwahl-03-11-2024). Both include downloadable **final official notices**, alongside provisional material. The final PDFs were downloaded and converted to text with `pdftotext -layout`.

| Round | Election date | Candidate vote counts | Valid votes | Reconciliation |
| --- | --- | --- | --- | --- |
| First | 20 October 2024 | 1,037; 1,525; 1,511 | 4,073 | All three candidate counts sum to the total |
| Runoff | 3 November 2024 | 1,978; 1,728 | 3,706 | Both counts sum to the total |

The first notice records the election committee meeting on 21 October; the runoff notice records its meeting on 4 November. Committee dates and publication dates must not replace election dates. Benjamin Henn is explicitly declared the runoff winner in the final notice.

The first-round leading candidates differ by only 14 votes, while the runoff difference is 250 votes. The relevant treatment contest is the decisive runoff, not the closest pair in an earlier round. The two rounds have been stored locally as one event with separate round records, and their totals validated.

### Gender and term evidence

The official Bavarian workbook (snapshot dated 14 July 2026, previously audited) records Hallbergmoos under key `178130`, winner Benjamin Henn, gender code `m`, election date **3 November 2024**, and first entry into office **1 January 2025**. The winner identity and election date match the final local notice.

This gives source-backed winner gender and a reported first-entry date. The opponent's gender remains unverified; no gender has been inferred from names. The local result forms' occupation wording is not treated as a dedicated gender field. No complete term interval or independent start-date corroboration has been established.

The elapsed period between election and reported first entry is about two months. Procurement must therefore not be assigned to the new winner automatically on election day. The pilot records the entry evidence separately from the election date, leaving the term end unresolved.

No mixed-gender RDD eligibility decision is made for this event until both finalists' source-backed gender and the other inclusion rules are established. Presence of a third first-round candidate alone does not settle eligibility; the decisive contest must be evaluated.

## Other district-municipality source probes

| Municipality | Evidence | Status |
| --- | --- | --- |
| Ismaning | [Official election page](https://ismaning.de/gemeinde-rathaus/wahlen/) links a 2020 mayoral-result archive at `okvote.osrz-akdb.de` | Official historical source link established; request to the linked host failed with proxy tunnel HTTP 403. This is a runtime access restriction, not evidence that the record is absent. No bypass attempted. |
| Neufahrn bei Freising | [Official municipality site](https://www.neufahrn.de/) links 2026 runoff, first working week and inauguration notices | Sources for terms are discoverable, but historical 2020/2014 records were not established in this probe. 2026 follow-up must not be assumed sufficient for procurement research. |

The Ismaning current workbook illustrates another timing pitfall: its latest listed election is in 2026 but its `Erster Amtsantritt` is 1 May 2014. That date cannot be used as the start of every later term. Hallbergmoos's first-entry match is useful because it concerns the newly elected officeholder; general application still requires event-level evidence.

## Register structure now piloted

Local ignored `data/interim/bavaria-register-pilot/` contains Hallbergmoos round records and separate term evidence. The intended schema and uncertainty rules are documented in [election-register-schema.md](election-register-schema.md). Candidate records and third-party PDFs have not been committed to the public repository.

## Next acquisition steps

- Continue source-backed finalist gender verification and dated official term notices.
- Extend district-municipality discovery with an explicit geographic/population sampling frame, recording unsuccessful retrievals.
- Investigate historical central access and available archived municipal result documents.
- Resolve the Ismaning host restriction through supported environment access configuration if that source is needed; use other already accessible official sources meanwhile.
- Keep newer off-cycle elections separate from 2020 contests when evaluating follow-up and power.
