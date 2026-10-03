# Bavaria historical pilot: Munich 2020

Checked on 3 October 2026. This is a source-access pilot, not a close-election identifying observation or a complete Bavarian register.

## Municipal archive located

The official Munich election host's root page contains a meta refresh to the current election. Its naming pattern led to reachable historical result pages:

- [15 March 2020 first round](https://www.wahlen-muenchen.de/ergebnisse/20200315oberbuergermeisterwahl/index.html).
- [29 March 2020 runoff](https://www.wahlen-muenchen.de/ergebnisse/20200329oberbuergermeisterwahl/index.html).

Both pages identify their results as official final results and are attributed to the municipal electoral office. Unlike the current state workbook's nomination labels, the historical tables contain named candidates and exact votes.

| Round | Candidate records | Valid votes | Check |
| --- | --- | --- | --- |
| First round | 14 | 542,733 | Candidate votes sum to valid votes |
| Runoff | 2 | 560,629 | Candidate votes sum to valid votes |

The runoff table records Kristina Frank (CSU), 158,773 votes, and Dieter Reiter (SPD), 401,856 votes. This is a clearly non-close contest; locating it validates the extraction path, not the existence of enough close mixed-gender races. Gender has not been independently coded from a dedicated supporting source. Actual terms also remain unverified.

Do not mistake the first-round page's final update timestamp for its election date. The page header and election context identify the round date; a timestamp after the runoff can reflect publication updates.

## Reproduce

```sh
python src/pilot/munich_2020.py
```

The standard-library script selects the candidate table by its headers, extracts both rounds, verifies vote reconciliation, and writes raw HTML, candidate records and URL/checksum summaries under ignored `outputs/munich-2020/`. Executed successfully on 3 October 2026. These raw files are not committed.

This municipal format is one adapter, not a universal Bavaria parser. Source discovery, date validation and archive coverage must precede scaling to other municipalities.

## Historical-source search limitations

Guessed state PDF filenames `b7361c_202051.pdf` and `b7361c_201451.pdf` returned HTTP 404. Guessed Munich short-form `obwahl` paths and a 2014 long-form runoff path also returned 404. Those failures do not imply that historical reports are absent. The successful 2020 paths use `oberbuergermeisterwahl`. A Google HTML search returned only a redirect page and provided no substantive search results.

A central, candidate-complete Bavarian 2020/2014 export remains unconfirmed. Draft provider questions are in [bavaria-data-inquiry.md](bavaria-data-inquiry.md); no inquiry has been sent.

## Term-history verification: NRW example

The [current official Kleve mayor page](https://www.kleve.de/stadt-kleve/verwaltung-und-politik/stadtverwaltung/buergermeister) states that Markus Dahmen has been mayor since 2025. The verified 2020 result instead names Wolfgang Gebing as winner. This confirms that the present officeholder page cannot be used as a historical treatment record. It does not establish the exact end date of the 2020 winner's term.

Term verification needs dated official notices, archived biographies, council records or other attributable historical sources. Store evidence and uncertainty per term; leave dates unresolved rather than assuming every winner remains until the next regular election.

## Next steps

1. Seek an official historical candidate-complete Bayern export or other archive route before collecting municipalities individually at scale.
2. Locate additional municipal archives covering 2020 and, where feasible, 2014; audit format and missingness.
3. Add separate source-backed gender and term records; do not derive gender merely from first names.
4. Extend NRW coverage beyond the already validated district-municipality runoffs only after the Bavaria access path is documented.
