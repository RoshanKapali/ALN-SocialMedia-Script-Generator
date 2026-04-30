# generator.py
# ------------
# All Groq API calls live here.
# Each function takes article text as input and returns generated content as a string.
# We import all prompts from aln_context.py — do not hardcode any prompts here.

import os
import sys
from groq import Groq
from dotenv import load_dotenv

# Load the .env file so GROQ_API_KEY is available
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
env_path = os.path.abspath(env_path)
load_dotenv(env_path, override=True)

from aln_context import get_system_prompt, CURRENT_EPISODE, CURRENT_DATE

# Initialize Groq client with API key from .env
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Best free model on Groq — high quality, fast
MODEL = "llama-3.3-70b-versatile"


def call_groq(system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
    """
    Single function that handles all Groq API calls.
    Uses the same OpenAI-style chat completions interface.
    max_tokens controls how long the response can be.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        import traceback
        error_msg = f"Groq API Error: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise Exception(error_msg)


def format_articles_for_prompt(articles: list[dict]) -> str:
    """
    Takes a list of article dicts and formats them into a structured string
    that the AI can read clearly.

    Each article dict should have:
    - headline (str)
    - url (str)
    - content (str)
    - impact_score (float, optional)

    Returns a formatted string to be used as the user message.
    """
    formatted = []
    for i, article in enumerate(articles, 1):
        block = f"""ARTICLE {i}:
Headline: {article.get('headline', 'No headline')}
URL: {article.get('url', 'No URL provided')}
Impact Score: {article.get('impact_score', 'N/A')}
Content: {article.get('content', '')}
"""
        formatted.append(block)
    return "\n---\n".join(formatted)


def generate_newsletter(articles: list[dict]) -> str:
    """
    Takes a list of article dicts and generates a Governance Weekly newsletter.
    The main issue is selected based on impact score or content significance.
    Sub-issues include Read More links from the provided URLs.
    Newsletter needs more tokens since it's a longer output.
    """
    system_prompt = get_system_prompt("newsletter")
    user_message = f"""Episode Number: {CURRENT_EPISODE}
Date: {CURRENT_DATE}

Here are this week's articles. Select the most significant one as the Main Issue
and use the remaining relevant ones as sub-issues. Use the URLs exactly as provided.

{format_articles_for_prompt(articles)}
"""
    return call_groq(system_prompt, user_message, max_tokens=1500)


def generate_linkedin(text: str) -> str:
    """
    Takes a single article text or topic description and generates a LinkedIn post.
    """
    system_prompt = get_system_prompt("linkedin")
    return call_groq(
        system_prompt,
        f"Generate a LinkedIn post from this content:\n\n{text}",
        max_tokens=400
    )


def generate_meta(text: str, meta_type: str = "general") -> str:
    """
    Takes a single article text or topic description and generates a Meta post.
    meta_type options: general, governance_weekly, hiring
    """
    system_prompt = get_system_prompt("meta")
    return call_groq(
        system_prompt,
        f"Meta post type: {meta_type}\n\nContent:\n{text}",
        max_tokens=400
    )


def generate_tiktok(text: str, tiktok_type: str = "informative") -> str:
    """
    Takes content and a TikTok type and generates a video script.
    tiktok_type options: informative, event, hiring, culture, fun
    """
    system_prompt = get_system_prompt("tiktok")
    return call_groq(
        system_prompt,
        f"TikTok type: {tiktok_type}\n\nContent:\n{text}",
        max_tokens=600
    )


def run_brand_check(content: str, format_type: str) -> dict:
    """
    Runs a brand tone check on any generated content.
    Returns a dict with the brand check result.
    """
    system_prompt = get_system_prompt("brand_check")
    result = call_groq(
        system_prompt,
        f"Format type: {format_type}\n\nContent:\n{content}",
        max_tokens=400
    )
    return {"brand_check_result": result}


def generate_all_formats(text: str, tiktok_type: str = "informative", meta_type: str = "general") -> dict:
    """
    Generates all 4 formats from a single text input.
    Used when the user selects 'Generate All' in the UI.
    Makes 4 separate Groq API calls — all free.
    """
    return {
        "linkedin": generate_linkedin(text),
        "meta": generate_meta(text, meta_type),
        "tiktok": generate_tiktok(text, tiktok_type),
        "newsletter": generate_newsletter([{
            "headline": "User provided content",
            "url": "",
            "content": text,
            "impact_score": None
        }])
    }