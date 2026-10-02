# Pilot source check — 3 October 2026

This follow-up establishes source access and selected parsing checks. It is not an analysis dataset, a power assessment, or a treatment-effect estimate.

## Schild resolved

**Schild, Christopher-Johannes (2013). *Do female mayors make a difference? Evidence from Bavaria*. IWQW Discussion Papers No. 07/2013. Friedrich-Alexander-Universität Erlangen-Nürnberg, Institut für Wirtschaftspolitik und Quantitative Wirtschaftsforschung.** [Stable repository record](https://hdl.handle.net/10419/81935); [primary PDF](https://www.econstor.eu/bitstream/10419/81935/1/766841529.pdf).

An OpenAlex title search located the record. EconStor independently confirmed the author, title, year and series; the PDF was obtained. Its abstract and election-data section were inspected. The paper studies municipal expenditure allocation and government size, using Bavarian candidate data with names, gender, profession, vote shares and nominations. Section 3.1 describes elections between 1984 and 2009 and municipal-boundary issues. Historical access in this paper does not establish present access to the same dataset.

The abstract reports no female-mayor effects on expenditure allocation or government size across the author's specifications, and distinguishes standing for reelection from winning conditional on standing. These are the paper's reported findings; precision and robustness still need full review. This resolves the citation marked unresolved in the initial review, without establishing the procurement novelty claim.

## Exact NRW votes: three-source probe succeeded

Detailed official downloads were obtained for Kleve (154036), Bedburg-Hau (154004), and Mettmann (158024), via the linked `aktuell/txtdateien/b<code>kw2000.txt` files. Each contains all first-round candidates and exact runoff votes.

| Municipality | First-round candidate rows | Runoff valid votes | Validation |
| --- | --- | --- | --- |
| Kleve | 6 | 13,889 | First-round and runoff candidate totals reconcile with valid votes |
| Bedburg-Hau | 3 | 5,440 | First-round and runoff candidate totals reconcile with valid votes |
| Mettmann | 4 | 12,889 | First-round and runoff candidate totals reconcile with valid votes |

These municipalities are convenience examples selected from the earlier export, not a random sample or verified mixed-gender sample. Candidate gender and actual terms have not been independently established. Exact counts allow unrounded margins once gender and eligibility are verified. Election dates are not substitutes for term-start dates.

## TED live search: succeeded

The anonymous endpoint `POST https://api.ted.europa.eu/v3/notices/search` returned records. Official [Search API documentation](https://docs.ted.europa.eu/api/latest/search.html) describes this endpoint.

Validated query:

```text
buyer-country = DEU AND buyer-name ~ Kleve AND publication-date >= 20210101 AND publication-date <= 20241231
```

With `scope: ALL`, page 1 and limit 10, the API reported **279 matching notices**, returned 10, and reported `timedOut: false`. This is a name-search count across notice types, not a count of Stadt Kleve contracts. An initial query using country value `DE` returned HTTP 400; `DEU` succeeded.

The returned sample includes Stadt Kleve, Kreisverwaltung Kleve, and Umweltbetriebe der Stadt Kleve AöR. It mixes `cn-standard` (competition notices), `can-standard` (award notices), and `corr` (corrections). Therefore buyer jurisdiction, notice type, related notices, lots, and duplicates must be resolved before counting awards.

A competition-notice XML download for **3715-2021** succeeded (21,653 bytes, legacy TED schema R2.0.9). Three award XML links (**10522-2021**, **63286-2021**, **85473-2021**) returned HTTP **202 with empty bodies**, including repeat attempts. Award-record XML retrieval and outcome extraction remain unresolved; the search success alone does not establish accessible bid or award-date data. Investigate the documented download route and alternatives before extending collection. Do not parse an empty response as a valid record.

## Reproduce the source probe

Run from the repository root with Python 3 and network access:

```sh
python src/pilot/source_probe.py
```

The script uses only the Python standard library, downloads the three exact election files, validates candidate totals for both rounds, and repeats the bounded TED search. It writes raw responses, a timestamped URL/request/checksum manifest, and an aggregate summary under ignored `outputs/source-probe/`. It does not download award XML, infer gender, link buyers, estimate effects, or create a representative sample. Search counts may change as source records change.

The probe was executed successfully on 3 October 2026. Full-text PDFs and raw source responses remain local and uncommitted.

## Remaining work

- Expand NRW extraction only after reviewing additional format cases, non-runoff contests, and independent-city records.
- Establish source-backed candidate gender and actual term dates.
- Resolve TED award downloads, then audit bids, dates, award values, lots, cancellations, corrections, and legacy/eForms differences.
- Audit buyer responsibility separately for municipal departments, county administrations, public-law entities and companies.
- Continue full-text review of German and French studies and the broader literature search.
- Confirm research-access and linkage conditions for Vergabestatistik before choosing it as the main source.
