# Peer Review: Cali Allocation Model (Inverted UN Scale v3)

This report provides a technical peer review of the Cali Allocation Model (unscale-v3), evaluating its structural design, mathematical basis, conceptual reasoning, sensitivity testing methodologies, and presenting actionable recommendations before its release to technical and policy audiences.

## 1. Design and Structure

**The repository is highly structured, modular, and well-designed.**
*   **Separation of Concerns:** Core mathematical logic (`src/cali_model/calculator.py`, `balance_analysis.py`) is decoupled from the frontend UI layers (`app.py`, `sensitivity.py`). This prevents UI components from intertwining with the allocation math, adhering to robust software design principles.
*   **Pipeline & Validation:** The data ingestion is handled appropriately via `duckdb` and `pandas`, coupled with rigorous `pytest` frameworks. The implementation of explicit validation checks (e.g., confirming exactly 196 CBD Parties, correctly mapping metadata, and identifying the EU) ensures persistent data integrity.
*   **Methodological Transparency:** By relying on idiomatic Python and Streamlit, the codebase remains accessible to technical policy advisors and data scientists who might need to verify the mechanics.

## 2. Mathematical Correctness

**The core implementation of the Final Share formula is mathematically correct.**
*   **Weight Normalization:** The distribution vectors ($IUSAF$, $TSAC$, $SOSAC$) safely normalize to 1.0 (or zero where components are inactive/zeroed), ensuring funds explicitly match the requested user parameters.
*   **SIDS Fallback Logic:** In the event that no SIDS are mathematically eligible, the code cleanly reabsorbs the $\gamma$ weight into the $\alpha$ base weight.
*   **Floor & Ceiling Constraints:** `_apply_floor_ceiling_shares()` accomplishes boundary constraints via an iterative redistribution algorithm. This ensures that bounded values freeze at limits while floating values continue to uniformly redistribute without breaking the 100% distribution property.
*   **Conservation Checks:** Regression and validation tests successfully assert `iplc_component + state_component = total_allocation`.

## 3. Reasoning and Soundness

**The conceptual reasoning behind the model parameters is sound, effectively translating equity and environmental stewardship goals into a quantitative framework.**
*   **IUSAF Base Foundation:** Inverting the UN scale successfully formalizes the principle of "capacity vs. need." The option for "Banded inversion" effectively acts as a noise-reduction mechanism to eliminate volatility caused by microscopic differences at the bottom and top of the assessment scale.
*   **TSAC (Terrestrial) & SOSAC (Ocean):** Utilizing land area clearly addresses raw terrestrial conservation scale obligations, and the flat uniform distribution of SOSAC acknowledges the non-linear operational costs needed for maritime conservation by Small Island Developing States (SIDS). 
*   **Blend Equilibrium:** Modulating TSAC and SOSAC as an overlay against the IUSAF structure limits major topological distortions to the established sovereignty/equity hierarchy.

## 4. Sensitivity Tests and Conclusions

**The sensitivity framework laid out in `sensitivity-plan.md` and executed in `balance_analysis.py` is exemplary.**
*   **Non-Advocacy Constraint:** The overarching directive to utilize disciplined, non-polemical prose ("measured, precise, restrained") ensures the tool operates as an objective policy dashboard rather than an advocacy piece.
*   **Threshold Metrics:** Defining structural breaks via explicit geometric thresholds (e.g., Spearman rank correlation dropping below 0.90, Top-20 turnover surpassing 20%) provides negotiators with an unbiased mathematical indicator of when parameter tuning fundamentally shifts to distribution redrafting. 
*   **Attack-Surface Analysis:** Pre-emptively testing counter-arguments establishes robustness well-calibrated for an adversarial review setting.

## 5. Recommendations for Improvement

Prior to presentation to a critical technical audience, consider the following technical and semantic refinements:

> [!TIP]
> **Refine the Semantics of "Gini-Optimal"**
> As accurately documented in `balance_analysis.py`, the so-called "Gini-Optimal" point (TSAC=0.05, SOSAC=0.03) minimizes statistical inequality but **fails to satisfy** the core TSAC/IUSAF dominance balance condition for China and Brazil. 
> *Recommendation:* Rename this to something functionally descriptive, such as the **"Gini-Minimised Setting"**. "Optimal" carries heavy normative weight and implies mathematical alignment with all model constraints (which it violates). Critics may point to this divergence to attack the entire "Optimal" preset.

> [!IMPORTANT]
> **Remove Hard-Coded Fallbacks for Transparency**
> Within `assign_un_band()`, a `0.0` un\_share is hard-coded to return Band 1 with a weight of 1.50 if the `config['bands']` iteration misses it.
> *Recommendation:* Ensure the `un_scale_bands.yaml` logic natively addresses $0.0$ bounds (e.g., using `min_threshold: -0.0001` for Band 1) so that all numerical definitions remain isolated in the configuration layer rather than scattered in Python functions.

> [!WARNING]
> **Iterative Convergence Bounds for Floor/Ceiling Logic**
> The `_apply_floor_ceiling_shares()` mechanism relies on a `while True:` loop to redistribute remaining shares to unconstrained states. While fast for $N=196$, an iterative bounds solver can exhibit infinite looping or float threshold staggering under highly adversarial ranges.
> *Recommendation:* Introduce a maximum iteration fail-safe limit (`max_iterations = 20`) with a logged warning, ensuring the function returns predictably even if user parameters (e.g. extremely high interacting floors) cause algorithmic stalling.

> [!TIP]
> **Decouple Policy Warnings from Absolute Weight Combinations**
> The warning checks (`get_stewardship_blend_feedback()`) hardcode a "mild warning" at $0.15$ and a "strong warning" at $0.20$ combined TSAC/SOSAC weight.
> *Recommendation:* Use resulting correlation coefficients (e.g. a Spearman dropping below 0.85) to dynamically trigger a "stewardship balance override" warning, rather than anchoring it to fixed combination sum thresholds. This reflects the *actual* mathematical outcome distortion rather than anticipating it.
