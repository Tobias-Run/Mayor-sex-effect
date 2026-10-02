# Initial literature and data review

Review date: 3 October 2026. This is a first source audit, not a completed systematic review or a feasibility approval. No treatment effects have been estimated. Provider contact has not been made.

## Initial assessment

There is a documented legal route to request anonymized procurement statistics for research. Municipality-level linkage remains unconfirmed. A usable official NRW election export is available, but it is a summary rather than a complete candidate register. Proceed with a pilot-source assessment; do not yet commit to the main RDD.

## Literature findings

### Florio and Spagnolo: primary paper obtained

Florio, Erminia, and Giancarlo Spagnolo (2026). *Female Mayors and Public Procurement*. CEIS Research Paper 623, revised 3 July 2026 according to [RePEc](https://ideas.repec.org/p/rtv/ceisrp/623.html). [Publisher PDF](https://ceistorvergata.it/RePEc/rpaper/RP623.pdf). DOI: [10.2139/ssrn.7046899](https://doi.org/10.2139/ssrn.7046899).

The PDF was downloaded and its abstract, data sections, empirical-strategy section, and relevant table notes inspected. This is a targeted initial reading, not a complete replication audit.

- Procurement data: ANAC, 2013–2019; election data: 2008–2019 (sections 3.1–3.2).
- Contract-phase data are complete for only around 49% of contracts; reported missing adjudication is around 76% for direct awards (section 3.1, printed pp. 7–8). These are the authors' reported figures, not recomputed statistics.
- The design uses decisive first rounds or runoffs according to Italian electoral rules; these rules must not be copied mechanically to Germany (section 4).
- Estimation is at contract level. Table notes restrict the reported analysis to municipalities with at least 5,000 residents. Appendix checks include contracts published at least six months after election.
- The abstract reports less negotiated contracting, more direct awards, fewer renegotiations, and no differences in winner characteristics or other post-award outcomes. This describes Italian findings, not an expectation for Germany.

The German protocol should explicitly distinguish publication dates from contract dates, investigate reporting selection, and justify its own municipal scope and weighting. Do not automatically inherit every control or polynomial specification from the Italian paper.

### Baskaran and Hessami: published version identified

Baskaran, Thushyanthan, and Zohal Hessami (2025). *Women in Political Bodies as Policymakers*. **Review of Economics and Statistics 107(6): 1501–1517**. DOI: [10.1162/rest_a_01352](https://doi.org/10.1162/rest_a_01352). The 2023 working-paper DOI remains [10.2139/ssrn.4377785](https://doi.org/10.2139/ssrn.4377785).

Crossref publication metadata and abstract were inspected. The abstract confirms Bavarian local council elections, mixed-gender races for last party-specific council seats, and public childcare expansion. It reports a 40% acceleration from an additional female councillor, concentrated in councils with few women. This magnitude is an abstract claim; full-text methods and robustness have not yet been reviewed. Councillor representation is distinct from electing a mayor.

### Bauhr and Charron: exact reference resolved

Bauhr, Monika, and Nicholas Charron (2021). *Will Women Executives Reduce Corruption? Marginalization and Network Inclusion*. **Comparative Political Studies 54(7): 1292–1322**. DOI: [10.1177/0010414020970218](https://doi.org/10.1177/0010414020970218). Crossref records online publication on 2 December 2020 and print publication in June 2021.

Metadata and abstract inspected. The abstract describes French municipal elections, procurement corruption-risk data for 2005–2016, RDD and first-difference designs, and results driven by newly elected women mayors. Corruption-risk indicators must not be treated as observed corruption. Full-text review remains pending.

### Schild: unresolved

The exact title *Do Female Mayors Make a Difference? Evidence from Bavaria* was searched in Crossref; no matching bibliographic record was established. A RePEc search page returned no usable result listing. These unsuccessful searches do not establish absence of the paper. Full author identity, year, outlet, stable link, and substantive claims remain unresolved. Search university repositories, author profiles, and working-paper collections next.

## Procurement data findings

| Source | Verified evidence | Consequence / unresolved issue |
| --- | --- | --- |
| [Destatis procurement statistics](https://www.destatis.de/DE/Themen/Staat/Oeffentliche-Finanzen/Vergabestatistik/_inhalt.html) | Collection began in October 2020; page currently describes public quarterly tables covering 2021–2024 | Public aggregates cannot support election-level linkage; availability of later microdata is unconfirmed |
| [VergStatVO § 5](https://www.gesetze-im-internet.de/vergstatvo/__5.html) | Universities and other research institutions can request statistical evaluations or anonymized data, subject to necessity and proportionate effort; Destatis may provide them on the ministry's behalf | Legal route exists; approval, researcher eligibility, identifier retention, dates, and linkage permission remain unconfirmed |
| [VergStatVO § 2](https://www.gesetze-im-internet.de/vergstatvo/__2.html) | Below-EU-threshold reporting applies to net contract values strictly exceeding EUR 50,000 and the other statutory conditions | Not a census of all municipal purchases; do not equate reporting threshold with permission to use a procedure |
| [Annex 1](https://www.gesetze-im-internet.de/vergstatvo/anlage_1.html) | Above-threshold form includes buyer name, postal code, EU notice number, contract date, bids, procedure, SME status, and differentiated sustainability criteria | Collected fields are not guaranteed research-release fields; no municipal AGS field was identified in this form |
| [Annex 8](https://www.gesetze-im-internet.de/vergstatvo/anlage_8.html) | Below-threshold form contains procedure, contract date, sustainability categories, and SME winner status; total bids and several other fields are voluntary | Single-bid and bid-count outcomes need a completeness audit; sustainability detail differs from Annex 1 |
| [FDZ catalogue](https://www.forschungsdatenzentrum.de/de/alle-daten) | Public catalogue inspected | No standard procurement microdata product was identified in this initial inspection; § 5 route should be assessed directly |
| [TED developer documentation](https://docs.ted.europa.eu/api/latest/index.html) | Anonymous search/retrieval of published notices is documented; TED Apps went into production on 14 November 2022 | Promising public pilot route; no live record query or historical coverage validation completed yet; schema changes require harmonization |
| [German notice service](https://www.oeffentlichevergabe.de/) | Site redirects to a JavaScript application | Static request did not establish API, historical coverage, or completeness; inspect official reuse documentation next |

Buyer postal codes are not unique municipality identifiers. Buyer names and responsibilities need audited mapping, and anonymization may prevent that mapping altogether. The Leitweg-ID is only mandatory for federal buyers in the inspected annexes; it cannot be assumed to solve municipal linkage.

## Election data: NRW 2020 first audit

The [official results page](https://www.wahlergebnisse.nrw/kommunalwahlen/2020/index.shtml) links a [semicolon-delimited district-municipality mayor export](https://www.wahlergebnisse.nrw/kommunalwahlen/2020/KW20_pers_gemeinden.txt). Download and parsing succeeded.

Initial file counts: **475 rows, 373 distinct municipality codes, 102 runoff rows dated 27 September 2020, and 15 rows recording no election**. These are file-level counts, not counts of eligible mixed-gender or close races. The file excludes the separate independent-city export.

Fields include municipality code/name, round date, two candidate-name slots, nominations, and percentages. There is no explicit gender field and no raw vote-count field. First-round rows can omit losing candidates after an outright win. Candidate-slot labels do not guarantee that the first slot wins the runoff: the downloaded file contains examples where the second candidate has the larger share. Percentages are rounded to one decimal place.

Therefore: obtain detailed candidate and vote-count results; do not derive gender from names alone; determine the winner from verified outcomes; normalize municipal identifiers with their territorial vintage; verify actual term dates separately. Do not compute near-zero RDD margins from rounded summary percentages where exact counts can be recovered.

The [Bavarian official elections page](https://www.statistik.bayern.de/wahlen/kommunalwahlen/) confirms normally six-year municipal terms and exceptions to synchronized elections. Candidate-level formats were not yet audited. Bavaria and NRW are pilot candidates, not a finalized study sample.

## Next work packages

1. Resolve Schild and obtain accessible full text for the German and French studies; expand the documented literature search beyond the pitch's anchors.
2. Inspect detailed NRW first-round and runoff results and raw counts; audit Bavaria's candidate-level availability.
3. Test TED public retrieval on a small municipal award sample, recording schema, missing bids, buyer mapping, and duplicates.
4. Prepare a provider inquiry covering research eligibility, accessible years, identifiers, date precision, linkage rules, storage, costs, and disclosure constraints. Sending it requires explicit authorization; no message has been sent.
5. Select the pilot only after these checks; count independently verified mixed-gender elections before a power assessment.

## Search and retrieval record

Crossref bibliographic queries: `Do Female Mayors Make a Difference Evidence from Bavaria`; `Women in Political Bodies as Policymakers`; `Bauhr Charron 2021 female mayors procurement corruption`. Exact DOI records were then retrieved for the published German and French papers. Official URLs and RePEc/publisher links above were fetched on 3 October 2026. A guessed NRW `bm.shtml` URL returned 404; the linked `index_bm.shtml` page was subsequently located. Local downloaded material is under ignored `outputs/source-review/`; third-party full texts and election rows have not been committed.
