# Miniproject Feedback and Assessment

## Report

**"Guidelines" below refers to the MQB report [MQB Miniproject report guidelines](https://mulquabio.github.io/MQB/notebooks/Appendix-MiniProj.html#the-report) [here](https://mulquabio.github.io/MQB/notebooks/Appendix-MiniProj.html) (which were provided to the students in advance).**


**Title:** “Comparison of Microbial Population Growth Models”

- **Introduction (15%)**  
  - **Score:** 10/15  
  - Briefly states data cleaning, multiple models (7) tested. Doesn't explain the rationale behind each model in detail. [MQB Miniproject report guidelines](https://mulquabio.github.io/MQB/notebooks/Appendix-MiniProj.html#the-report) suggest a clearer set of questions.

- **Methods (15%)**  
  - **Score:** 11/15  
  - LOF outlier removal is interesting. Minimal explanation of how each of the seven models is fit or validated. [MQB Miniproject report guidelines](https://mulquabio.github.io/MQB/notebooks/Appendix-MiniProj.html#the-report) emphasize replicability.

- **Results (20%)**  
  - **Score:** 13/20  
  - Summarizes that GAM often has top R²/AIC/BIC. Could show numeric detail on how many subsets each model “won.” The [MQB Miniproject report guidelines](https://mulquabio.github.io/MQB/notebooks/Appendix-MiniProj.html#the-report) suggest deeper numeric breakdown.

- **Tables/Figures (10%)**  
  - **Score:** 5/10  
  - A “summary table” is alluded to but not well integrated. Better figure/table referencing recommended.

- **Discussion (20%)**  
  - **Score:** 14/20  
  - Explains that GAM outperforms parametric approaches, with some mention of neural net or random forest. More reflection on data constraints or interpretability recommended.

- **Style/Structure (20%)**  
  - **Score:** 13/20  
  - Standard layout, references could be more explicit. The [MQB Miniproject report guidelines](https://mulquabio.github.io/MQB/notebooks/Appendix-MiniProj.html#the-report) advise cross-referencing results in the discussion thoroughly.

**Summary:** You went deeper, into demonstrating how advanced ML approaches (GAM, neural nets) can outperform simpler parametric models on some data. More numeric detail about subsets and deeper references to data would clarify results.

**Report Score:** 66

---


## Computing
### Project Structure & Workflow

**Strengths**

* `run.sh` provides a clear one‑line command to execute data cleaning, model fitting, and report compilation .
* Data import, preprocessing, model fitting, and evaluation are all handled within a single R script (`final.R`), simplifying dependency tracking.
* Covers a breadth of approaches—from linear and non‑linear least squares (NLLS) to generalized additive models (GAM), neural networks, and random forests—offering a robust comparative framework.

**Suggestions**

1. **Environment Reproducibility**:

   * **R dependencies**: Replace single `install.packages()` call in README with an `renv` workflow; commit `renv.lock` and run `Rscript -e "renv::restore()"` at the top of `final.R` or in `run.sh` to ensure consistent package versions.
   * **Python/CLI tools**: Document any external requirements (e.g., `pdflatex`) and their versions.

2. **Make Shell Entry More Robust**:

   * Switch the shebang in `run.sh` to `#!/usr/bin/env bash` and add `set -euo pipefail` to exit on errors or undefined variables.
   * Add a guard to ensure `run.sh` is executed from the project root (`cd "$(dirname "$0")"`).
   * Direct all output (`stdout` and `stderr`) to a log file under `results/` for auditing:

     ```bash
     bash run.sh 2>&1 | tee results/pipeline_$(date +%Y%m%d_%H%M).log
     ```

---

### README File

**Strengths**

* Clearly outlines goals, workflow steps, directory expectations, and output files .
* Provides both automated (`bash run.sh`) and manual instructions for LaTeX compilation, aiding troubleshooting.

**Suggestions**

1. Ensure that the described `Code/`, `Data/`, and `Results/` folders exist and contain the expected files.
2. **Installation Section**:

   * Replace `install.packages(c(...))` with a reference to `renv` or a helper script (`code/install_packages.R`) to set up dependencies.
   * Specify R version and system requirements (e.g. memory for randomForest).

3. **Usage Examples**: Show a complete minimal example:

   ```bash
   git clone <repo>
   cd project_root
   Rscript -e "renv::restore()"
   bash run.sh
   ```
4. Expand with common pitfalls (e.g., missing `Rlof` or `car` packages, LaTeX errors), linking to logs.
5. Add a LICENSE file and cite the source of `LogisticGrowthData.csv`.

---

## Shell Script: `run.sh`

**Recommendations**:

* **Portable shebang**:

  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  ```
* **Directory guard**:

  ```bash
  cd "$(dirname "$0")"
  ```
* **Logging**:

  ```bash
  bash run.sh 2>&1 | tee ../results/pipeline.log
  ```
* **Parameterization**: Accept `--data-dir` and `--results-dir` flags or environment variables to decouple code from fixed paths.

---

## `final.R` — Code Structure & Syntax

### Data Import & Preprocessing

* Replace hard-coded `"../Data/..."` with `here::here('data','LogisticGrowthData.csv')` so the script is portable across working directories.
* **Outlier Detection**:

  *Good choice for multivariate outliers. Consider wrapping LOF logic into a function (`detect_lof_outliers(df, k=10)`) and parameterizing `k`.
  * Using standardized residuals to flag >3σ is effective. However, chaining eight separate outlier flags leads to a wide dataset. Group this into a tidy pivoted structure (e.g. `model`, `resid_z`, `is_outlier`) for easier extension.
* Instead of multiple `%>% mutate()` calls interleaved with standalone operations, consolidate preprocessing into a single pipeline:

  ```r
  data_clean <- data_raw %>%
    filter(PopBio > 0, Time > 0) %>%
    mutate(LogPopBio = log(PopBio)) %>%
    na.omit() %>%
    distinct() %>%
    detect_lof_outliers(k = 10) %>%
    detect_resid_outliers(models = c('exp','gompertz', ...)) %>%
    filter(!is_any_outlier)
  ```

#### Model Fitting

* Create generic `fit_nls_model(formula, data, start, lower, upper)` for Gompertz and Logistic, returning a tibble of parameters, convergence status, and metrics.
* **Initial Values & Bounds**:

  * Currently, you use `max(PopBio)` and fixed starts (e.g., `r=0.01`). To guard against implausible starts, compute data‑driven ranges (e.g., `r ∈ [0, max_slope(data)]`) and supply `lower`/`upper` to `nlsLM()`.
  * Consider **nls.multstart** for systematic multi-start sampling over bounded parameter space.
* Wrapping each NLLS in `tryCatch()` is good. Capture errors and warnings into a structured log (e.g. a data frame with `model`, `ID`, `error_message`) instead of dropping silently.

#### Other Models (GAM, NN, RF)

* Your use of `ks = min(10, unique_time)` for GAM is sensible; extract it into `compute_knots(data)`.
* Normalizing then denormalizing is correct. Wrap into `fit_nn_model()` for clarity and reuse.
* Good default `ntree=500, mtry=1`; consider tuning `mtry` via `caret` or `ranger` for performance.

#### Prediction & Plotting Loop

* Pivoting predictions into long format is tidy. Abstract the plotting into `plot_comparison(df_pred, df_obs, palette)` that returns a `ggplot` object.
* The seven-model loop repeats code for computing metrics. Instead, build a list:

  ```r
  models <- list(
    Exp = exp_model,
    Gompertz = gompertz_model,
    ...
  )
  metrics <- imap(models, ~ compute_metrics(.x, data_subset, paste0('Predicted_', .y)))
  ```

#### Metrics Calculation

* After collecting metrics into a data frame, use `dplyr::count(Model, best = (R2 == max(R2)))` to tally wins rather than manual counters.

---

## NLLS Fitting Approach

**Strengths**

* Combining LOF and standardized residuals improves robustness of the cleaned dataset.
* Inclusion of mechanistic (Gompertz, Logistic) and empirical (polynomials, GAM, ML) methods allowed a comprehensive evaluation.

**Suggestions**

1. Adopt **nls.multstart** for both Gompertz and Logistic to automate multi-start and bounding; this also yields built‑in convergence diagnostics.
2. Constrain `K >= max(PopBio)`, `r >= 0`, `t0` within `Time` range to avoid non‑physical fits.
3. Implement leave‑one‑timepoint‑out Cross-Validation to assess out‑of‑sample predictive performance, supplementing in‑sample AIC/BIC.
4. Aggregate convergence statuses, warning messages, and runtime per model/ID into a summary report for diagnosing systematic fitting issues.
5. Compute Akaike weights (`AICcmodavg::Weights()`) or Bayesian model probabilities (via BIC approximation) to provide relative support beyond raw AIC/BIC counts.

---

## Summary

Your pipeline is functional and easy to run, with a thoughtful mix of statistical and machine‑learning approaches. To enhance reproducibility, maintainability, and analytic rigor, prioritize:

* **Environment locking** using **renv** and documented project structure.
* **Modularization** of repetitive code into well‑named functions and parameterized helpers.
* **Use of specialized libraries** (e.g. nls.multstart, AICcmodavg, caret/ranger) for more robust fitting and selection.
* **Structured logging** of all fitting outcomes and outlier decisions to aid debugging and transparency.

### **Score: 73**

---

## Overall Score: 66+73/2 = 72.25