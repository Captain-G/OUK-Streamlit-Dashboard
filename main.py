import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
import numpy as np

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TechPulse — Technology Intelligence Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Root theme */
:root {
    --bg:       #0A0C12;
    --surface:  #13161F;
    --surface2: #1C2030;
    --border:   #252A3A;
    --accent:   #00F5C3;
    --accent2:  #7B6EF6;
    --accent3:  #F5A623;
    --warn:     #F5536B;
    --text:     #E2E8F4;
    --muted:    #6B7696;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}

/* Headers */
h1 { font-family: 'Space Mono', monospace; color: var(--accent) !important; letter-spacing: -1px; }
h2, h3 { font-family: 'Space Mono', monospace; color: var(--text) !important; }

/* KPI cards */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.kpi-label { font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: var(--muted); margin-bottom: 6px; }
.kpi-value { font-family: 'Space Mono', monospace; font-size: 28px; font-weight: 700; color: var(--text); }
.kpi-delta { font-size: 12px; margin-top: 4px; }
.delta-up   { color: var(--accent); }
.delta-down { color: var(--warn); }

/* Section dividers */
.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: var(--accent);
    margin-bottom: 12px;
    padding-left: 2px;
}

/* Plotly chart bg override */
.js-plotly-plot .plotly .bg { fill: transparent !important; }

/* Table */
.dataframe { background: var(--surface) !important; color: var(--text) !important; }
</style>
""", unsafe_allow_html=True)

# ── Dummy Data Generation ──────────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

SECTORS = ["Artificial Intelligence", "Blockchain", "Cybersecurity", "Cloud Computing",
           "IoT", "Quantum Computing", "AR/VR", "FinTech"]

SECTOR_SHORT = ["AI", "Blockchain", "Cybersec", "Cloud", "IoT", "Quantum", "AR/VR", "FinTech"]

COLORS = ["#00F5C3", "#7B6EF6", "#F5A623", "#3DD9F5", "#F5536B",
          "#A8FF78", "#FFB347", "#FF69B4"]

COMPANIES = {
    "Artificial Intelligence": ["OpenAI", "Anthropic", "DeepMind", "Mistral AI", "Cohere"],
    "Blockchain": ["Ethereum Foundation", "Solana Labs", "Chainlink", "Polygon", "Avalanche"],
    "Cybersecurity": ["CrowdStrike", "Palo Alto", "SentinelOne", "Darktrace", "Wiz"],
    "Cloud Computing": ["AWS", "Azure", "Google Cloud", "Oracle Cloud", "Cloudflare"],
    "IoT": ["Arm Holdings", "Siemens IoT", "PTC Inc", "Bosch IoT", "Sierra Wireless"],
    "Quantum Computing": ["IBM Quantum", "IonQ", "D-Wave", "Rigetti", "QuEra"],
    "AR/VR": ["Meta Reality Labs", "Apple Vision", "Snap Inc", "Magic Leap", "Varjo"],
    "FinTech": ["Stripe", "Plaid", "Chime", "Revolut", "Klarna"],
}

# Funding data per sector (in $B)
funding_2023 = [45.2, 12.4, 18.7, 68.3, 9.1, 3.2, 7.8, 31.5]
funding_2024 = [82.6, 9.8, 22.1, 75.4, 11.3, 5.8, 6.2, 38.9]

# Monthly trend (12 months)
months = [(datetime(2024, 1, 1) + timedelta(days=30*i)).strftime("%b %y") for i in range(12)]

def make_trend(base, volatility=0.08, trend=0.03):
    vals = [base]
    for _ in range(11):
        chg = random.gauss(trend, volatility)
        vals.append(max(0.1, vals[-1] * (1 + chg)))
    return vals

sector_trends = {s: make_trend(funding_2024[i]/12, 0.12, 0.02) for i, s in enumerate(SECTORS)}

# Patent filings dummy
patents = {
    "AI": 18420, "Blockchain": 4230, "Cybersec": 7810, "Cloud": 12500,
    "IoT": 9340, "Quantum": 2180, "AR/VR": 5670, "FinTech": 6890
}

# Job postings
jobs = {
    "AI": 142300, "Cloud": 198400, "Cybersec": 87200, "FinTech": 63100,
    "Blockchain": 21400, "IoT": 34700, "AR/VR": 18900, "Quantum": 8200
}

# Top companies funding rounds ($M)
funding_rounds = []
for sector, companies in COMPANIES.items():
    for c in companies:
        funding_rounds.append({
            "Company": c,
            "Sector": sector,
            "Round": random.choice(["Seed", "Series A", "Series B", "Series C", "Series D", "IPO"]),
            "Amount ($M)": round(random.uniform(20, 800), 1),
            "Valuation ($B)": round(random.uniform(0.5, 120), 2),
            "Growth YoY": f"{random.randint(-12, 85)}%",
        })
df_rounds = pd.DataFrame(funding_rounds)

# Sentiment scores
sentiment_data = {
    "Sector": SECTOR_SHORT,
    "Social Score": [random.randint(60, 95) for _ in range(8)],
    "News Score":   [random.randint(50, 92) for _ in range(8)],
    "Investor Score": [random.randint(55, 98) for _ in range(8)],
}
df_sentiment = pd.DataFrame(sentiment_data)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ TechPulse")
    st.markdown("*Technology Intelligence Dashboard*")
    st.divider()

    selected_sectors = st.multiselect(
        "Filter Sectors",
        SECTORS,
        default=SECTORS[:5],
    )
    year_filter = st.selectbox("Benchmark Year", ["2024 vs 2023", "2023 vs 2022"], index=0)
    metric_focus = st.radio("Primary Metric", ["Funding", "Jobs", "Patents"], index=0)
    st.divider()
    st.caption("Data is illustrative/dummy. Updated: Jun 2025")

# ── Header ─────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("# ⚡ TechPulse")
    st.markdown("**Global Technology Sector Intelligence** · AI · Blockchain · Cloud · Cybersecurity · IoT · Quantum")
with col_h2:
    st.markdown(f"<div style='text-align:right; color: #6B7696; font-size:12px; padding-top:20px;'>Last refresh<br><span style='font-family:Space Mono; color:#00F5C3; font-size:14px'>{datetime.now().strftime('%d %b %Y')}</span></div>", unsafe_allow_html=True)

st.divider()

# ── KPI Row ────────────────────────────────────────────────────────────────────
st.markdown("<div class='section-label'>/ Global Snapshot</div>", unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    ("Total VC Funding", "$360.4B", "+24.1%", True),
    ("Active Startups", "128,400", "+11.8%", True),
    ("Tech Job Postings", "574,200", "+8.3%", True),
    ("M&A Deals (YTD)", "2,847", "-3.2%", False),
    ("Patent Filings", "66,040", "+17.5%", True),
]
for col, (label, val, delta, up) in zip([k1, k2, k3, k4, k5], kpis):
    arrow = "▲" if up else "▼"
    delta_cls = "delta-up" if up else "delta-down"
    col.markdown(f"""
<div class="kpi-card">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{val}</div>
  <div class="kpi-delta {delta_cls}">{arrow} {delta} YoY</div>
</div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 2: Funding Bar + Trend Line ───────────────────────────────────────────
st.markdown("<div class='section-label'>/ Investment Flow</div>", unsafe_allow_html=True)

col_bar, col_trend = st.columns([1, 1], gap="large")

with col_bar:
    # Filter by selected sectors
    mask = [s in selected_sectors for s in SECTORS]
    s_short = [SECTOR_SHORT[i] for i, m in enumerate(mask) if m]
    f23 = [funding_2023[i] for i, m in enumerate(mask) if m]
    f24 = [funding_2024[i] for i, m in enumerate(mask) if m]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="2023", x=s_short, y=f23,
                             marker_color="#252A3A", marker_line_width=0))
    fig_bar.add_trace(go.Bar(name="2024", x=s_short, y=f24,
                             marker_color="#00F5C3", marker_line_width=0))
    fig_bar.update_layout(
        title="VC Funding by Sector ($B)",
        barmode="group",
        plot_bgcolor="#13161F", paper_bgcolor="#13161F",
        font=dict(color="#E2E8F4", family="DM Sans"),
        title_font=dict(family="Space Mono", size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#1C2030", tickfont=dict(size=11)),
        yaxis=dict(gridcolor="#1C2030"),
        margin=dict(t=50, b=20, l=20, r=20),
        height=320,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_trend:
    fig_line = go.Figure()
    for i, s in enumerate(selected_sectors[:4]):
        fig_line.add_trace(go.Scatter(
            x=months, y=sector_trends[s],
            mode="lines", name=SECTOR_SHORT[SECTORS.index(s)],
            line=dict(color=COLORS[i], width=2),
            fill="tozeroy", fillcolor=f"rgba({int(COLORS[i][1:3],16)},{int(COLORS[i][3:5],16)},{int(COLORS[i][5:],16)},0.05)"
        ))
    fig_line.update_layout(
        title="Monthly Investment Trend ($B)",
        plot_bgcolor="#13161F", paper_bgcolor="#13161F",
        font=dict(color="#E2E8F4", family="DM Sans"),
        title_font=dict(family="Space Mono", size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.2),
        xaxis=dict(gridcolor="#1C2030"),
        yaxis=dict(gridcolor="#1C2030"),
        margin=dict(t=50, b=40, l=20, r=20),
        height=320,
    )
    st.plotly_chart(fig_line, use_container_width=True)

# ── Row 3: Donut + Radar + Scatter ────────────────────────────────────────────
st.markdown("<div class='section-label'>/ Sector Intelligence</div>", unsafe_allow_html=True)

col_donut, col_radar, col_scatter = st.columns([1, 1, 1], gap="large")

with col_donut:
    labels = [SECTOR_SHORT[i] for i, s in enumerate(SECTORS) if s in selected_sectors]
    vals   = [funding_2024[i] for i, s in enumerate(SECTORS) if s in selected_sectors]
    fig_donut = go.Figure(go.Pie(
        labels=labels, values=vals,
        hole=0.58,
        marker=dict(colors=COLORS[:len(labels)], line=dict(color="#0A0C12", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#E2E8F4"),
    ))
    fig_donut.update_layout(
        title="Funding Share 2024",
        showlegend=False,
        plot_bgcolor="#13161F", paper_bgcolor="#13161F",
        font=dict(color="#E2E8F4", family="DM Sans"),
        title_font=dict(family="Space Mono", size=13),
        margin=dict(t=50, b=10, l=10, r=10),
        height=320,
        annotations=[dict(text="$360B", x=0.5, y=0.5, font_size=18,
                          font_color="#00F5C3", font_family="Space Mono", showarrow=False)]
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_radar:
    categories = ["Funding", "Jobs", "Patents", "Startups", "M&A Activity"]
    radar_data = {
        "AI":         [98, 92, 95, 96, 88],
        "Cloud":      [85, 98, 78, 82, 90],
        "Cybersec":   [72, 84, 80, 75, 65],
        "Blockchain": [45, 52, 48, 60, 40],
    }
    fig_radar = go.Figure()
    for i, (sector, vals) in enumerate(radar_data.items()):
        fig_radar.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            name=sector,
            line=dict(color=COLORS[i], width=2),
            fill="toself",
            fillcolor=f"rgba({int(COLORS[i][1:3],16)},{int(COLORS[i][3:5],16)},{int(COLORS[i][5:],16)},0.08)",
        ))
    fig_radar.update_layout(
        title="Sector Health Radar",
        polar=dict(
            bgcolor="#13161F",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#252A3A", tickfont=dict(color="#6B7696", size=9)),
            angularaxis=dict(gridcolor="#252A3A", tickfont=dict(color="#E2E8F4", size=10)),
        ),
        plot_bgcolor="#13161F", paper_bgcolor="#13161F",
        font=dict(color="#E2E8F4", family="DM Sans"),
        title_font=dict(family="Space Mono", size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        margin=dict(t=50, b=10, l=10, r=10),
        height=320,
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_scatter:
    scatter_df = df_rounds[df_rounds["Sector"].isin(selected_sectors)].copy()
    fig_scatter = px.scatter(
        scatter_df, x="Amount ($M)", y="Valuation ($B)",
        color="Sector", size="Amount ($M)",
        hover_data=["Company", "Round"],
        color_discrete_sequence=COLORS,
        size_max=20,
    )
    fig_scatter.update_layout(
        title="Funding Round vs Valuation",
        plot_bgcolor="#13161F", paper_bgcolor="#13161F",
        font=dict(color="#E2E8F4", family="DM Sans"),
        title_font=dict(family="Space Mono", size=13),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
        xaxis=dict(gridcolor="#1C2030"),
        yaxis=dict(gridcolor="#1C2030"),
        margin=dict(t=50, b=20, l=20, r=20),
        height=320,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ── Row 4: Job Market + Patents Heatmap ───────────────────────────────────────
st.markdown("<div class='section-label'>/ Talent & Innovation Metrics</div>", unsafe_allow_html=True)

col_jobs, col_heat = st.columns([1, 1], gap="large")

with col_jobs:
    job_sectors = list(jobs.keys())
    job_vals    = list(jobs.values())
    sorted_pairs = sorted(zip(job_vals, job_sectors), reverse=True)
    j_vals, j_secs = zip(*sorted_pairs)

    bar_colors = ["#00F5C3" if v == max(j_vals) else "#7B6EF6" if v > 100000 else "#1C2030" for v in j_vals]
    fig_jobs = go.Figure(go.Bar(
        x=list(j_vals), y=list(j_secs),
        orientation="h",
        marker_color=bar_colors,
        marker_line_width=0,
        text=[f"{v:,.0f}" for v in j_vals],
        textposition="outside",
        textfont=dict(size=10, color="#E2E8F4"),
    ))
    fig_jobs.update_layout(
        title="Tech Job Postings by Sector",
        plot_bgcolor="#13161F", paper_bgcolor="#13161F",
        font=dict(color="#E2E8F4", family="DM Sans"),
        title_font=dict(family="Space Mono", size=13),
        xaxis=dict(gridcolor="#1C2030", tickformat=","),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        margin=dict(t=50, b=20, l=20, r=80),
        height=340,
    )
    st.plotly_chart(fig_jobs, use_container_width=True)

with col_heat:
    # Build heatmap: months vs sectors
    heat_sectors = SECTOR_SHORT[:6]
    heat_matrix  = np.array([
        [random.randint(30, 98) for _ in range(12)]
        for _ in range(6)
    ])
    fig_heat = go.Figure(go.Heatmap(
        z=heat_matrix,
        x=months,
        y=heat_sectors,
        colorscale=[[0, "#13161F"], [0.4, "#7B6EF6"], [0.7, "#00F5C3"], [1, "#F5A623"]],
        showscale=True,
        colorbar=dict(tickfont=dict(color="#E2E8F4"), outlinewidth=0),
    ))
    fig_heat.update_layout(
        title="Investor Sentiment Heatmap (0–100)",
        plot_bgcolor="#13161F", paper_bgcolor="#13161F",
        font=dict(color="#E2E8F4", family="DM Sans"),
        title_font=dict(family="Space Mono", size=13),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10)),
        margin=dict(t=50, b=20, l=20, r=20),
        height=340,
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ── Row 5: Company Funding Table ──────────────────────────────────────────────
st.markdown("<div class='section-label'>/ Recent Funding Rounds</div>", unsafe_allow_html=True)

sector_filter = st.selectbox("Filter by Sector", ["All"] + SECTORS, key="table_filter")

display_df = df_rounds.copy()
if sector_filter != "All":
    display_df = display_df[display_df["Sector"] == sector_filter]

display_df = display_df.sort_values("Amount ($M)", ascending=False).head(20).reset_index(drop=True)

st.dataframe(
    display_df,
    use_container_width=True,
    height=360,
    column_config={
        "Amount ($M)":  st.column_config.ProgressColumn("Amount ($M)",  min_value=0, max_value=800),
        "Valuation ($B)": st.column_config.NumberColumn("Valuation ($B)", format="$%.2fB"),
        "Growth YoY":   st.column_config.TextColumn("Growth YoY"),
    }
)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center; color:#6B7696; font-size:11px; padding: 8px 0;'>
  ⚡ TechPulse Dashboard · All data is illustrative and generated for demonstration purposes
  · Built with Streamlit + Plotly
</div>
""", unsafe_allow_html=True)