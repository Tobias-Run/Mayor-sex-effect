# Dated outcome/population addendum: called-procedure prototype

14 October 2026. This is the P3 measurement proposal requested in the [measurable-progress plan](measurable-progress-plan-2026-10-14.md#p3-test-procedure-choice-before-replacing-an-outcome). It documents a change of target population for calibration, **without adopting a new main-study primary outcome**. The frozen [outcome codebook v0.2](outcome-population-codebook.md) and its two nominated outcome candidates remain unchanged. This addendum is neither a preregistration nor retrospective confirmation of a primary family.

The project adapts **Florio and Spagnolo (2026), Female Mayors and Public Procurement**, with German precedents including Baskaran and Hessami (2018) and the [literature/design crosswalk](literature-design-crosswalk.md). Narrowing to publicly advertised TED procedures would change the observable procurement population and therefore limit comparison with the Italian paper. It does not isolate an effect of gender from the elected candidate's other attributes.

## One proposed measure, with its denominator

**Candidate variable:** `negotiated_called_procedure_share`, the municipal share of original-supported advertised procedures initiated through competitive negotiation, among original-supported advertised procedures in a common calendar window.

| Element | Proposed operational definition | Current status |
|---|---|---|
| Unit | One unique procurement procedure, anchored to its first original competition notice and connected corrections; lots, award documents and repeated versions do not add procedures | Compiled OCIDs are discovery keys; complete original graphs unverified |
| Numerator | Procedures explicitly classified as competitive negotiation with prior call in original Section IV.1.1; preserve legacy wording and detailed category | One original example verified; no full-period numerator constructed |
| Denominator | All unique in-scope called procedures with an original-supported municipal buyer and initial competition notice in the window; retain unknown-category counts separately | Coverage, revisions and some buyer roles remain unresolved |
| Population | Observable publicly advertised TED procedures for the named municipality; exclude utilities, joint/ambiguous buyer allocations and no-call procedures from this prototype | Different from all municipal purchases and all negotiated procedures |
| Common windows | Full calendar 2019 before the 2020 elections and full calendar 2021 afterwards, for every one of the 55 retained NRW elections; retain their election assignment through documented turnover | Proposed diagnostic windows; office and reporting comparability not certified |
| Operational timestamp | Original first competition-notice **publication day** in TED, after resolving corrections; dispatch date recorded separately | A reporting-time definition, not proof of the underlying procedure-choice decision day |
| Actual decision date | Use only an explicit supported municipal decision record for analyses claiming decision-time exposure; never substitute document year, publication, dispatch, contract start or award conclusion silently | Missing for the calibration originals; a decision-time estimand cannot currently be implemented |
| Unknown method | Keep the original literal category and an unresolved flag; do not drop it or code it as open | Unknown-category coverage must accompany any later share |
| Zero denominator | Share undefined when no supported procedure exists; retain the election and the reason, not a fabricated zero share | Absence from the source is currently missing coverage, not verified zero activity |
| Election weighting | Equal election weight would be a prospective design choice; municipal dependence and repeat elections remain explicit | No estimator adopted |

The proposed publication-based timestamp is deliberately labelled. The two inspected calls were dispatched three and five days before publication. That observation does not validate the time the authority chose the procedure, or establish that the same year/window/exposure classification holds for other notices. Acquisition around calendar boundaries would need adjacent source years; the two annual snapshots alone cannot prove a complete dispatch- or decision-year population.

## Selection and interpretation

Conditioning on a positive post-election denominator or on observing successful awards can select on treatment. The ratio is consequently a **conditional observed-procedure measure**, not automatically an unconditional municipal election ITT. Keeping all elections in an availability table makes the problem visible; it does not solve it. A defensible causal estimand would still need to handle undefined shares and treatment-induced changes in the population of advertised procedures before estimation. Equal election weights and pre-election covariates do not remove these problems.

No-call procedures cannot be added to the denominator using their award-publication dates as though those were call or procedure-choice dates. The cached source contains eleven explicitly labelled no-call processes in the publication-year diagnostic; one lacks an award date and two have award dates outside the source year. These are transformed-source findings, not original-verified contract dates. Similarly, a missing call document does not establish that the procedure had no prior call: thirty source processes are award-only but only eleven carry the explicit no-call label.

The original **all-procedure negotiated share** therefore remains unsupported. Narrowing the population avoids pretending to observe all procedures, but it also removes the no-call component potentially relevant to the Italian adaptation. It is not a costless relaxation of measurement rules and cannot be used to claim the original outcome is now available.

## Adoption decision

**Not adopted and not validated for a causal main study.** The proposal makes the measurement testable; it does not certify coverage, original graphs, buyer scope, decision timing, selection or useful precision. No procedure shares, causal effects or empirical prognostic R-squared were estimated. No third primary outcome is added. A future primary-family decision must explicitly choose, amend and justify the outcome/population before estimating effects. The [P3 audit decision](procedure-choice-calibration-decision.md) records the evidence and current access limits.
