# 🤝 TalentScout — AI Hiring Assistant

An intelligent chatbot that conducts initial candidate screening for technology positions. Powered by **Groq LLM (Llama 3.3 70B)** and built with **Streamlit**.

---

## 📋 Project Overview

TalentScout's Hiring Assistant, **Disha**, guides candidates through a structured screening interview:

1. **Greets & onboards** the candidate with a warm welcome
2. **Collects** key info: name, email, phone, experience, role, location
3. **Takes the tech stack** declaration from the candidate
4. **Auto-generates** tailored technical questions per technology
5. **Saves** a session record to local storage and gracefully wraps up

### ✨ Premium Bonus Features Included
- **UI/UX Overhaul**: Glassmorphism sidebar, animated gradient hero, live 5-step progress tracker, and premium chat bubbles.
- **Multilingual Support**: Auto-detects the candidate's language and natively translates both responses and internal state tracking.
- **Sentiment Analysis**: Live VADER NLP mood tracker measuring candidate emotional polarity.
- **Candidate Analytics**: Tracks average response time (Hesitation metric) and a session-wide Confidence Index (0-100%).

---

## 🚀 Quick Start

### 1. Clone / Download the project

```bash
git clone <your-repo-url>
cd talentscout
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

```bash
# Copy the example file
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```

Edit `.env` and add your Groq API key:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
```

> **Get a free key** at [console.groq.com](https://console.groq.com) — no credit card required.

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` in your browser.

---

## ☁️ Cloud Deployment (Hugging Face Spaces)

This project is fully ready for deployment to **Hugging Face Spaces** using the Streamlit SDK. 

### Step-by-Step Deployment:
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and create a new Space.
2. Select **Streamlit** as the Space SDK.
3. Once created, go to the Space Settings -> **Variables and secrets**.
4. Add a new secret:
   - Name: `GROQ_API_KEY`
   - Value: `<your_groq_api_key>`
5. Clone the space repository locally or upload your files directly via the HF UI. You need to upload:
   - `app.py`, `chatbot.py`, `data_handler.py`, `prompt_templates.py`, `sentiment_analyzer.py`
   - `requirements.txt`
6. The Space will automatically install the requirements and launch `app.py`.

*Note: In the cloud, the `data/candidates.json` file is reset every time the container restarts, which is expected behavior for a cloud-hosted demo without an external database.*

---

## 📁 Project Structure

```
talentscout/
├── app.py                  # Streamlit UI + session management
├── chatbot.py              # Groq API integration + conversation helpers
├── prompt_templates.py     # System prompt + tech question prompt
├── data_handler.py         # JSON-based candidate data storage
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore
├── data/
│   └── candidates.json     # Auto-created; stores candidate records
└── README.md
```

---

## 🧠 Technical Details

| Component       | Choice                              |
|-----------------|-------------------------------------|
| Frontend        | Streamlit 1.32+                     |
| LLM Provider    | Groq API                            |
| Model           | `llama-3.3-70b-versatile`           |
| Data Storage    | Local JSON (`data/candidates.json`) |
| Env Management  | python-dotenv                       |

---

## ✍️ Prompt Design

### System Prompt (`prompt_templates.py → SYSTEM_PROMPT`)

The system prompt establishes Aria's persona and enforces a **strict staged conversation flow**:

```
GREETING → INFO_GATHERING → TECH_STACK → TECH_QUESTIONS → WRAP_UP
```

Key design decisions:
- **Progressive info collection**: asks 1–2 fields at a time to avoid overwhelming candidates
- **Topic guardrails**: explicitly instructs the model to reject off-topic queries and redirect
- **Exit handling**: recognises natural language exit phrases (bye, quit, exit, stop, etc.)
- **Formatted output**: enforces structured `### Technology\n1. Q\n2. Q` format for technical questions
- **Data privacy notice**: reminds candidates why data is collected

### Tech Question Prompt (`TECH_QUESTION_PROMPT`)

A standalone prompt template used to regenerate questions if needed. Uses few-shot formatting constraints to ensure consistent, grouped output per technology.

---

## 🔒 Data Privacy

- Candidate data is stored **locally** in `data/candidates.json`
- Only recruitment-relevant fields are persisted
- No data is sent to third parties beyond the Groq LLM API for response generation
- Sensitive fields (email, phone) are stored solely for internal recruiter use
- The `data/` directory is `.gitignore`d so candidate data is never committed to version control

---

## ⚠️ Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Keeping LLM on-topic | Strong system prompt with explicit off-topic rejection rules |
| Multi-turn context | Full conversation history passed with every API call |
| Sidebar field extraction | Heuristic inference: what the assistant asks *next* tells us what was just answered |
| Graceful exit | Pre-call exit keyword detection before LLM call (no wasted API round-trip) |
| Auto-save on completion | Keyword detection on assistant response (`"next steps"`, `"we'll be in touch"`, etc.) |

---

## 💬 Usage Guide

1. Launch the app with `streamlit run app.py`
2. Aria will greet you automatically — just start typing
3. Answer each question naturally; Aria will guide you through the stages
4. When asked for your tech stack, list technologies separated by commas:
   > *"Python, Django, PostgreSQL, Docker, React"*
5. Aria will then ask 3–5 questions per technology
6. Type `bye`, `exit`, or `quit` at any time to end the session
7. Use the **Start New Session** button in the sidebar to restart

---

## 📦 Dependencies

```
streamlit>=1.32.0
groq>=0.5.0
python-dotenv>=1.0.0
vaderSentiment>=3.3.2
```
