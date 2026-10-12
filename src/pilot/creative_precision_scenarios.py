"""Assumption-only prognostic-adjustment sensitivity; not RDD power."""
import json,math
from pathlib import Path
from nrw_early_feasibility import balanced_required_n,gaussian_t_mde
from nrw_2025_validation import csv_write

def residual_effect(effect_sd,r_squared):
    if effect_sd<=0 or not 0<=r_squared<1:raise ValueError('Positive effect and R-squared in [0,1) required')
    return effect_sd/math.sqrt(1-r_squared)

def main():
    rows=[]
    for effect in (.25,.5,1.0):
        for r2 in (0,.25,.50,.75):
            rows.append({'target_effect_in_original_outcome_sd':effect,'assumed_pre_treatment_prognostic_r_squared':r2,'residual_sd_fraction':math.sqrt(1-r2),'balanced_total_elections_gaussian_benchmark':balanced_required_n(residual_effect(effect,r2),alpha=.025,power=.8),'per_test_alpha':.025,'target_power':.8,'r_squared_empirically_validated':False,'interpretation':'Optimistic equal-variance Gaussian two-group residual-variance scenario; not RDD power. No penalty for estimating prognostic controls, clustering or missingness.'})
    csv_write(Path('docs/feasibility/creative-precision-scenarios.csv'),rows)
    small=[{'independent_balanced_elections':n,'assumed_r_squared':r2,'mde_in_original_outcome_sd':gaussian_t_mde(n//2,n//2,alpha=.025,power=.8)*math.sqrt(1-r2)} for n in (4,6,12,24) for r2 in (0,.50,.75)]
    summary={'planning_scenarios':rows,'small_sample_mde_scenarios':small,'validated_baseline_outcome_correlations':0,'causal_effects_estimated':False,'certified_main_study_elections':0,'warning':'Neither current six-case cohort pooling nor the assumed R-squared is justified. Pre-election prognostic data could improve precision after valid linkage; post-treatment covariates, additional lots or arbitrary bandwidth choices do not add independent assignments.'}
    Path('docs/feasibility/creative-precision-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'scenarios':len(rows),'small_sample_scenarios':len(small)}))

if __name__=='__main__':main()
