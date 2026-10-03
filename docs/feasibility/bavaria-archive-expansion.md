# Bavarian municipal archive expansion

Checked on 3 October 2026. These are convenience source probes, not a representative sample or a verified mixed-gender RDD register.

## Two additional 2020 runoff sources validated

| City | Official result | Valid votes | Absolute candidate margin | Validation |
| --- | --- | --- | --- | --- |
| Augsburg | Eva Weber (CSU): 63,762; Dirk Wurm (SPD): 38,532 | 102,294 | 24.6642 percentage points | Exact candidate totals reconcile |
| Nuremberg | Marcus König (CSU): 103,865; SPD opponent: 95,237, abbreviated as Brehm in the result table | 199,102 | 4.3335 percentage points | Exact candidate totals reconcile |

The Nuremberg archive's table abbreviates candidate names. It must not be matched to candidates using surname alone: the 2014 archive also contains a Brehm entry under a different nomination. Recover full identities from the official candidate list or election report before assigning gender or connecting records across elections.

A narrow margin alone does not make a contest eligible. No source-backed two-candidate gender classification or exact term interval has been completed for these new probes. Neither contest is included in an analysis sample.

## Official archive navigation

- [Augsburg municipal elections 2020](https://www.augsburg.de/buergerservice-rathaus/rathaus/wahlen-abstimmungen/kommunalwahl-2020) links the first round and runoff, identifies Eva Weber and Dirk Wurm, and records the election dates.
- [Augsburg runoff result](https://www.augsburg.de/fileadmin/user_upload/verwaltungswegweiser/buergeramt/wahlen/kommunalwahlen/2020/ob-stichwahl/index.html) provides exact votes. It notes that the runoff was postal-only and precinct breakdowns are unavailable, so only the citywide result is shown.
- [Nuremberg 2020 runoff archive](https://www.nuernberg.de/internet/wahlen/komw2020_ergebnisse_obs.html) links the detailed result and official reports.
- [Nuremberg detailed runoff](https://www.nuernberg.de/datenwahlen/ko2020/prod/wahl-2020-03-29/09564000/html5/Buergermeisterwahl_Bayern_15_Gemeinde_Stadt_Nuernberg.html) contains exact totals and an Open Data CSV link. The CSV has not yet been downloaded in this check.
- [Nuremberg 2014 archive](https://www.nuernberg.de/internet/wahlen/ergebnisse_ob_2014.html) links an [official overall result](https://www.nuernberg.de/datenwahlen/ko2014/obw/ob14_ges.html), precinct results, and reports. The overall page was retrieved and shows nine candidate/nomination entries with exact votes; independent reconciliation and full-name recovery remain pending.
- [Munich 2020 runoff press area](https://www.wahlen-muenchen.de/ergebnisse/20200329oberbuergermeisterwahl/pressebereich.html) links a UTF-8, semicolon-delimited precinct CSV. This provides a potential machine-readable alternative to HTML; it has not been downloaded in this check.

Municipal archive navigation succeeded after guessed Augsburg and Nuremberg URLs returned 404. Record the successful linked sources, not the assumption that guessed failures mean data are absent.

## Code and verification

```sh
python src/pilot/additional_bavaria.py
python src/pilot/munich_2020.py
```

Both scripts ran successfully. The common HTML table reader is now in `src/pilot/html_tables.py`. The Munich probe was rerun after that refactor and both vote totals still reconcile. Raw HTML, candidate labels and checksums are saved under ignored outputs directories; record-level source data are not committed.

Absolute margins are descriptive differences divided by valid votes. They are not signed female-candidate running variables: that sign requires independent gender verification.

## Implications for acquisition

Bavaria now has three demonstrated municipal archive routes: Munich, Augsburg and Nuremberg. Their HTML schemas differ, supporting state-specific discovery and municipality-specific adapters rather than one guessed URL pattern. Large-city examples do not establish archival completeness for small municipalities, which may dominate the relevant mayoral-election universe.

The next register version should store source URL and retrieval date, full candidate identity, nomination, exact vote count, round date, source-backed gender and its verification status, actual term dates and supporting documents, municipal identifier/vintage, eligibility decision and exclusion reason. Unresolved fields must remain visibly unresolved.

Historical central access, smaller-municipality coverage, candidate gender and term histories remain the principal open tasks. The prepared Bavaria inquiry has not been sent.
