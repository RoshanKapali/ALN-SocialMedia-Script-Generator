# generator.py
# All Groq API calls live here.
import os, sys
from groq import Groq
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
env_path = os.path.abspath(env_path)
load_dotenv(env_path, override=True)

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from aln_context import get_system_prompt, CURRENT_EPISODE, CURRENT_DATE

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

def call_groq(system_prompt: str, user_message: str, max_tokens: int = 1000) -> str:
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
    formatted = []
    for i, article in enumerate(articles, 1):
        block = f'''ARTICLE {i}:
Headline: {article.get("headline", "No headline")}
URL: {article.get("url", "No URL provided")}
Impact Score: {article.get("impact_score", "N/A")}
Content: {article.get("content", "")}
'''
        formatted.append(block)
    return "\n---\n".join(formatted)

def generate_newsletter(articles: list[dict]) -> str:
    system_prompt = get_system_prompt("newsletter")
    user_message = f'''Episode Number: {CURRENT_EPISODE}
Date: {CURRENT_DATE}

Here are this week's articles. Select the most significant one as the Main Issue
and use the remaining relevant ones as sub-issues. Use the URLs exactly as provided.

{format_articles_for_prompt(articles)}
'''
    return call_groq(system_prompt, user_message, max_tokens=1500)

def generate_linkedin(text: str) -> str:
    system_prompt = get_system_prompt("linkedin")
    return call_groq(system_prompt, f"Generate a LinkedIn post from this content:\n\n{text}", max_tokens=400)

def generate_meta(text: str, meta_type: str = "general") -> str:
    system_prompt = get_system_prompt("meta")
    return call_groq(system_prompt, f"Meta post type: {meta_type}\n\nContent:\n{text}", max_tokens=600)

def generate_tiktok(text: str, tiktok_type: str = "informative") -> str:
    system_prompt = get_system_prompt("tiktok")
    return call_groq(system_prompt, f"TikTok type: {tiktok_type}\n\nContent:\n{text}", max_tokens=600)

def run_brand_check(content: str, format_type: str) -> dict:
    system_prompt = get_system_prompt("brand_check")
    result = call_groq(system_prompt, f"Format type: {format_type}\n\nContent:\n{content}", max_tokens=400)
    return {"brand_check_result": result}

def generate_all_formats(text: str, tiktok_type: str = "informative", meta_type: str = "general") -> dict:
    return {
        "linkedin": generate_linkedin(text),
        "meta": generate_meta(text, meta_type),
        "tiktok": generate_tiktok(text, tiktok_type),
        "newsletter": generate_newsletter([{"headline": "User provided content", "url": "", "content": text, "impact_score": None}])
    }
