"""
AI Video Assistant — Streamlit UI
Wraps the existing pipeline (utils.audio_processor, core.transcriber,
core.summarize, core.extractor, core.rag_engine) in a single-page interface.
"""

import streamlit as st
from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ────────────────────────────────────────────────────────────────────────
# Page config
# ────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wavelength — AI Video Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ────────────────────────────────────────────────────────────────────────
# Design tokens & global styles
# ────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg:        #0B0E14;
        --surface:   #141821;
        --surface2:  #1A1F2B;
        --border:    #242B3A;
        --ink:       #EDEDED;
        --muted:     #8B92A5;
        --accent:    #F2B84B;
        --accent-dim:#7A5E2A;
        --good:      #5FD0A6;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg) !important;
        color: var(--ink);
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { display: none; }
    .block-container { padding-top: 2.2rem; max-width: 1100px; }

    /* ---------- Hero ---------- */
    .hero-wrap {
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 6px;
    }
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 2.4rem;
        letter-spacing: -0.02em;
        color: var(--ink);
        margin: 0;
    }
    .hero-title span { color: var(--accent); }
    .hero-sub {
        font-family: 'Inter', sans-serif;
        color: var(--muted);
        font-size: 0.98rem;
        margin-top: 2px;
        margin-bottom: 1.8rem;
        letter-spacing: 0.01em;
    }

    /* waveform glyph */
    .wave { display: flex; align-items: center; gap: 3px; height: 34px; }
    .wave span {
        display: block;
        width: 4px;
        border-radius: 2px;
        background: var(--accent);
        animation: wv 1.2s ease-in-out infinite;
    }
    .wave span:nth-child(1){height:10px; animation-delay:0s;}
    .wave span:nth-child(2){height:22px; animation-delay:0.15s;}
    .wave span:nth-child(3){height:32px; animation-delay:0.3s;}
    .wave span:nth-child(4){height:18px; animation-delay:0.45s;}
    .wave span:nth-child(5){height:26px; animation-delay:0.6s;}
    .wave span:nth-child(6){height:12px; animation-delay:0.75s;}
    @keyframes wv {
        0%, 100% { transform: scaleY(0.4); opacity: 0.6; }
        50% { transform: scaleY(1); opacity: 1; }
    }
    .wave.idle span { animation: none; transform: scaleY(0.55); opacity: 0.5; }

    /* ---------- Pipeline strip ---------- */
    .pipe {
        display: flex;
        align-items: center;
        margin: 1.6rem 0 2.2rem 0;
        gap: 0;
    }
    .pipe-stage {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 16px;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: var(--surface);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: var(--muted);
        white-space: nowrap;
    }
    .pipe-stage.active {
        border-color: var(--accent);
        color: var(--accent);
        background: rgba(242,184,75,0.08);
    }
    .pipe-stage.done {
        border-color: var(--good);
        color: var(--good);
        background: rgba(95,208,166,0.06);
    }
    .pipe-dot {
        width: 7px; height: 7px; border-radius: 50%;
        background: var(--muted);
    }
    .pipe-stage.active .pipe-dot { background: var(--accent); box-shadow: 0 0 8px var(--accent); }
    .pipe-stage.done .pipe-dot { background: var(--good); }
    .pipe-line {
        flex: 1;
        height: 1px;
        background: var(--border);
        margin: 0 6px;
    }

    /* ---------- Cards ---------- */
    .card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1rem;
    }
    .card-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 10px;
        display: block;
    }
    .card h3 {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--ink);
        margin-top: 0;
    }

    /* transcript box */
    .transcript-box {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        line-height: 1.65;
        color: #C7CCDA;
        background: var(--surface2);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        max-height: 320px;
        overflow-y: auto;
        white-space: pre-wrap;
    }

    /* list items for action/decisions/questions */
    .item-row {
        display: flex;
        gap: 10px;
        padding: 9px 0;
        border-bottom: 1px solid var(--border);
        font-size: 0.93rem;
        color: var(--ink);
    }
    .item-row:last-child { border-bottom: none; }
    .item-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--accent);
        margin-top: 2px;
        flex-shrink: 0;
    }

    /* Tabs */
    [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--border); }
    [data-baseweb="tab"] {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--muted);
        font-size: 0.92rem;
    }
    [aria-selected="true"] { color: var(--accent) !important; }

    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        background: var(--surface2) !important;
        border: 1px solid var(--border) !important;
        color: var(--ink) !important;
        border-radius: 9px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }

    /* Buttons */
    .stButton button, .stFormSubmitButton button {
        background: var(--accent) !important;
        color: #14110A !important;
        border: none !important;
        border-radius: 9px !important;
        font-weight: 600 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        padding: 0.55rem 1.4rem !important;
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }
    .stButton button:hover, .stFormSubmitButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(242,184,75,0.28);
    }

    /* Radio / segmented control look */
    div[role="radiogroup"] { gap: 8px; }

    /* File uploader */
    [data-testid="stFileUploaderDropzone"] {
        background: var(--surface2) !important;
        border: 1.5px dashed var(--border) !important;
        border-radius: 12px !important;
    }

    /* Chat bubbles */
    .chat-user {
        background: var(--surface2);
        border: 1px solid var(--border);
        border-radius: 12px 12px 4px 12px;
        padding: 10px 14px;
        margin: 6px 0;
        color: var(--ink);
        max-width: 80%;
        margin-left: auto;
        font-size: 0.92rem;
    }
    .chat-assistant {
        background: rgba(242,184,75,0.07);
        border: 1px solid var(--accent-dim);
        border-radius: 12px 12px 12px 4px;
        padding: 10px 14px;
        margin: 6px 0;
        color: var(--ink);
        max-width: 85%;
        font-size: 0.92rem;
    }

    /* Misc cleanup */
    hr { border-color: var(--border); }
    .stAlert { border-radius: 10px; }
    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────────────────────────────────
# Session state
# ────────────────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state.result = None
if "stage" not in st.session_state:
    st.session_state.stage = "idle"  # idle | input | transcript | insights | chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "error" not in st.session_state:
    st.session_state.error = None

STAGE_ORDER = ["input", "transcript", "insights", "chat"]
STAGE_LABELS = {
    "input": "Input",
    "transcript": "Transcript",
    "insights": "Insights",
    "chat": "Chat",
}


def stage_index(stage: str) -> int:
    return STAGE_ORDER.index(stage) if stage in STAGE_ORDER else -1


# ────────────────────────────────────────────────────────────────────────
# Hero
# ────────────────────────────────────────────────────────────────────────
wave_class = "wave" if st.session_state.stage not in ("idle",) else "wave idle"
st.markdown(
    f"""
    <div class="hero-wrap">
        <div class="{wave_class}">
            <span></span><span></span><span></span><span></span><span></span><span></span>
        </div>
        <h1 class="hero-title">Wave<span>length</span></h1>
    </div>
    <p class="hero-sub">Turn any meeting or video into a transcript, a summary, and a conversation — point it at a link or a file.</p>
    """,
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────────────────────────────────
# Pipeline strip (visual progress)
# ────────────────────────────────────────────────────────────────────────
current_idx = stage_index(st.session_state.stage)
pipe_html = '<div class="pipe">'
for i, key in enumerate(STAGE_ORDER):
    cls = "pipe-stage"
    if i < current_idx or (key == "chat" and st.session_state.result):
        cls += " done"
    elif i == current_idx:
        cls += " active"
    pipe_html += f'<div class="{cls}"><span class="pipe-dot"></span>{STAGE_LABELS[key]}</div>'
    if i < len(STAGE_ORDER) - 1:
        pipe_html += '<div class="pipe-line"></div>'
pipe_html += "</div>"
st.markdown(pipe_html, unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────
# Input section
# ────────────────────────────────────────────────────────────────────────
if st.session_state.result is None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<span class="card-label">Source</span>', unsafe_allow_html=True)

    input_mode = st.radio(
        "Choose input type",
        ["YouTube URL", "Upload file"],
        horizontal=True,
        label_visibility="collapsed",
    )

    source = None
    if input_mode == "YouTube URL":
        source = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
        )
    else:
        uploaded = st.file_uploader(
            "Upload audio or video",
            type=["mp4", "mp3", "wav", "m4a", "mov", "webm"],
            label_visibility="collapsed",
        )
        if uploaded is not None:
            tmp_path = f"/tmp/{uploaded.name}"
            with open(tmp_path, "wb") as f:
                f.write(uploaded.getbuffer())
            source = tmp_path

    col_a, col_b = st.columns([2, 1])
    with col_a:
        language = st.selectbox(
            "Language",
            ["english", "hinglish"],
            label_visibility="collapsed",
        )
    with col_b:
        run = st.button("Run Assistant →", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if run:
        if not source:
            st.session_state.error = "Add a YouTube URL or upload a file first."
        else:
            st.session_state.error = None
            st.session_state.stage = "transcript"
            try:
                with st.status("Processing your source...", expanded=True) as status:
                    status.update(label="Extracting audio...")
                    chunks = process_input(source)

                    status.update(label="Transcribing...")
                    transcript = transcribe_all(chunks, language)

                    status.update(label="Generating title...")
                    title = generate_title(transcript)

                    status.update(label="Summarizing...")
                    summary = summarize(transcript)

                    status.update(label="Extracting action items...")
                    action_items = extract_action_items(transcript)

                    status.update(label="Extracting key decisions...")
                    decisions = extract_key_decisions(transcript)

                    status.update(label="Extracting open questions...")
                    questions = extract_questions(transcript)

                    status.update(label="Building chat index...")
                    rag_chain = build_rag_chain(transcript)

                    status.update(label="Done", state="complete")

                st.session_state.result = {
                    "title": title,
                    "transcript": transcript,
                    "summary": summary,
                    "action_items": action_items,
                    "key_decisions": decisions,
                    "open_questions": questions,
                    "rag_chain": rag_chain,
                }
                st.session_state.stage = "chat"
                st.rerun()
            except Exception as e:
                st.session_state.error = f"Something went wrong: {e}"
                st.session_state.stage = "input"

    if st.session_state.error:
        st.error(st.session_state.error)

# ────────────────────────────────────────────────────────────────────────
# Results
# ────────────────────────────────────────────────────────────────────────
else:
    result = st.session_state.result

    top_l, top_r = st.columns([5, 1])
    with top_l:
        st.markdown(
            f"<h3 style='font-family:Space Grotesk; margin-bottom:0;'>{result['title']}</h3>",
            unsafe_allow_html=True,
        )
    with top_r:
        if st.button("New session", use_container_width=True):
            st.session_state.result = None
            st.session_state.stage = "idle"
            st.session_state.chat_history = []
            st.rerun()

    tab_summary, tab_transcript, tab_chat = st.tabs(["📋 Insights", "📝 Transcript", "💬 Chat"])

    # ---- Insights tab ----
    with tab_summary:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="card-label">Summary</span>', unsafe_allow_html=True)
        st.write(result["summary"])
        st.markdown("</div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        def render_list_card(col, label, items):
            with col:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f'<span class="card-label">{label}</span>', unsafe_allow_html=True)
                items_list = items if isinstance(items, (list, tuple)) else [items]
                if not items_list or (len(items_list) == 1 and not str(items_list[0]).strip()):
                    st.markdown(
                        "<span style='color:var(--muted); font-size:0.88rem;'>Nothing found here.</span>",
                        unsafe_allow_html=True,
                    )
                else:
                    rows = "".join(
                        f'<div class="item-row"><span class="item-tag">{i+1:02d}</span><span>{str(it)}</span></div>'
                        for i, it in enumerate(items_list)
                    )
                    st.markdown(rows, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

        render_list_card(c1, "Action Items", result["action_items"])
        render_list_card(c2, "Key Decisions", result["key_decisions"])
        render_list_card(c3, "Open Questions", result["open_questions"])

    # ---- Transcript tab ----
    with tab_transcript:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="card-label">Full Transcript</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="transcript-box">{result["transcript"]}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            "Download transcript (.txt)",
            data=result["transcript"],
            file_name="transcript.txt",
            mime="text/plain",
        )

    # ---- Chat tab ----
    with tab_chat:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<span class="card-label">Ask about this meeting</span>', unsafe_allow_html=True)

        for role, msg in st.session_state.chat_history:
            css = "chat-user" if role == "user" else "chat-assistant"
            st.markdown(f'<div class="{css}">{msg}</div>', unsafe_allow_html=True)

        with st.form("chat_form", clear_on_submit=True):
            q_col, b_col = st.columns([5, 1])
            with q_col:
                question = st.text_input(
                    "Ask a question",
                    placeholder="What did we decide about the launch date?",
                    label_visibility="collapsed",
                )
            with b_col:
                send = st.form_submit_button("Ask", use_container_width=True)

        if send and question.strip():
            st.session_state.chat_history.append(("user", question.strip()))
            try:
                answer = ask_question(result["rag_chain"], question.strip())
            except Exception as e:
                answer = f"Couldn't get an answer: {e}"
            st.session_state.chat_history.append(("assistant", answer))
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)