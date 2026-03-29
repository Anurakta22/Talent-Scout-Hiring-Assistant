"""
sentiment_analyzer.py
---------------------
Text-based sentiment analysis for TalentScout Hiring Assistant.
Uses VADER (Valence Aware Dictionary and sEntiment Reasoner), which is
specifically tuned for conversational/social text — ideal for a chat context.

Sentiment labels map to candidate emotional states during the interview:
  Confident   → strong positive tone
  Positive    → mild positive / engaged
  Neutral     → flat / professional
  Uncertain   → mild negative / hesitant phrasing
  Stressed    → strong negative / frustrated tone
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Singleton analyzer — initializing once is enough
_analyzer = SentimentIntensityAnalyzer()

# Compound score thresholds (VADER range: -1.0 to +1.0)
THRESHOLDS = {
    "confident":  0.50,
    "positive":   0.10,
    "neutral_lo": -0.10,
    "uncertain":  -0.40,
    # below uncertain → "stressed"
}

SENTIMENT_META = {
    "Confident":  {"emoji": "😊", "color": "#34d399", "bar_color": "#10b981"},
    "Positive":   {"emoji": "🙂", "color": "#60a5fa", "bar_color": "#3b82f6"},
    "Neutral":    {"emoji": "😐", "color": "#94a3b8", "bar_color": "#64748b"},
    "Uncertain":  {"emoji": "😟", "color": "#fbbf24", "bar_color": "#f59e0b"},
    "Stressed":   {"emoji": "😰", "color": "#f87171", "bar_color": "#ef4444"},
}


def analyze(text: str) -> dict:
    """
    Analyze the sentiment of a candidate message.

    Args:
        text: Raw user message string.

    Returns:
        dict with keys:
            compound (float):  raw VADER compound score [-1, 1]
            label    (str):    human-readable sentiment label
            emoji    (str):    representative emoji
            color    (str):    hex color for the label
            bar_color(str):    hex color for progress bar
            score_pct(float):  0-100 value for UI progress bar
    """
    scores  = _analyzer.polarity_scores(text)
    compound = scores["compound"]
    label    = _compound_to_label(compound)
    meta     = SENTIMENT_META[label]

    # Map compound [-1, 1] → percentage [0, 100] for the progress bar
    score_pct = (compound + 1) / 2 * 100

    return {
        "compound":  compound,
        "label":     label,
        "emoji":     meta["emoji"],
        "color":     meta["color"],
        "bar_color": meta["bar_color"],
        "score_pct": round(score_pct, 1),
    }


def _compound_to_label(compound: float) -> str:
    """Map a VADER compound score to a candidate sentiment label."""
    if compound >= THRESHOLDS["confident"]:
        return "Confident"
    elif compound >= THRESHOLDS["positive"]:
        return "Positive"
    elif compound >= THRESHOLDS["neutral_lo"]:
        return "Neutral"
    elif compound >= THRESHOLDS["uncertain"]:
        return "Uncertain"
    else:
        return "Stressed"


def overall_sentiment(score_history: list[float]) -> dict:
    """
    Compute the overall sentiment from a session's compound score history.

    Args:
        score_history: List of compound floats from prior messages.

    Returns:
        Same structure as analyze(), based on the session average.
    """
    if not score_history:
        return analyze("")
    avg = sum(score_history) / len(score_history)
    label = _compound_to_label(avg)
    meta  = SENTIMENT_META[label]
    return {
        "compound":  round(avg, 3),
        "label":     label,
        "emoji":     meta["emoji"],
        "color":     meta["color"],
        "bar_color": meta["bar_color"],
        "score_pct": round((avg + 1) / 2 * 100, 1),
    }
