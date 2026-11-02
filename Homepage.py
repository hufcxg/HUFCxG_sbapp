import subprocess, sys
import streamlit as st

def _install_private():
    try:
        import HUFCxG
    except ImportError:
        import os
        token = st.secrets.get("GITHUB_PAT", "")
        owner = st.secrets.get("GITHUB_OWNER", "")
        repo  = st.secrets.get("GITHUB_REPO", "")
        
        if not all([token, owner, repo]):
            st.error("Missing one or more secrets: GITHUB_PAT, GITHUB_OWNER, GITHUB_REPO")
            st.stop()
        
        install_dir = "/tmp/hufcxg_packages"
        os.makedirs(install_dir, exist_ok=True)
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install",
            f"git+https://{token}@github.com/{owner}/{repo}.git",
            "--target", install_dir,
            "--quiet", "--disable-pip-version-check",
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            st.error(f"Package install failed:\n{result.stderr}")
            st.stop()
        
        if install_dir not in sys.path:
            sys.path.insert(0, install_dir)

_install_private()

from HUFCxG.theme import apply_theme, APP_NAME

st.set_page_config(
    page_title=APP_NAME,
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_theme()

# ── Password gate ──────────────────────────────────────────────────────────────

def _check_password() -> bool:
    if st.session_state.get("authenticated"):
        return True

    st.markdown(
        "<style>[data-testid='stSidebar'], [data-testid='collapsedControl'] "
        "{ display: none; }</style>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:18vh'></div>", unsafe_allow_html=True)
    col, _ = st.columns([2, 5])
    with col:
        st.markdown('<div class="kicker"></div>', unsafe_allow_html=True)
        st.markdown(f"# {APP_NAME}")
        pwd = st.text_input("Password", type="password", key="pwd_input")
        if pwd:
            if pwd == st.secrets.get("APP_PASSWORD", ""):
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    return False


if not _check_password():
    st.stop()

# ── Index ──────────────────────────────────────────────────────────────────────

st.markdown('<div class="kicker">Recruitment analysis</div>', unsafe_allow_html=True)
st.markdown(f"# {APP_NAME}")
st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

SECTIONS = [
    ("01", "Player statistics", "pages/1_Player_Statistics.py",
     "Percentiles, radar, role fit, shot maps, similar players and notes for one player."),
    ("02", "Scouting", "pages/2_Scouting.py",
     "The watchlist, and the Discard / Potential / Immediate pipeline."),
    ("03", "Player search", "pages/3_Player_Search.py",
     "Filter by stat ranges within a position group, or rank players by role fit."),
]

for num, name, path, desc in SECTIONS:
    c_num, c_name, c_desc = st.columns([0.5, 3, 8], vertical_alignment="center")
    c_num.markdown(f'<span class="index-row num" style="border:0;padding:0">{num}</span>',
                   unsafe_allow_html=True)
    with c_name:
        st.page_link(path, label=name)
    c_desc.markdown(f'<span style="color:#8a8f98">{desc}</span>', unsafe_allow_html=True)
    st.markdown("<hr style='margin:0.35rem 0'>", unsafe_allow_html=True)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
if st.button("Log out", key="logout"):
    st.session_state["authenticated"] = False
    st.rerun()
