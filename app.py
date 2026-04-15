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

# ---------- Styling ----------
st.markdown(
    """
    <style>
        :root {
            --bg: #ffffff;
            --card: #ffffff;
            --text: #18212f;
            --muted: #5f6b7a;
            --border: #e6ebf2;
            --blue: #2f6fed;
            --blue-soft: #5b8eff;
            --blue-light: #9bb9ff;
            --green: #1f9d61;
            --amber: #c98a14;
            --red: #cf3f3f;
        }

        .stApp {
            background: var(--bg);
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1450px;
        }

        .hero {
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 1.3rem 1.4rem 1.15rem 1.4rem;
            box-shadow: 0 8px 24px rgba(16, 24, 40, 0.04);
            margin-bottom: 1rem;
        }

        .hero-title {
            color: var(--text);
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
            letter-spacing: -0.02em;
        }

        .hero-subtitle {
            color: var(--muted);
            font-size: 0.98rem;
            margin-bottom: 0.8rem;
        }

        .hero-meta {
            display: inline-block;
            color: var(--muted);
            font-size: 0.85rem;
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.35rem 0.65rem;
            margin-right: 0.45rem;
        }

        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem 1.05rem 0.95rem 1.05rem;
            box-shadow: 0 8px 20px rgba(16, 24, 40, 0.035);
            height: 100%;
        }

        .kpi-label {
            color: var(--muted);
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 0.35rem;
        }

        .kpi-value {
            color: var(--text);
            font-size: 2rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            line-height: 1;
            margin-bottom: 0.4rem;
        }

        .kpi-delta {
            font-size: 0.88rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .pill {
            display: inline-block;
            padding: 0.25rem 0.55rem;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.01em;
            border: 1px solid transparent;
        }

        .pill-green { background: rgba(31, 157, 97, 0.10); color: var(--green); border-color: rgba(31, 157, 97, 0.18); }
        .pill-amber { background: rgba(201, 138, 20, 0.10); color: var(--amber); border-color: rgba(201, 138, 20, 0.18); }
        .pill-red { background: rgba(207, 63, 63, 0.10); color: var(--red); border-color: rgba(207, 63, 63, 0.18); }
        .pill-blue { background: rgba(47, 111, 237, 0.08); color: var(--blue); border-color: rgba(47, 111, 237, 0.14); }

        .section-title {
            color: var(--text);
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
            letter-spacing: -0.01em;
        }

        .section-note {
            color: var(--muted);
            font-size: 0.86rem;
            margin-top: -0.2rem;
            margin-bottom: 0.6rem;
        }

        .mini-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.55rem 0;
            border-bottom: 1px solid #eef2f7;
        }

        .mini-row:last-child {
            border-bottom: none;
        }

        .mini-label {
            color: var(--text);
            font-size: 0.9rem;
            font-weight: 600;
        }

        .mini-sub {
            color: var(--muted);
            font-size: 0.8rem;
            margin-top: 0.15rem;
        }

        .insight {
            padding: 0.7rem 0 0.55rem 0;
            border-bottom: 1px solid #eef2f7;
        }

        .insight:last-child { border-bottom: none; }

        .insight-title {
            color: var(--text);
            font-weight: 700;
            font-size: 0.9rem;
            margin-bottom: 0.2rem;
        }

        .insight-body {
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.45;
        }

        div[data-testid="stProgressBar"] > div > div > div > div {
            background: linear-gradient(90deg, #2f6fed 0%, #5b8eff 100%);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Helpers ----------
def pill_html(text: str, tone: str) -> str:
    tone_class = {
        "green": "pill-green",
        "amber": "pill-amber",
        "red": "pill-red",
        "blue": "pill-blue",
    }.get(tone, "pill-blue")
    return f'<span class="pill {tone_class}">{text}</span>'


def status_tone(status: str) -> str:
    return {
        "On Track": "green",
        "Watch": "amber",
        "At Risk": "red",
        "Complete": "blue",
    }.get(status, "blue")


def chart_layout(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(color="#18212f", family="Arial"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def region_status(value: float, metric: str) -> str:
    thresholds = {
        "engagement": (74, 66),
        "completion": (68, 60),
        "certification": (56, 48),
        "csat": (4.25, 4.10),
    }
    green, amber = thresholds[metric]
    if value >= green:
        return "On Track"
    if value >= amber:
        return "Watch"
    return "At Risk"

# ---------- Derived Data ----------
monthly = raw_df.groupby("Month_dt", as_index=False).agg({
    "Engagement Rate (%)": "mean",
    "Completion Rate (%)": "mean",
    "Certification Rate (%)": "mean",
    "CSAT (1-5)": "mean",
    "Active Learners": "sum",
    "Courses Launched": "sum",
})

curriculum_df = pd.DataFrame(
    {
        "Curriculum": [
            "IBX Essentials",
            "Interconnection Overview",
            "Interconnection 1",
            "Interconnection 2",
            "Power Concepts",
            "Data Center Design",
        ],
        "Completion": [84, 79, 73, 66, 77, 71],
    }
).sort_values("Completion", ascending=True)

segment_df = raw_df.groupby("Partner Type", as_index=False)["Active Learners"].sum().rename(columns={"Active Learners": "Learners"})

pipeline_df = pd.DataFrame(
    {
        "Stage": ["Intake", "Scoping", "In Development", "Review", "Ready to Launch"],
        "Projects": [11, 7, 6, 4, 8],
    }
)

latest = monthly.iloc[-1]
previous = monthly.iloc[-2]

kpis = {
    "Partner Engagement Rate": {
        "value": round(float(latest["Engagement Rate (%)"])),
        "delta": f"{latest['Engagement Rate (%)'] - previous['Engagement Rate (%)']:+.1f} pts vs prior month",
        "suffix": "%",
        "status": region_status(float(latest["Engagement Rate (%)"]), "engagement"),
    },
    "Course Completion Rate": {
        "value": round(float(latest["Completion Rate (%)"])),
        "delta": f"{latest['Completion Rate (%)'] - previous['Completion Rate (%)']:+.1f} pts vs prior month",
        "suffix": "%",
        "status": region_status(float(latest["Completion Rate (%)"]), "completion"),
    },
    "Certification Rate": {
        "value": round(float(latest["Certification Rate (%)"])),
        "delta": f"{latest['Certification Rate (%)'] - previous['Certification Rate (%)']:+.1f} pts vs prior month",
        "suffix": "%",
        "status": region_status(float(latest["Certification Rate (%)"]), "certification"),
    },
    "CSAT": {
        "value": round(float(latest["CSAT (1-5)"]), 2),
        "delta": f"{latest['CSAT (1-5)'] - previous['CSAT (1-5)']:+.2f} vs prior month",
        "suffix": "/5",
        "status": region_status(float(latest["CSAT (1-5)"]), "csat"),
    },
}
for meta in kpis.values():
    meta["tone"] = status_tone(meta["status"])

annual_goal = 80
current_goal = int(round(monthly["Engagement Rate (%)"].iloc[-1]))
program_launch = int(round(min(100, raw_df["Courses Launched"].sum() / 90 * 100)))

regional = raw_df[raw_df["Month_dt"] == raw_df["Month_dt"].max()].groupby("Region", as_index=False).agg({
    "Engagement Rate (%)": "mean",
    "Completion Rate (%)": "mean",
    "Certification Rate (%)": "mean",
    "CSAT (1-5)": "mean",
})
status_df = []
for _, row in regional.iterrows():
    status = region_status(float(row["Completion Rate (%)"]), "completion")
    progress = int(round((row["Engagement Rate (%)"] * 0.4) + (row["Completion Rate (%)"] * 0.35) + (row["Certification Rate (%)"] * 0.25)))
    status_df.append({
        "Initiative": f"{row['Region']} Regional Rollout",
        "Owner": "Enablement Ops" if row["Region"] == "AMER" else ("Regional PMO" if row["Region"] == "EMEA" else "Field Enablement"),
        "Status": status,
        "Progress": progress,
    })
status_df = pd.DataFrame(status_df)
status_df = pd.concat([
    status_df,
    pd.DataFrame([
        {"Initiative": "Assessment Standardization", "Owner": "Instructional Design", "Status": "On Track", "Progress": 78},
        {"Initiative": "Survey Process Adoption", "Owner": "Operations", "Status": "Watch", "Progress": 67},
    ])
], ignore_index=True)

insights = [
    (
        "Mid-year momentum is real",
        "Engagement and completion climbed steadily from Q1 through Q3, showing that the program moved beyond launch friction into sustained adoption."
    ),
    (
        "AMER leads, while APAC closed ground",
        "AMER established the strongest early performance, but APAC accelerated meaningfully in the second half, narrowing the gap by year end."
    ),
    (
        "August exposed a rollout strain point",
        "A visible August dip in completion and CSAT suggests temporary delivery friction, likely tied to regional launch readiness or content load."
    ),
]

risks = [
    (
        "EMEA completion remains softer",
        "EMEA improved through the year but still trails AMER on completion, indicating a need for tighter localization and reinforcement."
    ),
    (
        "Certification conversion lags engagement",
        "Partners are entering learning paths at healthy rates, but certification still converts more slowly than completions."
    ),
]

actions = [
    (
        "Reinforce advanced learning paths",
        "Add milestone nudges and scenario-based practice to help late-stage learners convert from completion into certification."
    ),
    (
        "Stabilize regional launch governance",
        "Tighten intake quality and readiness reviews before high-visibility regional pushes to reduce the risk of repeat dips."
    ),
]

one_line_story = "After a slower Q1 launch, global partner engagement and certification momentum strengthened through Q3, with AMER leading early and APAC gaining late before the program stabilized in Q4."

# ---------- Header ----------
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-title">Partner Enablement Program Dashboard</div>
        <div class="hero-subtitle">Live executive view of engagement, completion, certification, and delivery health across active partner enablement programs.</div>
        <span class="hero-meta">Updated {datetime.now().strftime('%b %d, %Y · %I:%M %p')}</span>
        <span class="hero-meta">Audience: Leadership</span>
        <span class="hero-meta">Regions: AMER · EMEA · APAC</span>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Dataset story", expanded=False):
    st.write(one_line_story)
    st.dataframe(raw_df.head(12), use_container_width=True, hide_index=True)

# ---------- KPI Cards ----------
kpi_cols = st.columns(4)
for col, (label, meta) in zip(kpi_cols, kpis.items()):
    with col:
        placeholder = st.empty()
        steps = 18
        final_value = meta["value"]
        for i in range(1, steps + 1):
            current = round(final_value * i / steps, 2) if isinstance(final_value, float) else int(round(final_value * i / steps))
            display_val = f"{current:.2f}" if isinstance(final_value, float) else f"{current}"
            placeholder.markdown(
                f"""
                <div class="card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{display_val}{meta['suffix']}</div>
                    <div class="kpi-delta" style="color:#2f6fed;">{meta['delta']}</div>
                    {pill_html(meta['status'], meta['tone'])}
                </div>
                """,
                unsafe_allow_html=True,
            )
            time.sleep(0.012)

st.markdown("<div style='height: 0.55rem;'></div>", unsafe_allow_html=True)

# ---------- Charts Row 1 ----------
left, right = st.columns([1.45, 1], gap="large")

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Monthly Performance Trend</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Engagement, completion, and certification rates across the 2025 program year.</div>', unsafe_allow_html=True)
    long_trend = monthly.melt(id_vars="Month_dt", value_vars=["Engagement Rate (%)", "Completion Rate (%)", "Certification Rate (%)"], var_name="Metric", value_name="Rate")
    fig_line = px.line(
        long_trend,
        x="Month_dt",
        y="Rate",
        color="Metric",
        markers=True,
        color_discrete_map={
            "Engagement Rate (%)": "#2f6fed",
            "Completion Rate (%)": "#5b8eff",
            "Certification Rate (%)": "#9bb9ff",
        },
    )
    fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
    fig_line.update_yaxes(range=[20, 90], gridcolor="#e9eef6", ticksuffix="%")
    fig_line.update_xaxes(gridcolor="#f1f4f9", tickformat="%b")
    st.plotly_chart(chart_layout(fig_line), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Completion by Curriculum</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Representative curriculum view for leadership discussion.</div>', unsafe_allow_html=True)
    fig_bar = px.bar(curriculum_df, x="Completion", y="Curriculum", orientation="h", text="Completion")
    fig_bar.update_traces(marker_color="#2f6fed", texttemplate="%{text}%", textposition="outside")
    fig_bar.update_xaxes(range=[0, 100], gridcolor="#e9eef6", ticksuffix="%")
    fig_bar.update_yaxes(gridcolor="#ffffff")
    st.plotly_chart(chart_layout(fig_bar), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height: 0.55rem;'></div>", unsafe_allow_html=True)

# ---------- Charts Row 2 ----------
col1, col2, col3 = st.columns([0.95, 1.05, 1.0], gap="large")

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Partner Segment Distribution</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Current learner mix across the partner audience.</div>', unsafe_allow_html=True)
    fig_donut = px.pie(
        segment_df,
        values="Learners",
        names="Partner Type",
        hole=0.66,
        color_discrete_sequence=["#2f6fed", "#5b8eff", "#9bb9ff"],
    )
    fig_donut.update_traces(textinfo="percent+label")
    st.plotly_chart(chart_layout(fig_donut), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Delivery Pipeline by Stage</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Current work distribution across the development lifecycle.</div>', unsafe_allow_html=True)
    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(x=pipeline_df["Stage"], y=pipeline_df["Projects"], fill="tozeroy", mode="lines+markers", line=dict(color="#2f6fed", width=3), marker=dict(size=8), name="Projects"))
    fig_area.update_yaxes(gridcolor="#e9eef6", rangemode="tozero")
    fig_area.update_xaxes(gridcolor="#f1f4f9")
    st.plotly_chart(chart_layout(fig_area), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Goal Progress</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-note">Annual engagement goal and overall launch completion.</div>', unsafe_allow_html=True)
    st.markdown('<div class="mini-label">Annual Partner Engagement Goal</div>', unsafe_allow_html=True)
    st.progress(current_goal / annual_goal)
    st.markdown(f"<div class='mini-sub'>{current_goal}% achieved against an {annual_goal}% year-end target.</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="mini-label">Program Launch Completion</div>', unsafe_allow_html=True)
    st.progress(program_launch / 100)
    st.markdown(f"<div class='mini-sub'>{program_launch}% of planned learning assets are launched or launch-ready.</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown(pill_html("Leadership View", "blue"), unsafe_allow_html=True)
    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='mini-sub'>The data reflects a healthy year-over-year build, with a temporary August disruption that leadership should treat as a governance signal rather than a structural performance problem.</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height: 0.55rem;'></div>", unsafe_allow_html=True)

# ---------- Bottom Row ----------
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
    st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown("<div style='height:0.7rem;'></div>", unsafe_allow_html=True)
    st.markdown(pill_html("Recommended Actions", "blue"), unsafe_allow_html=True)
    for title, body in actions:
        st.markdown(f"""
            <div class="insight">
                <div class="insight-title">{title}</div>
                <div class="insight-body">{body}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown("<div style='height: 0.55rem;'></div>", unsafe_allow_html=True)
st.caption("Synthetic dataset wired into the dashboard from partner_enablement_dataset.csv. Replace the CSV later if you want to simulate a different business story.")
