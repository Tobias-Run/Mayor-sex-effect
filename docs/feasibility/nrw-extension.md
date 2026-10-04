# NRW extension: six further close-election municipalities

Reviewed on **4 October 2026**. This acquisition step extends the original Iserlohn, Velbert and Geilenkirchen pilot. It supports the German adaptation of Florio and Spagnolo's Italian procurement study; the [literature note](../literature.md) records the German precedents. No causal effects have been estimated.

The subsequent [procedure and presentation audit](nrw-procedure-and-presentation-audit.md) adds a complete 225-notice identifier supplement, four narrowly index-supported total counts without dates and further historical primary evidence. Counts below describe this initial extension stage; its fixed strict parser and full-text outcomes remain unchanged.

## Acquisition and scope

The next six municipalities in the statewide, official-vote-verified mixed-prediction follow-up queue are Unna, Viersen, Werdohl, Frechen, Sendenhorst and Weilerswist. Together with the original three, these are the first nine acquisition leads. This ordering is a data-collection choice, not an RDD bandwidth, an eligible sample or a validated historical gender measure.

A complete two-page TED API search returned **464 distinct indexed contract-award notices** with publications in 2021–2024. The exact request, fields, retrieval time, page hashes and byte counts are pinned in the [request manifest](nrw-extension-ted-request-manifest.json). The query includes broad buyer-name matches; the return count is not a municipal contract count.

| Municipality | AGS | Absolute decisive margin, percentage points | Exact municipal-label notices |
| --- | --- | ---: | ---: |
| Unna | 05978036 | 1.2393 | 25 |
| Viersen | 05166032 | 1.6279 | 80 |
| Werdohl | 05962060 | 2.9947 | 8 |
| Frechen | 05362024 | 3.3449 | 19 |
| Sendenhorst | 05570040 | 4.8905 | 0 |
| Weilerswist | 05366040 | 4.9190 | 1 |
| **Total** | | | **133** |

The remaining 331 notices comprise **280 other-organization cases** outside the direct-city pilot and **51 scope-review cases**: 49 municipal variants/represented purchases and two multiple-buyer labels. The pending labels include Unna's central procurement unit and represented city purchases, purchases for Stadtbetriebe Unna, Frechen's leisure/bathing undertaking, represented Sendenhorst/Werdohl purchases and joint authorities. These cannot be accepted or rejected from a prefix alone. County and city names remain distinct.

In particular, Sendenhorst's zero exact-label notices coexist with a represented-city notice in review. Zero strict matches do not establish zero procurement or justify excluding the election.

There is no overlap with the original 92 retained notices. The combined acquisition inventory therefore contains **225 retained indexed notices across eight independent election events with retained notices**. Nine municipalities have been selected for acquisition; scope completeness and research eligibility remain unresolved. The original 92 already underwent full-text buyer review, whereas the new 133 use the narrower exact-label baseline.

## Outcomes and full-text access

Only five new indexed notices provide a safely scoped single awarded-contract date; **none provides a usable strictly typed total tender count**. The earlier full-text result remains **112 observed award-result units, including 106 with dates and total tender counts across three elections**. Notice counts and award-result counts cannot be added or used interchangeably.

Full-text acquisition was attempted for the 133 exact matches and 51 scope-review cases. TED's web PDF endpoint returned empty HTTP 202 responses with an explicit automated-access challenge. Empty responses were discarded; no new PDF is accepted in a source manifest. Automated attempts stopped. The working API search snapshot is a separate, official indexed-data interface; it does not supply the missing full notices. Therefore this extension is not a completed award-outcome or beneficiary audit.

## New named primary evidence

Five additional primary-source observations bring the combined presentation register to **11 observations and five pairs with both mixed public primary presentations**. Observation timing and authorship remain explicit; these are not automatically historical registry gender or treatment assignments.

| Candidate | Evidence | Timing and interpretation |
| --- | --- | --- |
| Katja Schuon, Unna | SPD Unna: “Die SPD bedankt sich bei ihrer Kandidatin Katja Schuon” | Article dated 28 September 2020; party-authored female candidate presentation |
| Dirk Wigant, Unna | Same article names Dirk Wigant and describes “dem CDU-Mann Wigant mit 221 Stimmen Vorsprung” | Historical male presentation; 221 equals the official runoff difference, 9,027 minus 8,806 |
| Sabine Anemüller, Viersen | Municipal *Viersen aktuell*, January 2024, PDF page 3: “Ihre Bürgermeisterin Sabine Anemüller” | Month precision retained as January 2024; no fabricated day or 2020 observation |
| Christoph Hopp, Viersen | Official public RIS: “Anrede: Herr Name: Christoph Hopp” | Current person presentation retrieved in October 2026; Hopp was the 2020 runoff loser |
| Katrin Reuscher, Sendenhorst | Official public RIS search returns one exact identity with `Anrede=Frau` | Current person presentation; no historical date or election-opponent observation inferred |

The [SPD article](https://spd-unna.de/aktuelles/dank-an-katja-schuon-glueckwunsch-fuer-dirk-wigant/) and its retrieval are pinned in the source manifest. [Viersen's January 2024 publication](https://www.viersen.de/system/files/2024-05/viersen-aktuell-01-2024.pdf) and the exact person/API URLs are pinned with hashes and retrieval times in the [evidence manifest](nrw-extension-evidence-source-manifest.csv).

Viersen's [official mayor page](https://www.viersen.de/rathaus-politik/stadtverwaltung-viersen/der-buergermeister) explicitly reports Christoph Hopp's entry on **1 November 2025**. This dates a successor's entry; it does not turn the 2020 loser into that year's winner or certify Sabine Anemüller's complete preceding term. Unna's current official page corroborates Dirk Wigant's identity and 2020 election without supplying an actual entry date.

Municipal site access for Frechen and Weilerswist encountered automated-access protection. Werdohl's RIS returned HTTP 403. Their sources were not bypassed. Werdohl's accessible 2026 disclosure document names a different current mayor and cannot establish the 2020 winner's historical presentation or tenure.

## Reproduction and next acquisition gates

Run from the repository root after reproducing the [statewide election register](nrw-statewide-election-register.md) and earlier pilot dependencies:

```bash
python src/pilot/nrw_extended_ted.py
python src/pilot/nrw_extension_evidence.py
python src/pilot/nrw_municipal_registers.py
python -m unittest discover -s tests
```

Raw snapshots and person/notice-level outputs remain local and ignored by Git. The TED acquisition command accepts `--download` only before its first snapshot exists and preserves the fixed query and field set. Primary evidence can be downloaded with `--download`; any changed checksum requires review. Generated aggregates are published in [nrw-extension-summary.csv](nrw-extension-summary.csv), alongside the [municipal-register audit](municipal-tenure-registers.md).

The combined suite passes **68 offline tests**. New safeguards cover county/city scope, represented/joint purchases, exact named person matching, dated party authorship, year-only boundaries, vacancies, deputy roles and successor timing. The two TED pages and 14 new primary/catalogue sources pass hash and byte checks.

Next priorities are authorized full-text access, the 51-case scope queue, both finalists' dated presentation in the remaining municipalities, actual initial/renewal boundaries, procurement authority and procedure deduplication. The 106 earlier dated/count units remain useful for measurement checks; independent-election coverage must expand before precision or causal analysis can be assessed.
