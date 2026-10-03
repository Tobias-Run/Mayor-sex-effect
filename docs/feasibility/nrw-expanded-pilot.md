# NRW: expanded buyer scope and full-notice outcome audit

Checked on 3 October 2026. The [original operational pilot](nrw-operational-pilot.md) remains a reproducible 55-notice baseline. This supplement completes its buyer-scope queue and expands full-document measurement. The project adapts **Florio and Spagnolo's [Female Mayors and Public Procurement](https://doi.org/10.2139/ssrn.7046899)** to Germany, drawing on the [German literature and data precedents](../literature.md). **No treatment effect or analytical sample has been estimated.**

**Subsequent update:** the [latest follow-up](nrw-pilot-completion.md) resolves the two legacy layouts below and supplies 57 supported units, including 52 with both date and total count. It also adds exact archived Iserlohn presentation and separate entry/activity evidence. The 54/49 counts below describe the earlier scope-expansion stage; running the current updated outcome parser yields the subsequent totals.

**The fixed 115-notice TED query now supplies 92 individually accepted municipal notices. Fifty full PDFs have been acquired and pinned; 46 belong to the expanded municipal cohort. Their supported award sections yield 54 award/lot-result units, including 49 with both an explicit contract date and a total tender count.** The relevant independent electoral units remain the same three 2020 municipal elections.

## All original scope cases reviewed

The original 40 municipal-prefix cases and one multiple-label case have now been checked against their full contracting-authority sections and procurement scope. The [41-row decision register](nrw-buyer-scope-review.csv) contains exact indexed labels, a notice-specific decision, AGS where accepted, and a short checked scope quotation. The [50-PDF manifest](nrw-expanded-source-manifest.csv) records source URLs, SHA-256 hashes, file sizes and UTC retrieval timestamps. The original [TED request manifest](nrw-ted-request-manifest.json) defines the unchanged search window and fields.

| Reviewed case type | Notices | Decision |
| --- | ---: | --- |
| City departments and mayor/department name variants | 28 | Retain as the identified city administration |
| City explicitly represented by KoPart, ISPEX or KUBUS | 9 | Retain as represented-city notices; preserve the agent distinction |
| Regional beneficiaries named after Iserlohn | 2 | Exclude from a single-city treatment assignment |
| Joint city/company or city/public-establishment authorities | 2 | Exclude from the single-city cohort |

Thus, 37 notices supplement the strict 55-notice baseline, yielding **92**. The remaining **23** are 19 separate-organization notices, two regional-beneficiary notices and two joint-authority notices. There is no unresolved buyer-scope case within this particular 115-notice snapshot. This does not prove that every city alias, notice type or below-threshold procurement has been acquired.

| Municipality | Original strict aliases | Accepted departments/variants | Accepted represented-city notices | Expanded total |
| --- | ---: | ---: | ---: | ---: |
| Iserlohn | 36 | 1 | 0 | **37** |
| Velbert | 4 | 27 | 7 | **38** |
| Geilenkirchen | 15 | 0 | 2 | **17** |
| Total | **55** | **28** | **9** | **92** |

This gives **83 city-administration notices without an external representation label** and **nine explicitly represented-city notices**. The split is available for future eligibility decisions; representation does not establish the mayor's personal decision authority.

The full notices explain why name-prefix matching alone fails. Iserlohn notice [247575-2023](https://ted.europa.eu/de/notice/247575-2023/pdf) concerns the six-municipality LenneSchiene regional management service; [249146-2023](https://ted.europa.eu/de/notice/249146-2023/pdf) concerns Hemer, Iserlohn and Menden together. Velbert notice [321058-2021](https://ted.europa.eu/de/notice/321058-2021/pdf) names the city and its municipal utility jointly. Notice [254083-2024](https://ted.europa.eu/de/notice/254083-2024/pdf) has both the city and Technische Betriebe Velbert AöR as buyers. A Velbert performance location does not turn those joint authorities into a sole-city buyer.

Conversely, the seven KoPart notices explicitly name the city of Velbert as the represented contracting authority and locate the supplies there. The Geilenkirchen ISPEX gas and KUBUS electricity notices likewise describe procurement for that city. The code applies these **individual notice decisions**; it does not accept unseen notices merely because their names contain a city or agent.

## Full outcomes: lots, typed counts and missing dates

Of 50 pinned full notices, four concern the excluded joint/regional cases. The outcome pipeline reviews **46 retained municipal notices**:

| Full-notice result | Notices |
| --- | ---: |
| Supported awarded results | 39 |
| Explicit non-awards / closed procedures without a winner | 5 |
| Award-layout cases requiring further manual handling | 2 |
| Total reviewed municipal notices | **46** |

The supported awards yield **34 legacy units** and **20 eForm lot-result units**. The eForm unit is a separately scoped awarded lot result; the parser rejects multiple contracts within one lot rather than treating them as one independently identified contract.

| Recovered measure | Award/lot-result units |
| --- | ---: |
| Supported awarded units | **54** |
| Explicit contract-conclusion date | 52 |
| Explicit total received-tender count | 50 |
| Both date and total tender count | **49** |
| Reported one-euro award value requiring review | 15 |
| Dated Geilenkirchen units within its source-bounded council-head role | 7 |

Counts include the two legacy contracts from the original pilot; they are not additions to be counted twice. Related lots are retained separately without increasing the number of electoral clusters. No unit is assigned main-study mayoral treatment or verified procurement responsibility.

The new eForm parser binds each result to the matching lot definition. It accepts the statistical category **“Angebote”** for total tenders, preserving the distinction from electronic, SME, foreign-bidder or other subsets. For example, a lot can report several subgroup counts alongside its total. Reading the first count would silently change the outcome. Some notices report electronic submissions only; their total tender count remains unknown.

**Winner-selection date is not contract-conclusion date.** Velbert notice [188186-2024](https://ted.europa.eu/de/notice/188186-2024/pdf) provides a winner-selection date and five total tenders but no explicit contract date; that date stays missing. The earlier Iserlohn example still demonstrates that a 2021 publication may describe a December 2020 contract. The publication query window does not define the contract observation window.

Five non-awards are kept outside awarded tender-count outcomes: `133960-2021`, `133968-2021`, `579253-2021`, `565529-2023` and `251250-2024`. The last eForm notice explicitly states that no winner was selected and the competition is closed. A non-award is not a zero-tender awarded contract.

Two retained legacy notices remain in an explicit outcome-layout review queue. Iserlohn `131327-2021` does not supply the scalar awarded-value field required by the current reconciled parser. Geilenkirchen `370898-2022` has an unnumbered award section within a multi-lot notice. Neither case is forced into a scalar value or guessed lot mapping; their reported errors and source provenance remain in local audits.

## Monetary and environmental measurement findings

**Fifteen Velbert award units across seven KoPart notices report EUR 1.00 per awarded unit.** The notice totals equal the number of one-euro units, so arithmetic reconciliation succeeds. This does not validate those amounts as economic prices. The pipeline flags each as `nominal_one_euro_needs_review`; they cannot enter a monetary outcome until their meaning is established. Geilenkirchen's KUBUS electricity notice `707371-2023` also has an indexed notice total of one euro while its two lot results lack individual tender values. A consistent number is not necessarily a usable expenditure measure.

All 20 extracted eForm awarded-lot definitions explicitly report **“Keine strategische Beschaffung”** in the strategic-goal field. That statement must remain distinct from environmental specifications and award criteria. For example, the KUBUS electricity procurement describes supply from renewable energy sources while reporting no strategic procurement goal. The legacy ISPEX gas notice `508498-2021` specifies CO2-neutral gas while using price as the award criterion. Coding every missing indexed environmental field or every “no strategic procurement” statement as absence of environmental requirements would lose those distinctions.

The pilot therefore stores strategic-goal wording and award-criterion wording separately and leaves main environmental/social outcome coding open. A project about nature, geothermal energy or a green supply specification is not automatically an environmental award criterion. A coding protocol must define which of those concepts the extension to the Italian study intends to measure and then review coverage across forms and years.

## Velbert: a dated primary candidate statement

The local Green party's [29 April 2020 article](https://www.gruene-velbert.de/schulentwicklung-voellig-entgegen-elternwillen/) identifies **“Fraktionsvorsitzende Bündnis 90/Die Grünen und Bürgermeisterkandidatin Frau Dr. Esther Kanschat”**. The date and title are checked together in the pinned page, then matched to the official state's decisive finalist `Kanschat, Dr. Esther`. Source SHA-256 and retrieval timestamp are embedded in `nrw_candidate_followup.py`.

Together with Lukrafka's dated municipal gazette signature, this supplies the second NRW pair with both mixed public primary presentations documented. The combined register contains **four municipal official title observations and one dated party-authored observation**. Only **Geilenkirchen** has both presentations from municipal official sources. Kanschat's party statement is kept in its own evidence category; it is not relabelled as a registry field or municipal record. A current 2025 party page was also found, but the historical 2020 statement is the evidence used here. Iserlohn's other finalist still lacks equivalent primary evidence in this pilot.

Actual renewed-term boundaries for Iserlohn and Velbert and continuous procurement authority remain open. The Geilenkirchen council-head interval is retained from the [original official-source audit](nrw-operational-pilot.md#named-official-presentation-and-historical-role-boundaries). Seven dated full-document award units overlap it; this is temporal consistency, not proof of who made the procurement decision.

## Reproduce the supplement

After reproducing the original [election and operational pilots](nrw-operational-pilot.md#reproduction-tests-and-release-scope), run from the repository root:

```bash
python src/pilot/nrw_buyer_scope.py --download
python src/pilot/nrw_full_ted_awards.py --download
python src/pilot/nrw_candidate_followup.py --download
python -m unittest discover -s tests -v
```

Omit `--download` to audit cached sources. Changed PDFs or HTML fail their pins and require review. The scope script verifies every decision against the exact indexed buyer list, PDF authority section and scope quotation, then checks full coverage of the original queue. The full-notice script preserves unsupported layouts as explicit review cases. Both use Python's standard library and Poppler's `pdftotext`.

All three supplement pipelines run successfully against the real sources. **39 offline tests pass**, including eight new checks of joint/regional scope, buyer-section boundaries, typed tender counts, winner versus contract dates, multiple lots/contracts, closed non-awards, nominal values and party-source provenance.

Generated person, contract, lot and source-audit records remain local under `outputs/nrw-buyer-scope/`, `outputs/nrw-full-ted/` and `outputs/nrw-candidate-followup/`; the underlying pages and PDFs stay under ignored raw-data directories. The public repository provides original code, limited cited source facts, the decision/source manifests, and the [aggregate supplement summary](nrw-expanded-pilot-summary.csv).

## Remaining gates

The next priorities are actual office boundaries in Iserlohn and Velbert, primary evidence for Iserlohn's other finalist, the two unsupported award layouts, and expansion of full-document recovery beyond these 46 retained notices. Repeated procedures, amendments, represented purchasing and related lots need a documented eligibility/deduplication rule. Coverage still excludes other notice types and procurement below TED reporting thresholds. The main design also needs consistent gender measurement, outcome definitions and enough independent eligible elections for useful precision. GitHub Pages remains deferred until completion of the research.

The two unsupported layout cases and Iserlohn finalist presentation identified at this stage are now resolved in the [latest follow-up](nrw-pilot-completion.md). Formal office boundaries, monetary meaning/reconciliation and broader outcome/cluster coverage remain open.
