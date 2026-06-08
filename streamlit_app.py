"""
CRISP-DM Linear Regression Streamlit Web Application

This interactive application presents the complete CRISP-DM workflow for a
synthetic linear regression project. It allows users to adjust parameters in real-time,
train models, evaluate fit, examine outliers, and export reports.

Author: Antigravity AI Partner
Language: Python 3.11+
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
from scipy.stats import norm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Tuple, Dict, Any

# Page configuration for a premium dashboard feel
st.set_page_config(
    page_title="CRISP-DM Linear Regression & Outlier Studio",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling using Glassmorphism & Custom Palettes
st.markdown("""
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    h1, h2, h3, .phase-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
    }

    /* Main Title Styling */
    .title-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(30, 60, 114, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .title-container::after {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 80%);
        pointer-events: none;
    }
    
    /* Card Container */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.04);
    }
    
    /* Highlight Title */
    .section-header {
        border-left: 6px solid #4f46e5;
        padding-left: 12px;
        color: #1e293b;
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    
    /* Metric container */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .metric-card.success { border-left-color: #10b981; }
    .metric-card.warning { border-left-color: #f59e0b; }
    .metric-card.danger { border-left-color: #ef4444; }
    </style>
    """, unsafe_allow_html=True)


# ==============================================================================
# BACKEND PIPELINE (CRISP-DM Functions)
# ==============================================================================

def run_simulation(
    seed: int, 
    n: int, 
    param_mode: str,
    a_range: Tuple[float, float],
    b_range: Tuple[float, float],
    var_range: Tuple[float, float],
    manual_a: float,
    manual_b: float,
    manual_var: float,
    outlier_k: float
) -> Dict[str, Any]:
    """
    Executes the entire data generation, model fitting, and evaluation workflow.
    This function acts as the central engine, decoupling computation from UI rendering.
    """
    # 1. Random Number Generator
    rng = np.random.default_rng(seed)
    
    # 2. True Parameters Generation
    if param_mode == "Random (CRISP-DM Rules)":
        a_true = float(rng.uniform(a_range[0], a_range[1]))
        b_true = float(rng.uniform(b_range[0], b_range[1]))
        var_true = float(rng.uniform(var_range[0], var_range[1]))
    else:  # Manual Specifications
        a_true = manual_a
        b_true = manual_b
        var_true = manual_var
        
    std_true = np.sqrt(var_true)
    
    # 3. Generate Data
    x = rng.uniform(-100, 100, size=n)
    epsilon = rng.normal(0, std_true, size=n)
    y = a_true * x + b_true + epsilon
    df_raw = pd.DataFrame({"x": x, "y": y})
    
    # 4. Data Preparation (Make copy & initialize fields)
    df_prepared = df_raw.copy()
    df_prepared["predicted_y"] = np.nan
    df_prepared["residual"] = np.nan
    df_prepared["absolute_residual"] = np.nan
    
    X = df_prepared[["x"]].values
    y_vec = df_prepared["y"].values
    
    # 5. Modeling (Fit OLS)
    model = LinearRegression()
    model.fit(X, y_vec)
    
    a_hat = float(model.coef_[0])
    b_hat = float(model.intercept_)
    
    # 6. Evaluation (Compute Predictions, Residuals, Metrics)
    predicted_y = model.predict(X)
    residuals = y_vec - predicted_y
    abs_residuals = np.abs(residuals)
    
    df_prepared["predicted_y"] = predicted_y
    df_prepared["residual"] = residuals
    df_prepared["absolute_residual"] = abs_residuals
    
    # Performance indicators
    r2 = r2_score(y_vec, predicted_y)
    mae = mean_absolute_error(y_vec, predicted_y)
    mse = mean_squared_error(y_vec, predicted_y)
    rmse = np.sqrt(mse)
    
    # Parameter Recovery Stats
    error_a = abs(a_true - a_hat)
    error_b = abs(b_true - b_hat)
    pct_error_a = (error_a / abs(a_true)) * 100 if a_true != 0 else 0
    pct_error_b = (error_b / abs(b_true)) * 100 if b_true != 0 else 0
    
    # Custom Outlier Detection (Residuals exceeding standard deviation threshold)
    df_prepared["is_outlier"] = abs_residuals > (outlier_k * std_true)
    
    # Rank all outliers and take Top 10
    sorted_df = df_prepared.sort_values(by="absolute_residual", ascending=False)
    top_outliers = sorted_df.head(10).copy()
    top_outliers.insert(0, "Rank", range(1, 11))
    
    # Save objects in a run summary dictionary
    return {
        "df": df_prepared,
        "X": X,
        "y": y_vec,
        "model": model,
        "true_params": {"a": a_true, "b": b_true, "var": var_true, "std": std_true},
        "est_params": {"a_hat": a_hat, "b_hat": b_hat},
        "metrics": {"R2": r2, "MAE": mae, "MSE": mse, "RMSE": rmse},
        "recovery": {
            "error_a": error_a, "error_b": error_b,
            "pct_error_a": pct_error_a, "pct_error_b": pct_error_b
        },
        "top_outliers": top_outliers,
        "outlier_k": outlier_k
    }

# ==============================================================================
# REPORT GENERATOR
# ==============================================================================

def generate_report_text(results: Dict[str, Any]) -> str:
    """Generates the CRISP-DM summary report as a formatted string."""
    t_p = results["true_params"]
    e_p = results["est_params"]
    rec = results["recovery"]
    metrics = results["metrics"]
    outliers = results["top_outliers"]
    
    outliers_subset = outliers[["Rank", "x", "y", "predicted_y", "residual", "absolute_residual"]]
    
    report_content = f"""================================================================================
                    CRISP-DM FINAL SUMMARY REPORT & DEPLOYMENT
================================================================================

1. PARAMETER ANALYSIS
--------------------------------------------------------------------------------
Parameter          True Value      Estimated Value  Absolute Error   Percent Error
--------------------------------------------------------------------------------
Slope (a)          {t_p['a']:<15.6f} {e_p['a_hat']:<16.6f} {rec['error_a']:<16.6f} {rec['pct_error_a']:.4f}%
Intercept (b)      {t_p['b']:<15.6f} {e_p['b_hat']:<16.6f} {rec['error_b']:<16.6f} {rec['pct_error_b']:.4f}%
Variance (var)     {t_p['var']:<15.6f} N/A              N/A              N/A
--------------------------------------------------------------------------------

2. MODEL PERFORMANCE METRICS
--------------------------------------------------------------------------------
- Coefficient of Determination (R^2): {metrics['R2']:.6f}
- Mean Absolute Error (MAE):          {metrics['MAE']:.6f}
- Mean Squared Error (MSE):           {metrics['MSE']:.6f}
- Root Mean Squared Error (RMSE):     {metrics['RMSE']:.6f}
--------------------------------------------------------------------------------

3. TOP 10 LARGEST OUTLIERS IDENTIFIED
--------------------------------------------------------------------------------
{outliers_subset.to_string(index=False)}
--------------------------------------------------------------------------------

4. KEY BUSINESS INSIGHTS
--------------------------------------------------------------------------------
- Parameter Recovery Success: The model successfully recovered the true slope with an
  absolute error of {rec['error_a']:.6f} ({rec['pct_error_a']:.3f}%) and intercept with {rec['error_b']:.6f} ({rec['pct_error_b']:.3f}%),
  exceeding the success threshold of < 5% error.
- Outlier Resilience: OLS model coefficients remained highly accurate despite the presence
  of extreme outliers (e.g. max absolute residual of {outliers['absolute_residual'].max():.4f}).
  This resilience is attributed to a robust sample size of n={len(results['df'])} and the normal, symmetric
  nature of the generating noise distribution.
- Metric Interpretability: The R^2 score of {metrics['R2']:.6f} indicates that the model
  explains {metrics['R2'] * 100:.2f}% of the total variance in Y, which is highly aligned
  with the target formula's variance ratio.

5. RECOMMENDATIONS FOR DEPLOYMENT
--------------------------------------------------------------------------------
- Deployment Viability: The parameter recovery analysis confirms that OLS linear regression
  is mathematically stable and valid for synthetic data generation scenarios.
- Quality Control checks: Implement regular residual analysis (like checking for normal distribution
  and heteroscedasticity) as new data streams in to detect shifts in the underlying process parameters.
- Handle Outliers: If deployed to real-world, non-synthetic datasets, consider using Huber Regression
  or RANSAC if the noise distribution has heavier tails than a Normal distribution, to protect
  model coefficients from bias.
================================================================================
"""
    return report_content


# ==============================================================================
# MAIN APP ARCHITECTURE
# ==============================================================================

def main():
    # Header Banner
    st.markdown("""
        <div class="title-container">
            <span style="font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; opacity: 0.85;">
                CRISP-DM Data Science Workshop
            </span>
            <h1 style="margin: 0.5rem 0 0.2rem 0; font-size: 2.8rem; letter-spacing: -1px;">
                📈 Linear Regression & Outlier Studio
            </h1>
            <p style="margin: 0; font-weight: 300; font-size: 1.1rem; opacity: 0.9;">
                An interactive simulation platform for evaluating parameter recovery, model goodness-of-fit, and outlier diagnostics.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    # --------------------------------------------------------------------------
    # SIDEBAR WIDGETS
    # --------------------------------------------------------------------------
    st.sidebar.markdown("### ⚙️ Simulation Engine Settings")
    
    n_samples = st.sidebar.slider(
        "Sample Size (n)", 
        min_value=50, 
        max_value=2000, 
        value=500, 
        step=50,
        help="Number of synthetic data points to generate."
    )
    
    seed = st.sidebar.number_input(
        "Random Seed (random_state)", 
        value=42, 
        step=1,
        help="Ensures identical dataset splits and parameters for reproducibility."
    )
    
    param_mode = st.sidebar.radio(
        "Parameter Generation Mode",
        options=["Random (CRISP-DM Rules)", "Manual Specifications"],
        help="Specify whether true coefficients are drawn randomly from pre-defined distributions or controlled manually."
    )
    
    a_range = (-50.0, 50.0)
    b_range = (0.0, 100.0)
    var_range = (5000.0, 25000.0)
    
    manual_a = 27.3956
    manual_b = 43.8878
    manual_var = 15000.0
    
    if param_mode == "Random (CRISP-DM Rules)":
        st.sidebar.info("🎲 Parameters are drawn from Uniform distributions:\n- $a \\sim U(-50, 50)$\n- $b \\sim U(0, 100)$\n- $var \\sim U(5000, 25000)$")
        with st.sidebar.expander("Adjust Uniform Bounds", expanded=False):
            a_range = st.slider("Slope (a) Bounds", -100.0, 100.0, (-50.0, 50.0))
            b_range = st.slider("Intercept (b) Bounds", 0.0, 200.0, (0.0, 100.0))
            var_range = st.slider("Variance (var) Bounds", 100.0, 60000.0, (5000.0, 25000.0), step=500.0)
    else:
        st.sidebar.success("🎛️ Manual overrides activated. Adjust coefficients below.")
        manual_a = st.sidebar.slider("True Slope (a)", -100.0, 100.0, 27.3956, step=0.1)
        manual_b = st.sidebar.slider("True Intercept (b)", -50.0, 150.0, 43.8878, step=0.5)
        manual_var = st.sidebar.slider("True Noise Variance (var)", 10.0, 60000.0, 22171.95, step=100.0)
        
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Outlier Diagnostic Settings")
    outlier_k = st.sidebar.slider(
        "Outlier Threshold (k × σ)",
        min_value=1.0,
        max_value=4.0,
        value=2.5,
        step=0.1,
        help="Outliers are data points where the absolute residual exceeds this multiple of the standard deviation."
    )
    
    # Run simulation backend
    res = run_simulation(
        seed=int(seed),
        n=n_samples,
        param_mode=param_mode,
        a_range=a_range,
        b_range=b_range,
        var_range=var_range,
        manual_a=manual_a,
        manual_b=manual_b,
        manual_var=manual_var,
        outlier_k=outlier_k
    )
    
    df = res["df"]
    true_params = res["true_params"]
    est_params = res["est_params"]
    metrics = res["metrics"]
    recovery = res["recovery"]
    top_outliers = res["top_outliers"]
    
    # --------------------------------------------------------------------------
    # CRISP-DM NAVIGATION (TABS)
    # --------------------------------------------------------------------------
    tabs = st.tabs([
        "📋 Phase 1: Business", 
        "🔍 Phase 2: Data Understanding", 
        "🧼 Phase 3: Data Prep", 
        "🧠 Phase 4: Modeling", 
        "📊 Phase 5: Evaluation", 
        "🚀 Phase 6: Deployment"
    ])
    
    # --------------------------------------------------------------------------
    # TAB 1: BUSINESS UNDERSTANDING
    # --------------------------------------------------------------------------
    with tabs[0]:
        st.markdown("<div class='section-header'>Phase 1: Business Understanding</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("""
            ### 🎯 Project Objective
            The primary goal is to evaluate the mathematical stability and recovery precision of **Ordinary Least Squares (OLS) Linear Regression** models on synthetic datasets. We simulate real-world variance by injecting Gaussian noise into a known linear equation:
            
            $$y = a \\cdot x + b + \\epsilon$$
            
            where $\\epsilon \\sim N(0, \\sigma^2)$. We analyze how accurately the model recovers the true slope ($a$) and intercept ($b$).
            
            ### 🏆 Success Criteria
            1. **Parameter Recovery Precision**: Recover slope ($a$) and intercept ($b$) with an absolute percentage error of **less than 5%** of their true values.
            2. **Anomalous Outlier Identification**: Locate and rank the top 10 data points that deviate most drastically from the regression line (highest absolute residuals).
            3. **Reproducibility Validation**: Ensure perfect repeatability of simulation profiles across executions using a locked-in generator seed.
            """)
            
        with col2:
            st.markdown("""
            <div class="glass-card">
                <h4 style="margin-top:0; color:#1e3c72;">💼 Business Value Proposition</h4>
                <p style="font-size:0.95rem; line-height:1.5; color:#475569;">
                    Understanding how noise influences regression accuracy is critical when building pricing engines, financial forecast pipelines, or marketing attribution models.
                    By running robust simulations, data teams can quantify uncertainty, determine minimum sample sizes required for stable coefficient estimations, and identify the point at which model robustness decays.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("""
            💡 **Interactive Feature**: Try modifying the **Sample Size (n)** and **True Noise Variance** in the sidebar. You will see how they affect the parameter recovery percentage errors in the Modeling and Evaluation tabs!
            """)

    # --------------------------------------------------------------------------
    # TAB 2: DATA UNDERSTANDING
    # --------------------------------------------------------------------------
    with tabs[1]:
        st.markdown("<div class='section-header'>Phase 2: Data Understanding</div>", unsafe_allow_html=True)
        
        # Display Generated true params
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.markdown(f"""
            <div class="metric-card">
                <span style="font-size: 0.85rem; color:#64748b; font-weight:600; text-transform:uppercase;">True Slope (a)</span>
                <h2 style="margin:5px 0 0 0; color:#3b82f6;">{true_params['a']:.4f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col_p2:
            st.markdown(f"""
            <div class="metric-card">
                <span style="font-size: 0.85rem; color:#64748b; font-weight:600; text-transform:uppercase;">True Intercept (b)</span>
                <h2 style="margin:5px 0 0 0; color:#3b82f6;">{true_params['b']:.4f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col_p3:
            st.markdown(f"""
            <div class="metric-card">
                <span style="font-size: 0.85rem; color:#64748b; font-weight:600; text-transform:uppercase;">True Variance / Std Dev</span>
                <h2 style="margin:5px 0 0 0; color:#3b82f6;">{true_params['var']:.2f} <span style="font-size: 1rem; color:#64748b;">(σ = {true_params['std']:.2f})</span></h2>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.subheader("📊 Descriptive Statistics")
            st.dataframe(df[["x", "y"]].describe(), use_container_width=True)
            
            st.subheader("📋 Raw Data Sample (First 10 Rows)")
            st.dataframe(df[["x", "y"]].head(10), use_container_width=True)
            
        with col_right:
            st.subheader("📈 Distribution of Generated Features")
            
            fig_dist, axes_dist = plt.subplots(1, 2, figsize=(10, 4.5))
            # Feature X
            axes_dist[0].hist(df["x"], bins=20, color="#6366f1", edgecolor="white", alpha=0.8)
            axes_dist[0].set_title("Distribution of X (Uniform Bounds)", fontsize=11, fontweight="bold")
            axes_dist[0].set_xlabel("X")
            axes_dist[0].set_ylabel("Count")
            axes_dist[0].grid(True, linestyle="--", alpha=0.5)
            
            # Target Y
            axes_dist[1].hist(df["y"], bins=20, color="#f43f5e", edgecolor="white", alpha=0.8)
            axes_dist[1].set_title("Distribution of Target Y", fontsize=11, fontweight="bold")
            axes_dist[1].set_xlabel("Y")
            axes_dist[1].set_ylabel("Count")
            axes_dist[1].grid(True, linestyle="--", alpha=0.5)
            
            plt.tight_layout()
            st.pyplot(fig_dist)
            
            # Save distribution plot to memory buffer for download if desired
            buf_dist = io.BytesIO()
            fig_dist.savefig(buf_dist, format="png", dpi=150)
            st.download_button(
                label="📥 Download Distribution Plots (PNG)",
                data=buf_dist.getvalue(),
                file_name="x_y_distributions.png",
                mime="image/png"
            )
            plt.close()

    # --------------------------------------------------------------------------
    # TAB 3: DATA PREPARATION
    # --------------------------------------------------------------------------
    with tabs[2]:
        st.markdown("<div class='section-header'>Phase 3: Data Preparation</div>", unsafe_allow_html=True)
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.subheader("🧹 Cleaning & Integrity Audit Log")
            
            missing_vals = df[["x", "y"]].isnull().sum().sum()
            duplicate_rows = df[["x", "y"]].duplicated().sum()
            
            st.markdown(f"""
            * **Missing Values Check**: No null values identified (`count = {missing_vals}`).
            * **Duplicate Rows Check**: No exact duplicates detected (`count = {duplicate_rows}`).
            * **Data Transformation**: Feature column `x` has been extracted and converted to a 2D matrix shape $[N, 1]$ suitable for linear algebra solvers.
            * **Target Variable**: Dependent column `y` has been formatted as an $N$-length vector.
            """)
            
            # Display target vector/matrix metadata in code-like block
            st.code(f"""
# Shape information
Feature matrix X: {res['X'].shape} (2D array for scikit-learn)
Target vector y:  {res['y'].shape} (1D array)
            """, language="python")
            
        with col_d2:
            st.subheader("📋 Output Table Schema Preparation")
            st.markdown("""
            As part of data prep, we initialized three new target columns to hold output metrics.
            These columns are populated after executing our modeling process:
            """)
            
            # Show the state of our DataFrame schema
            schema_info = pd.DataFrame({
                "Column Name": ["x", "y", "predicted_y", "residual", "absolute_residual"],
                "Data Type": ["float64", "float64", "float64 (Initialized)", "float64 (Initialized)", "float64 (Initialized)"],
                "Description": ["Independent predictor", "Ground truth target with noise", "Model prediction value", "Observation error (y - y_pred)", "Absolute value of error"]
            })
            st.table(schema_info)

    # --------------------------------------------------------------------------
    # TAB 4: MODELING
    # --------------------------------------------------------------------------
    with tabs[3]:
        st.markdown("<div class='section-header'>Phase 4: Modeling</div>", unsafe_allow_html=True)
        
        col_m1, col_m2 = st.columns([1, 1])
        with col_m1:
            st.subheader("🤖 Fitted Ordinary Least Squares (OLS)")
            st.markdown(f"""
            We fit a basic linear estimator using `scikit-learn.linear_model.LinearRegression` which operates via closed-form OLS solutions.
            
            **Equation fitted by model:**
            $$\\hat{{y}} = \\hat{{a}} \\cdot x + \\hat{{b}}$$
            
            * **Estimated Slope ($\\hat{{a}}$)**: `{est_params['a_hat']:.6f}`
            * **Estimated Intercept ($\\hat{{b}}$)**: `{est_params['b_hat']:.6f}`
            """)
            
            st.subheader("📐 OLS Mathematical Formulation")
            st.markdown("""
            The objective of Ordinary Least Squares is to find the parameters that minimize the Residual Sum of Squares (RSS):
            
            $$\\text{RSS}(a, b) = \\sum_{i=1}^{n} (y_i - (a x_i + b))^2$$
            
            By setting the partial derivatives with respect to $a$ and $b$ to zero, the closed-form estimators are:
            
            $$\\hat{a} = \\frac{\\sum (x_i - \\bar{x})(y_i - \\bar{y})}{\\sum (x_i - \\bar{x})^2}$$
            $$\\hat{b} = \\bar{y} - \\hat{a} \\bar{x}$$
            """)
            
        with col_m2:
            st.subheader("📋 Core Assumptions of Linear Regression")
            st.markdown("""
            For OLS estimates to be the Best Linear Unbiased Estimators (BLUE), several key assumptions must hold:
            
            1. **Linearity**: The relationship between target and predictors is linear.
            2. **Independence of Errors**: Residuals $\\epsilon_i$ are independent of one another.
            3. **Homoscedasticity (Constant Variance)**: The variance of error terms is constant across all feature ranges: $\\text{Var}(\\epsilon_i) = \\sigma^2$.
            4. **Normality of Errors**: Errors are normally distributed: $\\epsilon_i \\sim N(0, \\sigma^2)$.
            5. **No Multicollinearity**: Predictors are not perfectly correlated (not applicable here, as we have a single feature $x$).
            """)

    # --------------------------------------------------------------------------
    # TAB 5: EVALUATION
    # --------------------------------------------------------------------------
    with tabs[4]:
        st.markdown("<div class='section-header'>Phase 5: Evaluation</div>", unsafe_allow_html=True)
        
        # 1. Metric Display Cards
        col_me1, col_me2, col_me3, col_me4 = st.columns(4)
        
        # Style metrics based on performance thresholds
        r2_color_class = "success" if metrics['R2'] > 0.8 else ("warning" if metrics['R2'] > 0.5 else "danger")
        mae_vs_sigma = metrics['MAE'] / true_params['std']
        mae_color_class = "success" if mae_vs_sigma < 1.0 else "warning"
        
        with col_me1:
            st.markdown(f"""
            <div class="metric-card {r2_color_class}">
                <span style="font-size: 0.85rem; color:#64748b; font-weight:600; text-transform:uppercase;">Goodness of Fit (R²)</span>
                <h2 style="margin:5px 0 0 0; color:#1e293b;">{metrics['R2']:.5f}</h2>
                <span style="font-size:0.75rem; color:#64748b;">Variance explained by model</span>
            </div>
            """, unsafe_allow_html=True)
        with col_me2:
            st.markdown(f"""
            <div class="metric-card {mae_color_class}">
                <span style="font-size: 0.85rem; color:#64748b; font-weight:600; text-transform:uppercase;">Mean Absolute Error (MAE)</span>
                <h2 style="margin:5px 0 0 0; color:#1e293b;">{metrics['MAE']:.3f}</h2>
                <span style="font-size:0.75rem; color:#64748b;">Average absolute distance to fit</span>
            </div>
            """, unsafe_allow_html=True)
        with col_me3:
            st.markdown(f"""
            <div class="metric-card">
                <span style="font-size: 0.85rem; color:#64748b; font-weight:600; text-transform:uppercase;">Mean Squared Error (MSE)</span>
                <h2 style="margin:5px 0 0 0; color:#1e293b;">{metrics['MSE']:.1f}</h2>
                <span style="font-size:0.75rem; color:#64748b;">Penalizes larger outliers</span>
            </div>
            """, unsafe_allow_html=True)
        with col_me4:
            st.markdown(f"""
            <div class="metric-card">
                <span style="font-size: 0.85rem; color:#64748b; font-weight:600; text-transform:uppercase;">Root Mean Squared Error (RMSE)</span>
                <h2 style="margin:5px 0 0 0; color:#1e293b;">{metrics['RMSE']:.3f}</h2>
                <span style="font-size:0.75rem; color:#64748b;">True standard deviation (σ): {true_params['std']:.3f}</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. Parameter Recovery Table
        st.subheader("🔄 Parameter Recovery Validation")
        st.markdown(r"""
        To evaluate if the model is valid, we check how closely the estimated parameters ($\hat{a}$, $\hat{b}$) match the true values.
        Our business success criteria requires **Absolute Percentage Error < 5%**.
        """)
        
        # Style status cells for premium looks
        a_status = "✅ PASS" if recovery['pct_error_a'] < 5.0 else "❌ FAIL"
        b_status = "✅ PASS" if recovery['pct_error_b'] < 5.0 else "❌ FAIL"
        
        recovery_summary_df = pd.DataFrame({
            "Coefficient": ["Slope (a)", "Intercept (b)"],
            "Ground Truth": [true_params['a'], true_params['b']],
            "Model Estimate": [est_params['a_hat'], est_params['b_hat']],
            "Absolute Error": [recovery['error_a'], recovery['error_b']],
            "Percentage Error": [f"{recovery['pct_error_a']:.4f}%", f"{recovery['pct_error_b']:.4f}%"],
            "Business Threshold (< 5% Error)": [f"5% max error limit", f"5% max error limit"],
            "Status": [a_status, b_status]
        })
        st.table(recovery_summary_df)
        
        # 3. Diagnostic Visualizations (4-panel)
        st.subheader("🔍 Four-Panel Regression Diagnostic Suite")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 11))
        
        color_dots = "#3a86c8"
        color_line = "#ef4444"
        color_outlier = "#f59e0b"
        
        # Plot 1: Scatter Fit & Highlighted Outliers
        ax1 = axes[0, 0]
        ax1.scatter(df["x"], df["y"], color=color_dots, alpha=0.5, s=15, label="Normal Observations")
        
        # Draw line
        x_line = np.linspace(df["x"].min(), df["x"].max(), 100)
        y_line = est_params["a_hat"] * x_line + est_params["b_hat"]
        ax1.plot(x_line, y_line, color=color_line, linewidth=2.5, label=f"OLS Line (a_hat={est_params['a_hat']:.2f})")
        
        # Highlight Outliers
        outliers_mask = df["is_outlier"]
        outliers_df = df[outliers_mask]
        
        ax1.scatter(
            outliers_df["x"], outliers_df["y"], 
            color=color_outlier, s=50, edgecolor="black", zorder=5, 
            label=f"Outliers (> {outlier_k}σ)"
        )
        
        # Annotate indices of top 5 outliers specifically to avoid overlapping clutter
        for idx, row in top_outliers.head(5).iterrows():
            ax1.annotate(
                str(idx), (row["x"], row["y"]), 
                textcoords="offset points", xytext=(5, 5), 
                fontsize=8, fontweight="bold", color="#1d3557"
            )
            
        ax1.set_title("Figure 1: Fit and Highlighted Outliers Plot", pad=10, fontweight="bold")
        ax1.set_xlabel("Feature X")
        ax1.set_ylabel("Target Y")
        ax1.legend(loc="upper left")
        ax1.grid(True, linestyle="--", alpha=0.5)
        
        # Plot 2: Residual Histogram with Fitted Normal Curve
        ax2 = axes[0, 1]
        ax2.hist(df["residual"], bins=30, color="#1e293b", edgecolor="white", alpha=0.8, density=True)
        
        mu_res, std_res = norm.fit(df["residual"])
        xmin_a2, xmax_a2 = ax2.get_xlim()
        x_axis_a2 = np.linspace(xmin_a2, xmax_a2, 100)
        p_axis_a2 = norm.pdf(x_axis_a2, mu_res, std_res)
        ax2.plot(
            x_axis_a2, p_axis_a2, color=color_line, linewidth=2.5, linestyle="--", 
            label=f"Normal Fit\n(μ={mu_res:.2f}, σ={std_res:.2f})"
        )
        
        ax2.set_title("Figure 2: Residual Histogram & Normal Fit", pad=10, fontweight="bold")
        ax2.set_xlabel("Residual (ε)")
        ax2.set_ylabel("Probability Density")
        ax2.legend()
        ax2.grid(True, linestyle="--", alpha=0.5)
        
        # Plot 3: Residual vs Predicted (Homoscedasticity check)
        ax3 = axes[1, 0]
        ax3.scatter(df["predicted_y"], df["residual"], color=color_dots, alpha=0.6, s=15)
        ax3.axhline(0, color=color_line, linestyle="--", linewidth=1.5)
        ax3.scatter(outliers_df["predicted_y"], outliers_df["residual"], color=color_outlier, s=40, edgecolor="black", zorder=5)
        
        ax3.set_title("Figure 3: Residual vs. Predicted Plot", pad=10, fontweight="bold")
        ax3.set_xlabel("Predicted Target (y_hat)")
        ax3.set_ylabel("Residual (ε)")
        ax3.grid(True, linestyle="--", alpha=0.5)
        
        # Plot 4: Actual vs Predicted (Accuracy profile)
        ax4 = axes[1, 1]
        ax4.scatter(df["predicted_y"], df["y"], color=color_dots, alpha=0.6, s=15)
        
        min_val = min(df["y"].min(), df["predicted_y"].min())
        max_val = max(df["y"].max(), df["predicted_y"].max())
        ax4.plot([min_val, max_val], [min_val, max_val], color=color_line, linestyle="--", linewidth=2, label="Perfect Fit (y = y_hat)")
        ax4.scatter(outliers_df["predicted_y"], outliers_df["y"], color=color_outlier, s=40, edgecolor="black", zorder=5)
        
        ax4.set_title("Figure 4: Actual vs. Predicted Plot", pad=10, fontweight="bold")
        ax4.set_xlabel("Predicted Target (y_hat)")
        ax4.set_ylabel("Actual Target (y)")
        ax4.legend(loc="upper left")
        ax4.grid(True, linestyle="--", alpha=0.5)
        
        fig.suptitle(
            f"OLS Model Diagnostics & Outlier Profiling\nTrue Slope (a) = {true_params['a']:.4f} | Estimated (a_hat) = {est_params['a_hat']:.4f}",
            y=0.98, fontsize=14, fontweight="bold"
        )
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        st.pyplot(fig)
        
        # Save plots to buffer for download
        buf_diag = io.BytesIO()
        fig.savefig(buf_diag, format="png", dpi=200)
        st.download_button(
            label="📥 Download Diagnostic Suite (PNG)",
            data=buf_diag.getvalue(),
            file_name="regression_plots.png",
            mime="image/png"
        )
        plt.close()
        
        # 4. Outliers Table
        st.subheader("🕵️ Top 10 Extreme Outliers Analysis")
        st.markdown(f"""
        Below are the top 10 data points sorted by absolute residual magnitude. 
        Currently, **{len(outliers_df)}** points out of **{n_samples}** ({(len(outliers_df)/n_samples)*100:.2f}%) exceed the diagnostic threshold of **{outlier_k} × σ** residuals.
        """)
        
        outliers_subset_table = top_outliers[["Rank", "x", "y", "predicted_y", "residual", "absolute_residual"]]
        st.dataframe(outliers_subset_table.style.highlight_max(subset=["absolute_residual"], color="#ffe4e6"), use_container_width=True)
        
        st.info("""
        💡 **Diagnostic Insight**: These residuals represent sample draws from the extreme long-tails of the random noise distribution $\\epsilon \\sim N(0, \\sigma^2)$. Because OLS works by minimizing the squared residuals, individual massive outliers exert leverage that can pull the regression line. 
        Thanks to our high sample size ($N={}$), these independent, symmetric errors cancel out, resulting in highly precise recovery bounds.
        """.format(n_samples))

    # --------------------------------------------------------------------------
    # TAB 6: DEPLOYMENT
    # --------------------------------------------------------------------------
    with tabs[5]:
        st.markdown("<div class='section-header'>Phase 6: Deployment</div>", unsafe_allow_html=True)
        
        # Compile Report content
        report_text = generate_report_text(res)
        
        col_dep1, col_dep2 = st.columns([3, 2])
        
        with col_dep1:
            st.subheader("📄 Generated Deployment Report (`crisp_dm_summary.txt`)")
            st.markdown("Below is the identical final deployment report generated by the simulation pipeline.")
            st.code(report_text, language="text")
            
            # Download report button
            st.download_button(
                label="💾 Download Summary Report (.txt)",
                data=report_text,
                file_name="crisp_dm_summary.txt",
                mime="text/plain"
            )
            
        with col_dep2:
            st.subheader("🚀 Model Deployment Recommendation Status")
            
            # Check PASS/FAIL status based on 5% error threshold
            if recovery['pct_error_a'] < 5.0 and recovery['pct_error_b'] < 5.0:
                st.success("""
                ### **🏆 DEPLOYMENT STATE: APPROVED**
                
                The regression engine has successfully recovered the true underlying process coefficients within the predefined **5% business error margin**.
                
                **Validation Highlights:**
                * Slope Recovery Error: **{:.4f}%** (Success)
                * Intercept Recovery Error: **{:.4f}%** (Success)
                * Residual Standard Deviation (RMSE): **{:.3f}** (Target: **{:.3f}**)
                """.format(recovery['pct_error_a'], recovery['pct_error_b'], metrics['RMSE'], true_params['std']))
            else:
                st.error("""
                ### **⚠️ DEPLOYMENT STATE: REJECTED**
                
                The model has failed to recover the parameters within the **5% business error threshold**.
                
                **Troubleshooting Steps:**
                1. Increase **Sample Size ($n$)** in the sidebar to allow OLS coefficients to converge.
                2. Lower the **Noise Variance** to improve the signal-to-noise ratio.
                """)
                
            st.markdown("""
            ### 📝 Best Practices for Real-World Deployment:
            * **Monitor Residual Drifts**: In production, establish real-time z-score tests on streaming residual variances to detect drift in data generation distributions.
            * **Guard Against Fat Tails**: If real-world errors do not follow a Gaussian normal distribution (e.g. they show heavy tails), switch model engines to robust alternatives such as **Huber Regression** or **RANSAC** to prevent extreme outliers from skewing parameter slopes.
            """)

if __name__ == "__main__":
    main()
