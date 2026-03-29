"""
chatbot.py
----------
Core chatbot logic for TalentScout Hiring Assistant.
Handles Groq API communication and conversation state management.
"""

import os
from groq import Groq
from dotenv import load_dotenv
from prompt_templates import SYSTEM_PROMPT

load_dotenv()

# Exit keywords that gracefully end the conversation
EXIT_KEYWORDS = {"exit", "quit", "bye", "goodbye", "stop", "end", "cancel"}

# Fields to collect in order during INFO_GATHERING stage
REQUIRED_FIELDS = [
    "full_name",
    "email",
    "phone",
    "years_of_experience",
    "desired_positions",
    "current_location",
]

FIELD_LABELS = {
    "full_name": "Full Name",
    "email": "Email Address",
    "phone": "Phone Number",
    "years_of_experience": "Years of Experience",
    "desired_positions": "Desired Position(s)",
    "current_location": "Current Location",
}


def get_groq_client() -> Groq:
    """Initialize and return the Groq API client."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Please set it in your .env file."
        )
    return Groq(api_key=api_key)


def is_exit_intent(user_input: str) -> bool:
    """
    Check whether the user's message signals intent to end the conversation.

    Args:
        user_input: Raw user message string.

    Returns:
        True if an exit keyword is detected.
    """
    tokens = user_input.lower().split()
    return any(token in EXIT_KEYWORDS for token in tokens)


def chat(
    user_message: str,
    conversation_history: list,
    model: str = "llama-3.3-70b-versatile",
) -> str:
    """
    Send a message to the Groq LLM and return the assistant's reply.

    Args:
        user_message:         The latest user input.
        conversation_history: Full message history (list of role/content dicts).
        model:                Groq model identifier to use.

    Returns:
        The assistant's response string.
    """
    client = get_groq_client()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )

    return response.choices[0].message.content


def get_farewell_message() -> str:
    """Return a graceful exit message when the user ends the conversation early."""
    return (
        "Thank you for your time! 😊 It was a pleasure speaking with you. "
        "If you ever wish to complete the screening, feel free to come back. "
        "We at **TalentScout** wish you all the best in your career journey! 🚀"
    )


def get_initial_greeting() -> str:
    """Return the first message shown when a new session starts."""
    return (
        "👋 **Hello and welcome to TalentScout!**\n\n"
        "I'm **Disha**, your AI hiring assistant. I'm here to help with the initial screening "
        "for positions at our partner companies.\n\n"
        "Here's what we'll do today:\n"
        "1. 📋 Collect some basic information about you\n"
        "2. 💻 Learn about your tech stack\n"
        "3. ❓ Ask a few technical questions tailored to your skills\n\n"
        "> 🔒 *Your data is collected solely for recruitment purposes and handled in compliance "
        "with data privacy standards.*\n\n"
        "You can type **exit** or **bye** at any time to end the session.\n\n"
        "Let's get started! Could you please share your **full name**?"
    )
