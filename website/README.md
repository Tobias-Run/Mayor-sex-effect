# Interactive research companion — planned

**Hosting target:** GitHub Pages at `https://tobias-run.github.io/Mayor-sex-effect/`.

**Publication state:** deferred until completion of the empirical research and manuscript. This URL is a planned destination, not an existing site. No website build or Pages deployment workflow is included at this stage.

## Reader experience

The eventual companion should let readers trace how the question, source coverage, sample construction, identification assumptions, and estimates connect:

1. Read the research question, main result, estimand, and limits of interpretation.
2. Explore state and time coverage and the sample-selection flow.
3. Inspect the running-variable distribution and outcome plots around the cutoff.
4. Compare approved bandwidths, observation windows, and robustness specifications.
5. Examine estimates with confidence intervals, units, sample counts, and clear outcome definitions.
6. Follow citations, methodology, code, and reproducibility instructions.

Interactions must expose which specification is shown. Confirmatory and exploratory analyses must be distinguished. Bandwidth changes must use validated estimates or a validated computation method, not an illustrative slider that invents results. Include accessible static equivalents, keyboard controls, and readable mobile layouts.

## Architecture to choose after research completion

Use a static site compatible with GitHub Pages and the repository subpath `/Mayor-sex-effect/`. Select the framework after the analysis stack is established; Quarto is one candidate. Export reviewed aggregate data and specification results from the analysis pipeline with metadata identifying the code commit and data vintage. Browser-side filtering should use these approved artifacts.

Do not load confidential microdata into the browser. Public-safe visualizations must satisfy provider disclosure rules, including small-cell restrictions where applicable. An interactive reader cannot be assumed to reproduce restricted microdata analysis in the browser.

## Release gate

- Empirical analysis, robustness review, and manuscript are complete.
- Figures and exported results reconcile with the manuscript and reproducibility package.
- Licensing, disclosure, and redistribution checks are complete.
- Interactions, uncertainty displays, accessibility, links, and repository-subpath routing are tested.
- The publication decision is documented before enabling Pages and its deployment workflow.

Until then, maintain this specification alongside the research. The user has requested GitHub Pages as the eventual host; do not substitute another hosting service.
