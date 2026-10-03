# NRW 2020: exact-margin screen and evidence priorities

Date: 3 October 2026. This screen uses all 102 successfully validated district-municipality runoff files. It includes every gender combination; it is **not** a mixed-gender RDD sample or a power analysis.

## Counts from exact votes

| Inclusive absolute margin | Runoff elections |
| --- | --- |
| At most 1 percentage point | 3 |
| At most 2 percentage points | 10 |
| At most 5 percentage points | 23 |
| At most 10 percentage points | 37 |

Margin = absolute difference between the two candidates' exact votes, divided by valid runoff votes, multiplied by 100. It is a candidate-to-candidate margin, not the winner's distance above 50%; these differ by a factor of two in a two-candidate race. The project protocol uses candidate-to-candidate margins.

These counts are upper bounds on mixed-gender contests within this particular audited runoff subset, not on all NRW mayoral elections. Independent cities, eligible outright first-round victories and other election dates have not been screened. Gender and term verification can only reduce this subset's eligibility counts.

## How to use the screen

Prioritize source checks for near-cutoff cases, while preserving the full 102-event universe and logging missingness. Do not infer gender from names or select observations using procurement outcomes. Candidate identity, both gender records, actual terms, and buyer linkage remain prerequisites for analysis.

The closest source codes are 962024 (0.3972 pp), 378016 (0.6862 pp), and 158032 (0.8985 pp). These identifiers remain source codes until full AGS and territorial vintage validation. Do not label these events mixed-gender before supporting evidence is obtained.

## Reproduce

```sh
python src/pilot/nrw_runoffs.py
python src/pilot/nrw_margin_screen.py
```

The margin script checks the per-file audit status and exact valid-vote totals before counting. It writes the full event screen under ignored `outputs/nrw-runoff-audit/`. It was executed successfully. Counts use exact votes rather than published rounded percentages.

## Bayern evidence follow-up

The Hallbergmoos municipal council page embeds a separate official citizen-information system. Following that link located the [council membership page](https://buergerinfo-hallbergmoos.digitalfabrix.de/kp0040.asp?__kgrnr=1) and [Stefan Kronner's member record](https://buergerinfo-hallbergmoos.digitalfabrix.de/pe0051.asp?__kpenr=46). The current record supports the full-name identity and lists SPD membership, but exposes no explicit gender field in the inspected content. Gender remains unresolved rather than inferred from the name or photograph.

The 2024 election notice labels this candidate's nomination independently; a current council party field is not a substitute for the historical nomination. Both should retain their dates and source contexts. Tanja Knieler is listed as second deputy mayor on the council page, but she is not one of the 2024 runoff candidates. Her current office title must not be used to manufacture a mixed-gender decisive contest.

The official embedded council-system route is a useful lead for historical memberships and term documentation. No dated term-start corroboration or complete opponent-gender record was established in this follow-up.

## Next checks

1. Verify the finalist identities and gender of NRW near-cutoff events using official nominations, biographies and archived records.
2. Continue Bayerns historical and district-municipality source inventory, including official council-system histories.
3. Build election-specific term intervals rather than reuse current officeholder pages.
4. Count fully verified eligible elections before assessing precision; these descriptive bands do not select a final RDD bandwidth.
