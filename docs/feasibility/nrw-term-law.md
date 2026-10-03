# NRW: historical term rules and individual office-entry evidence

Checked on 4 October 2026 (Europe/Berlin). This institutional audit supports the [complete NRW procurement pilot](nrw-complete-pilot.md). It verifies historical statutes rather than substituting the latest law for the rules governing 2020. **The mayoral entry rule requires acceptance and predecessor exit; it expressly requires no separate appointment.**

## Primary legal sources

The [seven-source manifest](nrw-term-law-source-manifest.csv) pins three historical version pages and their linked statute texts, plus a current LBG navigation page used only to select the historical version. Older statutes are embedded as separate HTML documents; the audit verifies that each version page links to the pinned text.

| Source version | Provision | Verified content |
| --- | --- | --- |
| [GO NRW, 1 November 2020](https://recht.nrw.de/lrgv/gesetz/01112020-gemeindeordnung-fuer-das-land-nordrhein-westfalen-go-nrw-bekanntmachung-der) | § 42(1) | Council members are elected for five years |
| Same historical GO version | § 65(1), (3) | Regular mayors are elected for five years alongside the council; oath and introduction take place in a council meeting |
| [KWahlG, 7 May 2020](https://recht.nrw.de/lrgv/gesetz/07052020-bekanntmachung-der-neufassung-des-kommunalwahlgesetzes-kommunalwahlgesetz) | Reproduced Article 5 § 2 of the 2013 transition act | “Die Wahlperiode der im Jahr 2020 gewählten Vertretungen beginnt am 1. November 2020.” |
| [LBG NRW, 25 May 2018](https://recht.nrw.de/lrgv/gesetz/25052018-gesetz-ueber-die-beamtinnen-und-beamten-des-landes-nordrhein-westfalen) | § 118(3) | Office begins with acceptance, no earlier than predecessor exit, without a separate appointment |

The official LBG version navigation lists 25 May 2018 followed by 16 July 2021. The 2018 text is therefore the historical version selected for the 2020 entry rule. The current navigation snapshot is not applied as substantive 2020 law. GO's regular council rule and the transition start produce the calendar interval **[1 November 2020, 1 November 2025)**; the end is exclusive.

The decisive historical LBG sentence is:

> Das Beamtenverhältnis wird mit dem Tage der Annahme der Wahl, frühestens mit dem Ausscheiden der Vorgängerin oder des Vorgängers aus dem Amt, begründet (Amtsantritt) und bedarf keiner Ernennung.

The following sentence states that the relationship ends with the term. Early exits, invalid elections and successor timing require event-specific evidence. The scheduled council interval is not automatically a certified uninterrupted term for each mayor.

## What to collect for individual terms

For an identified winning election, verify **acceptance of that election** and the **first day the predecessor is outside office**. The latter differs from the predecessor's last day in office. Conditional on both components being verified, entry cannot precede either date. Later acceptance can place entry after the scheduled period start. Oath/introduction, first day at work, election day, current biography and initial entry into an older term remain separate observations.

This corrects the earlier generic request for appointment evidence in the NRW workstream. Seek acceptance/entry records, predecessor exits and renewal/continuity records. Do not make an appointment certificate a required data gate when the applicable statute expressly dispenses with appointment. Bavaria retains its own institutional rules.

| Pilot winner | Existing evidence | Individual term status |
| --- | --- | --- |
| Daniela Ritzerfeld, Geilenkirchen | Named historical council-head role, 1 November 2020–31 October 2025 | Source-bounded head role aligns with the statutory calendar; acceptance, interruptions and procurement authority are not thereby certified |
| Michael Joithe, Iserlohn | Self-authored entry claim of 2 November 2020; official mayoral activity on 9 November | Acceptance and predecessor-exit evidence unresolved; neither 1 nor 2 November is automatically assigned as legal entry |
| Dirk Lukrafka, Velbert | Dated mayoral signature on 12 November 2020; 2020 reelection and earlier biography | Actual renewed-term entry and continuity unresolved; the 2014 date does not date the 2020 renewed term |

Joithe's reported 2 November entry is one day after the scheduled council-period start. That difference can reflect different events or later acceptance; it is not resolved by choosing the calendar date or interpreting the biography's wording as a legal certificate. His 19 October 2020 procurement notice predates both dates. The Iserlohn deputy's personal-record end on 11 November 2025 likewise cannot serve as the full-time mayor's end.

## Contract calendar check

`nrw_term_law.py` verifies five quoted historical legal statements and compares the complete pilot's contract dates with the regular council interval:

| Calendar position | Observed award units |
| --- | ---: |
| Inside the regular council period | 108 |
| Before the period | 1 |
| Contract date missing | 3 |
| Total | **112** |

The earlier contract is Iserlohn [131327-2021](https://ted.europa.eu/de/notice/131327-2021/pdf), concluded on 19 October 2020 and published in 2021. Publication-window selection must not replace contract-date eligibility. There are **zero certified individual entry-date, main-treatment or procurement-responsibility assignments** from this legal audit.

After constructing the [complete pilot](nrw-complete-pilot.md#reproduction), run `python src/pilot/nrw_term_law.py --download`. Cached source bytes are checked against pinned hashes. Four offline tests protect predecessor timing, delayed acceptance, missing individual components and half-open calendar boundaries. The combined project suite has 58 passing tests. Changed legal-source snapshots require review before changing pins.
