import base64
import html
from io import BytesIO
from pathlib import Path

import requests
import streamlit as st

st.set_page_config(
    page_title="CricPredictor",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ====================== Config ======================
DEFAULT_API_URL = "https://cricket-predictor-xi.vercel.app"
ENDPOINTS = {
    "next": "/NextOverRuns",
    "first": "/FirstInningsScore",
    "win": "/WinProbablity",
}
SLOGAN = "Every over tells a story. Predict the next chapter."

if "page" not in st.session_state:
    st.session_state.page = "home"


def go(name: str):
    st.session_state.page = name


page = st.session_state.page


# ====================== Background ======================
@st.cache_data
def background_css() -> str:
    """Finds background.* next to this file (or in ./static) and embeds it."""
    here = Path(__file__).parent
    for folder in (here, here / "static"):
        if not folder.exists():
            continue
        for f in sorted(folder.glob("background*")):
            ext = f.suffix.lower()
            if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                continue
            data = f.read_bytes()
            mime = "jpeg" if ext in (".jpg", ".jpeg") else ext[1:]
            if len(data) > 1_500_000:          # shrink very large pictures
                try:
                    from PIL import Image
                    img = Image.open(BytesIO(data)).convert("RGB")
                    img.thumbnail((1920, 1920))
                    buf = BytesIO()
                    img.save(buf, "JPEG", quality=82)
                    data, mime = buf.getvalue(), "jpeg"
                except Exception:
                    pass
            return f"url(data:image/{mime};base64,{base64.b64encode(data).decode()})"
    return "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"


overlay = (
    "linear-gradient(rgba(0,0,0,0.28), rgba(0,0,0,0.28))"
    if page == "home"
    else "linear-gradient(rgba(0,0,0,0.50), rgba(0,0,0,0.50))"
)

CSS = f"""
<style>
:root {{ --bg: {background_css()}; }}

/* page colour + picture layers live on <body>, behind everything */
html, body {{ background: #0b1620 !important; }}
body::before {{
    content: "";
    position: fixed; inset: 0; z-index: -1;
    background: var(--bg) center / cover no-repeat;
    filter: blur(28px) brightness(0.7);
    transform: scale(1.1);
}}
body::after {{
    content: "";
    position: fixed; inset: 0; z-index: -1;
    background-image: {overlay}, var(--bg);
    background-size: 100% 100%, cover;
    background-position: center, center;
    background-repeat: no-repeat;
}}

/* let the picture show through Streamlit's containers */
.stApp, [data-testid="stApp"], [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stHeader"] {{
    background: transparent !important;
}}
#MainMenu, footer, [data-testid="stToolbar"] {{ display: none !important; }}

/* text */
.stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp li,
[data-testid="stWidgetLabel"] p, div[role="radiogroup"] label p {{
    color: #ffffff;
}}
.stApp button p, .stApp button span {{ color: inherit !important; }}

/* inputs */
[data-baseweb="input"], [data-baseweb="base-input"] {{
    background: rgba(255,255,255,0.95) !important;
    border-radius: 8px;
}}
[data-baseweb="input"] input {{
    color: #111 !important;
    -webkit-text-fill-color: #111 !important;
}}
[data-testid="stNumberInput"] button {{
    background: #e9e9e9 !important;
    color: #111 !important;
}}

/* buttons */
.stButton > button {{
    border-radius: 999px;
    font-weight: 600;
    padding: 0.6rem 1.2rem;
}}
.stButton button[kind="primary"], .stButton button[data-testid="stBaseButton-primary"] {{
    background: #f5a623 !important;
    color: #111 !important;
    border: none !important;
}}
.stButton button[kind="secondary"], .stButton button[data-testid="stBaseButton-secondary"] {{
    background: rgba(255,255,255,0.12) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
}}

/* hero */
.hero {{ text-align: center; padding-top: 20vh; padding-bottom: 1.5rem; }}
.hero h1 {{ font-size: 4.2rem; font-weight: 800; margin-bottom: 0.5rem; color: #fff; }}
.hero p  {{ font-size: 1.5rem; opacity: 0.95; color: #fff; }}
.hero h1, .hero p {{ text-shadow: 0 2px 14px rgba(0,0,0,0.8); }}

/* results */
.metrics {{ display: flex; gap: 2.5rem; flex-wrap: wrap; margin: 0.5rem 0 0.8rem; }}
.metric .v {{ font-size: 2.6rem; font-weight: 800; color: #fff; }}
.metric .l {{ font-size: 0.9rem; opacity: 0.8; color: #fff; }}
.line {{ margin: 0.3rem 0; color: #fff; }}
.bar {{ height: 14px; border-radius: 99px; background: rgba(255,255,255,0.2); overflow: hidden; margin: 0.8rem 0 1rem; }}
.bar > div {{ height: 100%; background: #f5a623; }}
.box {{ padding: 1rem 1.1rem; border-radius: 8px; margin-top: 1rem; line-height: 1.55; color: #fff; }}
.box.analysis {{ background: rgba(70,140,255,0.22); border-left: 4px solid #5aa9ff; }}
.box.verdict  {{ background: rgba(46,160,67,0.30);  border-left: 4px solid #3fb950; font-weight: 600; }}
.box.error    {{ background: rgba(220,53,69,0.30);  border-left: 4px solid #ff5a6a; }}
</style>
"""

HIDE_SIDEBAR = """
<style>
[data-testid="stSidebar"], [data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"], [data-testid="stExpandSidebarButton"] {
    display: none !important;
}
</style>
"""

CARD = """
<style>
.block-container {
    background: rgba(0, 0, 0, 0.62);
    border-radius: 16px;
    padding: 2rem 2.5rem !important;
    margin: 3rem auto 2rem auto;
    max-width: 1200px;
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)
st.markdown(HIDE_SIDEBAR, unsafe_allow_html=True)
if page != "home":
    st.markdown(CARD, unsafe_allow_html=True)


# ====================== HTML helpers ======================
def h(x) -> str:
    return html.escape("" if x is None else str(x))


def hb(x) -> str:
    return h(x).replace("\n", "<br>")


def show(*parts: str):
    st.markdown("".join(parts), unsafe_allow_html=True)


def metrics_html(items) -> str:
    cells = "".join(
        f'<div class="metric"><div class="v">{h(v)}</div><div class="l">{h(l)}</div></div>'
        for v, l in items
    )
    return f'<div class="metrics">{cells}</div>'


def line_html(label, value) -> str:
    if value is None:
        return ""
    return f'<div class="line"><b>{h(label)}:</b> {h(value)}</div>'


def analysis_html(d: dict) -> str:
    text = d.get("Analysis") or d.get("Ananlysis")
    if not text:
        return ""
    return f'<div class="box analysis"><b>Analysis</b><br>{hb(text)}</div>'


def error_html(msg: str) -> str:
    return f'<div class="box error">{hb(msg)}</div>'


# ====================== API + inputs ======================
def call_api(path: str, payload: dict):
    api_url = DEFAULT_API_URL.rstrip("/")
    try:
        resp = requests.post(f"{api_url}{path}", json=payload, timeout=30)
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to server"
    except requests.exceptions.Timeout:
        return None, "The API took too long to respond."

    if resp.status_code == 200:
        return resp.json(), None

    if resp.status_code == 422:
        try:
            msgs = []
            for err in resp.json().get("detail", []):
                field = ".".join(str(x) for x in err.get("loc", []) if x != "body")
                text = err.get("msg", "").replace("Value error, ", "")
                msgs.append(f"{field}: {text}" if field else text)
            return None, "\n".join(msgs) or "Invalid input."
        except Exception:
            return None, "Invalid input."

    try:
        detail = resp.json().get("detail", resp.text)
    except Exception:
        detail = resp.text
    return None, f"Server error ({resp.status_code}): {detail}"


def common_inputs(prefix: str):
    c1, c2, c3 = st.columns(3)
    overs = c1.number_input("Overs completed", 1, 19, 10, key=f"{prefix}_overs")
    score = c2.number_input("Current score", 0, 400, 80, key=f"{prefix}_score")
    wickets = c3.number_input("Wickets lost", 0, 9, 2, key=f"{prefix}_wkts")
    return int(overs), int(score), int(wickets)


def last_over_inputs(prefix: str):
    c1, c2 = st.columns(2)
    runs = c1.number_input("Runs in last over", 0, 50, 8, key=f"{prefix}_rl")
    wkts = c2.number_input("Wickets in last over", 0, 6, 0, key=f"{prefix}_wl")
    return int(runs), int(wkts)


def client_check(score, wickets, runs_last=None, wkts_last=None, target=None):
    errors = []
    if runs_last is not None and runs_last > score:
        errors.append("Runs in last over can't exceed the score.")
    if wkts_last is not None and wkts_last > wickets:
        errors.append("Wickets in last over can't exceed total wickets.")
    if target is not None and target <= score:
        errors.append("Target must be greater than the current score.")
    return errors


def run(path, payload, errors, render):
    if errors:
        show(error_html("\n".join(errors)))
        return
    with st.spinner("Predicting..."):
        data, err = call_api(path, payload)
    if err:
        show(error_html(err))
    else:
        render(data)


# ====================== Left menu (every page except home) ======================
def render_menu():
    st.markdown("### CricPredictor")
    st.button("Next Over Runs", use_container_width=True,
              type="primary" if page == "next" else "secondary",
              on_click=go, args=("next",))
    st.button("First Innings Score", use_container_width=True,
              type="primary" if page == "first" else "secondary",
              on_click=go, args=("first",))
    st.button("Win Probability", use_container_width=True,
              type="primary" if page == "win" else "secondary",
              on_click=go, args=("win",))
    st.markdown("---")
    st.button("Home", use_container_width=True, on_click=go, args=("home",))


# ====================== Pages ======================
def page_home():
    show(f'<div class="hero"><h1>CricPredictor</h1><p>{h(SLOGAN)}</p></div>')
    _, mid, _ = st.columns([1, 1, 1])
    mid.button("Predict", type="primary", use_container_width=True,
               on_click=go, args=("menu",))


def page_menu():
    show('<div class="hero"><h1>Choose a prediction</h1>'
         "<p>Pick one from the menu on the left</p></div>")


def page_next():
    st.title("Next Over Runs")
    overs, score, wickets = common_inputs("no")
    innings = st.radio("Innings", [1, 2], horizontal=True)
    target = 0
    if innings == 2:
        target = int(st.number_input("Target", 1, 500, 160, key="no_target"))

    if st.button("Predict next over", type="primary"):
        errors = client_check(score, wickets, target=target if innings == 2 else None)
        payload = {"overs": overs, "Score": score, "Wickets": wickets,
                   "Innings": innings, "Target": target}

        def render(d):
            show(metrics_html([(d.get("Predicted_Runs"), "Predicted runs in next over")]),
                 line_html("Likely range", d.get("Likely_Range")),
                 line_html("Now", d.get("Current_Situation")),
                 line_html("After next over", d.get("After_Next_Over")),
                 analysis_html(d))

        run(ENDPOINTS["next"], payload, errors, render)


def page_first():
    st.title("First Innings Score")
    overs, score, wickets = common_inputs("fi")
    runs_last, wkts_last = last_over_inputs("fi")

    if st.button("Predict final score", type="primary"):
        errors = client_check(score, wickets, runs_last, wkts_last)
        payload = {"overs": overs, "Score": score, "Wickets": wickets,
                   "Runs_In_Last_Over": runs_last, "Wickets_In_Last_Over": wkts_last}

        def render(d):
            show(metrics_html([(d.get("Predicted_Score"), "Predicted final score")]),
                 line_html("Likely range", d.get("Likely_Range")),
                 line_html("Now", d.get("Current_Situation")),
                 line_html("Remaining", d.get("Remaining")),
                 analysis_html(d))

        run(ENDPOINTS["first"], payload, errors, render)


def page_win():
    st.title("Win Probability")
    overs, score, wickets = common_inputs("wp")
    runs_last, wkts_last = last_over_inputs("wp")
    target = int(st.number_input("Target", 1, 500, 170, key="wp_target"))

    if st.button("Predict win probability", type="primary"):
        errors = client_check(score, wickets, runs_last, wkts_last, target)
        payload = {"overs": overs, "Current_Score": score, "Total_Wickets": wickets,
                   "Runs_Last_Over": runs_last, "Wickets_Last_Over": wkts_last,
                   "Target": target}

        def render(d):
            def pct(x):
                try:
                    return float(str(x).replace("%", ""))
                except ValueError:
                    return 0.0

            chase = pct(d.get("Chasing_Team_Win", d.get("Chase Win", 0)))
            bowl = pct(d.get("Bowling_Team_Win", 0))
            width = min(max(chase, 0.0), 100.0)
            verdict = d.get("Verdict")
            show(metrics_html([(f"{chase:.1f}%", "Chasing team"),
                               (f"{bowl:.1f}%", "Bowling team")]),
                 f'<div class="bar"><div style="width:{width}%"></div></div>',
                 f'<div class="box verdict">{h(verdict)}</div>' if verdict else "",
                 line_html("Situation", d.get("Match_Situation")),
                 analysis_html(d))

        run(ENDPOINTS["win"], payload, errors, render)


if page == "home":
    page_home()
else:
    menu_col, content_col = st.columns([1, 3], gap="large")
    with menu_col:
        render_menu()
    with content_col:
        if page == "menu":
            page_menu()
        elif page == "next":
            page_next()
        elif page == "first":
            page_first()
        elif page == "win":
            page_win()
