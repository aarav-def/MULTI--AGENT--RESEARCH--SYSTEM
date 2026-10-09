import time
import streamlit as st

from agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Deep Research Lab",
    page_icon="🔶",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ----------------------------------------------------------------------------
# Theme: black + orange (dark mode)
# ----------------------------------------------------------------------------
ORANGE = "#FF7A00"
ORANGE_SOFT = "#FFA24D"
BLACK = "#000000"
PANEL = "#0E0E0E"
PANEL_2 = "#161616"
BORDER = "#2A2A2A"
MUTED = "#B58A5C"

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700;800&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'IBM Plex Sans', sans-serif;
    color: {ORANGE};
}}
.stApp {{
    background:
        radial-gradient(900px 400px at 85% -10%, rgba(255,122,0,0.14), transparent 60%),
        {BLACK};
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding-top: 2.2rem; max-width: 1100px; }}

/* Headings */
h1, h2, h3, h4 {{
    font-family: 'Bricolage Grotesque', sans-serif !important;
    color: {ORANGE} !important;
    letter-spacing: -0.02em;
}}
p, li, span, label, div {{ color: {ORANGE}; }}
.stMarkdown p, .stMarkdown li {{ color: {ORANGE_SOFT}; line-height: 1.7; }}
.stMarkdown a {{ color: {ORANGE}; text-decoration: underline; }}
.stMarkdown code {{ background: {PANEL_2}; color: {ORANGE}; border: 1px solid {BORDER}; }}
.stMarkdown blockquote {{ border-left: 3px solid {ORANGE}; color: {ORANGE_SOFT}; }}

/* Hero */
.hero-title {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: 3.4rem;
    line-height: 1.02;
    letter-spacing: -0.035em;
    color: {ORANGE};
    margin: 0 0 0.6rem 0;
}}
.hero-sub {{
    font-size: 1.08rem;
    color: {MUTED};
    max-width: 640px;
    margin-bottom: 1.6rem;
}}

/* Input */
.stTextInput input {{
    background: {PANEL} !important;
    color: {ORANGE} !important;
    border: 1.5px solid {BORDER} !important;
    border-radius: 12px !important;
    padding: 0.95rem 1.1rem !important;
    font-size: 1.05rem !important;
}}
.stTextInput input:focus {{
    border-color: {ORANGE} !important;
    box-shadow: 0 0 0 3px rgba(255,122,0,0.22) !important;
}}
.stTextInput input::placeholder {{ color: #7a5a3a !important; }}
.stTextInput label {{ display: none; }}

/* Buttons */
.stButton > button, .stDownloadButton > button {{
    background: {ORANGE};
    color: {BLACK} !important;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    font-size: 1.02rem;
    padding: 0.8rem 1.4rem;
    width: 100%;
    transition: background 0.15s ease, transform 0.1s ease;
}}
.stButton > button p, .stDownloadButton > button p {{ color: {BLACK} !important; }}
.stButton > button:hover, .stDownloadButton > button:hover {{
    background: {ORANGE_SOFT};
    color: {BLACK} !important;
}}
.stButton > button:active {{ transform: scale(0.98); }}
.stButton > button:disabled {{ background: #3a2a18; }}

/* Pipeline tracker */
.tracker {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 1.4rem 0 1.6rem 0;
}}
.step {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 14px 16px;
}}
.step .name {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
    color: {ORANGE};
}}
.step .desc {{ font-size: 0.86rem; color: {MUTED}; margin-top: 2px; }}
.step .state {{ font-size: 0.84rem; margin-top: 10px; color: #6b5033; }}
.step.active {{
    border-color: {ORANGE};
    background: linear-gradient(180deg, rgba(255,122,0,0.16), {PANEL});
    box-shadow: 0 0 0 1px {ORANGE} inset;
}}
.step.active .state {{ color: {ORANGE}; }}
.step.active .state::before {{
    content: "";
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: {ORANGE};
    margin-right: 8px;
    animation: pulse 1s ease-in-out infinite;
}}
.step.done {{ border-color: #7a3d00; }}
.step.done .state {{ color: {ORANGE_SOFT}; }}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.25; }}
}}
@media (prefers-reduced-motion: reduce) {{
    .step.active .state::before {{ animation: none; }}
}}
@media (max-width: 800px) {{
    .tracker {{ grid-template-columns: repeat(2, 1fr); }}
    .hero-title {{ font-size: 2.3rem; }}
}}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{ gap: 6px; border-bottom: 1px solid {BORDER}; }}
.stTabs [data-baseweb="tab"] {{
    background: transparent;
    color: {MUTED};
    border-radius: 10px 10px 0 0;
    padding: 10px 18px;
    font-weight: 500;
}}
.stTabs [aria-selected="true"] {{ color: {ORANGE} !important; background: {PANEL}; }}
.stTabs [data-baseweb="tab-highlight"] {{ background-color: {ORANGE} !important; }}

/* Report panel */
.panel {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
}}

/* Metrics + misc */
[data-testid="stMetricValue"] {{ color: {ORANGE}; font-family: 'Bricolage Grotesque'; }}
[data-testid="stMetricLabel"] p {{ color: {MUTED}; }}
.stAlert {{ background: {PANEL}; border: 1px solid {BORDER}; }}
hr {{ border-color: {BORDER}; }}
:focus-visible {{ outline: 2px solid {ORANGE}; outline-offset: 2px; }}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
STEPS = [
    ("Search", "Finds recent, reliable sources"),
    ("Read", "Scrapes the best page in depth"),
    ("Write", "Drafts the full report"),
    ("Review", "Critic scores and critiques it"),
]


def to_text(content) -> str:
    """LangChain messages can return a str or a list of content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(block.get("text", ""))
            else:
                parts.append(str(block))
        return "\n".join(p for p in parts if p)
    return str(content)


def render_tracker(placeholder, current: int, finished: bool = False):
    """current = index of the running step; finished = all steps done."""
    cards = []
    for i, (name, desc) in enumerate(STEPS):
        if finished or i < current:
            cls, state = "done", "Done"
        elif i == current:
            cls, state = "active", "Working"
        else:
            cls, state = "", "Waiting"
        cards.append(
            f'<div class="step {cls}"><div class="name">{name}</div>'
            f'<div class="desc">{desc}</div><div class="state">{state}</div></div>'
        )
    placeholder.markdown(
        f'<div class="tracker">{"".join(cards)}</div>', unsafe_allow_html=True
    )


def run_pipeline(topic: str, tracker_slot) -> dict:
    """Same logic as pipeline.run_research_pipeline, with live UI updates."""
    state = {}
    started = time.time()

    render_tracker(tracker_slot, 0)
    search_agent = build_search_agent()
    search_result = search_agent.invoke(
        {"messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]}
    )
    state["search_results"] = to_text(search_result["messages"][-1].content)

    render_tracker(tracker_slot, 1)
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f"Based on the following search results about '{topic}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{state['search_results'][:800]}",
                )
            ]
        }
    )
    state["scraped_content"] = to_text(reader_result["messages"][-1].content)

    render_tracker(tracker_slot, 2)
    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )
    state["report"] = to_text(
        writer_chain.invoke({"topic": topic, "research": research_combined})
    )

    render_tracker(tracker_slot, 3)
    state["feedback"] = to_text(critic_chain.invoke({"report": state["report"]}))

    render_tracker(tracker_slot, 4, finished=True)
    state["topic"] = topic
    state["seconds"] = round(time.time() - started, 1)
    return state


# ----------------------------------------------------------------------------
# Layout
# ----------------------------------------------------------------------------
st.markdown('<div class="hero-title">Deep Research Lab</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Four agents search the web, read the best source, write a report, '
    "and critique it. Enter a topic and watch each step run.</div>",
    unsafe_allow_html=True,
)

col_input, col_btn = st.columns([5, 1.3], vertical_alignment="center")
with col_input:
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Impact of solid-state batteries on electric vehicles",
        key="topic_input",
    )
with col_btn:
    run_clicked = st.button("Start research", disabled=not topic.strip())

tracker_slot = st.empty()
render_tracker(tracker_slot, -1)

if run_clicked and topic.strip():
    try:
        with st.spinner("Agents are researching. This can take a minute or two."):
            st.session_state["result"] = run_pipeline(topic.strip(), tracker_slot)
    except Exception as e:
        st.session_state.pop("result", None)
        render_tracker(tracker_slot, -1)
        st.error(
            f"The pipeline stopped with an error: {e}\n\n"
            "Check your API keys in .env and your internet connection, then try again."
        )

result = st.session_state.get("result")

if result:
    render_tracker(tracker_slot, 4, finished=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Topic", result["topic"][:28] + ("…" if len(result["topic"]) > 28 else ""))
    m2.metric("Report length", f"{len(result['report'].split()):,} words")
    m3.metric("Run time", f"{result['seconds']} s")

    tab_report, tab_feedback, tab_search, tab_scrape = st.tabs(
        ["Final report", "Critic feedback", "Search results", "Scraped content"]
    )

    with tab_report:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(result["report"])
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            "Download report (.md)",
            data=result["report"],
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_feedback:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(result["feedback"])
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_search:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(result["search_results"])
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_scrape:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown(result["scraped_content"])
        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Your report will appear here once the four steps finish.")