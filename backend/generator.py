# generator.py
# ------------
# All Gemini API calls live here.
# Each function takes article text as input and returns generated content as a string.
# We import all prompts from aln_context.py — do not hardcode any prompts here.

import os
import sys
from dotenv import load_dotenv

# Load the .env file so GEMINI_API_KEY is available
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
env_path = os.path.abspath(env_path)
load_dotenv(env_path, override=True)

# Get the API key - try multiple sources
api_key = os.getenv("GEMINI_API_KEY")

# If not found in env, try to read from .env file manually
if not api_key:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, '..', '.env')
    env_path = os.path.abspath(env_path)
    print(f"GEMINI_API_KEY not in environment, reading from: {env_path}")
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            content = f.read()
            print(f"File content: {content[:100]}")
            for line in content.split('\n'):
                if 'GEMINI_API_KEY' in line:
                    parts = line.split('=')
                    if len(parts) == 2:
                        api_key = parts[1].strip()
                        print(f"Found GEMINI_API_KEY: {api_key[:30]}...")
                        break

if not api_key:
    # HARDCODE for debugging - replace with actual key from aistudio.google.com
    print("WARNING: Using hardcoded API key!")
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyCWnNfkbP_jEcPPRIVpsEJbt8ZR7ak4VKE")

# Set it for the Google Auth library
os.environ["GOOGLE_API_KEY"] = api_key

# Add parent directory to path so we can import aln_context.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from aln_context import get_system_prompt, CURRENT_EPISODE, CURRENT_DATE

# Now import and configure Gemini after env vars are set
import google.generativeai as genai

# Configure Gemini with your API key - this sets it globally
genai.configure(api_key=api_key)

# Create model - it will use the globally configured API key
model = genai.GenerativeModel("gemini-2.0-flash")


def call_gemini(system_prompt: str, user_message: str) -> str:
    """
    Single function that handles all Gemini API calls.
    Combines system prompt + user message into one prompt
    since Gemini handles it slightly differently than OpenAI.
    """
    try:
        full_prompt = f"{system_prompt}\n\n{user_message}"
        response = model.generate_content(full_prompt)
        # Check if response has text attribute
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                parts = candidate.content.parts
                if parts:
                    return str(parts[0])
        return str(response)
    except Exception as e:
        import traceback
        error_msg = f"Gemini API Error: {str(e)}\n{traceback.format_exc()}"
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
    """
    system_prompt = get_system_prompt("newsletter")

    # Add episode number and date to the user message
    user_message = f"""Episode Number: {CURRENT_EPISODE}
Date: {CURRENT_DATE}

Here are this week's articles. Select the most significant one as the Main Issue
and use the remaining relevant ones as sub-issues. Use the URLs exactly as provided.

{format_articles_for_prompt(articles)}
"""
    return call_gemini(system_prompt, user_message)


def generate_linkedin(text: str) -> str:
    """
    Takes a single article text or topic description and generates a LinkedIn post.
    """
    system_prompt = get_system_prompt("linkedin")
    return call_gemini(system_prompt, f"Generate a LinkedIn post from this content:\n\n{text}")


def generate_twitter(text: str) -> str:
    """
    Takes a single article text or topic description and generates a Twitter/X thread.
    """
    system_prompt = get_system_prompt("twitter")
    return call_gemini(system_prompt, f"Generate a Twitter/X thread:\n\n{text}")


def generate_tiktok(text: str, tiktok_type: str = "informative") -> str:
    """
    Takes content and a TikTok type and generates a video script.

    tiktok_type options: informative, event, hiring, culture, fun
    The type is injected into the user message so the AI adapts accordingly.
    """
    system_prompt = get_system_prompt("tiktok")
    return call_gemini(system_prompt, f"TikTok type: {tiktok_type}\n\nContent:\n{text}")


def run_brand_check(content: str, format_type: str) -> dict:
    """
    Runs a brand tone check on any generated content.
    Returns a dict with the brand check result.

    format_type is just for labeling in the response (e.g. "LinkedIn", "Newsletter")
    """
    system_prompt = get_system_prompt("brand_check")
    result = call_gemini(system_prompt, f"Format type: {format_type}\n\nContent:\n{content}")
    return {"brand_check_result": result}


def generate_all_formats(text: str, tiktok_type: str = "informative") -> dict:
    """
    Convenience function that generates all 4 formats from a single text input.
    Used when the user selects "Generate All" in the UI.
    Returns a dict with all 4 outputs.

    Note: This makes 4 separate API calls. Each costs roughly $0.001-0.002.
    Total cost per "Generate All" click: roughly $0.004-0.008 (less than 1 paisa).
    """
    return {
        "linkedin": generate_linkedin(text),
        "twitter": generate_twitter(text),
        "tiktok": generate_tiktok(text, tiktok_type),
        # For single text input, newsletter treats the text as one article
        "newsletter": generate_newsletter([{
            "headline": "User provided content",
            "url": "",
            "content": text,
            "impact_score": None
        }])
    }
