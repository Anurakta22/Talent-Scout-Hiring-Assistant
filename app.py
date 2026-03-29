"""
app.py
------
Streamlit frontend for the TalentScout Hiring Assistant chatbot.
Manages session state, renders the chat UI, and orchestrates conversation flow.
Enhanced UI: animated header, progress tracker, glassmorphism sidebar, premium chat bubbles.
"""

import streamlit as st
import re
import time
from chatbot import chat, is_exit_intent, get_initial_greeting, get_farewell_message
from data_handler import save_candidate
from sentiment_analyzer import analyze, overall_sentiment

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="TalentScout | Hiring Assistant",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Premium CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide default Streamlit chrome (keep sidebar toggle visible) ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }

/* Style the sidebar collapse/expand toggle arrow */
[data-testid="collapsedControl"] {
    background: rgba(99,102,241,0.15) !important;
    border-radius: 0 10px 10px 0 !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-left: none !important;
    color: #818cf8 !important;
    top: 50% !important;
}
[data-testid="collapsedControl"]:hover {
    background: rgba(99,102,241,0.3) !important;
}

/* ── Main background ── */
.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #111827 60%, #0d1f3c 100%);
    min-height: 100vh;
}

/* ── Animated header banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1e2a45 0%, #162032 50%, #1a1040 100%);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 20px;
    padding: 2.2rem 2.5rem;
    margin-bottom: 1.5rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(99,102,241,0.15), 0 2px 8px rgba(0,0,0,0.4);
    position: relative;
    overflow: hidden;
    animation: fadeSlideIn 0.6s ease-out;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(99,102,241,0.08) 0%, transparent 60%),
                radial-gradient(circle at 70% 50%, rgba(236,72,153,0.06) 0%, transparent 60%);
    animation: rotateBg 12s linear infinite;
}
@keyframes rotateBg {
    from { transform: rotate(0deg); }
    to   { transform: rotate(360deg); }
}
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(-20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    position: relative;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    color: #94a3b8;
    font-size: 1rem;
    margin: 0.4rem 0 0;
    font-weight: 400;
    position: relative;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    color: #a5b4fc;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 0.25rem 0.9rem;
    border-radius: 20px;
    margin-bottom: 0.8rem;
    position: relative;
}

/* ── Progress tracker ── */
.progress-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin: 1.2rem 0 0.5rem;
    flex-wrap: wrap;
}
.prog-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    min-width: 80px;
}
.prog-dot {
    width: 32px; height: 32px;
    border-radius: 50%;
    border: 2px solid rgba(99,102,241,0.3);
    background: rgba(30,42,69,0.8);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    color: #475569;
    transition: all 0.4s ease;
    position: relative;
    z-index: 1;
}
.prog-dot.active {
    border-color: #818cf8;
    background: rgba(99,102,241,0.2);
    color: #c7d2fe;
    box-shadow: 0 0 12px rgba(99,102,241,0.4);
    animation: pulse 2s infinite;
}
.prog-dot.done {
    border-color: #34d399;
    background: rgba(52,211,153,0.15);
    color: #6ee7b7;
    box-shadow: 0 0 8px rgba(52,211,153,0.25);
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 12px rgba(99,102,241,0.4); }
    50%       { box-shadow: 0 0 20px rgba(99,102,241,0.7); }
}
.prog-label {
    font-size: 0.65rem;
    color: #475569;
    text-align: center;
    font-weight: 500;
    letter-spacing: 0.3px;
}
.prog-label.active { color: #a5b4fc; }
.prog-label.done   { color: #6ee7b7; }
.prog-line {
    width: 40px; height: 2px;
    background: rgba(99,102,241,0.15);
    margin-bottom: 18px;
    transition: background 0.4s ease;
}
.prog-line.done { background: rgba(52,211,153,0.4); }

/* ── Chat container ── */
.chat-area {
    max-width: 820px;
    margin: 0 auto;
}

/* ── Chat message overrides ── */
[data-testid="stChatMessage"] {
    background: rgba(17, 24, 39, 0.6) !important;
    border: 1px solid rgba(99,102,241,0.1) !important;
    border-radius: 16px !important;
    backdrop-filter: blur(8px);
    margin-bottom: 0.6rem !important;
    transition: border-color 0.2s;
    animation: msgIn 0.3s ease-out;
}
[data-testid="stChatMessage"]:hover {
    border-color: rgba(99,102,241,0.25) !important;
}
@keyframes msgIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: rgba(17,24,39,0.8) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 14px !important;
    color: #e2e8f0 !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(129,140,248,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}

/* ── Sidebar glassmorphism ── */
[data-testid="stSidebar"] {
    background: rgba(13,19,33,0.92) !important;
    border-right: 1px solid rgba(99,102,241,0.15) !important;
    backdrop-filter: blur(16px);
}

.sidebar-header {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 1rem;
}

.info-card {
    background: rgba(99,102,241,0.07);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.2s, background 0.2s;
}
.info-card:hover {
    background: rgba(99,102,241,0.12);
    border-color: rgba(99,102,241,0.3);
}
.info-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 2px;
}
.info-value {
    font-size: 0.88rem;
    color: #e2e8f0;
    font-weight: 400;
    word-break: break-word;
}
.info-value.empty { color: #475569; font-style: italic; }

/* ── New session button ── */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(79,70,229,0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(79,70,229,0.5) !important;
}

/* ── Session ended notice ── */
.ended-notice {
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 14px;
    padding: 1.5rem;
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    margin-top: 1rem;
}

/* ── Privacy notice ── */
.privacy-note {
    font-size: 0.75rem;
    color: #374151;
    text-align: center;
    line-height: 1.5;
    padding: 0.5rem;
    border-top: 1px solid rgba(99,102,241,0.1);
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------
def init_session() -> None:
    """Initialize all required session state variables."""
    defaults = {
        "messages": [],
        "history": [],
        "candidate_info": {},
        "conversation_ended": False,
        "greeted": False,
        "data_saved": False,
        "stage": 0,
        "sentiment_scores": [],      # list of per-message compound floats
        "last_sentiment": None,      # most recent message sentiment dict
        "response_times": [],        # list of seconds taken to respond
        "question_start_time": None, # timestamp of the last AI message
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _extract_candidate_info(user_msg: str, assistant_reply: str) -> None:
    """
    Heuristically update candidate_info and stage based on conversation context.
    Strategy: infer which field the assistant just asked for next, store the
    previous user answer under the matching field.
    """
    info = st.session_state.candidate_info
    lower = assistant_reply.lower()

    if "email" in lower and "full_name" not in info:
        info["full_name"] = user_msg.strip()
        st.session_state.stage = max(st.session_state.stage, 1)

    elif "phone" in lower and "email" not in info:
        info["email"] = user_msg.strip()
        st.session_state.stage = max(st.session_state.stage, 1)

    elif "years" in lower and "phone" not in info:
        info["phone"] = user_msg.strip()
        st.session_state.stage = max(st.session_state.stage, 1)

    elif "position" in lower and "years_of_experience" not in info:
        info["years_of_experience"] = user_msg.strip()
        st.session_state.stage = max(st.session_state.stage, 1)

    elif "location" in lower and "desired_positions" not in info:
        info["desired_positions"] = user_msg.strip()
        st.session_state.stage = max(st.session_state.stage, 1)

    elif "tech stack" in lower and "current_location" not in info:
        info["current_location"] = user_msg.strip()
        st.session_state.stage = max(st.session_state.stage, 2)

    elif (
        any(kw in lower for kw in ["technical question", "let's start with", "here are your questions", "first question"])
        and "tech_stack" not in info
    ):
        info["tech_stack"] = user_msg.strip()
        st.session_state.stage = max(st.session_state.stage, 3)

    completion_signals = ["next steps", "thank you for", "screening is complete", "we'll be in touch", "all the best"]
    if any(kw in lower for kw in completion_signals):
        st.session_state.stage = 4

    st.session_state.candidate_info = info


def _validate_input(user_input: str, assistant_reply: str, info: dict) -> str | None:
    """
    Hardcoded validation to intercept invalid data before it reaches the LLM.
    Returns an error message string if invalid, or None if valid.
    """
    lower = assistant_reply.lower()

    # If the assistant just asked for an email
    if "email" in lower and "?" in assistant_reply and "email" not in info:
        # Basic regex for email validation
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", user_input.strip()):
            return "⚠️ That doesn't look like a valid email address. Please provide a valid email (e.g., name@example.com)."

    # If the assistant just asked for a phone number
    if "phone" in lower and "?" in assistant_reply and "phone" not in info:
        # Strip spaces and punctuation to check digits
        digits = re.sub(r'\D', '', user_input)
        if len(digits) < 10:
            return "⚠️ That doesn't look like a valid phone number. Please provide a complete phone number with at least 10 digits."

    return None


def render_progress_bar(stage: int) -> None:
    """Render an animated interview progress tracker."""
    steps = [
        ("👋", "Greeting"),
        ("📋", "Info"),
        ("💻", "Tech Stack"),
        ("❓", "Questions"),
        ("✅", "Done"),
    ]
    html = '<div class="progress-wrap">'
    for i, (icon, label) in enumerate(steps):
        if i < stage:
            dot_cls   = "done"
            label_cls = "done"
            line_cls  = "done"
        elif i == stage:
            dot_cls   = "active"
            label_cls = "active"
            line_cls  = ""
        else:
            dot_cls   = ""
            label_cls = ""
            line_cls  = ""

        html += f'''
        <div class="prog-step">
            <div class="prog-dot {dot_cls}">{icon}</div>
            <div class="prog-label {label_cls}">{label}</div>
        </div>'''
        if i < len(steps) - 1:
            html += f'<div class="prog-line {line_cls}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_sentiment_panel() -> None:
    """
    Render a live mood tracker panel in the sidebar.
    Shows current message sentiment + session overall trend.
    """
    scores = st.session_state.sentiment_scores
    last   = st.session_state.last_sentiment

    st.markdown('<div class="sidebar-header">🎭 Mood Tracker</div>', unsafe_allow_html=True)

    if not scores:
        st.markdown(
            '<div class="info-card"><div class="info-value empty">Waiting for candidate responses…</div></div>',
            unsafe_allow_html=True,
        )
        return

    # ── Latest message sentiment ──
    if last:
        st.markdown(
            f'''<div class="info-card">
                <div class="info-label">💬 Latest Message</div>
                <div style="display:flex; align-items:center; gap:8px; margin-top:4px;">
                    <span style="font-size:1.4rem">{last["emoji"]}</span>
                    <span style="color:{last["color"]}; font-weight:600; font-size:0.95rem">{last["label"]}</span>
                    <span style="color:#475569; font-size:0.75rem">({last["compound"]:+.2f})</span>
                </div>
                <div style="background:rgba(255,255,255,0.06); border-radius:6px; height:6px; margin-top:8px; overflow:hidden;">
                    <div style="width:{last["score_pct"]}%; height:100%; background:{last["bar_color"]};
                                border-radius:6px; transition:width 0.5s ease;"></div>
                </div>
            </div>''',
            unsafe_allow_html=True,
        )

    # ── Overall session sentiment ──
    overall = overall_sentiment(scores)
    st.markdown(
        f'''<div class="info-card">
            <div class="info-label">📊 Session Overall</div>
            <div style="display:flex; align-items:center; gap:8px; margin-top:4px;">
                <span style="font-size:1.4rem">{overall["emoji"]}</span>
                <span style="color:{overall["color"]}; font-weight:600; font-size:0.95rem">{overall["label"]}</span>
                <span style="color:#475569; font-size:0.75rem">({overall["compound"]:+.2f} avg)</span>
            </div>
            <div style="background:rgba(255,255,255,0.06); border-radius:6px; height:6px; margin-top:8px; overflow:hidden;">
                <div style="width:{overall["score_pct"]}%; height:100%; background:{overall["bar_color"]};
                            border-radius:6px; transition:width 0.5s ease;"></div>
            </div>
            <div style="color:#475569; font-size:0.72rem; margin-top:6px;">{len(scores)} message(s) analyzed</div>
        </div>''',
        unsafe_allow_html=True,
    )


def render_analytics_panel() -> None:
    """Render the Candidate Analytics panel (Confidence Index & Avg Response Time)."""
    scores = st.session_state.sentiment_scores
    times = st.session_state.response_times

    # Only show meaningful data if we have at least 1 response
    if not scores or not times:
        return

    st.markdown('<div class="sidebar-header">📈 Candidate Analytics</div>', unsafe_allow_html=True)

    # Calculate Confidence Index (0-100% based on VADER compound)
    overall = overall_sentiment(scores)
    confidence = overall["score_pct"]
    
    # Calculate Average Response Time
    avg_time = sum(times) / len(times)
    
    # Determine tags
    if avg_time < 15:
        time_tag = "⚡ Fast"
        time_color = "#34d399"
    elif avg_time < 45:
        time_tag = "⏱️ Normal"
        time_color = "#60a5fa"
    else:
        time_tag = "⏳ Thoughtful"
        time_color = "#fbbf24"

    conf_color = overall["color"]

    st.markdown(
        f'''<div class="info-card">
            <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                <div>
                    <div class="info-label">Confidence Index</div>
                    <div style="font-size:1.4rem; font-weight:700; color:{conf_color};">
                        {confidence}%
                    </div>
                </div>
                <div style="text-align:right;">
                    <div class="info-label">Avg Response</div>
                    <div style="font-size:1.4rem; font-weight:700; color:#e2e8f0;">
                        {avg_time:.1f}s
                    </div>
                    <div style="font-size:0.7rem; color:{time_color}; margin-top:2px;">{time_tag}</div>
                </div>
            </div>
        </div>''',
        unsafe_allow_html=True,
    )


def render_sidebar(info: dict) -> None:
    """Render the glassmorphism sidebar with candidate info cards."""
    with st.sidebar:
        st.markdown('<div class="sidebar-header">📋 Candidate Profile</div>', unsafe_allow_html=True)

        fields = [
            ("👤", "Name",       info.get("full_name", "")),
            ("📧", "Email",      info.get("email", "")),
            ("📍", "Location",   info.get("current_location", "")),
            ("🏢", "Role",       info.get("desired_positions", "")),
            ("⏱️", "Experience", info.get("years_of_experience", "")),
            ("🛠️", "Tech Stack", info.get("tech_stack", "")),
        ]

        for icon, label, val in fields:
            val_class = "info-value" if val else "info-value empty"
            display   = val if val else "Not yet collected"
            st.markdown(
                f'''<div class="info-card">
                    <div class="info-label">{icon} {label}</div>
                    <div class="{val_class}">{display}</div>
                </div>''',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        render_sentiment_panel()
        render_analytics_panel()
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔄 Start New Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown(
            '<div class="privacy-note">🔒 Data collected solely for recruitment '
            'purposes in compliance with privacy standards.</div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Initialize
# ---------------------------------------------------------------------------
init_session()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
render_sidebar(st.session_state.candidate_info)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-badge">✦ AI-Powered Recruitment</div>
    <h1 class="hero-title">🌟 TalentScout</h1>
    <p class="hero-subtitle">Your intelligent hiring assistant — meet <strong>Disha</strong></p>
</div>
""", unsafe_allow_html=True)

# Progress bar
render_progress_bar(st.session_state.stage)

st.markdown("<br>", unsafe_allow_html=True)

if not st.session_state.greeted:
    greeting = get_initial_greeting()
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    st.session_state.history.append({"role": "assistant",  "content": greeting})
    st.session_state.greeted = True
    st.session_state.question_start_time = time.time()

# ---------------------------------------------------------------------------
# Render Chat History
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
    avatar = "🌟" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Chat Input
# ---------------------------------------------------------------------------
if st.session_state.conversation_ended:
    st.markdown("""
    <div class="ended-notice">
        🎉 Session complete! Click <strong>Start New Session</strong> in the sidebar to begin again.
    </div>
    """, unsafe_allow_html=True)
else:
    user_input = st.chat_input("Type your message here… (type 'exit' to end)")

    if user_input:
        # Calculate response time
        if st.session_state.question_start_time:
            resp_time = time.time() - st.session_state.question_start_time
            st.session_state.response_times.append(resp_time)

        # -- Display user message --
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # -- Exit intent --
        if is_exit_intent(user_input):
            farewell = get_farewell_message()
            if not st.session_state.data_saved and st.session_state.candidate_info:
                st.session_state.candidate_info["interview_completed"] = False
                save_candidate(st.session_state.candidate_info)
                st.session_state.data_saved = True
            with st.chat_message("assistant", avatar="🌟"):
                st.markdown(farewell)
            st.session_state.messages.append({"role": "assistant", "content": farewell})
            st.session_state.conversation_ended = True
            st.session_state.stage = 4
            st.rerun()

        else:
            # -- Input Validation Interceptor --
            # Check what the assistant asked in the LAST message
            validation_error = None
            if len(st.session_state.history) > 0:
                last_assistant_msg = st.session_state.history[-1]["content"]
                validation_error = _validate_input(user_input, last_assistant_msg, st.session_state.candidate_info)

            if validation_error:
                # Reject it immediately without calling the LLM
                with st.chat_message("assistant", avatar="🌟"):
                    st.markdown(validation_error)
                st.session_state.history.append({"role": "user", "content": user_input})
                st.session_state.history.append({"role": "assistant", "content": validation_error})
                st.session_state.messages.append({"role": "assistant", "content": validation_error})

            else:
                # -- Regular LLM response --
                with st.chat_message("assistant", avatar="🌟"):
                    with st.spinner("Disha is typing…"):
                        try:
                            response = chat(user_input, st.session_state.history)
                        except ValueError as e:
                            response = (
                                f"⚠️ **Configuration error:** {e}\n\n"
                                "Please ensure your `GROQ_API_KEY` is set in the `.env` file."
                            )
                        except Exception as e:
                            response = (
                                "⚠️ An unexpected error occurred. Please try again.\n\n"
                                f"*Error: {e}*"
                            )
                    
                    # Clean the hidden state tracking tag before displaying
                    clean_response = re.sub(r'\[STAGE:.*?\]', '', response, flags=re.IGNORECASE).strip()
                    st.markdown(clean_response)

                # -- Update history --
                st.session_state.history.append({"role": "user",      "content": user_input})
                st.session_state.history.append({"role": "assistant",  "content": response})  # LLM needs to remember the tags
                st.session_state.messages.append({"role": "assistant", "content": clean_response}) # User doesn't see them

                # -- Sentiment analysis on user message --
                sentiment = analyze(user_input)
                st.session_state.sentiment_scores.append(sentiment["compound"])
                st.session_state.last_sentiment = sentiment

                # -- Extract info + update stage --
                _extract_candidate_info(user_input, response)

                # -- Auto-save on completion --
                completion_signals = ["next steps", "thank you for", "screening is complete", "we'll be in touch", "all the best"]
                if (
                    not st.session_state.data_saved
                    and any(kw in response.lower() for kw in completion_signals)
                    and st.session_state.candidate_info
                ):
                    st.session_state.candidate_info["interview_completed"] = True
                    save_candidate(st.session_state.candidate_info)
                    st.session_state.data_saved = True
                
                # Restart the timer for the next user response
                st.session_state.question_start_time = time.time()
