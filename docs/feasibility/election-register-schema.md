# Election register schema — pilot specification

The pilot separates electoral events, rounds, candidates and office terms. This is a schema specification, not a completed nationwide register.

| Entity | Required fields | Validation / unresolved cases |
| --- | --- | --- |
| Municipality | Local source key, state, AGS when verified, name, geographic vintage, territory type | County administrations excluded; mergers and identifier changes documented |
| Election event | Event ID, municipality ID, regular/off-cycle status, final result status, decisive round | One event can have several rounds; first rounds preceding runoffs are not separate treatment assignments |
| Round | Date, round number, exact valid votes, invalid ballots when available, source URL, retrieval time/checksum | Candidate votes reconcile; committee and publication dates distinguished from election date |
| Candidate-round | Source identity, full name when available, nomination, exact votes, winner flag | Nomination label or surname alone does not establish identity |
| Candidate evidence | Recorded gender, evidence URL/file and location, verification status | Missing gender stays unknown; no inference from first names; source ambiguities recorded |
| Term | Officeholder identity, actual start/end if established, first-ever entry separately, evidence and confidence | Election date, inauguration and first-ever entry are distinct; reelections and acting periods require own records |
| Eligibility | Decision, reason, rule version, reviewer/date | Unknown fields prevent automatic RDD inclusion; close margin does not imply mixed-gender eligibility |

## Key checks

- Unique municipality/event/round/candidate keys; correction versions retained rather than counted twice.
- Exact vote counts agree with valid votes; percentages calculated from counts rather than rounded displays.
- Gender and timing evidence remain separate from mathematical winner determination.
- Source coverage, access failures, missing records, unresolved identities and ineligible contests are reported separately.
- Signed female-minus-male margins are calculated only after the eligible decisive contest and both genders are established.
- Source-reported facts and analyst decisions are distinguished. Population thresholds, honorary-mayor inclusion and observation windows remain research decisions to justify.

Raw and candidate-level pilot data remain local under ignored `data/` and `outputs/`. Any eventual release requires a data-rights review.
