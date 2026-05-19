"""
app.py
------
Advanced Climate Modeling Platform — Interactive Dashboard
Streamlit + Plotly professional UI

Run with:
    streamlit run app.py
    Open: http://localhost:8501
"""

import json
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import xarray as xr
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pathlib import Path

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Climate Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark background */
    .stApp { background-color: #0d1117; }
    .main .block-container { padding-top: 1rem; padding-bottom: 1rem; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
        border-right: 1px solid #21262d;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #21262d;
        border-radius: 8px;
        padding: 12px 16px;
    }
    div[data-testid="metric-container"] label { color: #8b949e !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #58a6ff !important; font-size: 1.4rem;
    }

    /* Headers */
    h1, h2, h3, h4 { color: #f0f6fc; }
    .stMarkdown p { color: #8b949e; }

    /* Section divider */
    hr { border-color: #21262d; }

    /* Tabs */
    button[data-baseweb="tab"] { color: #8b949e; }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #58a6ff; border-bottom: 2px solid #58a6ff;
    }
</style>
""", unsafe_allow_html=True)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent
DATA_ZARR        = BASE / "data/zarr/processed_climate.zarr"
GLOBAL_MEANS_CSV = BASE / "outputs/reports/global_means.csv"
ENSEMBLE_CSV     = BASE / "outputs/reports/ensemble_stats.csv"
INDICES_CSV      = BASE / "outputs/reports/climate_indices.csv"
BIAS_CSV         = BASE / "outputs/reports/bias_corrected.csv"
DOWNSCALE_CSV    = BASE / "outputs/reports/downscaled_station.csv"
METADATA_JSON    = BASE / "metadata/run_metadata.json"

PLOTLY_DARK = dict(
    template="plotly_dark",
    paper_bgcolor="#0d1117",
    plot_bgcolor="#161b22",
    font_color="#c9d1d9",
)

# ── Data loaders (cached) ─────────────────────────────────────────────────────
@st.cache_data
def load_global_means():
    if not GLOBAL_MEANS_CSV.exists(): return None
    return pd.read_csv(GLOBAL_MEANS_CSV, parse_dates=["time"])

@st.cache_data
def load_ensemble():
    if not ENSEMBLE_CSV.exists(): return None
    return pd.read_csv(ENSEMBLE_CSV, index_col="time", parse_dates=True)

@st.cache_data
def load_indices():
    if not INDICES_CSV.exists(): return None
    return pd.read_csv(INDICES_CSV)

@st.cache_data
def load_bias():
    if not BIAS_CSV.exists(): return None
    return pd.read_csv(BIAS_CSV, parse_dates=["time"])

@st.cache_data
def load_downscale():
    if not DOWNSCALE_CSV.exists(): return None
    return pd.read_csv(DOWNSCALE_CSV, parse_dates=["time"])

@st.cache_data
def load_zarr_snapshot():
    """Load one time slice for spatial maps (light load)."""
    if not DATA_ZARR.exists(): return None
    ds = xr.open_zarr(str(DATA_ZARR))
    return ds.isel(time=0).compute()

@st.cache_data
def load_metadata():
    if not METADATA_JSON.exists(): return {}
    return json.loads(METADATA_JSON.read_text())

# ── Pipeline status checker ───────────────────────────────────────────────────
def pipeline_status():
    files = {
        "Raw NetCDF":         BASE / "data/raw/synthetic_climate.nc",
        "Processed NetCDF":   BASE / "data/processed/processed_climate.nc",
        "Zarr Store":         DATA_ZARR,
        "Global Means CSV":   GLOBAL_MEANS_CSV,
        "Climate Indices CSV":INDICES_CSV,
        "Ensemble Stats CSV": ENSEMBLE_CSV,
        "Bias Corrected CSV": BIAS_CSV,
        "Downscaled CSV":     DOWNSCALE_CSV,
        "Run Metadata JSON":  METADATA_JSON,
    }
    return {k: v.exists() for k, v in files.items()}

# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🌍 Climate Platform")
    st.markdown("**Advanced Climate Modeling Platform**")
    st.markdown("*Prototype — Pangeo-style analytics*")
    st.markdown("---")

    st.markdown("### Navigation")
    page = st.radio(
        "",
        [
            "📊 Overview",
            "🌡️ Temperature Analytics",
            "🌧️ Precipitation",
            "📈 Climate Indices",
            "🎲 Ensemble Analysis",
            "🔧 Bias Correction",
            "📍 Downscaling",
            "🗺️ Spatial Maps",
            "📋 Metadata & FAIR",
            "🔬 Pipeline Status",
        ],
        label_visibility="hidden",
    )

    st.markdown("---")
    st.markdown("### Pipeline")
    if st.button("▶ Run Full Pipeline", use_container_width=True):
        with st.spinner("Running pipeline…"):
            try:
                import subprocess, sys
                result = subprocess.run(
                    [sys.executable, "-m", "src.pipeline"],
                    capture_output=True, text=True, cwd=str(BASE)
                )
                if result.returncode == 0:
                    st.success("Pipeline completed!")
                    st.cache_data.clear()
                else:
                    st.error("Pipeline failed — check logs/")
                    st.code(result.stderr[-2000:])
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("**Author:** Saif Ud Din Khan")
    st.markdown("**Stack:** Python · Xarray · Dask · Zarr · Plotly")

# ═════════════════════════════════════════════════════════════════════════════
# PAGES
# ═════════════════════════════════════════════════════════════════════════════

# ── Overview ──────────────────────────────────────────────────────────────────
if page == "📊 Overview":
    st.title("🌍 Advanced Climate Modeling Platform")
    st.markdown(
        "Prototype climate science platform demonstrating the full workflow of a "
        "modern climate analytics system — from data generation to bias correction, "
        "ensemble uncertainty, and statistical downscaling."
    )

    # Architecture cards
    col1, col2, col3, col4, col5 = st.columns(5)
    cards = [
        ("🏗️", "Model Layer",  "CESM · MPAS · NEMO"),
        ("⚙️", "HPC Layer",    "Slurm · Dask"),
        ("💾", "Data Layer",   "NetCDF · Zarr"),
        ("📐", "Analytics",    "Xarray · sklearn"),
        ("📡", "Sharing",      "Streamlit · FAIR"),
    ]
    for col, (icon, title, sub) in zip([col1, col2, col3, col4, col5], cards):
        col.markdown(f"""
        <div style="background:#161b22;border:1px solid #21262d;border-radius:8px;
                    padding:14px;text-align:center;">
            <div style="font-size:1.8rem">{icon}</div>
            <div style="color:#58a6ff;font-weight:600;font-size:.9rem">{title}</div>
            <div style="color:#8b949e;font-size:.78rem;margin-top:4px">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Key metrics
    df_gm = load_global_means()
    df_en = load_ensemble()
    df_bc = load_bias()
    df_ds = load_downscale()

    col1, col2, col3, col4 = st.columns(4)
    if df_gm is not None:
        col1.metric("Mean Temperature", f"{df_gm['tas_global_K'].mean():.2f} K",
                    f"+{(df_gm['tas_global_K'].iloc[-1]-df_gm['tas_global_K'].iloc[0]):.2f} K trend")
        col2.metric("Mean Precipitation", f"{df_gm['pr_global_mm'].mean():.2f} mm/day")
    if df_en is not None and "ensemble_std" in df_en.columns:
        col3.metric("Ensemble Spread (σ)", f"{df_en['ensemble_std'].mean():.3f} K")
    if df_bc is not None:
        col4.metric("Bias Corrected", f"{df_bc['correction_applied'].mean():.3f} K avg")

    st.markdown("---")

    # Quick temperature chart
    if df_gm is not None:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_gm["time"], y=df_gm["tas_global_K"],
            mode="lines", name="Global Mean Temp",
            line=dict(color="#58a6ff", width=2),
            fill="tozeroy", fillcolor="rgba(88,166,255,0.08)"
        ))
        fig.update_layout(
            title="Global Mean Temperature Overview",
            xaxis_title="Time", yaxis_title="Temperature (K)",
            height=320, **PLOTLY_DARK
        )
        st.plotly_chart(fig, use_container_width=True)


# ── Temperature Analytics ─────────────────────────────────────────────────────
elif page == "🌡️ Temperature Analytics":
    st.title("🌡️ Temperature Analytics")

    df = load_global_means()
    if df is None:
        st.warning("Run the pipeline first: `python -m src.pipeline`"); st.stop()

    # Global mean with trend line
    z = np.polyfit(range(len(df)), df["tas_global_K"], 1)
    trend_line = np.polyval(z, range(len(df)))

    fig = make_subplots(rows=2, cols=1, subplot_titles=["Monthly Global Mean", "Annual Mean"])
    fig.add_trace(go.Scatter(x=df["time"], y=df["tas_global_K"],
                             mode="lines", name="Monthly",
                             line=dict(color="#58a6ff", width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["time"], y=trend_line,
                             mode="lines", name="Linear Trend",
                             line=dict(color="#f85149", width=2, dash="dash")), row=1, col=1)

    df["year"] = df["time"].dt.year
    annual = df.groupby("year")["tas_global_K"].mean().reset_index()
    fig.add_trace(go.Bar(x=annual["year"], y=annual["tas_global_K"],
                         name="Annual Mean", marker_color="#238636"), row=2, col=1)

    fig.update_layout(height=550, **PLOTLY_DARK,
                      yaxis_title="Temperature (K)", yaxis2_title="Temperature (K)")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Min Temperature",  f"{df['tas_global_K'].min():.3f} K")
    col2.metric("Max Temperature",  f"{df['tas_global_K'].max():.3f} K")
    col3.metric("Warming Trend",    f"{z[0]*12:.4f} K/year")


# ── Precipitation ─────────────────────────────────────────────────────────────
elif page == "🌧️ Precipitation":
    st.title("🌧️ Precipitation Analysis")

    df = load_global_means()
    if df is None:
        st.warning("Run the pipeline first."); st.stop()

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Monthly Precipitation", "Monthly Distribution"])
    fig.add_trace(go.Bar(x=df["time"], y=df["pr_global_mm"],
                         name="Precipitation", marker_color="#1f6feb"), row=1, col=1)
    df["month"] = df["time"].dt.month
    monthly_box = df.groupby("month")["pr_global_mm"].apply(list).reset_index()
    for m, vals in zip(monthly_box["month"], monthly_box["pr_global_mm"]):
        fig.add_trace(go.Box(y=vals, name=str(m),
                             marker_color="#388bfd"), row=1, col=2)

    fig.update_layout(height=420, showlegend=False, **PLOTLY_DARK,
                      yaxis_title="mm day⁻¹", yaxis2_title="mm day⁻¹")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Mean Precip", f"{df['pr_global_mm'].mean():.3f} mm/day")
    col2.metric("Max Precip",  f"{df['pr_global_mm'].max():.3f} mm/day")
    col3.metric("Min Precip",  f"{df['pr_global_mm'].min():.3f} mm/day")


# ── Climate Indices ────────────────────────────────────────────────────────────
elif page == "📈 Climate Indices":
    st.title("📈 Climate Extreme Indices")

    df = load_indices()
    if df is None:
        st.warning("Run the pipeline first."); st.stop()

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Annual Heatwave Fraction", "Year-over-Year Change"])
    fig.add_trace(go.Bar(x=df["year"], y=df["heatwave_fraction"],
                         marker_color="#f85149", name="Heatwave Fraction"), row=1, col=1)
    if len(df) > 1:
        change = df["heatwave_fraction"].diff().dropna()
        fig.add_trace(go.Bar(x=df["year"][1:], y=change,
                             marker_color=["#238636" if v > 0 else "#f85149" for v in change],
                             name="Change"), row=1, col=2)
    fig.update_layout(height=380, **PLOTLY_DARK,
                      yaxis_title="Fraction of hot grid cells",
                      yaxis2_title="Change")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    col1.metric("Mean Heatwave Fraction", f"{df['heatwave_fraction'].mean():.3f}")
    col2.metric("Max Heatwave Fraction",  f"{df['heatwave_fraction'].max():.3f}")

    st.info(
        "**Heatwave fraction**: proportion of the global grid that exceeded the "
        "95th-percentile temperature threshold in each year. Higher = more widespread heat."
    )


# ── Ensemble Analysis ─────────────────────────────────────────────────────────
elif page == "🎲 Ensemble Analysis":
    st.title("🎲 Ensemble Uncertainty Analysis")

    df = load_ensemble()
    if df is None:
        st.warning("Run the pipeline first."); st.stop()

    member_cols = [c for c in df.columns if c.startswith("member_")]

    fig = go.Figure()
    colors = px.colors.sequential.Plasma
    for i, col in enumerate(member_cols):
        fig.add_trace(go.Scatter(
            x=df.index, y=df[col], mode="lines",
            name=col.replace("_", " ").title(),
            line=dict(width=1, color=colors[i * (len(colors)//len(member_cols))]),
            opacity=0.6,
        ))
    if "ensemble_mean" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["ensemble_mean"], mode="lines",
            name="Ensemble Mean", line=dict(color="white", width=2.5)
        ))
    if "ensemble_std" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index.tolist() + df.index.tolist()[::-1],
            y=(df["ensemble_mean"] + df["ensemble_std"]).tolist() +
              (df["ensemble_mean"] - df["ensemble_std"]).tolist()[::-1],
            fill="toself", fillcolor="rgba(200,160,255,0.15)",
            line=dict(color="rgba(0,0,0,0)"), name="±1σ", showlegend=True
        ))
    fig.update_layout(
        title="5-Member Ensemble Temperature Timeseries",
        xaxis_title="Time", yaxis_title="Temperature (K)",
        height=420, **PLOTLY_DARK
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Mean Spread (σ)", f"{df['ensemble_std'].mean():.4f} K")
    col2.metric("Max Spread",      f"{df['ensemble_std'].max():.4f} K")
    col3.metric("N Members",       len(member_cols))

    st.info(
        "**Ensemble mean** shows the robust climate signal. "
        "**σ (spread)** quantifies model uncertainty — wider spread = higher uncertainty."
    )


# ── Bias Correction ───────────────────────────────────────────────────────────
elif page == "🔧 Bias Correction":
    st.title("🔧 Bias Correction")

    df = load_bias()
    if df is None:
        st.warning("Run the pipeline first."); st.stop()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["raw_tas_K"],
                             mode="lines", name="Raw Model",
                             line=dict(color="#f85149", width=1.5)))
    fig.add_trace(go.Scatter(x=df["time"], y=df["bias_corrected_K"],
                             mode="lines", name="Bias Corrected",
                             line=dict(color="#3fb950", width=1.5)))
    fig.update_layout(
        title="Monthly Bias Correction: Raw vs Corrected Temperature",
        xaxis_title="Time", yaxis_title="Temperature (K)",
        height=380, **PLOTLY_DARK
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=df["time"], y=df["correction_applied"],
                          name="Correction Applied",
                          marker_color=["#3fb950" if v > 0 else "#f85149"
                                        for v in df["correction_applied"]]))
    fig2.update_layout(title="Correction Applied per Month",
                       xaxis_title="Time", yaxis_title="ΔT (K)",
                       height=280, **PLOTLY_DARK)
    st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)
    col1.metric("Mean Correction", f"{df['correction_applied'].mean():.3f} K")
    col2.metric("Max Correction",  f"{abs(df['correction_applied']).max():.3f} K")


# ── Downscaling ───────────────────────────────────────────────────────────────
elif page == "📍 Downscaling":
    st.title("📍 Statistical Downscaling")

    df = load_downscale()
    if df is None:
        st.warning("Run the pipeline first."); st.stop()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=df["observed_station_K"],
                             mode="lines+markers", name="Observed Station",
                             line=dict(color="#58a6ff", width=1.5),
                             marker=dict(size=4)))
    fig.add_trace(go.Scatter(x=df["time"], y=df["downscaled_station_K"],
                             mode="lines+markers", name="Downscaled",
                             line=dict(color="#f9b872", width=1.5, dash="dash"),
                             marker=dict(size=4)))
    fig.update_layout(
        title="Statistical Downscaling — Station Temperature",
        xaxis_title="Time", yaxis_title="Temperature (K)",
        height=380, **PLOTLY_DARK
    )
    st.plotly_chart(fig, use_container_width=True)

    # Scatter: observed vs downscaled
    fig2 = px.scatter(df, x="observed_station_K", y="downscaled_station_K",
                      title="Observed vs Downscaled (Scatter)",
                      labels={"observed_station_K": "Observed (K)",
                              "downscaled_station_K": "Downscaled (K)"},
                      template="plotly_dark", color_discrete_sequence=["#f9b872"])
    lim = [df["observed_station_K"].min()-1, df["observed_station_K"].max()+1]
    fig2.add_trace(go.Scatter(x=lim, y=lim, mode="lines",
                              name="1:1 Line", line=dict(color="white", dash="dot")))
    fig2.update_layout(height=380, paper_bgcolor="#0d1117", plot_bgcolor="#161b22")
    st.plotly_chart(fig2, use_container_width=True)

    corr = df["observed_station_K"].corr(df["downscaled_station_K"])
    rmse = np.sqrt(((df["observed_station_K"] - df["downscaled_station_K"])**2).mean())
    col1, col2 = st.columns(2)
    col1.metric("Correlation (R)", f"{corr:.4f}")
    col2.metric("RMSE", f"{rmse:.4f} K")


# ── Spatial Maps ──────────────────────────────────────────────────────────────
elif page == "🗺️ Spatial Maps":
    st.title("🗺️ Spatial Climate Maps")

    snap = load_zarr_snapshot()
    if snap is None:
        st.warning("Run the pipeline first."); st.stop()

    variable = st.selectbox("Variable", ["tas", "pr", "sfcWind"])
    data = snap[variable].values
    lat  = snap["lat"].values
    lon  = snap["lon"].values

    cmap_map = {"tas": "RdBu_r", "pr": "Blues", "sfcWind": "YlGnBu"}
    unit_map  = {"tas": "K", "pr": "mm day⁻¹", "sfcWind": "m s⁻¹"}

    fig = go.Figure(go.Heatmap(
        z=data, x=lon, y=lat,
        colorscale=cmap_map[variable],
        colorbar=dict(title=unit_map[variable], tickfont=dict(color="#c9d1d9")),
    ))
    fig.update_layout(
        title=f"Spatial Map — {variable} (first timestep)",
        xaxis_title="Longitude", yaxis_title="Latitude",
        height=460, **PLOTLY_DARK
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Note: Showing first timestep (2000-01). Use the pipeline to generate full timeseries analysis.")


# ── Metadata & FAIR ───────────────────────────────────────────────────────────
elif page == "📋 Metadata & FAIR":
    st.title("📋 Metadata & FAIR Alignment")

    meta = load_metadata()
    if not meta:
        st.warning("Run the pipeline first."); st.stop()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📄 Run Metadata")
        st.markdown(f"**Project:** {meta.get('project', 'N/A')}")
        st.markdown(f"**Author:** {meta.get('author', 'N/A')}")
        st.markdown(f"**Run time:** {meta.get('run_timestamp', 'N/A')}")
        st.markdown(f"**Platform:** {meta.get('platform_style', 'N/A')}")

        st.markdown("### 🏗️ Model Architecture Alignment")
        for m in meta.get("model_architecture_alignment", []):
            st.markdown(f"- {m}")

    with col2:
        st.markdown("### ✅ FAIR Alignment")
        fair = meta.get("fair_alignment", {})
        for k, v in fair.items():
            icon = {"Findable": "🔍", "Accessible": "🔓",
                    "Interoperable": "🔗", "Reusable": "♻️"}.get(k, "✅")
            st.markdown(f"**{icon} {k}:** {v}")

        st.markdown("### 🔬 Technology Stack")
        stack = meta.get("technology_stack", {})
        for k, v in stack.items():
            v_str = ", ".join(v) if isinstance(v, list) else v
            st.markdown(f"**{k.capitalize()}:** {v_str}")

    st.markdown("---")
    st.markdown("### 📦 Pipeline Steps")
    steps = meta.get("pipeline_steps", [])
    for s in steps:
        with st.expander(f"Step {s['step']}: {s['name']}"):
            st.markdown(f"**Script:** `{s['script']}`")
            if "output" in s:
                st.markdown(f"**Output:** `{s['output']}`")
            if "outputs" in s:
                for o in s["outputs"]:
                    st.markdown(f"- `{o}`")


# ── Pipeline Status ────────────────────────────────────────────────────────────
elif page == "🔬 Pipeline Status":
    st.title("🔬 Pipeline Status")
    st.markdown("Check which pipeline outputs have been generated.")

    status = pipeline_status()

    total = len(status)
    done  = sum(status.values())

    st.progress(done / total)
    st.markdown(f"**{done}/{total}** outputs generated")
    st.markdown("")

    for name, exists in status.items():
        icon = "✅" if exists else "⚠️"
        color = "#238636" if exists else "#b08800"
        st.markdown(
            f'<div style="background:#161b22;border:1px solid #21262d;border-radius:6px;'
            f'padding:8px 14px;margin:4px 0;color:{color}">'
            f'{icon} {name}</div>',
            unsafe_allow_html=True
        )

    if done < total:
        st.markdown("---")
        st.markdown("**To generate missing outputs, run:**")
        st.code("python -m src.pipeline", language="bash")
