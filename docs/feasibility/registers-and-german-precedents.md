# Election registers and lessons from German research

Checked: 3 October 2026. This is a targeted source review, not an exhaustive audit of all 16 states or proof that no research dataset exists.

## Finding: national geographic backbone, decentralized election records

No nationwide official historical register containing all mayoral candidates, exact votes, candidate gender, decisive rounds, and actual terms was identified in the inspected sources. The defensible working assumption is to construct a harmonized register from state and municipal sources, while continuing to search for reusable research datasets.

This conclusion concerns data availability observed in this review. It does not mean that every state's statistical office centrally holds every mayoral election, or that research groups and commercial providers lack cross-state collections.

| Source / level | Evidence inspected | Value for this project | Limitation |
| --- | --- | --- | --- |
| [Federal Returning Officer: responsibilities](https://www.bundeswahlleiterin.de/ueber-uns/aufgaben.html) | Responsibilities describe Bundestag and European Parliament elections | Official orientation and federal election sources | No nationwide mayoral candidate register identified; federal election results are not mayoral results |
| [GV-ISys municipality directory](https://www.destatis.de/DE/Themen/Laender-Regionen/Regionales/Gemeindeverzeichnis/_inhalt.html) | National directory includes AGS, ARS, municipality names, administrative-seat postal codes, population and territorial classifications; quarterly/yearly formats described | National municipality universe and identifier backbone; denominator for coverage audits | Geographic register, not a candidate or officeholder history; use matching territorial vintages rather than current identifiers blindly |
| [NRW official 2020 election results](https://www.wahlergebnisse.nrw/kommunalwahlen/2020/index.shtml) | Summary and detailed exact-vote exports already downloaded | Verified state-source extraction path | Gender, terms, and independent-city records still need work |
| [Bavarian municipal elections](https://www.statistik.bayern.de/wahlen/kommunalwahlen/) | Official page states municipalities conduct the elections, the state returning officer is not responsible, and the statistical office evaluates/publishes results | Strong pilot candidate and historical research precedent | Present candidate-level access and formats still need confirmation |
| [Hessian statistics election page](https://statistik.hessen.de/unsere-zahlen/wahlen) | Official election inventory inspected | Additional state lead; Schild notes historical Hessian data | Council election listings alone do not confirm complete mayoral candidate histories |
| [Thuringian election portal](https://wahlen.thueringen.de/) | Lists individual mayoral elections and notes that the state returning officer is not responsible for municipal elections | Concrete source lead for asynchronously held elections | Record-level format, historical completeness, gender and terms not audited |
| [Baden-Württemberg statistics election page](https://www.statistik-bw.de/Wahlen/) | Municipal election topic page inspected | Institutional/source lead | Council-election statistics do not establish mayoral coverage; Schild's 2013 footnote reports no central collection at that time, which must not be treated as a verified current fact |
| Research catalogues | OpenAlex located the German papers; GESIS search frontend returned HTTP 403 | Search author datasets and replication archives separately | No nationwide usable candidate dataset established by this search; GESIS could not be reviewed |

Current officeholder directories, lists of municipalities, and aggregate counts of female mayors cannot reconstruct narrow defeats, exact vote margins, or historical treatment dates. They may be useful supplementary verification sources, but are not substitutes for election records.

## What we can learn from Schild (2013)

Source: [EconStor record](https://hdl.handle.net/10419/81935) and [primary PDF](https://www.econstor.eu/bitstream/10419/81935/1/766841529.pdf). Sections 3–4, Table 1 and footnotes 15, 17, 19–22 inspected.

- **Data route:** Bavarian Statistical Office election data include names, gender, profession, vote shares and nominations. Finance, tax, population and covariate data also come from the state statistical office. This gives us a concrete institutional data lead, not an assurance that a downloadable dataset is currently available.
- **Comparable institutions:** Restriction to Bavaria reduces institutional heterogeneity. Footnote 15 explains the historical availability advantage and notes differing municipal law across states. We should pilot one state first and document comparability before pooling.
- **Decisive rounds:** First rounds leading to runoffs are not counted as separate decisive elections. Runoff results establish the final contest. We should explicitly represent election events and rounds, avoiding duplicate treatment assignment.
- **Actual identifying sample:** Table 1 reports 12,692 elections in 1978–2009, but only 547 two-candidate contests with one woman. These are historical counts reported by the author, not our sample. Large nominal election datasets can still yield few identifying cases.
- **Nonstandard contests:** Uncontested elections and write-in votes need rules. Footnote 22 reclassifies rare nominally two-candidate elections with more than 10% unlisted votes. We should inspect the modern rules and justify our own eligibility criteria rather than copy this threshold.
- **Territorial changes and off-cycle elections:** Municipal geography and exceptional dates are documented. The paper checks sensitivity to excluding off-cycle elections. Our register should record municipal vintage, early exits and successor terms where available.
- **Outcome timing:** Section 4 compares averages of years 4–6 after election with years −3 to −1 before it. Smoothing addresses noisy budgets. This inspires explicit observation windows and lag checks, but those long windows cannot simply be transferred to procurement data beginning in October 2020.
- **Validity:** Predetermined municipal characteristics inform continuity checks. Use baseline covariates with clear measurement timing.

The paper's fiscal outcomes, historical population of municipalities and reported null results are not procurement results and do not imply a null effect for our study.

## What we can learn from Baskaran and Hessami

Published reference: [Review of Economics and Statistics (2025), DOI 10.1162/rest_a_01352](https://doi.org/10.1162/rest_a_01352). Full-text reading here uses the accessible **2023 IZA Discussion Paper 15983**, [EconStor record](https://hdl.handle.net/10419/272610), [PDF](https://www.econstor.eu/bitstream/10419/272610/1/dp15983.pdf). Final published-version changes have not been checked. The IZA-hosted PDF initially returned HTTP 503; the EconStor copy was retrieved successfully.

- **Hand collection can be necessary:** The introduction explicitly says their candidate-level Bavarian council data are unavailable from centralized official sources. Their collection covers 224,448 candidates in elections in 2002, 2008 and 2014. This is council data, so it does not contradict Schild's state-source mayoral data.
- **Audit the missing municipalities:** Section 3.1.1 reports complete data for 76.9% of municipalities in 2014, 49.1% in 2008 and 28.3% in 2002. It compares included and excluded municipalities and reports that included municipalities have 28% more inhabitants. Our scraping success and archival availability should therefore be outcomes of an explicit coverage audit, not invisible sample restrictions.
- **Separate outcome and election coverage:** Childcare data cover all 2,056 Bavarian municipalities for 2006–2017, while candidate coverage is incomplete. We should separately document election availability, procurement availability, and successful linkage.
- **Measurement stability:** Section 3.1.2 favors changes in childcare spots per 1,000 residents over growth rates because zero baselines and small denominators cause problems. For procurement, zero observed contracts, rates with small award denominators, and changes in reporting need explicit treatment; missing records are not automatically zeros.
- **Institutional identification:** Mixed-gender competition for the last party-specific council seat holds party context relatively fixed. That identification cannot be copied to mayoral winner comparisons, where the opposing candidates can differ in party. Our estimand must retain that distinction.
- **Inference and diagnostics:** The working paper documents municipal clustering, covariate checks, and multiple specifications. The useful lesson is to respect the independent assignment unit and examine validity; the precise estimators need to match our mayoral design.

The introduction and section 3.1.1 give slightly different municipality totals (1,634 and 1,632). We will not silently select one as a reconstructed study count; check the final article and replication material before using it quantitatively.

## Recommended project implementation

1. Build a national municipality backbone using an appropriate historical GV-ISys vintage, including source and territorial-change metadata.
2. Build state-specific extraction adapters, starting with NRW's verified exact-vote route and assessing Bavaria's data access in parallel.
3. Maintain separate municipality, election-event, round, candidate, and term tables; store source-backed gender and uncertainty explicitly.
4. Track the universe and each exclusion: unavailable election record, incomplete candidate list, unverifiable gender, ineligible contest, unknown term date, missing procurement, ambiguous buyer mapping.
5. Report counts of mixed-gender decisive elections within plausible margins before assessing power. State pools are conditional on comparable institutions and adequate data quality.
6. Search replication archives and author repositories for reusable data. A provider/author inquiry can be drafted if useful, but no correspondence has been sent.

No raw candidate data or third-party PDFs are included in this commit. No claim of exhaustive nationwide coverage is made.

## Search record and limits

Official pages listed above fetched on 3 October 2026. OpenAlex searches included `Women in Political Bodies as Policymakers`, `German mayor elections dataset nationwide`, and `German local elections database mayor`; the latter two yielded mainly irrelevant results and do not establish absence of a register. Direct checks of federal responsibilities and GV-ISys provide the strongest national-level evidence. GESIS could not be inspected due to HTTP 403. Commercial/current-officeholder sources and all remaining state portals have not yet been comprehensively audited.
