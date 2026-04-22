import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Partner Enablement Program Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_FILE = Path(__file__).parent / "partner_enablement_dataset.csv"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    df["Month_dt"] = pd.to_datetime(df["Month"] + "-01")
    return df


raw_df = load_data()

st.markdown(
    """
    <style>
        :root {
            --bg: #ffffff;
            --card: #ffffff;
            --text: #142133;
            --muted: #475569;
            --border: #e6ebf2;
            --blue: #2f6fed;
            --teal: #17867d;
            --gold: #c08a1a;
            --slate: #6b7b8f;
            --green: #1f9d61;
            --amber: #c98a14;
            --red: #cf3f3f;
        }
        .stApp { background: var(--bg); }
        .block-container { padding-top: 2.45rem; padding-bottom: 3rem; max-width: 1540px; }
        .hero { background: var(--card); border: 1px solid var(--border); border-radius: 24px; padding: 1.9rem 2rem 1.55rem 2rem; box-shadow: 0 3px 10px rgba(15,23,42,0.05); margin-bottom: 1.25rem; }
        .hero-title { color: var(--text); font-size: 2.3rem; font-weight: 750; margin-bottom: 0.32rem; letter-spacing: -0.035em; line-height: 1.08; }
        .hero-subtitle { color: var(--muted); font-size: 1.12rem; line-height: 1.62; margin-bottom: 1.05rem; max-width: 1080px; }
        .hero-meta { display: inline-block; color: var(--muted); font-size: 0.98rem; background: #ffffff; border: 1px solid var(--border); border-radius: 999px; padding: 0.46rem 0.78rem; margin-right: 0.52rem; margin-bottom: 0.35rem; }
        .card { background: var(--card); border: 1px solid var(--border); border-radius: 21px; padding: 1.45rem 1.45rem 1.35rem 1.45rem; box-shadow: 0 2px 8px rgba(15,23,42,0.05); height: 100%; }
        .kpi-label { color: var(--muted); font-size: 1.06rem; font-weight: 650; margin-bottom: 0.55rem; }
        .kpi-value { color: var(--text); font-size: 2.6rem; font-weight: 760; letter-spacing: -0.045em; line-height: 1; margin-bottom: 0.55rem; }
        .kpi-delta { color: var(--muted); font-size: 1rem; font-weight: 620; margin-bottom: 0.82rem; line-height: 1.48; }
        .pill { display: inline-block; padding: 0.30rem 0.68rem; border-radius: 999px; font-size: 0.84rem; font-weight: 720; letter-spacing: 0.01em; border: 1px solid transparent; }
        .pill-green { background: rgba(31,157,97,0.10); color: var(--green); border-color: rgba(31,157,97,0.18); }
        .pill-amber { background: rgba(201,138,20,0.10); color: var(--amber); border-color: rgba(201,138,20,0.18); }
        .pill-red { background: rgba(207,63,63,0.10); color: var(--red); border-color: rgba(207,63,63,0.18); }
        .pill-blue { background: rgba(47,111,237,0.08); color: var(--blue); border-color: rgba(47,111,237,0.14); }
        .section-title { color: var(--text); font-size: 1.22rem; font-weight: 740; margin-bottom: 0.55rem; letter-spacing: -0.02em; line-height: 1.25; }
        .section-note { color: var(--muted); font-size: 1rem; line-height: 1.62; margin-top: 0; margin-bottom: 1.05rem; }
        .mini-row { display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding: 0.9rem 0; border-bottom: 1px solid #edf2f7; }
        .mini-row:last-child { border-bottom: none; }
        .mini-label { color: var(--text); font-size: 1.02rem; font-weight: 650; line-height: 1.42; }
        .mini-sub { color: var(--muted); font-size: 0.96rem; line-height: 1.62; margin-top: 0.18rem; }
        .insight { padding: 0.92rem 0 0.78rem 0; border-bottom: 1px solid #edf2f7; }
        .insight:last-child { border-bottom: none; }
        .insight-title { color: var(--text); font-weight: 720; font-size: 1.02rem; margin-bottom: 0.28rem; line-height: 1.44; }
        .insight-body { color: var(--muted); font-size: 0.97rem; line-height: 1.66; }
        div[data-testid="stProgressBar"] > div > div > div > div { background: linear-gradient(90deg,#2f6fed 0%,#17867d 100%); }
        div[data-testid="stExpander"] details summary p { font-size: 1rem; font-weight: 650; }
    </style>
    """,
    unsafe_allow_html=True,
)


def pill_html(text: str, tone: str) -> str:
    tone_class = {"green": "pill-green", "amber": "pill-amber", "red": "pill-red", "blue": "pill-blue"}.get(tone, "pill-blue")
    return f'<span class="pill {tone_class}">{text}</span>'


def status_tone(status: str) -> str:
    return {"On Track": "green", "Watch": "amber", "At Risk": "red", "Complete": "blue"}.get(status, "blue")


def base_chart_layout(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        title_text="",
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        margin=dict(l=18, r=18, t=28, b=14),
        font=dict(color="#142133", family="Arial", size=14),
        hoverlabel=dict(font_size=13),
        showlegend=False,
    )
    fig.update_xaxes(title_text="", showgrid=True, gridcolor="#edf2f7", gridwidth=1, zeroline=False, showline=False, tickfont=dict(size=12, color="#334155"), title_font=dict(size=13, color="#142133"))
    fig.update_yaxes(title_text="", showgrid=True, gridcolor="#edf2f7", gridwidth=1, zeroline=False, showline=False, tickfont=dict(size=12, color="#334155"), title_font=dict(size=13, color="#142133"))
    return fig


def chart_with_legend(fig: go.Figure) -> go.Figure:
    fig = base_chart_layout(fig)
    fig.update_layout(showlegend=True, legend=dict(title_text="", orientation="h", yanchor="bottom", y=1.05, xanchor="left", x=0, font=dict(size=12, color="#334155"), itemsizing="constant"))
    return fig


def region_status(value: float, metric: str) -> str:
    thresholds = {"engagement": (74, 66), "completion": (68, 60), "certification": (56, 48), "csat": (4.25, 4.10)}
    green, amber = thresholds[metric]
    if value >= green: return "On Track"
    if value >= amber: return "Watch"
    return "At Risk"


def make_sparkline(series: pd.Series, color: str) -> go.Figure:
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(series))), y=series.tolist(),
        mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=f"rgba({r},{g},{b},0.10)",
        hoverinfo="skip",
    ))
    fig.update_layout(
        title_text="",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        height=52,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def curriculum_bar_color(v: int) -> str:
    if v >= 78: return "#1f9d61"
    if v >= 70: return "#c98a14"
    return "#cf3f3f"


# ── Data prep ────────────────────────────────────────────────────────────────
monthly = raw_df.groupby("Month_dt", as_index=False).agg({
    "Engagement Rate (%)": "mean", "Completion Rate (%)": "mean",
    "Certification Rate (%)": "mean", "CSAT (1-5)": "mean",
    "Active Learners": "sum", "Courses Launched": "sum",
})

curriculum_raw = [
    ("IBX Essentials", 84), ("Interconnection Overview", 79), ("Power Concepts", 77),
    ("Interconnection 1", 73), ("Data Center Design", 71), ("Interconnection 2", 66),
]
curriculum_df = pd.DataFrame({
    "Curriculum": [r[0] for r in curriculum_raw],
    "Completion":  [r[1] for r in curriculum_raw],
    "BarColor":    [curriculum_bar_color(r[1]) for r in curriculum_raw],
}).sort_values("Completion", ascending=True)

segment_df = raw_df.groupby("Partner Type", as_index=False)["Active Learners"].sum().rename(columns={"Active Learners": "Learners"})

pipeline_df = pd.DataFrame({
    "Stage": ["Intake", "Scoping", "In Development", "Review", "Ready to Launch"],
    "Projects": [11, 7, 6, 4, 8],
})

latest   = monthly.iloc[-1]
previous = monthly.iloc[-2]

kpi_spark_col = {
    "Partner Engagement Rate": "#2f6fed",
    "Course Completion Rate":  "#17867d",
    "Certification Rate":      "#c08a1a",
    "CSAT":                    "#6b7b8f",
}
kpi_spark_series = {
    "Partner Engagement Rate": monthly["Engagement Rate (%)"],
    "Course Completion Rate":  monthly["Completion Rate (%)"],
    "Certification Rate":      monthly["Certification Rate (%)"],
    "CSAT":                    monthly["CSAT (1-5)"],
}

kpis = {
    "Partner Engagement Rate": {
        "value": round(float(latest["Engagement Rate (%)"])),
        "delta": f"{latest['Engagement Rate (%)'] - previous['Engagement Rate (%)']:+.1f} pts vs prior month",
        "suffix": "%", "status": region_status(float(latest["Engagement Rate (%)"]), "engagement"),
    },
    "Course Completion Rate": {
        "value": round(float(latest["Completion Rate (%)"])),
        "delta": f"{latest['Completion Rate (%)'] - previous['Completion Rate (%)']:+.1f} pts vs prior month",
        "suffix": "%", "status": region_status(float(latest["Completion Rate (%)"]), "completion"),
    },
    "Certification Rate": {
        "value": round(float(latest["Certification Rate (%)"])),
        "delta": f"{latest['Certification Rate (%)'] - previous['Certification Rate (%)']:+.1f} pts vs prior month",
        "suffix": "%", "status": region_status(float(latest["Certification Rate (%)"]), "certification"),
    },
    "CSAT": {
        "value": round(float(latest["CSAT (1-5)"]), 2),
        "delta": f"{latest['CSAT (1-5)'] - previous['CSAT (1-5)']:+.2f} vs prior month",
        "suffix": "/5", "status": region_status(float(latest["CSAT (1-5)"]), "csat"),
    },
}
for meta in kpis.values():
    meta["tone"] = status_tone(meta["status"])

annual_goal   = 80
cert_goal     = 60
current_goal  = int(round(monthly["Engagement Rate (%)"].iloc[-1]))
current_cert  = int(round(monthly["Certification Rate (%)"].iloc[-1]))
program_launch = int(round(min(100, raw_df["Courses Launched"].sum() / 90 * 100)))

regional = raw_df[raw_df["Month_dt"] == raw_df["Month_dt"].max()].groupby("Region", as_index=False).agg({
    "Engagement Rate (%)": "mean", "Completion Rate (%)": "mean",
    "Certification Rate (%)": "mean", "CSAT (1-5)": "mean",
})

status_rows = []
for _, row in regional.iterrows():
    status = region_status(float(row["Completion Rate (%)"]), "completion")
    progress = int(round((row["Engagement Rate (%)"] * 0.4) + (row["Completion Rate (%)"] * 0.35) + (row["Certification Rate (%)"] * 0.25)))
    status_rows.append({
        "Initiative": f"{row['Region']} Regional Rollout",
        "Owner": "Enablement Ops" if row["Region"] == "AMER" else ("Regional PMO" if row["Region"] == "EMEA" else "Field Enablement"),
        "Status": status, "Progress": progress,
    })

status_df = pd.concat([
    pd.DataFrame(status_rows),
    pd.DataFrame([
        {"Initiative": "Assessment Standardization", "Owner": "Instructional Design", "Status": "On Track", "Progress": 78},
        {"Initiative": "Survey Process Adoption",    "Owner": "Operations",            "Status": "Watch",    "Progress": 67},
    ]),
], ignore_index=True)

insights = [
    ("Mid-year momentum is real", "Engagement and completion climbed steadily from Q1 through Q3, showing that the program moved beyond launch friction into sustained adoption."),
    ("AMER leads, while APAC closed ground", "AMER established the strongest early performance, but APAC accelerated meaningfully in the second half, narrowing the gap by year end."),
    ("August exposed a rollout strain point", "A visible August dip in completion and CSAT suggests temporary delivery friction, likely tied to regional launch readiness or content load."),
]
risks = [
    ("EMEA completion remains softer", "EMEA improved through the year but still trails AMER on completion, indicating a need for tighter localization and reinforcement."),
    ("Certification conversion lags engagement", "Partners are entering learning paths at healthy rates, but certification still converts more slowly than completions."),
]
actions = [
    ("Reinforce advanced learning paths", "Add milestone nudges and scenario-based practice to help late-stage learners convert from completion into certification."),
    ("Stabilize regional launch governance", "Tighten intake quality and readiness reviews before high-visibility regional pushes to reduce the risk of repeat dips."),
]
one_line_story = (
    "After a slower Q1 launch, global partner engagement and certification momentum strengthened through Q3, "
    "with AMER leading early and APAC gaining late before the program stabilized in Q4."
)

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
    <div class="hero">
        <div class="hero-title">Partner Enablement Program Dashboard</div>
        <div class="hero-subtitle">Live executive view of engagement, completion, certification, and delivery health across active partner enablement programs.</div>
        <span class="hero-meta">Updated {datetime.now().strftime('%b %d, %Y · %I:%M %p')}</span>
        <span class="hero-meta">Audience: Leadership</span>
        <span class="hero-meta">Regions: AMER · EMEA · APAC</span>
    </div>
""", unsafe_allow_html=True)

with st.expander("Dataset story", expanded=False):
    st.write(one_line_story)
    st.dataframe(raw_df.head(12), use_container_width=True, hide_index=True)

# ── Date range filter ─────────────────────────────────────────────────────────
all_months   = sorted(monthly["Month_dt"].unique())
month_labels = [pd.Timestamp(m).strftime("%b %Y") for m in all_months]

filter_col, _ = st.columns([2, 3])
with filter_col:
    date_range = st.select_slider(
        "Filter date range",
        options=month_labels,
        value=(month_labels[0], month_labels[-1]),
        label_visibility="collapsed",
    )

start_month = pd.Timestamp(datetime.strptime(date_range[0], "%b %Y"))
end_month   = pd.Timestamp(datetime.strptime(date_range[1], "%b %Y"))
monthly_filtered = monthly[(monthly["Month_dt"] >= start_month) & (monthly["Month_dt"] <= end_month)].copy()

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# ── KPI cards + sparklines ────────────────────────────────────────────────────
kpi_cols = st.columns(4, gap="large")
for col, (label, meta) in zip(kpi_cols, kpis.items()):
    with col:
        placeholder = st.empty()
        steps = 18
        final_value = meta["value"]
        for i in range(1, steps + 1):
            current = (round(final_value * i / steps, 2) if isinstance(final_value, float) else int(round(final_value * i / steps)))
            display_val = f"{current:.2f}" if isinstance(final_value, float) else f"{current}"
            placeholder.markdown(f"""
                <div class="card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{display_val}{meta['suffix']}</div>
                    <div class="kpi-delta">{meta['delta']}</div>
                    {pill_html(meta['status'], meta['tone'])}
                </div>
            """, unsafe_allow_html=True)
            time.sleep(0.01)
        spark_fig = make_sparkline(kpi_spark_series[label], kpi_spark_col[label])
        st.plotly_chart(spark_fig, use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='height: 0.95rem;'></div>", unsafe_allow_html=True)

# ── Trend line + curriculum bars ─────────────────────────────────────────────
left, right = st.columns([1.45, 1], gap="large")

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Performance Trend (Monthly)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Engagement, completion, and certification rates across the selected date range.</div>', unsafe_allow_html=True)
    trend_df = monthly_filtered.melt(
        id_vars="Month_dt",
        value_vars=["Engagement Rate (%)", "Completion Rate (%)", "Certification Rate (%)"],
        var_name="Metric", value_name="Rate",
    )
    trend_df["Metric"] = trend_df["Metric"].map({
        "Engagement Rate (%)":    "Engagement",
        "Completion Rate (%)":    "Completion",
        "Certification Rate (%)": "Certification",
    })
    fig_line = px.line(trend_df, x="Month_dt", y="Rate", color="Metric", markers=True,
        color_discrete_map={"Engagement": "#2f6fed", "Completion": "#17867d", "Certification": "#c08a1a"})
    fig_line.update_layout(title_text="")
    fig_line.update_traces(line=dict(width=3), marker=dict(size=8, line=dict(width=1.8, color="#FFFFFF")),
        hovertemplate="%{x|%b %Y}<br>%{fullData.name}: %{y:.0f}%<extra></extra>")
    fig_line.update_yaxes(range=[20, 90], ticksuffix="%", tickmode="linear", dtick=10)
    fig_line.update_xaxes(tickformat="%b", ticklabelmode="period")
    st.plotly_chart(chart_with_legend(fig_line), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Curriculum Completion Performance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Color shows performance tier: '
        '<span style="color:#1f9d61;font-weight:700">■ Strong (&ge;78%)</span>&nbsp; '
        '<span style="color:#c98a14;font-weight:700">■ Watch (70–77%)</span>&nbsp; '
        '<span style="color:#cf3f3f;font-weight:700">■ At Risk (&lt;70%)</span></div>',
        unsafe_allow_html=True,
    )
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=curriculum_df["Completion"], y=curriculum_df["Curriculum"],
        orientation="h",
        text=[f"{v}%" for v in curriculum_df["Completion"]],
        textposition="outside", cliponaxis=False,
        marker=dict(color=curriculum_df["BarColor"]),
        hovertemplate="%{y}: %{x}%<extra></extra>",
        showlegend=False, name="",
    ))
    fig_bar.update_layout(title_text="")
    fig_bar.update_xaxes(range=[0, 100], ticksuffix="%", tickmode="linear", dtick=20)
    fig_bar.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(base_chart_layout(fig_bar), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height: 0.95rem;'></div>", unsafe_allow_html=True)

# ── Donut + pipeline + goal progress ─────────────────────────────────────────
col1, col2, col3 = st.columns([0.95, 1.05, 1.0], gap="large")

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Partner Segment Distribution</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Current learner mix across the partner audience.</div>', unsafe_allow_html=True)
    fig_donut = px.pie(segment_df, values="Learners", names="Partner Type", hole=0.68, color="Partner Type",
        color_discrete_map={"Reseller": "#2f6fed", "Distributor": "#17867d", "Strategic": "#c08a1a"})
    fig_donut.update_layout(title_text="", showlegend=False)
    fig_donut.update_traces(textinfo="percent", textfont=dict(size=13, color="#142133"),
        marker=dict(line=dict(color="#FFFFFF", width=2.2)),
        hovertemplate="%{label}: %{value:,} learners (%{percent})<extra></extra>",
        sort=False, showlegend=False, name="")
    fig_donut.update_layout(margin=dict(l=10, r=10, t=12, b=10),
        annotations=[dict(text="Partner<br>Mix", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="#334155"))])
    st.plotly_chart(base_chart_layout(fig_donut), use_container_width=True)
    st.markdown("<div class='mini-sub'>Reseller, Distributor, and Strategic partner segments are balanced enough to support broad rollout coverage without overconcentration.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Delivery Pipeline by Stage</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Current work distribution across the development lifecycle.</div>', unsafe_allow_html=True)
    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(
        x=pipeline_df["Stage"], y=pipeline_df["Projects"],
        fill="tozeroy", mode="lines+markers",
        line=dict(color="#17867d", width=3),
        marker=dict(size=8, color="#17867d", line=dict(color="#FFFFFF", width=1.8)),
        fillcolor="rgba(23,134,125,0.14)",
        hovertemplate="%{x}: %{y} projects<extra></extra>",
        showlegend=False, name="",
    ))
    fig_area.update_layout(title_text="")
    fig_area.update_yaxes(rangemode="tozero", dtick=2)
    st.plotly_chart(base_chart_layout(fig_area), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Goal Progress</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Annual engagement, certification, and launch completion targets.</div>', unsafe_allow_html=True)

    # Engagement goal
    st.markdown('<div class="mini-label">Annual Partner Engagement Goal</div>', unsafe_allow_html=True)
    st.progress(min(current_goal / annual_goal, 1.0))
    st.markdown(f"<div class='mini-sub'>{current_goal}% achieved against an {annual_goal}% year-end target.</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)

    # Certification goal (new)
    cert_tone = "green" if current_cert >= cert_goal else ("amber" if current_cert >= cert_goal * 0.85 else "red")
    st.markdown('<div class="mini-label">Certification Rate Goal</div>', unsafe_allow_html=True)
    st.progress(min(current_cert / cert_goal, 1.0))
    st.markdown(
        f"<div class='mini-sub'>{current_cert}% achieved against a {cert_goal}% year-end target. "
        f"{pill_html(region_status(current_cert, 'certification'), cert_tone)}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)

    # Launch completion
    st.markdown('<div class="mini-label">Program Launch Completion</div>', unsafe_allow_html=True)
    st.progress(program_launch / 100)
    st.markdown(f"<div class='mini-sub'>{program_launch}% of planned learning assets are launched or launch-ready.</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)

    st.markdown(pill_html("Leadership View", "blue"), unsafe_allow_html=True)
    st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mini-sub'>The data reflects a healthy year-over-year build, with a temporary August disruption that leadership should treat as a governance signal rather than a structural performance problem.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height: 0.95rem;'></div>", unsafe_allow_html=True)

# ── Bottom row ────────────────────────────────────────────────────────────────
left_bottom, middle_bottom, right_bottom = st.columns([1.1, 0.9, 1.0], gap="large")

with left_bottom:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Initiative Status</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Current delivery health for strategic enablement workstreams.</div>', unsafe_allow_html=True)
    for _, row in status_df.iterrows():
        st.markdown(f"""
            <div class="mini-row">
                <div>
                    <div class="mini-label">{row['Initiative']}</div>
                    <div class="mini-sub">Owner: {row['Owner']} · Progress: {row['Progress']}%</div>
                </div>
                <div>{pill_html(row['Status'], status_tone(row['Status']))}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with middle_bottom:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Executive Insights</div>', unsafe_allow_html=True)
    for title, body in insights:
        st.markdown(f"""
            <div class="insight">
                <div class="insight-title">{title}</div>
                <div class="insight-body">{body}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right_bottom:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Risks & Recommended Actions</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Condensed action layer for leadership review.</div>', unsafe_allow_html=True)
    st.markdown(pill_html("Risks", "amber"), unsafe_allow_html=True)
    for title, body in risks:
        st.markdown(f"""
            <div class="insight">
                <div class="insight-title">{title}</div>
                <div class="insight-body">{body}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)
    st.markdown(pill_html("Recommended Actions", "blue"), unsafe_allow_html=True)
    for title, body in actions:
        st.markdown(f"""
            <div class="insight">
                <div class="insight-title">{title}</div>
                <div class="insight-body">{body}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height: 0.85rem;'></div>", unsafe_allow_html=True)
st.caption("Synthetic dataset wired into the dashboard from partner_enablement_dataset.csv.This is dummy data for AI April, for Michael Bourgeois. App version 5.2. ")
