# NRW close pairs: priority evidence follow-up

Completed on **5 October 2026** using the unchanged [measurement codebook, version 1](candidate-exposure-codebook.md). The project adapts **Florio and Spagnolo (2026)**; its [literature note](../literature.md) documents the Italian design and German precedents. This follow-up concerns historical public gender presentation and does not assign administrative sex/gender or certify research exposure.

**Five of the eight missing candidate presentations are now supported. Four additional pairs are classified.** Among the 15 decisions within 2 percentage points, **27/30 candidate presentations** and **13/15 pairs** are supported: four mixed, nine same-presentation and two unresolved pairs. The three missing presentations are in Heiden (both finalists) and Viersen (one finalist).

| Checkpoint | Supported candidates in priority 15 | Mixed pairs | Same pairs | Unresolved pairs |
| --- | ---: | ---: | ---: | ---: |
| Initial review | 22/30 | 4 | 5 | 6 |
| After this follow-up | 27/30 | 4 | 9 | 2 |

The full 55-pair checkpoint is **40/110 supported candidate presentations; six mixed, ten same and 39 unresolved pairs**. No additional mixed pair, female-presented win or female-presented loss has been added. The six mixed pairs still contain two wins and four losses. These descriptive acquisition counts do not choose an RDD bandwidth or establish adequate precision.

## Closed gaps and stronger evidence

| Municipality | New evidence | Date and section | Result |
| --- | --- | --- | --- |
| Leichlingen | [Official inaugural council minute](https://sessionnet.owl-it.de/leichlingen/bi/getfile.asp?id=136971&type=do), `leichlingen-minutes-nov2020` | 9 November 2020; physical PDF p6, agenda item 7 | A direct named masculine address closes the second finalist. Pair becomes same-presentation; evidence tiers B/C. The deputy nomination does not supply a full-time mayoral term. |
| Herzebrock-Clarholz | [UWG's own runoff invitation](https://uwg-herzebrock-clarholz.de/2020/09/16/der-unabhaengige-kandidatencheck/), `herzebrock-uwg-invitation-2020` | 16 September 2020; invitations to the 21/23 September public meetings before the 27 September runoff | Both finalists are directly addressed with named masculine wording. Pair becomes same-presentation; tier C/C. Primary authorship is distinct from political impartiality. |
| Übach-Palenberg | [Official inaugural council minute](https://www.up-rat.de/sessionnetbi/getfile.php?id=44198&type=do), `uebach-minutes-nov2020` | 4 November 2020; physical PDF p2, attendance | A named masculine address closes the second finalist. Pair becomes same-presentation; tier B/B. The spaced compound given name is manually corroborated against the official vote file and the dated party nomination; no surname is repaired. |
| Herten | [Official municipal biography](https://www.herten.de/rathaus/buergermeister), `herten-mayor-retrospective` | Publication date unverified; paragraph explicitly describing the 2020 electoral loss | An unambiguous personal pronoun is directly attached to the named 2020 event. Pair becomes same-presentation; tier B/B. Evidence is flagged retrospective. |
| Viersen | [Official 1 September 2020 council minute](https://ris.viersen.de/sdnetrim/UGhVM0hpd2NXNFdFcExjZZNArkUqB2KCCvqFjexZYYqaVE6eS8I3hjiRzs-md0xl/Oeffentliche_Niederschrift_Rat_01.09.2020.pdf), `viersen-minutes-sep2020` | Physical PDF p1, named chair and feminine role; RIS export separately dated 20 October 2022 | Strengthens the already supported finalist with official-authored tier B evidence. The other finalist remains unresolved. |

The three relevant official PDF pages were also rendered and visually inspected. This complements the exact text-locator checks and is not an independent second-person review.

## Remaining gaps

**Heiden:** the 2020 CDU programme, candidate introductions, newsletters and council/campaign articles were inspected. Generic masculine titles and neutral first-person statements do not qualify. Three party-hosted texts are newspaper reports or reprints; hosting does not make their narrative primary-authored. The current municipal biography uses ambiguous last-election wording, and the 2024 party reelection statement lacks an explicit 2020 presentation link. The public RIS and candidate-home routes returned HTTP 403, and the Green party home returned HTTP 503. The earlier inaccessible SPD programme route remains recorded. No protected access route was bypassed.

**Viersen:** the 2020 council and school-committee records, a named September 2020 MIT visit and the current municipal biography were inspected. The missing finalist appears in contemporary records, but names and generic masculine role labels do not suffice. A possessive in a paragraph headed by a generic school role was conservatively left unassigned. A later newspaper nomination retrospective is secondary; the current official biography does not explicitly describe the 2020 event. The supported finalist's additional official evidence cannot fill the other finalist's field.

Both pairs keep an explicit unresolved status and have no signed gender margin. Lack of evidence is not evidence of matching presentations. These are completed follow-up dispositions, not a claim that no qualifying source can ever be found.

## Search, provenance and validation

The existing [source manifest](nrw-close-pair-source-manifest.csv) retains its original 123 routes and adds **57 follow-up routes: 53 acquired originals and four unavailable attempts**. In total, **168 originals are cached and checksum-verified; 12 failed routes remain recorded**. Navigation source IDs link published council/calendar pages to the retrieved documents. Declared charsets are retained: some Heiden pages use Latin-1, and exact text checks now honor that encoding. No accepted assignment uses a search snippet.

The separate [follow-up query log](nrw-close-pair-priority-search-log.csv) contains **all 60 exact queries**, mapped to **15 complete request/response artifacts** in the [response inventory](nrw-close-pair-priority-search-responses.csv). These records complement the earlier initial-search inventory without rewriting its documented gaps. Timestamp semantics distinguish request times from the one batch timestamp recorded immediately after response return.

The Viersen historical calendar was retrieved through its documented public GET endpoint using the ordinary public page session. Its pinned JSON supplies discovery routes, not candidate labels. Reconstructing that dynamic response requires a current ordinary public session; it is not a static document guaranteed to reproduce byte-for-byte through a bare GET. Accepted presentation evidence is independently pinned in the linked public documents. Changed live originals require renewed inspection and new pins.

**Validation:** all 380 original election detail files were reparsed; all 382 statewide summary/detail pins and all 168 available review pins matched. The 55 vote margins, rounds and winners agree with the initial review. The unchanged codebook hash, exact locators, finalist identities and complete two-person dispositions pass the audit. **132 offline tests pass**, including a new check that legacy encoding preserves the named identity locator.

The [current 55-row ledger](nrw-close-election-evidence-summary.csv), [checkpoint JSON](nrw-close-election-checkpoint.json) and [main review](nrw-close-election-evidence-review.md) reflect these results. Raw originals, rendered pages, complete discovery responses and person-level annotations remain local under the [data policy](../data-management.md). FP05 retains its initial-review-complete status with this additional priority checkpoint. Carry all 39 unresolved pairs into FP06, retain a bounded acquisition queue for the three priority gaps, and complete FP02/FP04 before selecting main-study outcomes and windows. GitHub Pages remains deferred until research completion.
