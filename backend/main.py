# main.py
# -------
# The main FastAPI backend. All API routes are defined here.
# Run with: uvicorn main:app --reload --port 8000
# API docs available at: http://localhost:8000/docs

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Import our custom modules
from generator import (
    generate_newsletter,
    generate_linkedin,
    generate_meta,
    generate_tiktok,
    generate_all_formats,
    run_brand_check
)
from scraper import scrape_url, extract_pdf_text

# Initialize FastAPI app
app = FastAPI(
    title="ALN Content Generator API",
    description="Generates ALN-specific content for newsletter, LinkedIn, Meta, and TikTok",
    version="1.0.0"
)

# CORS middleware — allows the frontend HTML file to call this API
# Without this, the browser will block all requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, replace * with your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- REQUEST MODELS ---
# Pydantic models define what JSON the API expects to receive

class TextInput(BaseModel):
    text: str                        # the article text pasted by the user
    format_type: str                 # "newsletter", "linkedin", "meta", "tiktok", "all"
    tiktok_type: Optional[str] = "informative"  # only used when format_type is "tiktok"
    meta_type: Optional[str] = "general"       # only used when format_type is "meta"
    run_brand_check: Optional[bool] = False      # whether to also run the brand checker

class UrlInput(BaseModel):
    url: str                         # the URL to scrape
    format_type: str
    tiktok_type: Optional[str] = "informative"
    meta_type: Optional[str] = "general"
    run_brand_check: Optional[bool] = False

class ArticleListInput(BaseModel):
    # Used specifically for newsletter generation with multiple articles
    articles: list[dict]             # list of {headline, url, content, impact_score}


# --- ROUTES ---

@app.get("/")
def root():
    """Health check — confirms the API is running."""
    return {"status": "ALN Content Generator is running"}


@app.post("/generate/text")
async def generate_from_text(data: TextInput):
    """
    Main generation endpoint. Accepts pasted article text and returns
    generated content in the requested format.
    """
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        # Generate content based on which format was requested
        if data.format_type == "all":
            result = generate_all_formats(data.text, data.tiktok_type, data.meta_type)
        elif data.format_type == "newsletter":
            result = {"newsletter": generate_newsletter([{
                "headline": "User input",
                "url": "",
                "content": data.text,
                "impact_score": None
            }])}
        elif data.format_type == "linkedin":
            result = {"linkedin": generate_linkedin(data.text)}
        elif data.format_type == "meta":
            result = {"meta": generate_meta(data.text, data.meta_type)}
        elif data.format_type == "tiktok":
            result = {"tiktok": generate_tiktok(data.text, data.tiktok_type)}
        else:
            raise HTTPException(status_code=400, detail=f"Unknown format_type: {data.format_type}")

        # Optionally run brand check on the first output
        if data.run_brand_check:
            first_output = list(result.values())[0]
            brand = run_brand_check(first_output, data.format_type)
            result["brand_check"] = brand["brand_check_result"]

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/url")
async def generate_from_url(data: UrlInput):
    """
    Scrapes the given URL, extracts article text, then generates content.
    """
    # First scrape the URL
    scraped = scrape_url(data.url)

    if "error" in scraped:
        raise HTTPException(status_code=400, detail=scraped["error"])

    # Use the scraped text as input — same logic as /generate/text
    text = scraped["content"]

    try:
        if data.format_type == "all":
            result = generate_all_formats(text, data.tiktok_type, data.meta_type)
        elif data.format_type == "newsletter":
            result = {"newsletter": generate_newsletter([{
                "headline": scraped["headline"],
                "url": data.url,
                "content": text,
                "impact_score": None
            }])}
        elif data.format_type == "linkedin":
            result = {"linkedin": generate_linkedin(text)}
        elif data.format_type == "meta":
            result = {"meta": generate_meta(text, data.meta_type)}
        elif data.format_type == "tiktok":
            result = {"tiktok": generate_tiktok(text, data.tiktok_type)}
        else:
            raise HTTPException(status_code=400, detail=f"Unknown format_type: {data.format_type}")

        if data.run_brand_check:
            first_output = list(result.values())[0]
            brand = run_brand_check(first_output, data.format_type)
            result["brand_check"] = brand["brand_check_result"]

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/pdf")
async def generate_from_pdf(
    file: UploadFile = File(...),
    format_type: str = Form(...),
    tiktok_type: str = Form("informative"),
    meta_type: str = Form("general"),
    run_brand_check_flag: bool = Form(False)
):
    """
    Accepts an uploaded PDF file, extracts text, then generates content.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()
    extracted = extract_pdf_text(file_bytes)

    if "error" in extracted:
        raise HTTPException(status_code=400, detail=extracted["error"])

    text = extracted["content"]

    try:
        if format_type == "all":
            result = generate_all_formats(text, tiktok_type, meta_type)
        elif format_type == "linkedin":
            result = {"linkedin": generate_linkedin(text)}
        elif format_type == "meta":
            result = {"meta": generate_meta(text, meta_type)}
        elif format_type == "tiktok":
            result = {"tiktok": generate_tiktok(text, tiktok_type)}
        elif format_type == "newsletter":
            result = {"newsletter": generate_newsletter([{
                "headline": "PDF upload",
                "url": "",
                "content": text,
                "impact_score": None
            }])}
        else:
            raise HTTPException(status_code=400, detail=f"Unknown format_type: {format_type}")

        if run_brand_check_flag:
            first_output = list(result.values())[0]
            brand = run_brand_check(first_output, format_type)
            result["brand_check"] = brand["brand_check_result"]

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/newsletter/articles")
async def generate_newsletter_from_articles(data: ArticleListInput):
    """
    Dedicated newsletter route that accepts multiple articles at once.
    Used when the scraper has already collected this week's articles.
    Each article should have: headline, url, content, impact_score.
    """
    if not data.articles:
        raise HTTPException(status_code=400, detail="No articles provided.")

    try:
        result = generate_newsletter(data.articles)
        return {"newsletter": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
