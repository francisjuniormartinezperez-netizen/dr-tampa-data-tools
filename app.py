import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from PIL import Image
import numpy as np
import re

st.set_page_config(
    page_title="DR Scouting Data Tools",
    layout="wide"
)

NAVY = "#021426"
PANEL = "#061F35"
BORDER = "#164E73"
TEXT = "#EAF4FF"
MUTED = "#A9BDD0"
BLUE = "#8FD3FF"
WHITE = "#FFFFFF"

BASE_DIR = Path(".")
ASSETS_DIR = BASE_DIR / "assets"
VIDEOS_DIR = BASE_DIR / "Videos"

ASSETS_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

LOGO_PATH = ASSETS_DIR / "Tampa_logo.png"

pitch_colors = {
    "Fastball": "#FF3333",
    "FourSeamFastBall": "#FF3333",
    "4-Seam Fastball": "#FF3333",
    "Sinker": "#FF8C00",
    "Slider": "#2DA8FF",
    "Sweeper": "#31C4FF",
    "Curveball": "#9B59D0",
    "ChangeUp": "#53C653",
    "Changeup": "#53C653",
    "Splitter": "#18D0D0",
    "Cutter": "#FF66C4",
    "Other": "#A0A0A0"
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.stApp {{
    background:
        radial-gradient(circle at top center, rgba(12,67,111,0.55) 0%, rgba(3,27,52,0.88) 32%, rgba(2,15,29,1) 78%),
        linear-gradient(180deg, #031B34, {NAVY});
    color: {TEXT};
}}

.main .block-container {{
    padding-top: 0.6rem;
    padding-left: 1.4rem;
    padding-right: 1.4rem;
    max-width: 1700px;
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #03182B, #021426);
    border-right: 1px solid {BORDER};
}}

section[data-testid="stSidebar"] * {{
    color: {TEXT};
}}

hr {{
    border: none;
    border-top: 1px solid rgba(143,211,255,0.25);
    margin-top: 10px;
    margin-bottom: 16px;
}}

.header-title {{
    text-align: center;
    color: {BLUE};
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 7px;
    margin-top: -4px;
}}

.header-subtitle {{
    text-align: center;
    color: {MUTED};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 4px;
    margin-top: 7px;
    margin-bottom: 14px;
}}

.section-title {{
    color: {BLUE};
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 8px;
}}

.panel {{
    background: linear-gradient(180deg, rgba(8,42,69,0.98), rgba(4,28,49,0.98));
    border: 1px solid rgba(143,211,255,0.22);
    border-radius: 10px;
    padding: 16px;
    box-shadow: 0 0 25px rgba(0,0,0,0.20);
}}

.metric-panel {{
    background: linear-gradient(180deg, #0B3455, #082A45);
    border: 1px solid rgba(143,211,255,0.20);
    border-radius: 9px;
    padding: 14px 10px;
    text-align: center;
    min-height: 96px;
}}

.metric-label {{
    color: {BLUE};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}

.metric-value {{
    color: {WHITE};
    font-size: 31px;
    font-weight: 500;
    line-height: 1.1;
    margin-top: 8px;
}}

.metric-unit {{
    color: {MUTED};
    font-size: 11px;
    margin-top: 2px;
    text-transform: uppercase;
}}

.player-name {{
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 0.5px;
}}

.player-meta {{
    color: {MUTED};
    font-size: 14px;
    margin-top: 4px;
}}

.info-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 7px 16px;
    font-size: 13px;
}}

.info-label {{
    color: {MUTED};
}}

.info-value {{
    color: {TEXT};
    font-weight: 500;
}}

.summary-text {{
    color: {TEXT};
    font-size: 13px;
    line-height: 1.55;
}}

.footer {{
    color: {MUTED};
    font-size: 11px;
    text-align: center;
    margin-top: 18px;
    letter-spacing: 0.5px;
}}

div[data-testid="stFileUploader"] {{
    background-color: rgba(8,42,69,0.75);
    border: 1px dashed rgba(143,211,255,0.35);
    border-radius: 10px;
    padding: 10px;
}}

.stDataFrame {{
    border: 1px solid rgba(143,211,255,0.18);
    border-radius: 8px;
}}

.stSelectbox label {{
    color: {BLUE} !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    font-size: 11px !important;
    letter-spacing: 0.6px;
}}
</style>
""", unsafe_allow_html=True)


def clean_name(name):
    return re.sub(r'[^A-Za-z0-9_-]+', '_', str(name).strip())


def style_fig(fig, height=410):
    fig.update_layout(
        height=height,
        plot_bgcolor=PANEL,
        paper_bgcolor=PANEL,
        font=dict(color=TEXT, size=11),
        margin=dict(l=45, r=25, t=38, b=42),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT, size=10)
        )
    )

    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.30)",
        linecolor="rgba(255,255,255,0.20)",
        tickfont=dict(color=TEXT, size=10),
        title_font=dict(color=TEXT, size=11)
    )

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.30)",
        linecolor="rgba(255,255,255,0.20)",
        tickfont=dict(color=TEXT, size=10),
        title_font=dict(color=TEXT, size=11)
    )

    return fig


def metric_box(label, value, unit=""):
    st.markdown(f"""
    <div class="metric-panel">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-unit">{unit}</div>
    </div>
    """, unsafe_allow_html=True)


def make_demo_data():
    np.random.seed(7)

    pitch_types = (
        ["4-Seam Fastball"] * 113 +
        ["Sinker"] * 47 +
        ["Slider"] * 43 +
        ["Changeup"] * 32 +
        ["Curveball"] * 15
    )

    demo = pd.DataFrame({
        "Pitcher": ["Angel Montero"] * len(pitch_types),
        "TaggedPitchType": pitch_types,
    })

    velo_map = {
        "4-Seam Fastball": 92,
        "Sinker": 90,
        "Slider": 84,
        "Changeup": 82,
        "Curveball": 77
    }

    spin_map = {
        "4-Seam Fastball": 2350,
        "Sinker": 2150,
        "Slider": 2480,
        "Changeup": 1850,
        "Curveball": 2320
    }

    ivb_map = {
        "4-Seam Fastball": 17,
        "Sinker": 13,
        "Slider": 2,
        "Changeup": 10,
        "Curveball": -2
    }

    hb_map = {
        "4-Seam Fastball": -8,
        "Sinker": 12,
        "Slider": -5,
        "Changeup": -10,
        "Curveball": -6
    }

    demo["RelSpeed"] = demo["TaggedPitchType"].map(velo_map) + np.random.normal(0, 1.2, len(demo))
    demo["SpinRate"] = demo["TaggedPitchType"].map(spin_map) + np.random.normal(0, 80, len(demo))
    demo["InducedVertBreak"] = demo["TaggedPitchType"].map(ivb_map) + np.random.normal(0, 2.5, len(demo))
    demo["HorzBreak"] = demo["TaggedPitchType"].map(hb_map) + np.random.normal(0, 2.5, len(demo))
    demo["RelSide"] = np.random.normal(-0.4, 0.55, len(demo))
    demo["RelHeight"] = np.random.normal(5.8, 0.35, len(demo))
    demo["PlateLocSide"] = np.random.normal(0, 0.85, len(demo))
    demo["PlateLocHeight"] = np.random.normal(2.5, 0.75, len(demo))
    demo["Extension"] = np.random.normal(6.3, 0.25, len(demo))
    demo["PitchNo"] = range(1, len(demo) + 1)

    demo["PitchCall"] = np.random.choice(
        ["StrikeCalled", "StrikeSwinging", "FoulBall", "InPlay", "BallCalled"],
        len(demo),
        p=[0.30, 0.20, 0.22, 0.18, 0.10]
    )

    return demo


def safe_metric(df, col, func="mean", decimals=1):
    if col not in df.columns or df.empty:
        return "-"
    if func == "mean":
        return round(df[col].mean(), decimals)
    if func == "max":
        return round(df[col].max(), decimals)
    return "-"


# HEADER
if LOGO_PATH.exists():
    logo = Image.open(LOGO_PATH)
    c1, c2, c3 = st.columns([1.2, 2.4, 1.2])
    with c2:
        st.image(logo, use_container_width=True)
else:
    st.markdown("""
    <div style="text-align:center; font-size:36px; font-weight:800; color:#EAF4FF; letter-spacing:3px;">
        TAMPA BAY
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="header-title">DR TAMPA DATA TOOLS</div>
<div class="header-subtitle">INTERNATIONAL PLAYER EVALUATION HUB</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# SIDEBAR
st.sidebar.markdown("## DR Tampa Data Tools")
st.sidebar.markdown("Internal Player Evaluation")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("Upload TrackMan CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = make_demo_data()

if "Pitcher" in df.columns:
    players = sorted(df["Pitcher"].dropna().unique())
else:
    players = ["Angel Montero"]

selected_player = st.sidebar.selectbox("Select Player", players)

player_df = df[df["Pitcher"] == selected_player].copy() if "Pitcher" in df.columns else df.copy()

if player_df.empty:
    player_df = df.copy()

pitch_types_available = ["All"]
if "TaggedPitchType" in player_df.columns:
    pitch_types_available += sorted(player_df["TaggedPitchType"].dropna().unique().tolist())

pitch_calls_available = ["All"]
if "PitchCall" in player_df.columns:
    pitch_calls_available += sorted(player_df["PitchCall"].dropna().unique().tolist())

st.sidebar.markdown("### Filters")
pitch_filter = st.sidebar.selectbox("Pitch Type", pitch_types_available)
call_filter = st.sidebar.selectbox("Pitch Call", pitch_calls_available)

filtered_df = player_df.copy()

if pitch_filter != "All" and "TaggedPitchType" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["TaggedPitchType"] == pitch_filter]

if call_filter != "All" and "PitchCall" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["PitchCall"] == call_filter]

st.sidebar.markdown("### Data Source")
if uploaded_file:
    st.sidebar.write(f"CSV: {uploaded_file.name}")
else:
    st.sidebar.write("Demo TrackMan Data")

st.sidebar.write(f"Rows: {len(filtered_df):,}")

st.sidebar.download_button(
    "Export Filtered Data",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name=f"{clean_name(selected_player)}_filtered_trackman.csv",
    mime="text/csv"
)

# PLAYER OVERVIEW
left, right = st.columns([1.12, 2.88])

with left:
    st.markdown('<div class="section-title">Player Overview</div>', unsafe_allow_html=True)

    initials = "".join([x[:1] for x in str(selected_player).split()[:2]]).upper()
    if not initials:
        initials = "DT"

    st.markdown(f"""
    <div class="panel">
        <div style="display:flex; gap:18px; align-items:center;">
            <div style="
                width:105px; height:105px; border-radius:50%;
                background:linear-gradient(180deg,#9FD6FF,#5C9DCE);
                display:flex; align-items:center; justify-content:center;
                font-size:34px; font-weight:800; color:white;">
                {initials}
            </div>
            <div>
                <div class="player-name">{str(selected_player).upper()}</div>
                <div class="player-meta">RHP &nbsp; | &nbsp; Pitcher</div>
            </div>
        </div>
        <hr>
        <div class="info-grid">
            <div class="info-label">Age</div><div class="info-value">17</div>
            <div class="info-label">Height</div><div class="info-value">6'2"</div>
            <div class="info-label">Weight</div><div class="info-value">175 lbs</div>
            <div class="info-label">Bats / Throws</div><div class="info-value">R / R</div>
            <div class="info-label">Academy</div><div class="info-value">DR Baseball Academy</div>
            <div class="info-label">Scout</div><div class="info-value">Francis</div>
        </div>
        <hr>
        <div class="summary-text">
            Athletic right-handed pitcher with projectable frame and advanced arm speed.
            Works in the zone and shows feel for multiple pitches. Continue evaluating command,
            pitchability and performance against hitters.
        </div>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-title">TrackMan Summary</div>', unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)

    avg_velo = safe_metric(filtered_df, "RelSpeed", "mean", 1)
    max_velo = safe_metric(filtered_df, "RelSpeed", "max", 1)

    if "PitchCall" in filtered_df.columns and not filtered_df.empty:
        strike_calls = ["StrikeCalled", "StrikeSwinging", "FoulBall", "InPlay"]
        whiff_calls = ["StrikeSwinging"]
        strike_pct = round(filtered_df["PitchCall"].isin(strike_calls).mean() * 100, 1)
        whiff_pct = round(filtered_df["PitchCall"].isin(whiff_calls).mean() * 100, 1)
    else:
        strike_pct = "-"
        whiff_pct = "-"

    with m1:
        metric_box("AVG VELO", avg_velo, "mph")
    with m2:
        metric_box("MAX VELO", max_velo, "mph")
    with m3:
        metric_box("STRIKE %", strike_pct, "%")
    with m4:
        metric_box("WHIFF %", whiff_pct, "%")
    with m5:
        metric_box("TOTAL PITCHES", f"{len(filtered_df):,}", "")

    st.markdown("<br>", unsafe_allow_html=True)

    a1, a2 = st.columns([1.55, 1])

    with a1:
        st.markdown('<div class="section-title">Pitch Arsenal</div>', unsafe_allow_html=True)

        if "TaggedPitchType" in filtered_df.columns and not filtered_df.empty:
            agg = {"Pitches": ("TaggedPitchType", "count")}

            for col, label in {
                "RelSpeed": "Avg Velo",
                "SpinRate": "Avg Spin",
                "InducedVertBreak": "IVB",
                "HorzBreak": "HB",
                "Extension": "Extension"
            }.items():
                if col in filtered_df.columns:
                    agg[label] = (col, "mean")

            arsenal = filtered_df.groupby("TaggedPitchType").agg(**agg).reset_index()
            arsenal["Usage %"] = arsenal["Pitches"] / arsenal["Pitches"].sum() * 100

            for col in arsenal.columns:
                if col not in ["TaggedPitchType", "Pitches"]:
                    arsenal[col] = arsenal[col].round(1)

            st.dataframe(arsenal, use_container_width=True, height=265)

    with a2:
        st.markdown('<div class="section-title">Pitch Usage Distribution</div>', unsafe_allow_html=True)

        if "TaggedPitchType" in filtered_df.columns and not filtered_df.empty:
            usage = filtered_df["TaggedPitchType"].value_counts().reset_index()
            usage.columns = ["Pitch Type", "Pitches"]

            fig_usage = px.pie(
                usage,
                names="Pitch Type",
                values="Pitches",
                hole=0.60,
                color="Pitch Type",
                color_discrete_map=pitch_colors
            )

            fig_usage.update_traces(
                textinfo="percent",
                marker=dict(line=dict(color="#031B34", width=2))
            )

            fig_usage = style_fig(fig_usage, height=305)
            st.plotly_chart(fig_usage, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# CHARTS
g1, g2, g3 = st.columns(3)

with g1:
    st.markdown('<div class="section-title">Pitch Location</div>', unsafe_allow_html=True)

    if {"PlateLocSide", "PlateLocHeight"}.issubset(filtered_df.columns) and not filtered_df.empty:
        fig_loc = px.scatter(
            filtered_df,
            x="PlateLocSide",
            y="PlateLocHeight",
            color="TaggedPitchType" if "TaggedPitchType" in filtered_df.columns else None,
            color_discrete_map=pitch_colors,
            hover_data=[c for c in ["PitchNo", "TaggedPitchType", "PitchCall", "RelSpeed"] if c in filtered_df.columns]
        )

        fig_loc.add_shape(
            type="rect",
            x0=-0.83,
            x1=0.83,
            y0=1.5,
            y1=3.5,
            line=dict(color=WHITE, width=2)
        )

        fig_loc.update_traces(marker=dict(size=7, opacity=0.88, line=dict(width=0.5, color=WHITE)))
        fig_loc.update_xaxes(range=[-3, 3], title="Horizontal Location")
        fig_loc.update_yaxes(range=[0, 5], title="Vertical Location")

        fig_loc = style_fig(fig_loc)
        st.plotly_chart(fig_loc, use_container_width=True)

with g2:
    st.markdown('<div class="section-title">Movement Profile</div>', unsafe_allow_html=True)

    if {"HorzBreak", "InducedVertBreak"}.issubset(filtered_df.columns) and not filtered_df.empty:
        fig_move = px.scatter(
            filtered_df,
            x="HorzBreak",
            y="InducedVertBreak",
            color="TaggedPitchType" if "TaggedPitchType" in filtered_df.columns else None,
            color_discrete_map=pitch_colors,
            hover_data=[c for c in ["PitchNo", "TaggedPitchType", "RelSpeed", "SpinRate"] if c in filtered_df.columns]
        )

        fig_move.update_traces(marker=dict(size=7, opacity=0.90, line=dict(width=0.4, color=WHITE)))
        fig_move.update_xaxes(title="Horizontal Break")
        fig_move.update_yaxes(title="Induced Vertical Break")

        fig_move = style_fig(fig_move)
        st.plotly_chart(fig_move, use_container_width=True)

with g3:
    st.markdown('<div class="section-title">Release Point</div>', unsafe_allow_html=True)

    if {"RelSide", "RelHeight"}.issubset(filtered_df.columns) and not filtered_df.empty:
        fig_rel = px.scatter(
            filtered_df,
            x="RelSide",
            y="RelHeight",
            color="TaggedPitchType" if "TaggedPitchType" in filtered_df.columns else None,
            color_discrete_map=pitch_colors,
            hover_data=[c for c in ["PitchNo", "TaggedPitchType", "RelSpeed"] if c in filtered_df.columns]
        )

        fig_rel.update_traces(marker=dict(size=7, opacity=0.88, line=dict(width=0.4, color=WHITE)))
        fig_rel.update_xaxes(title="Release Side")
        fig_rel.update_yaxes(title="Release Height")

        fig_rel = style_fig(fig_rel)
        st.plotly_chart(fig_rel, use_container_width=True)

g4, g5, g6 = st.columns(3)

with g4:
    st.markdown('<div class="section-title">Velocity Trend</div>', unsafe_allow_html=True)

    if "RelSpeed" in filtered_df.columns and not filtered_df.empty:
        velo_df = filtered_df.reset_index(drop=True)
        velo_df["Pitch #"] = velo_df.index + 1

        fig_velo = px.line(
            velo_df,
            x="Pitch #",
            y="RelSpeed",
            color="TaggedPitchType" if "TaggedPitchType" in velo_df.columns else None,
            color_discrete_map=pitch_colors,
            markers=True
        )

        fig_velo.update_traces(line=dict(width=2), marker=dict(size=4))
        fig_velo.update_xaxes(title="Pitch Number")
        fig_velo.update_yaxes(title="Velocity")

        fig_velo = style_fig(fig_velo)
        st.plotly_chart(fig_velo, use_container_width=True)

with g5:
    st.markdown('<div class="section-title">Velocity Distribution</div>', unsafe_allow_html=True)

    if {"RelSpeed", "TaggedPitchType"}.issubset(filtered_df.columns) and not filtered_df.empty:
        fig_box = px.box(
            filtered_df,
            x="TaggedPitchType",
            y="RelSpeed",
            color="TaggedPitchType",
            color_discrete_map=pitch_colors,
            points="all"
        )

        fig_box.update_xaxes(title="")
        fig_box.update_yaxes(title="Velocity")

        fig_box = style_fig(fig_box)
        st.plotly_chart(fig_box, use_container_width=True)

with g6:
    st.markdown('<div class="section-title">Pitch Call Distribution</div>', unsafe_allow_html=True)

    if "PitchCall" in filtered_df.columns and not filtered_df.empty:
        call_counts = filtered_df["PitchCall"].value_counts().reset_index()
        call_counts.columns = ["Pitch Call", "Count"]

        fig_call = px.pie(
            call_counts,
            names="Pitch Call",
            values="Count",
            hole=0.60
        )

        fig_call.update_traces(marker=dict(line=dict(color="#031B34", width=2)))
        fig_call = style_fig(fig_call)
        st.plotly_chart(fig_call, use_container_width=True)

# TABLE + VIDEO
t1, t2 = st.columns([1.45, 1])

with t1:
    st.markdown('<div class="section-title">Full TrackMan Data</div>', unsafe_allow_html=True)

    show_cols = [c for c in [
        "PitchNo", "TaggedPitchType", "PitchCall", "RelSpeed",
        "SpinRate", "InducedVertBreak", "HorzBreak", "Extension",
        "PlateLocSide", "PlateLocHeight", "RelSide", "RelHeight"
    ] if c in filtered_df.columns]

    if show_cols:
        st.dataframe(filtered_df[show_cols], use_container_width=True, height=340)
    else:
        st.dataframe(filtered_df, use_container_width=True, height=340)

with t2:
    st.markdown('<div class="section-title">Video Library</div>', unsafe_allow_html=True)

    player_folder = VIDEOS_DIR / clean_name(selected_player)
    player_folder.mkdir(exist_ok=True)

    uploaded_video = st.file_uploader("Upload Video", type=["mp4", "mov"], key="video_upload")

    if uploaded_video:
        video_path = player_folder / uploaded_video.name
        with open(video_path, "wb") as f:
            f.write(uploaded_video.read())
        st.success("Video saved.")

    video_files = list(player_folder.glob("*.mp4")) + list(player_folder.glob("*.mov"))

    if video_files:
        for video in video_files:
            st.video(str(video))
            st.caption(video.name)
    else:
        st.info("No videos uploaded for this player.")

st.markdown(
    "<div class='footer'>DR TAMPA DATA TOOLS v1.0 &nbsp; | &nbsp; CONFIDENTIAL — FOR INTERNAL USE ONLY</div>",
    unsafe_allow_html=True
)