import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from PIL import Image
import numpy as np
import re

st.set_page_config(page_title="INTERNATIONAL SCOUTING & PLAYER DEVELOPMENT", layout="wide")

BASE_DIR = Path(".")
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "Data"
VIDEOS_DIR = BASE_DIR / "Videos"

ASSETS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(exist_ok=True)

LOGO_PATH = ASSETS_DIR / "Tampa_logo.gif"

NAVY = "#021426"
PANEL = "#061F35"
TEXT = "#EAF4FF"
MUTED = "#A9BDD0"
BLUE = "#8FD3FF"
WHITE = "#FFFFFF"

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
        radial-gradient(circle at top center, rgba(12,67,111,0.45) 0%, rgba(3,27,52,0.90) 35%, rgba(2,15,29,1) 85%),
        linear-gradient(180deg, #031B34, {NAVY});
    color: {TEXT};
}}

.main .block-container {{
    padding-top: 0.7rem;
    max-width: 1700px;
}}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #03182B, #021426);
    border-right: 1px solid rgba(143,211,255,0.20);
}}

section[data-testid="stSidebar"] * {{
    color: {TEXT};
}}

.header-title {{
    text-align: center;
    color: {BLUE};
    font-size: 24px;
    font-weight: 800;
    letter-spacing: 5px;
    margin-top: 2px;
}}

.header-subtitle {{
    text-align: center;
    color: {MUTED};
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 3px;
    margin-top: 8px;
    margin-bottom: 16px;
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
    min-height: 94px;
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
    font-size: 30px;
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
    font-size: 27px;
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

hr {{
    border: none;
    border-top: 1px solid rgba(143,211,255,0.25);
    margin-top: 10px;
    margin-bottom: 16px;
}}

.stDataFrame {{
    border: 1px solid rgba(143,211,255,0.18);
    border-radius: 8px;
}}
</style>
""", unsafe_allow_html=True)


def clean_name(name):
    return re.sub(r'[^A-Za-z0-9_-]+', '_', str(name).strip())


def metric_box(label, value, unit=""):
    st.markdown(f"""
    <div class="metric-panel">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-unit">{unit}</div>
    </div>
    """, unsafe_allow_html=True)


def style_fig(fig, height=410):
    fig.update_layout(
        height=height,
        plot_bgcolor=PANEL,
        paper_bgcolor=PANEL,
        font=dict(color=TEXT, size=11),
        margin=dict(l=45, r=25, t=38, b=42),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT, size=10))
    )
    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.30)",
        linecolor="rgba(255,255,255,0.20)"
    )
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.08)",
        zerolinecolor="rgba(255,255,255,0.30)",
        linecolor="rgba(255,255,255,0.20)"
    )
    return fig


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
    demo["SessionDate"] = "2026-05-31"
    demo["SessionType"] = "Bullpen"
    demo["SourceFile"] = "demo_bullpen_2026-05-31.csv"

    demo["PitchCall"] = np.random.choice(
        ["StrikeCalled", "StrikeSwinging", "FoulBall", "InPlay", "BallCalled"],
        len(demo),
        p=[0.30, 0.20, 0.22, 0.18, 0.10]
    )

    return demo


def detect_session_date(file_name, df):
    date_from_name = re.search(r"(20\d{2}-\d{2}-\d{2})", file_name)

    if date_from_name:
        return date_from_name.group(1)

    if "Date" in df.columns:
        try:
            return pd.to_datetime(df["Date"].iloc[0]).strftime("%Y-%m-%d")
        except Exception:
            return str(df["Date"].iloc[0])

    return "Unknown"


def detect_session_type(file_name):
    name = file_name.lower()

    if "bullpen" in name:
        return "Bullpen"
    if "livebp" in name or "live_bp" in name or "live" in name:
        return "Live BP"
    if "game" in name or "juego" in name:
        return "Game"

    return "Unknown"


def load_all_trackman_csvs():
    csv_files = sorted(DATA_DIR.glob("*.csv"))

    all_data = []

    for file in csv_files:
        try:
            temp = pd.read_csv(file)
            temp["SourceFile"] = file.name
            temp["SessionDate"] = detect_session_date(file.name, temp)
            temp["SessionType"] = detect_session_type(file.name)
            all_data.append(temp)
        except Exception as e:
            st.warning(f"Could not read {file.name}: {e}")

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        combined = combined.drop_duplicates()
        return combined

    return make_demo_data()


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
    c1, c2, c3 = st.columns([1.25, 2.5, 1.25])
    with c2:
        st.image(logo, use_container_width=True)
else:
    st.error("Logo not found. Put your logo here: assets/Tampa_logo.png")

st.markdown("""
<div class="header-title">INTERNATIONAL SCOUTING & PLAYER DEVELOPMENT</div>
<div class="header-subtitle">DOMINICAN REPUBLIC OPERATIONS &nbsp; | &nbsp; FRANCIS MARTINEZ • VIDEO • SCOUTING • DEVELOPMENT </div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# LOAD DATA
df = load_all_trackman_csvs()
csv_files = sorted(DATA_DIR.glob("*.csv"))

# SIDEBAR
st.sidebar.markdown("## Player Evaluation")
st.sidebar.markdown("Dominican Republic Operations")
st.sidebar.markdown("---")
# PLAYER TYPE MODULE
player_type = st.sidebar.radio(
    "Player Type",
    ["Pitchers", "Hitters"]
)

# =========================
# HITTER MODULE
# =========================
if player_type == "Hitters":

    if "Batter" not in df.columns:
        st.warning("No encontré columna 'Batter' en el CSV. Para usar el módulo de bateadores, el CSV debe tener una columna llamada Batter.")
        st.stop()

    hitters = sorted(df["Batter"].dropna().astype(str).unique())
    selected_hitter = st.sidebar.selectbox("Select Hitter", hitters)

    hitter_df = df[df["Batter"].astype(str) == str(selected_hitter)].copy()

    def find_col(possible_names):
        for col in possible_names:
            if col in hitter_df.columns:
                return col
        return None

    ev_col = find_col(["ExitSpeed", "ExitVelocity", "ExitVelo", "ExitVel"])
    la_col = find_col(["Angle", "LaunchAngle", "Launch Angle"])
    distance_col = find_col(["Distance", "HitDistance", "CarryDistance"])
    bearing_col = find_col(["Bearing", "Direction", "HitDirection"])
    hit_type_col = find_col(["TaggedHitType", "HitType", "BattedBallType"])
    result_col = find_col(["PlayResult", "Result", "PitchCall"])

    st.markdown('<div class="section-title">Hitter Profile</div>', unsafe_allow_html=True)

    left, right = st.columns([1.1, 2.9])

    with left:
        initials = "".join([x[:1] for x in str(selected_hitter).split()[:2]]).upper()

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
                    <div class="player-name">{str(selected_hitter).upper()}</div>
                    <div class="player-meta">Hitter &nbsp; | &nbsp; Dominican Republic</div>
                </div>
            </div>
            <hr>
            <div class="summary-text">
                Offensive evaluation module focused on exit velocity, launch angle,
                spray direction, batted ball quality and contact profile.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-title">Batted Ball Summary</div>', unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns(5)

        bbe = len(hitter_df)

        avg_ev = round(hitter_df[ev_col].mean(), 1) if ev_col else "-"
        max_ev = round(hitter_df[ev_col].max(), 1) if ev_col else "-"
        avg_la = round(hitter_df[la_col].mean(), 1) if la_col else "-"

        if ev_col:
            hard_hit = round((hitter_df[ev_col] >= 95).mean() * 100, 1)
        else:
            hard_hit = "-"

        if la_col:
            sweet_spot = round(hitter_df[la_col].between(8, 32).mean() * 100, 1)
        else:
            sweet_spot = "-"

        with c1:
            metric_box("Batted Balls", bbe, "")
        with c2:
            metric_box("Avg EV", avg_ev, "mph")
        with c3:
            metric_box("Max EV", max_ev, "mph")
        with c4:
            metric_box("Avg LA", avg_la, "deg")
        with c5:
            metric_box("Hard Hit %", hard_hit, "%")

    st.markdown("<br>", unsafe_allow_html=True)

    h1, h2 = st.columns(2)

    with h1:
        st.markdown('<div class="section-title">Exit Velocity vs Launch Angle</div>', unsafe_allow_html=True)

        if ev_col and la_col:
            fig_ev_la = px.scatter(
                hitter_df,
                x=la_col,
                y=ev_col,
                color=hit_type_col if hit_type_col else None,
                hover_data=[c for c in ["Batter", "Pitcher", "PitchCall", "PlayResult", "TaggedHitType", "Distance"] if c in hitter_df.columns]
            )

            fig_ev_la.add_shape(
                type="rect",
                x0=8,
                x1=32,
                y0=95,
                y1=max(120, hitter_df[ev_col].max() + 5),
                line=dict(color="rgba(143,211,255,0.6)", width=2),
                fillcolor="rgba(143,211,255,0.07)"
            )

            fig_ev_la.update_xaxes(title="Launch Angle", range=[-40, 60])
            fig_ev_la.update_yaxes(title="Exit Velocity", range=[40, max(120, hitter_df[ev_col].max() + 5)])

            fig_ev_la = style_fig(fig_ev_la, height=430)
            st.plotly_chart(fig_ev_la, use_container_width=True)
        else:
            st.info("Necesito columnas de Exit Velocity y Launch Angle.")

    with h2:
        st.markdown('<div class="section-title">Spray Chart</div>', unsafe_allow_html=True)

        if bearing_col and distance_col:
            spray_df = hitter_df.copy()

            fig_spray = px.scatter(
                spray_df,
                x=bearing_col,
                y=distance_col,
                color=hit_type_col if hit_type_col else None,
                hover_data=[c for c in ["Batter", "ExitSpeed", "Angle", "PlayResult", "TaggedHitType"] if c in spray_df.columns]
            )

            fig_spray.update_xaxes(title="Spray Direction / Bearing")
            fig_spray.update_yaxes(title="Distance")

            fig_spray = style_fig(fig_spray, height=430)
            st.plotly_chart(fig_spray, use_container_width=True)
        else:
            st.info("Para Spray Chart necesito columnas tipo Bearing/Direction y Distance/HitDistance.")

    h3, h4 = st.columns(2)

    with h3:
        st.markdown('<div class="section-title">Contact Quality</div>', unsafe_allow_html=True)

        if hit_type_col:
            agg = {"Batted Balls": (hit_type_col, "count")}

            if ev_col:
                agg["Avg EV"] = (ev_col, "mean")
                agg["Max EV"] = (ev_col, "max")

            if la_col:
                agg["Avg LA"] = (la_col, "mean")

            contact_table = (
                hitter_df
                .groupby(hit_type_col)
                .agg(**agg)
                .reset_index()
            )

            for col in contact_table.columns:
                if col not in [hit_type_col, "Batted Balls"]:
                    contact_table[col] = contact_table[col].round(1)

            st.dataframe(contact_table, use_container_width=True, height=330)
        else:
            st.info("No encontré columna de tipo de batazo.")

    with h4:
        st.markdown('<div class="section-title">Result Distribution</div>', unsafe_allow_html=True)

        if result_col:
            result_counts = hitter_df[result_col].value_counts().reset_index()
            result_counts.columns = ["Result", "Count"]

            fig_result = px.pie(
                result_counts,
                names="Result",
                values="Count",
                hole=0.60
            )

            fig_result.update_traces(marker=dict(line=dict(color="#031B34", width=2)))
            fig_result = style_fig(fig_result, height=330)
            st.plotly_chart(fig_result, use_container_width=True)
        else:
            st.info("No encontré columna de resultado.")

    t1, t2 = st.columns([1.45, 1])

    with t1:
        st.markdown('<div class="section-title">Full Hitter Data</div>', unsafe_allow_html=True)

        hitter_cols = [c for c in [
            "Date", "Batter", "Pitcher", "TaggedHitType", "PlayResult",
            "ExitSpeed", "ExitVelocity", "Angle", "LaunchAngle",
            "Bearing", "Direction", "Distance", "HitDistance",
            "PitchCall", "TaggedPitchType"
        ] if c in hitter_df.columns]

        st.dataframe(
            hitter_df[hitter_cols] if hitter_cols else hitter_df,
            use_container_width=True,
            height=340
        )

    with t2:
        st.markdown('<div class="section-title">Video Library</div>', unsafe_allow_html=True)

        hitter_folder = VIDEOS_DIR / clean_name(selected_hitter)
        hitter_folder.mkdir(exist_ok=True)

        video_files = list(hitter_folder.glob("*.mp4")) + list(hitter_folder.glob("*.mov"))

        if video_files:
            for video in video_files:
                st.video(str(video))
                st.caption(video.name)
        else:
            st.info("No videos uploaded for this hitter.")

    st.markdown(
        "<div class='footer'>HITTER EVALUATION MODULE v1.0 &nbsp; | &nbsp; CONFIDENTIAL — FOR INTERNAL USE ONLY</div>",
        unsafe_allow_html=True
    )

    st.stop()
if "Pitcher" in df.columns:
    players = sorted(df["Pitcher"].dropna().astype(str).unique())
else:
    players = ["Angel Montero"]

selected_player = st.sidebar.selectbox("Select Player", players)

st.sidebar.markdown("### Session Filters")

if "SessionDate" in df.columns:
    session_dates = ["All"] + sorted(df["SessionDate"].dropna().astype(str).unique().tolist())
    selected_date = st.sidebar.selectbox("Session Date", session_dates)
else:
    selected_date = "All"

if "SessionType" in df.columns:
    session_types = ["All"] + sorted(df["SessionType"].dropna().astype(str).unique().tolist())
    selected_session_type = st.sidebar.selectbox("Session Type", session_types)
else:
    selected_session_type = "All"

player_df = df[df["Pitcher"].astype(str) == str(selected_player)].copy() if "Pitcher" in df.columns else df.copy()

if selected_date != "All" and "SessionDate" in player_df.columns:
    player_df = player_df[player_df["SessionDate"].astype(str) == selected_date]

if selected_session_type != "All" and "SessionType" in player_df.columns:
    player_df = player_df[player_df["SessionType"] == selected_session_type]

pitch_types_available = ["All"]
if "TaggedPitchType" in player_df.columns:
    pitch_types_available += sorted(player_df["TaggedPitchType"].dropna().astype(str).unique().tolist())

pitch_calls_available = ["All"]
if "PitchCall" in player_df.columns:
    pitch_calls_available += sorted(player_df["PitchCall"].dropna().astype(str).unique().tolist())

st.sidebar.markdown("### Pitch Filters")
pitch_filter = st.sidebar.selectbox("Pitch Type", pitch_types_available)
call_filter = st.sidebar.selectbox("Pitch Call", pitch_calls_available)

filtered_df = player_df.copy()

if pitch_filter != "All" and "TaggedPitchType" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["TaggedPitchType"].astype(str) == pitch_filter]

if call_filter != "All" and "PitchCall" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["PitchCall"].astype(str) == call_filter]
# -------------------------
# SESSION VIEW
# -------------------------

with st.expander("Session View", expanded=True):

    col1, col2, col3 = st.columns(3)

    with col1:
        session_view = st.radio(
            "Session Type",
            ["All Sessions", "Bullpen", "Live BP", "Game"],
            horizontal=True
        )

    with col2:
        if "SessionDate" in filtered_df.columns:
            session_dates = ["All"] + sorted(
                filtered_df["SessionDate"].dropna().astype(str).unique()
            )

            selected_session_date = st.selectbox(
                "Session Date",
                session_dates
            )
        else:
            selected_session_date = "All"

    with col3:
        if "SourceFile" in filtered_df.columns:
            source_files = ["All"] + sorted(
                filtered_df["SourceFile"].dropna().astype(str).unique()
            )

            selected_source_file = st.selectbox(
                "Source File",
                source_files
            )
        else:
            selected_source_file = "All"

if session_view != "All Sessions" and "SessionType" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["SessionType"] == session_view
    ]

if selected_session_date != "All" and "SessionDate" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["SessionDate"].astype(str)
        == selected_session_date
    ]

if selected_source_file != "All" and "SourceFile" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["SourceFile"].astype(str)
        == selected_source_file
    ]

# -------------------------
# DATA SOURCE
# -------------------------

st.sidebar.markdown("### Data Source")
st.sidebar.markdown("### Data Source")

if csv_files:
    st.sidebar.write("TrackMan Database Loaded")
    st.sidebar.write(f"CSV Files: {len(csv_files)}")
    st.sidebar.write(f"Total Rows: {len(df):,}")
else:
    st.sidebar.write("Demo TrackMan Data")

st.sidebar.write(f"Filtered Rows: {len(filtered_df):,}")

st.sidebar.download_button(
    "Export Filtered Data",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name=f"{clean_name(selected_player)}_filtered_trackman.csv",
    mime="text/csv"
)
# PLAYER BOARD
st.markdown('<div class="section-title">Player Board</div>', unsafe_allow_html=True)

if "Pitcher" in df.columns:
    board = df.groupby("Pitcher").agg(
        TotalPitches=("Pitcher", "count"),
        AvgVelo=("RelSpeed", "mean") if "RelSpeed" in df.columns else ("Pitcher", "count"),
        MaxVelo=("RelSpeed", "max") if "RelSpeed" in df.columns else ("Pitcher", "count"),
        LatestSession=("SessionDate", "max") if "SessionDate" in df.columns else ("Pitcher", "count"),
    ).reset_index()

    if "PitchCall" in df.columns:
        strike_calls = ["StrikeCalled", "StrikeSwinging", "FoulBall", "InPlay"]

        strike_df = (
            df.assign(IsStrike=df["PitchCall"].isin(strike_calls))
            .groupby("Pitcher")
            .agg(StrikePct=("IsStrike", "mean"))
            .reset_index()
        )

        strike_df["StrikePct"] = (strike_df["StrikePct"] * 100).round(1)
        board = board.merge(strike_df, on="Pitcher", how="left")

    if "RelSpeed" in df.columns:
        board["AvgVelo"] = board["AvgVelo"].round(1)
        board["MaxVelo"] = board["MaxVelo"].round(1)

    board = board.rename(columns={
        "Pitcher": "Player",
        "TotalPitches": "Pitches",
        "AvgVelo": "Avg Velo",
        "MaxVelo": "Max Velo",
        "LatestSession": "Latest Session",
        "StrikePct": "Strike %"
    })

    st.dataframe(board, use_container_width=True, height=260)

else:
    st.info("Player Board will appear when the CSV has a Pitcher column.")
# TOP DASHBOARD
dash1, dash2, dash3, dash4, dash5 = st.columns(5)

with dash1:
    metric_box("Players Tracked", len(players), "")
with dash2:
    metric_box("CSV Files", len(csv_files), "")
with dash3:
    metric_box("Total Pitches", f"{len(df):,}", "")
with dash4:
    metric_box("Videos Available", len(list(VIDEOS_DIR.glob('**/*.mp4'))), "")
with dash5:
    if "SessionDate" in df.columns:
        metric_box("Sessions Logged", df["SessionDate"].nunique(), "")
    else:
        metric_box("Sessions Logged", "-", "")

st.markdown("<br>", unsafe_allow_html=True)

# SESSION HISTORY
st.markdown('<div class="section-title">Session History</div>', unsafe_allow_html=True)

if {"Pitcher", "SessionDate", "SessionType", "SourceFile"}.issubset(df.columns):

    group_cols = ["Pitcher", "SessionDate", "SessionType", "SourceFile"]

    agg_dict = {
        "Pitches": ("Pitcher", "count")
    }

    if "RelSpeed" in df.columns:
        agg_dict["Avg Velo"] = ("RelSpeed", "mean")
        agg_dict["Max Velo"] = ("RelSpeed", "max")

    if "PitchCall" in df.columns:
        strike_calls = ["StrikeCalled", "StrikeSwinging", "FoulBall", "InPlay"]

        temp_sessions = df.copy()
        temp_sessions["IsStrike"] = temp_sessions["PitchCall"].isin(strike_calls)

        agg_dict["Strike %"] = ("IsStrike", "mean")
    else:
        temp_sessions = df.copy()

    sessions = (
        temp_sessions
        .groupby(group_cols)
        .agg(**agg_dict)
        .reset_index()
        .sort_values(["SessionDate", "Pitcher"], ascending=[False, True])
    )

    if "Avg Velo" in sessions.columns:
        sessions["Avg Velo"] = sessions["Avg Velo"].round(1)

    if "Max Velo" in sessions.columns:
        sessions["Max Velo"] = sessions["Max Velo"].round(1)

    if "Strike %" in sessions.columns:
        sessions["Strike %"] = (sessions["Strike %"] * 100).round(1)

    sessions = sessions.rename(columns={
        "Pitcher": "Player",
        "SessionDate": "Date",
        "SessionType": "Type",
        "SourceFile": "File"
    })

    preferred_cols = [
        "Player",
        "Date",
        "Type",
        "Pitches",
        "Avg Velo",
        "Max Velo",
        "Strike %",
        "File"
    ]

    display_cols = [c for c in preferred_cols if c in sessions.columns]

    st.dataframe(
        sessions[display_cols],
        use_container_width=True,
        height=260
    )

else:
    st.info("Session history will appear when CSV files are loaded inside the Data folder.")
# PLAYER PROFILE + TRACKMAN SUMMARY
left, right = st.columns([1.12, 2.88])

with left:
    st.markdown('<div class="section-title">Player Profile</div>', unsafe_allow_html=True)

    initials = "".join([x[:1] for x in str(selected_player).split()[:2]]).upper()
    if not initials:
        initials = "DR"
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
                <div class="player-meta">Pitcher &nbsp; | &nbsp; Dominican Republic</div>
            </div>
        </div>
        <hr>
        <div class="info-grid">
            <div class="info-label">Status</div><div class="info-value">Follow</div>
            <div class="info-label">Age</div><div class="info-value">17</div>
            <div class="info-label">Height</div><div class="info-value">6'2"</div>
            <div class="info-label">Weight</div><div class="info-value">175 lbs</div>
            <div class="info-label">Bats / Throws</div><div class="info-value">R / R</div>
            <div class="info-label">Scout</div><div class="info-value">Francis</div>
        </div>
        <hr>
        <div class="summary-text">
            Athletic pitcher with projectable frame and present arm speed.
            Continue monitoring strike throwing, pitch shape, command and game usage.
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
        metric_box("Avg Velo", avg_velo, "mph")
    with m2:
        metric_box("Max Velo", max_velo, "mph")
    with m3:
        metric_box("Strike %", strike_pct, "%")
    with m4:
        metric_box("Whiff %", whiff_pct, "%")
    with m5:
        metric_box("Total Pitches", f"{len(filtered_df):,}", "")

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
        else:
            st.info("No pitch type data available for this selection.")

    with a2:
        st.markdown('<div class="section-title">Pitch Usage</div>', unsafe_allow_html=True)

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
            fig_usage.update_traces(textinfo="percent", marker=dict(line=dict(color="#031B34", width=2)))
            fig_usage = style_fig(fig_usage, height=305)
            st.plotly_chart(fig_usage, use_container_width=True)
        else:
            st.info("No pitch usage available.")

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
            hover_data=[
                c for c in [
                    "PitchNo",
                    "TaggedPitchType",
                    "PitchCall",
                    "RelSpeed",
                    "SpinRate",
                    "SessionDate",
                    "SessionType"
                ] if c in filtered_df.columns
            ]
        )

        fig_loc.update_traces(
            marker=dict(
                size=8,
                opacity=0.88,
                line=dict(width=0.6, color="white")
            )
        )

        # Strike zone outer box
        zone_left = -0.83
        zone_right = 0.83
        zone_bottom = 1.5
        zone_top = 3.5

        fig_loc.add_shape(
            type="rect",
            x0=zone_left,
            x1=zone_right,
            y0=zone_bottom,
            y1=zone_top,
            line=dict(color="white", width=2.5),
            fillcolor="rgba(255,255,255,0.015)"
        )

        # 9-zone vertical lines
        one_third_x = zone_left + (zone_right - zone_left) / 3
        two_third_x = zone_left + 2 * (zone_right - zone_left) / 3

        for x in [one_third_x, two_third_x]:
            fig_loc.add_shape(
                type="line",
                x0=x,
                x1=x,
                y0=zone_bottom,
                y1=zone_top,
                line=dict(color="rgba(255,255,255,0.35)", width=1)
            )

        # 9-zone horizontal lines
        one_third_y = zone_bottom + (zone_top - zone_bottom) / 3
        two_third_y = zone_bottom + 2 * (zone_top - zone_bottom) / 3

        for y in [one_third_y, two_third_y]:
            fig_loc.add_shape(
                type="line",
                x0=zone_left,
                x1=zone_right,
                y0=y,
                y1=y,
                line=dict(color="rgba(255,255,255,0.35)", width=1)
            )

        # Home plate
        plate_y = 0.85
        plate_width = 1.0
        plate_depth = 0.35

        fig_loc.add_shape(
            type="path",
            path=f"""
                M {-plate_width/2} {plate_y}
                L {plate_width/2} {plate_y}
                L {plate_width/2} {plate_y - plate_depth/2}
                L 0 {plate_y - plate_depth}
                L {-plate_width/2} {plate_y - plate_depth/2}
                Z
            """,
            line=dict(color="rgba(255,255,255,0.75)", width=2),
            fillcolor="rgba(255,255,255,0.06)"
        )

        # Center line
        fig_loc.add_shape(
            type="line",
            x0=0,
            x1=0,
            y0=0.5,
            y1=4.5,
            line=dict(color="rgba(255,255,255,0.12)", width=1, dash="dot")
        )

        fig_loc.update_xaxes(
            range=[-2.5, 2.5],
            title="Horizontal Location",
            zeroline=False
        )

        fig_loc.update_yaxes(
            range=[0.5, 4.6],
            title="Vertical Location",
            zeroline=False
        )

        fig_loc = style_fig(fig_loc, height=430)

        fig_loc.update_layout(
            showlegend=True,
            legend_title_text="Pitch Type"
        )

        st.plotly_chart(fig_loc, use_container_width=True)

    else:
        st.info("Pitch location data not available.")
with g2:
    st.markdown('<div class="section-title">Movement Profile</div>', unsafe_allow_html=True)

    if {"HorzBreak", "InducedVertBreak"}.issubset(filtered_df.columns) and not filtered_df.empty:
        fig_move = px.scatter(
            filtered_df,
            x="HorzBreak",
            y="InducedVertBreak",
            color="TaggedPitchType" if "TaggedPitchType" in filtered_df.columns else None,
            color_discrete_map=pitch_colors,
            hover_data=[
                c for c in [
                    "PitchNo",
                    "TaggedPitchType",
                    "RelSpeed",
                    "SpinRate",
                    "SessionDate",
                    "SessionType"
                ] if c in filtered_df.columns
            ]
        )

        fig_move.update_traces(
            marker=dict(
                size=8,
                opacity=0.90,
                line=dict(width=0.6, color=WHITE)
            )
        )

        # Plano cartesiano
        fig_move.add_shape(
            type="line",
            x0=-25,
            x1=25,
            y0=0,
            y1=0,
            line=dict(color="rgba(255,255,255,0.55)", width=2)
        )

        fig_move.add_shape(
            type="line",
            x0=0,
            x1=0,
            y0=-25,
            y1=25,
            line=dict(color="rgba(255,255,255,0.55)", width=2)
        )

        # Cuadrantes sutiles
        fig_move.add_shape(
            type="rect",
            x0=0, x1=25, y0=0, y1=25,
            fillcolor="rgba(143,211,255,0.04)",
            line=dict(width=0),
            layer="below"
        )

        fig_move.add_shape(
            type="rect",
            x0=-25, x1=0, y0=0, y1=25,
            fillcolor="rgba(255,255,255,0.025)",
            line=dict(width=0),
            layer="below"
        )

        fig_move.add_shape(
            type="rect",
            x0=-25, x1=0, y0=-25, y1=0,
            fillcolor="rgba(143,211,255,0.04)",
            line=dict(width=0),
            layer="below"
        )

        fig_move.add_shape(
            type="rect",
            x0=0, x1=25, y0=-25, y1=0,
            fillcolor="rgba(255,255,255,0.025)",
            line=dict(width=0),
            layer="below"
        )

        fig_move.update_xaxes(
            title="Horizontal Break",
            range=[-25, 25],
            zeroline=False
        )

        fig_move.update_yaxes(
            title="Induced Vertical Break",
            range=[-25, 25],
            zeroline=False
        )

        fig_move = style_fig(fig_move)

        st.plotly_chart(fig_move, use_container_width=True)
    else:
        st.info("Movement data not available.")

with g3:
    st.markdown('<div class="section-title">Release Point</div>', unsafe_allow_html=True)

    if {"RelSide", "RelHeight"}.issubset(filtered_df.columns) and not filtered_df.empty:
        fig_rel = px.scatter(
            filtered_df,
            x="RelSide",
            y="RelHeight",
            color="TaggedPitchType" if "TaggedPitchType" in filtered_df.columns else None,
            color_discrete_map=pitch_colors,
            hover_data=[
                c for c in [
                    "PitchNo",
                    "TaggedPitchType",
                    "PitchCall",
                    "RelSpeed",
                    "SessionDate",
                    "SessionType"
                ] if c in filtered_df.columns
            ]
        )

        fig_rel.update_traces(
            marker=dict(
                size=8,
                opacity=0.88,
                line=dict(width=0.6, color="white")
            )
        )

        avg_side = filtered_df["RelSide"].mean()
        avg_height = filtered_df["RelHeight"].mean()

        # Average release lines
        fig_rel.add_shape(
            type="line",
            x0=avg_side,
            x1=avg_side,
            y0=4.0,
            y1=7.5,
            line=dict(color="rgba(255,255,255,0.55)", width=2, dash="dash")
        )

        fig_rel.add_shape(
            type="line",
            x0=-3.5,
            x1=3.5,
            y0=avg_height,
            y1=avg_height,
            line=dict(color="rgba(255,255,255,0.55)", width=2, dash="dash")
        )

        # Consistency box around average
        fig_rel.add_shape(
            type="rect",
            x0=avg_side - 0.35,
            x1=avg_side + 0.35,
            y0=avg_height - 0.25,
            y1=avg_height + 0.25,
            line=dict(color="rgba(143,211,255,0.75)", width=2),
            fillcolor="rgba(143,211,255,0.08)"
        )

        fig_rel.update_xaxes(
            range=[-3.5, 3.5],
            title="Release Side",
            zeroline=False
        )

        fig_rel.update_yaxes(
            range=[4.0, 7.5],
            title="Release Height",
            zeroline=False
        )

        fig_rel = style_fig(fig_rel, height=430)

        fig_rel.update_layout(
            showlegend=True,
            legend_title_text="Pitch Type"
        )

        st.plotly_chart(fig_rel, use_container_width=True)

        # Release consistency table
        if "TaggedPitchType" in filtered_df.columns:
            rel_table = (
                filtered_df
                .groupby("TaggedPitchType")
                .agg(
                    Pitches=("TaggedPitchType", "count"),
                    AvgRelSide=("RelSide", "mean"),
                    AvgRelHeight=("RelHeight", "mean"),
                    RelSideSTD=("RelSide", "std"),
                    RelHeightSTD=("RelHeight", "std")
                )
                .reset_index()
            )

            for col in ["AvgRelSide", "AvgRelHeight", "RelSideSTD", "RelHeightSTD"]:
                rel_table[col] = rel_table[col].round(2)

            st.dataframe(rel_table, use_container_width=True, height=180)

    else:
        st.info("Release data not available.")

g4, g5, g6 = st.columns(3)

g4, g5, g6 = st.columns(3)

with g4:
    st.markdown('<div class="section-title">Session Velocity Trend</div>', unsafe_allow_html=True)

    if {"RelSpeed", "SessionDate"}.issubset(filtered_df.columns) and not filtered_df.empty:
        trend_group_cols = ["SessionDate"]

        if "SessionType" in filtered_df.columns:
            trend_group_cols.append("SessionType")

        if "TaggedPitchType" in filtered_df.columns:
            trend_group_cols.append("TaggedPitchType")

        velo_trend = (
            filtered_df
            .groupby(trend_group_cols)
            .agg(
                AvgVelo=("RelSpeed", "mean"),
                MaxVelo=("RelSpeed", "max"),
                Pitches=("RelSpeed", "count")
            )
            .reset_index()
        )

        velo_trend["AvgVelo"] = velo_trend["AvgVelo"].round(1)
        velo_trend["MaxVelo"] = velo_trend["MaxVelo"].round(1)

        fig_velo = px.line(
            velo_trend,
            x="SessionDate",
            y="AvgVelo",
            color="TaggedPitchType" if "TaggedPitchType" in velo_trend.columns else None,
            markers=True,
            color_discrete_map=pitch_colors,
            hover_data=[
                c for c in [
                    "SessionType",
                    "TaggedPitchType",
                    "AvgVelo",
                    "MaxVelo",
                    "Pitches"
                ] if c in velo_trend.columns
            ]
        )

        fig_velo.update_traces(
            line=dict(width=3),
            marker=dict(size=8, line=dict(width=1, color=WHITE))
        )

        fig_velo.update_xaxes(title="Session Date")
        fig_velo.update_yaxes(title="Average Velocity")

        fig_velo = style_fig(fig_velo, height=410)

        st.plotly_chart(fig_velo, use_container_width=True)

    elif "RelSpeed" in filtered_df.columns and not filtered_df.empty:
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

        fig_velo = style_fig(fig_velo, height=410)
        st.plotly_chart(fig_velo, use_container_width=True)

    else:
        st.info("Velocity data not available.")


with g5:
    st.markdown('<div class="section-title">Velocity Histogram</div>', unsafe_allow_html=True)

    if "RelSpeed" in filtered_df.columns and not filtered_df.empty:
        hist_df = filtered_df.copy()

        fig_hist = px.histogram(
            hist_df,
            x="RelSpeed",
            color="TaggedPitchType" if "TaggedPitchType" in hist_df.columns else None,
            color_discrete_map=pitch_colors,
            nbins=18,
            opacity=0.85,
            hover_data=[
                c for c in [
                    "TaggedPitchType",
                    "PitchCall",
                    "SessionDate",
                    "SessionType"
                ] if c in hist_df.columns
            ]
        )

        fig_hist.update_traces(
            marker_line_color="rgba(255,255,255,0.35)",
            marker_line_width=1
        )

        fig_hist.update_xaxes(title="Velocity")
        fig_hist.update_yaxes(title="Pitch Count")

        fig_hist = style_fig(fig_hist, height=410)

        st.plotly_chart(fig_hist, use_container_width=True)

    else:
        st.info("Velocity data not available.")


with g6:
    st.markdown('<div class="section-title">Velocity Percentiles</div>', unsafe_allow_html=True)

    if {"RelSpeed", "TaggedPitchType"}.issubset(filtered_df.columns) and not filtered_df.empty:
        velo_percentiles = (
            filtered_df
            .groupby("TaggedPitchType")
            .agg(
                Pitches=("RelSpeed", "count"),
                Avg=("RelSpeed", "mean"),
                Max=("RelSpeed", "max"),
                P90=("RelSpeed", lambda x: x.quantile(0.90)),
                P75=("RelSpeed", lambda x: x.quantile(0.75)),
                P50=("RelSpeed", lambda x: x.quantile(0.50)),
            )
            .reset_index()
        )

        for col in ["Avg", "Max", "P90", "P75", "P50"]:
            velo_percentiles[col] = velo_percentiles[col].round(1)

        st.dataframe(
            velo_percentiles,
            use_container_width=True,
            height=410
        )

    elif "RelSpeed" in filtered_df.columns and not filtered_df.empty:
        velo_percentiles = pd.DataFrame({
            "Metric": ["Avg", "Max", "P90", "P75", "P50"],
            "Velocity": [
                round(filtered_df["RelSpeed"].mean(), 1),
                round(filtered_df["RelSpeed"].max(), 1),
                round(filtered_df["RelSpeed"].quantile(0.90), 1),
                round(filtered_df["RelSpeed"].quantile(0.75), 1),
                round(filtered_df["RelSpeed"].quantile(0.50), 1),
            ]
        })

        st.dataframe(
            velo_percentiles,
            use_container_width=True,
            height=410
        )

    else:
        st.info("Velocity data not available.")
# TABLE + VIDEO
t1, t2 = st.columns([1.45, 1])

with t1:
    st.markdown('<div class="section-title">Full TrackMan Data</div>', unsafe_allow_html=True)

    show_cols = [c for c in [
        "SessionDate", "SessionType", "SourceFile",
        "PitchNo", "TaggedPitchType", "PitchCall", "RelSpeed",
        "SpinRate", "InducedVertBreak", "HorzBreak", "Extension",
        "PlateLocSide", "PlateLocHeight", "RelSide", "RelHeight"
    ] if c in filtered_df.columns]

    st.dataframe(filtered_df[show_cols] if show_cols else filtered_df, use_container_width=True, height=340)

with t2:
    st.markdown('<div class="section-title">Video Library</div>', unsafe_allow_html=True)

    player_folder = VIDEOS_DIR / clean_name(selected_player)
    player_folder.mkdir(exist_ok=True)

    video_files = list(player_folder.glob("*.mp4")) + list(player_folder.glob("*.mov"))

    if video_files:
        for video in video_files:
            st.video(str(video))
            st.caption(video.name)
    else:
        st.info("No videos uploaded for this player.")

st.markdown(
    "<div class='footer'>PLAYER EVALUATION PLATFORM v1.1 &nbsp; | &nbsp; CONFIDENTIAL — FOR INTERNAL USE ONLY</div>",
    unsafe_allow_html=True
)