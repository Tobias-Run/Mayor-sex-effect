# Bavaria first, NRW second: extraction audit

Date: 3 October 2026. Work order follows the requested Bavaria-first sequence. No RDD sample or treatment-effect estimates have been produced.

## 1. Bavaria: official workbook obtained and audited

[Official mayoral-results page](https://www.statistik.bayern.de/wahlen/kommunalwahlen/bgm/index.html) links an [Excel workbook](https://www.statistik.bayern.de/mam/wahlen/kommunalwahlen/bgm/wahlergebnisse_mandatsr%C3%A4ger.xlsx), described as updated on **14 July 2026**. Download succeeded.

The workbook has two sheets:

| Sheet | Audited records | Information |
| --- | --- | --- |
| Officeholders | 2,127, including 2,056 municipalities and 71 counties | Municipality key, territory type, election date, first entry into office, office title, incumbent name, gender, birth year, turnout, vote share, nomination |
| Election results | 2,443, including 2,338 municipal round records | Date, runoff flag, eligible voters, turnout, invalid and valid ballots, nomination labels and exact votes |

Municipal officeholders comprise **25 independent cities and 2,031 district municipalities**. Source gender codes are `m` for 1,798 and `w` for 258 municipal officeholders. These are snapshot counts, not female-treatment election counts. The result sheet contains **283 municipal runoff rows**, not 283 verified mixed-gender races.

### Limitations and use

- The officeholder sheet explicitly records gender, which can support source-backed winner verification.
- The result sheet identifies nomination labels (`Kennwort`) rather than names and gender of every candidate. We cannot reliably assign losing-candidate gender from a party label.
- `Erster Amtsantritt` is first entry into office, not necessarily the start of the latest reelection term. Actual term intervals need separate construction.
- This is a current snapshot of officeholders and associated results, not a complete historical election panel. It cannot establish all pre-2026 contests or predecessor histories.
- County executives must be excluded from the municipal-mayor sample. Professional and honorary mayor roles must be distinguished and their eligibility justified.
- Source municipality keys have six digits; normalize with the state prefix and historical geographic validation rather than assuming they are already full AGS values.
- The official page states majority election with a runoff between the two highest-vote candidates when nobody obtains more than half of valid votes. Exceptions and historical rule changes still require legal review.

Next Bavaria step: locate archived candidate-complete 2020/2014 results or confirm state statistical-office access to historical candidate records. Use current workbook records as supporting evidence, not as a substitute for losing candidates or term histories.

### Reproduce

```sh
python src/pilot/bavaria_workbook.py data/raw/bavaria/officeholders-2026.xlsx
```

Download the linked workbook into the ignored raw-data path first. The parser uses Python's standard library, checks key headers, and prints aggregate sheet counts. It does not infer missing candidate identities or assess vote reconciliation. The original workbook remains local.

Downloaded workbook SHA-256: `ee4801b905b4dcd87f85cc1e7854d43e4ef243f67b2aa6fd2e01e3285270af07`.

## 2. NRW: all 102 district-municipality runoffs audited

After the Bavaria workbook audit, the NRW probe was expanded from three examples to **all 102 runoff municipalities** present in the [official 2020 district-municipality summary export](https://www.wahlergebnisse.nrw/kommunalwahlen/2020/KW20_pers_gemeinden.txt).

**102/102 detailed files downloaded and validated; no failures in this run.** Each file contains exactly two candidates with runoff vote counts; their totals match reported valid runoff votes. All recorded first-round candidate votes also reconcile with first-round valid votes.

This validates the extraction format across the runoff subset. It does not establish gender, actual term dates, narrow-margin eligibility, or representative coverage of all NRW elections. Non-runoff contests and independent-city mayoral elections remain outside this audit. County executives are outside this export.

```sh
python src/pilot/nrw_runoffs.py
```

The script uses Python's standard library and four concurrent HTTP requests at most. It writes downloaded files, per-file URLs/checksums and validation results under ignored `outputs/nrw-runoff-audit/`. Source responses and candidate-level records have not been uploaded to GitHub.

## Immediate priorities

1. Bavaria: historical candidate-complete access, especially 2020/2014, plus both candidates' gender and actual terms.
2. NRW: source-backed gender and term verification for the validated runoff records; independent-city and non-runoff format audits next.
3. Both states: explicit election eligibility, territory vintage, source completeness, and municipality-to-buyer mapping.
4. Only after these steps, count verified mixed-gender close races and assess power.

Both audit scripts were executed successfully. Publication of the interactive GitHub Pages companion remains deferred until research completion.
