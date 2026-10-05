"""Early NRW linkage, selection and optimistic precision audit; no effect estimates.

Run from the repository root. Uses the frozen pilot and existing presentation
dispositions. The Gaussian two-group benchmark is not an RDD power calculation.
Person-level independent-review packets remain under ignored data/interim.
"""
import argparse
import csv
import hashlib
import itertools
import json
import math
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.stats import chi, norm, t

DOC = Path("docs/feasibility")
OUT = Path("outputs/nrw-early-feasibility")
START, END = "2023-11-01", "2024-12-31"
REVIEW = Path("data/interim/nrw-close-pair-screen/reviews.json")


def csv_rows(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fields=None):
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def pin(path):
    data = Path(path).read_bytes()
    return {"artifact": str(path), "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest()}


def verify_baseline():
    rows = csv_rows(DOC / "baseline-source-hashes.csv")
    for row in rows:
        current = pin(row["artifact"])
        if current["sha256"] != row["sha256"] or current["bytes"] != int(row["bytes"]):
            raise ValueError("Frozen baseline changed: " + row["artifact"])
    return len(rows)


def finalist_data(event):
    people = [p for p in event["candidates"]
              if not event["has_runoff"] or p["votes_runoff"] is not None]
    field = "votes_runoff" if event["has_runoff"] else "votes_first"
    total = event["runoff_valid_votes"] if event["has_runoff"] else event["first_valid_votes"]
    if len(people) != 2 or total <= 0 or sum(p[field] for p in people) != total:
        raise ValueError("Decisive votes do not reconcile")
    winner = max(range(2), key=lambda i: people[i][field])
    if people[0][field] == people[1][field]:
        raise ValueError("Tied assignment")
    return people, field, total, winner


def labels_for(review):
    labels = []
    for candidate in review["candidates"]:
        values = {e["label"] for e in candidate["accepted_evidence"]}
        if len(values) > 1 or values - {"female", "male"}:
            raise ValueError("This audit does not impute conflicts/other presentations")
        labels.append(next(iter(values), None))
    return labels


def pair_status(labels):
    if None in labels:
        return "unresolved"
    return "mixed_public_presentation" if set(labels) == {"female", "male"} else "same_public_presentation"


def optimistic_options(labels, winner):
    """Possible cutoff sides if unknowns resolve to opposite binary presentations.

    These are conditional upper-bound scenarios, never new candidate assignments.
    """
    choices = [(label,) if label else ("female", "male") for label in labels]
    return {p[winner] == "female" for p in itertools.product(*choices)
            if set(p) == {"female", "male"}}


def design_support(margins):
    """Algebraic support only; no outcomes or regression coefficients."""
    r = np.asarray(margins, dtype=float)
    d = (r > 0).astype(float)
    if not len(r):
        return {"linear_rank": 0, "linear_columns": 4, "quadratic_rank": 0,
                "quadratic_columns": 6, "linear_residual_df": 0, "quadratic_residual_df": 0}
    linear = np.column_stack((np.ones(len(r)), d, r, d*r))
    quadratic = np.column_stack((linear, r*r, d*r*r))
    lr, qr = int(np.linalg.matrix_rank(linear)), int(np.linalg.matrix_rank(quadratic))
    return {"linear_rank": lr, "linear_columns": 4, "quadratic_rank": qr,
            "quadratic_columns": 6, "linear_residual_df": len(r)-lr,
            "quadratic_residual_df": len(r)-qr}


def gaussian_t_power(effect_sd, treated, control, alpha=0.05):
    """Exact pooled two-sample t power under independent equal-variance normals.

    Integrate over the chi distribution of the pooled residual SD. This avoids
    numerical noncentral-t failures for extremely small degrees of freedom.
    No running-variable slopes, kernel, reporting selection or RDD correction.
    """
    if treated < 1 or control < 1 or treated + control <= 2:
        raise ValueError("Both groups and positive residual degrees of freedom required")
    if not 0 < alpha < 1:
        raise ValueError("Invalid alpha")
    df = treated + control - 2
    ncp = effect_sd / math.sqrt(1/treated + 1/control)
    critical = t.ppf(1-alpha/2, df)

    def integrand(s):
        threshold = critical*s/math.sqrt(df)
        return (norm.cdf(-threshold-ncp) + norm.sf(threshold-ncp))*chi.pdf(s, df)

    lower, upper = chi.ppf([1e-12, 1-1e-12], df)
    return float(quad(integrand, lower, upper, epsabs=1e-9, epsrel=1e-9)[0])


def gaussian_t_mde(treated, control, alpha=0.05, power=0.8):
    if not alpha < power < 1:
        raise ValueError("Target power must exceed alpha and be below one")
    upper = 1.0
    while gaussian_t_power(upper, treated, control, alpha) < power:
        upper *= 2
    return float(brentq(lambda effect: gaussian_t_power(effect, treated, control, alpha)-power,
                        0, upper, xtol=1e-8))


def balanced_required_n(effect_sd, alpha=0.05, power=0.8):
    if effect_sd <= 0:
        raise ValueError("Positive effect size required")
    lo, hi = 2, 4
    while gaussian_t_power(effect_sd, hi, hi, alpha) < power:
        hi *= 2
    while lo < hi:
        mid = (lo+hi)//2
        if gaussian_t_power(effect_sd, mid, mid, alpha) >= power:
            hi = mid
        else:
            lo = mid+1
    return 2*lo


def prepare_review(rows, reviews, events, sources):
    """Prepare all 16 classified pairs plus 12 stratified unresolved audit pairs.

    Suppress prior labels, margins, votes, winner and prediction fields. Original
    content may still reveal those facts: this is not guaranteed full blinding.
    """
    classified = [r for r in rows if r["pair_status"] != "unresolved"]
    unknown = [r for r in rows if r["pair_status"] == "unresolved"]
    sort_key = lambda r: hashlib.sha256(("second-review-v1:"+r["ags"]).encode()).hexdigest()
    chosen = []
    for supported, target in [(1, 4), (0, 8)]:
        pool = [r for r in unknown if int(r["supported_candidates"]) == supported]
        priority = [r for r in pool if Decimal(r["absolute_margin_pp"]) <= 2]
        picked = priority + sorted([r for r in pool if r not in priority], key=sort_key)[:target-len(priority)]
        if len(picked) != target:
            raise ValueError("Independent-review stratum changed")
        chosen.extend(picked)
    selected = sorted(classified+chosen, key=sort_key)
    root = Path("data/interim/nrw-independent-review")
    root.mkdir(parents=True, exist_ok=True)
    forms, mapping = [], []
    for index, row in enumerate(selected, 1):
        case_id = f"R{index:03d}"
        ags = row["ags"]
        original = reviews[ags]
        acquired = []
        for sid in original["reviewed_source_ids"]:
            source = sources[sid]
            if source["status"] != "acquired" or sid.startswith("nrw-result-"):
                continue
            data = Path(source["local_file"]).read_bytes()
            if len(data) != int(source["bytes"]) or hashlib.sha256(data).hexdigest() != source["sha256"]:
                raise ValueError("Reviewer original differs from source pin")
            acquired.append({k: source[k] for k in ["source_id", "source_url", "sha256", "local_file", "retrieved_at_utc"]})
        people, _, _, _ = finalist_data(events[ags])
        ordered = list(people)
        if int(sort_key(row)[0], 16) % 2:
            ordered.reverse()
        packet = {"case_id": case_id, "measurement_codebook": str(DOC / "candidate-exposure-codebook.md"),
                  "municipality_for_identity": events[ags]["municipality_source"],
                  "target_event_year": 2020,
                  "candidates": [{"slot": slot, "official_candidate_name": p["candidate_name_source"]}
                                 for slot, p in zip(["A", "B"], ordered)],
                  "original_sources": acquired,
                  "blinding_limit": "Original sources and municipality/name may reveal office or election outcome. No prior labels/votes/predictions supplied."}
        (root / (case_id+".json")).write_text(json.dumps(packet, ensure_ascii=False, indent=2)+"\n")
        mapping.append({"case_id": case_id, "ags": ags, "first_coder_pair_status": row["pair_status"],
                        "first_coder_supported_candidates": row["supported_candidates"]})
        for slot in ["A", "B"]:
            forms.append(dict(case_id=case_id, candidate_slot=slot, reviewer_id="", reviewed_at_utc="",
                              independent_presentation="", identity_status="", primary_authorship="",
                              historical_2020_link="", source_id="", evidence_locator="",
                              page_or_section="", disagreement_reason="", additional_search_minutes=""))
    write_csv(root / "second-coder-form.csv", forms)
    key_root = Path("data/interim/nrw-independent-review-key")
    key_root.mkdir(parents=True, exist_ok=True)
    write_csv(key_root / "first-coder-key.csv", mapping)
    # Remove only this script's obsolete generated key from the reviewer folder.
    old_key = root / "first-coder-key.csv"
    if old_key.exists():
        old_key.unlink()
    return {"prepared_pairs": len(selected), "prepared_candidates": len(forms),
            "classified_pairs": len(classified), "unresolved_audit_pairs": len(chosen),
            "unresolved_one_supported": 4, "unresolved_neither_supported": 8,
            "second_coding_completed": False, "independent_reviewer_assigned": False,
            "local_packet_directory": str(root), "local_key_directory": str(key_root),
            "form_fields": list(forms[0])}


def run(prepare_independent=False):
    OUT.mkdir(parents=True, exist_ok=True)
    frozen_count = verify_baseline()
    paths = [DOC / "baseline-source-hashes.csv", DOC / "nrw-close-election-evidence-summary.csv",
             DOC / "nrw-close-election-checkpoint.json", DOC / "candidate-exposure-codebook.md",
             DOC / "nrw-close-pair-source-manifest.csv", REVIEW,
             Path("outputs/nrw-election-register/events.json"),
             Path("outputs/nrw-procedure-scope/observations.json"),
             Path("outputs/nrw-buyer-followup/records.json")]
    before = [pin(p) for p in paths]
    rows = csv_rows(paths[1]); checkpoint = json.loads(paths[2].read_text())
    worksheet = json.loads(REVIEW.read_text())
    if worksheet["codebook_sha256"] != pin(paths[3])["sha256"]:
        raise ValueError("Measurement codebook changed")
    if checkpoint["local_review_sha256"] != pin(REVIEW)["sha256"]:
        raise ValueError("Candidate worksheet changed")
    reviews = {r["ags"]: r for r in worksheet["reviews"]}
    events = {r["ags"]: r for r in json.loads(paths[6].read_text()) if r["decisive_pair"]}
    observations = json.loads(paths[7].read_text())
    notices = json.loads(paths[8].read_text())
    sources = {r["source_id"]: r for r in csv_rows(paths[4])}
    if len(rows) != 55 or len(events) != 214 or len(observations) != 123 or len(notices) != 237:
        raise ValueError("Pilot checkpoint cardinalities changed")
    notice_counts = Counter(r["ags"] for r in notices)
    options, margins, linkage, candidate_support = {}, {}, [], []
    for row in rows:
        ags = row["ags"]; event = events[ags]; review = reviews[ags]
        people, field, total, winner = finalist_data(event)
        if [p["candidate_name_source"] for p in people] != [c["candidate_name_source"] for c in review["candidates"]]:
            raise ValueError("Candidate identity/order changed")
        labels = labels_for(review)
        if pair_status(labels) != row["pair_status"]:
            raise ValueError("Public and local candidate dispositions disagree")
        options[ags] = optimistic_options(labels, winner)
        if row["pair_status"] == "mixed_public_presentation":
            female = labels.index("female")
            signed = (people[female][field]-people[1-female][field])*100/total
            if not math.isclose(signed, float(row["signed_female_minus_male_margin_pp"]), abs_tol=1e-12):
                raise ValueError("Signed margin disagrees with original exact votes")
            margins[ags] = signed
        local = [r for r in observations if r["ags"] == ags]
        window = [r for r in local if r["timing_disposition"] == "documented_competition_chronology_supported"
                  and START <= r["candidate_competition_date"] <= END]
        official_docs = [sources[sid] for sid in review["reviewed_source_ids"]
                         if sid in sources and not sid.startswith("nrw-result-")
                         and sources[sid]["status"] == "acquired"
                         and sources[sid]["authorship"] in {"official municipal primary", "official primary"}]
        linkage.append(dict(ags=ags, municipality=row["municipality"], absolute_margin_pp=row["absolute_margin_pp"],
                            pair_status=row["pair_status"], female_presented_winner=row["female_presented_winner"],
                            retained_pilot_result_notices=notice_counts[ags], pilot_dated_count_units=len(local),
                            pilot_dated_count_notices=len({r["publication_number"] for r in local}),
                            candidate_window_called_dated_count_units=len(window),
                            candidate_window_called_result_notices=len({r["publication_number"] for r in window}),
                            acquired_non_election_official_documents=len(official_docs),
                            reporting_coverage="not_systematically_audited", deduplication="pending",
                            independent_second_coding="not_completed", common_followup="not_selected",
                            actual_exposure="not_certified", main_sample_eligibility="pending",
                            zero_count_interpretation="zero supported pilot records, not zero procurement"))
        for i, (person, label) in enumerate(zip(people, labels)):
            candidate_support.append({"ags": ags, "winner": i == winner, "supported": label is not None,
                                      "documentation_group": "none_acquired" if not official_docs else "one_or_two" if len(official_docs) <= 2 else "three_or_more",
                                      "round": row["decisive_round"], "margin_band": "within_2_pp" if Decimal(row["absolute_margin_pp"]) <= 2 else "over_2_to_10_pp"})
    scenarios = []
    geometry = []
    for cutoff in [1, 2, 5, 10]:
        band = [r for r in rows if Decimal(r["absolute_margin_pp"]) <= cutoff]
        known = [r for r in band if r["ags"] in margins]
        known_margins = [margins[r["ags"]] for r in known]
        n1 = sum(v > 0 for v in known_margins); n0 = len(known)-n1
        scenarios.append((f"confirmed_within_{cutoff}pp", n1, n0, "Existing supported presentations; procurement/window eligibility not assumed."))
        geometry.append(dict(scenario=f"confirmed_within_{cutoff}pp", treated=n1, control=n0, **design_support(known_margins)))
        if cutoff in [2, 10]:
            possible = [options[r["ags"]] for r in band if options[r["ags"]]]
            low = sum(p == {True} for p in possible); high = sum(True in p for p in possible)
            optimal = min(max(len(possible)//2, low), high)
            scenarios.append((f"optimistic_all_unknowns_mixed_within_{cutoff}pp", optimal, len(possible)-optimal,
                              f"Conditional upper bound: every unresolved pair can become binary mixed; best feasible balance. Possible female wins {low}..{high}. No assignments/coverage certified."))
    linked = [r for r in linkage if r["ags"] in margins and r["candidate_window_called_dated_count_units"]]
    linked_margins = [margins[r["ags"]] for r in linked]
    linked_n1 = sum(v > 0 for v in linked_margins); linked_n0 = len(linked)-linked_n1
    scenarios.append(("provisionally_linked_candidate_window", linked_n1, linked_n0, "At least one existing supported called dated/count unit in Nov2023-Dec2024; incomplete pilot, not final sample."))
    geometry.append(dict(scenario="provisionally_linked_candidate_window", treated=linked_n1, control=linked_n0, **design_support(linked_margins)))
    precision = []
    for name, n1, n0, limit in scenarios:
        for alpha in [0.05, 0.025]:
            valid = n1 > 0 and n0 > 0 and n1+n0 > 2
            se = math.sqrt(1/n1+1/n0) if valid else None
            precision.append(dict(scenario=name, female_wins=n1, female_losses=n0, elections=n1+n0,
                                  per_test_alpha=alpha, target_power=0.8,
                                  normal_approx_mde_sd=(norm.ppf(1-alpha/2)+norm.ppf(.8))*se if valid else "",
                                  gaussian_pooled_t_mde_sd=gaussian_t_mde(n1, n0, alpha) if valid else "",
                                  pooled_t_df=n1+n0-2 if valid else "",
                                  status="optimistic_non_RDD_benchmark" if valid else "not_estimable_no_cutoff_side_or_df",
                                  limitation=limit))
    sensitivity = []
    effect_power = []
    for row in precision:
        if row["status"] != "optimistic_non_RDD_benchmark":
            continue
        for sd_pp in [5, 10, 20]:
            sensitivity.append(dict(scenario=row["scenario"], per_test_alpha=row["per_test_alpha"],
                                    assumed_municipal_outcome_sd_pp=sd_pp,
                                    gaussian_t_mde_pp=row["gaussian_pooled_t_mde_sd"]*sd_pp,
                                    within_0_to_100pp_outcome_range=row["gaussian_pooled_t_mde_sd"]*sd_pp <= 100,
                                    interpretation="Hypothetical SD grid; not measured variance, a substantively justified threshold, or exact bounded-outcome/RDD power."))
            for effect_pp in [5, 10, 20]:
                effect_power.append(dict(scenario=row["scenario"], per_test_alpha=row["per_test_alpha"],
                                         assumed_municipal_outcome_sd_pp=sd_pp, hypothetical_effect_pp=effect_pp,
                                         gaussian_t_power=gaussian_t_power(effect_pp/sd_pp, row["female_wins"], row["female_losses"], row["per_test_alpha"]),
                                         interpretation="Assumption-based effect/variance grid; not substantive thresholds, effect estimates or RDD power."))
    needed = [dict(effect_sd=d, per_test_alpha=alpha, target_power=.8,
                   balanced_total_elections=balanced_required_n(d, alpha),
                   interpretation="Gaussian two-group benchmark; not an RDD sample target or sufficient-go threshold")
              for d in [.25, .5, 1.] for alpha in [.05, .025]]
    selection = []
    for dimension, groups in [("candidate_election_result", ["winner", "loser"]),
                              ("decisive_round", sorted({r["round"] for r in candidate_support})),
                              ("absolute_margin_band", ["within_2_pp", "over_2_to_10_pp"]),
                              ("acquired_non_election_official_documents", ["none_acquired", "one_or_two", "three_or_more"])]:
        for group in groups:
            key = {"decisive_round": "round", "absolute_margin_band": "margin_band",
                   "acquired_non_election_official_documents": "documentation_group"}.get(dimension)
            subset = [r for r in candidate_support if
                      ("winner" if r["winner"] else "loser") == group] if dimension == "candidate_election_result" else [r for r in candidate_support if r[key] == group]
            supported = sum(r["supported"] for r in subset)
            selection.append(dict(dimension=dimension, group=group, candidate_records=len(subset),
                                  supported_candidates=supported, unresolved_candidates=len(subset)-supported,
                                  support_rate=supported/len(subset) if subset else ""))
    states = Counter()
    for row in rows:
        parts = [r for r in candidate_support if r["ags"] == row["ags"]]
        states[(next(r for r in parts if r["winner"])["supported"],
                next(r for r in parts if not r["winner"])["supported"])] += 1
    packet = prepare_review(rows, reviews, events, sources) if prepare_independent else None
    write_csv(DOC / "nrw-early-linkage-matrix.csv", linkage)
    write_csv(DOC / "nrw-early-precision-benchmarks.csv", precision)
    write_csv(DOC / "nrw-early-precision-sensitivity.csv", sensitivity)
    write_csv(DOC / "nrw-early-effect-size-power.csv", effect_power)
    write_csv(DOC / "nrw-early-precision-required-elections.csv", needed)
    write_csv(DOC / "nrw-early-design-support.csv", geometry)
    write_csv(DOC / "nrw-early-selection-audit.csv", selection)
    write_csv(DOC / "nrw-early-feasibility-input-hashes.csv", before)
    if [pin(p) for p in paths] != before:
        raise ValueError("Input artifacts changed during audit")
    verify_baseline()
    summary = dict(checked_at_utc=datetime.now(timezone.utc).isoformat(), candidate_window_start=START,
                   candidate_window_end=END, baseline_artifacts_unchanged=frozen_count,
                   all_55_pair_counts=dict(Counter(r["pair_status"] for r in rows)),
                   confirmed_mixed_pairs=6, confirmed_mixed_pairs_with_any_pilot_dated_count=sum(r["pair_status"] == "mixed_public_presentation" and r["pilot_dated_count_units"] > 0 for r in linkage),
                   candidate_window_linked_mixed_pairs=len(linked), candidate_window_female_wins=linked_n1,
                   candidate_window_female_losses=linked_n0, candidate_window_observed_units=sum(r["candidate_window_called_dated_count_units"] for r in linked),
                   certified_main_study_elections=0, independent_second_coding_completed=False,
                   candidate_support_pair_patterns={f"winner_{'supported' if a else 'unresolved'}_loser_{'supported' if b else 'unresolved'}": count for (a,b),count in states.items()},
                   independent_review_packet=packet, variance_source="assumed_grid_not_treatment_outcome_estimates",
                   numerical_environment={"numpy": np.__version__, "scipy": scipy.__version__},
                   benchmark="independent_equal_variance_Gaussian_two_group_test_not_RDD",
                   causal_effects_estimated=False, decision="continue_bounded_feasibility_adaptation_audit_no_main_study_go")
    if summary["candidate_window_linked_mixed_pairs"] != 3 or linked_n1 != 1 or linked_n0 != 2:
        raise ValueError("Existing candidate-window pilot linkage changed")
    (DOC / "nrw-early-feasibility-checkpoint.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n")
    if packet:
        (OUT / "independent-review-packet-summary.json").write_text(json.dumps(packet, indent=2)+"\n")
        write_csv(DOC / "independent-coding-template.csv", [], packet["form_fields"])
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-independent-review", action="store_true")
    args = parser.parse_args()
    run(args.prepare_independent_review)
