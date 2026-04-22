# scraper.py
# ----------
# Handles extracting clean article text from two sources:
# 1. A URL — fetches the webpage and pulls the main article text
# 2. An uploaded PDF file — extracts all text from the PDF
#
# The extracted text is then passed to generator.py for AI processing.

import requests
import pdfplumber
from bs4 import BeautifulSoup
import io


def scrape_url(url: str) -> dict:
    """
    Fetches a webpage and extracts the main article text.
    Works best with news websites like Kathmandu Post, Ratopati, etc.

    Returns a dict with:
    - headline: the page title or og:title
    - content: the extracted article text
    - url: the original URL passed in
    """
    try:
        headers = {
            # Pretend to be a browser so websites don't block the request
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # raises error if page doesn't load

        soup = BeautifulSoup(response.text, "html.parser")

        # Try to get the headline from og:title meta tag first, then fall back to <title>
        og_title = soup.find("meta", property="og:title")
        headline = og_title["content"] if og_title else (soup.title.string if soup.title else "No headline found")

        # Remove script and style tags — they add noise to the extracted text
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Try to find the main article body — common tags used by news sites
        article_body = (
            soup.find("article") or
            soup.find("div", class_=lambda c: c and "article" in c.lower()) or
            soup.find("div", class_=lambda c: c and "content" in c.lower()) or
            soup.find("main") or
            soup.find("body")
        )

        # Extract text and clean up whitespace
        raw_text = article_body.get_text(separator=" ", strip=True)
        # Collapse multiple spaces and newlines into single spaces
        clean_text = " ".join(raw_text.split())

        return {
            "headline": headline.strip(),
            "content": clean_text[:4000],  # limit to 4000 chars to keep API costs low
            "url": url
        }

    except requests.exceptions.Timeout:
        return {"error": "The URL took too long to load. Try again or paste the text manually."}
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to that URL. Check if the link is valid."}
    except Exception as e:
        return {"error": f"Could not extract content from URL: {str(e)}"}


def extract_pdf_text(file_bytes: bytes) -> dict:
    """
    Extracts all text from an uploaded PDF file.
    Accepts raw bytes (from FastAPI's UploadFile.read()).

    Returns a dict with:
    - content: all extracted text joined together
    - headline: "Extracted from PDF upload"
    - url: empty string (no URL for uploaded files)
    """
    try:
        text_pages = []

        # Wrap bytes in a file-like object so pdfplumber can read it
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:  # some pages may be blank or image-only
                    text_pages.append(page_text)

        full_text = "\n".join(text_pages)

        if not full_text.strip():
            return {"error": "Could not extract text from this PDF. It may be image-based (scanned)."}

        return {
            "headline": "Extracted from PDF upload",
            "content": full_text[:4000],  # limit to keep API costs low
            "url": ""
        }

    except Exception as e:
        return {"error": f"PDF extraction failed: {str(e)}"}
