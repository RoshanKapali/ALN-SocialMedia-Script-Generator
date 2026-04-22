# ALN Social Media Script Generator

A powerful content generation tool that automatically creates social media scripts for newsletters, LinkedIn posts, Twitter threads, and TikTok videos using Google's Gemini AI API.

## Features

- 📰 **Newsletter Generation** - Create comprehensive newsletter content from articles
- 💼 **LinkedIn Posts** - Generate professional LinkedIn posts from article text
- 🐦 **Twitter/X Threads** - Create engaging Twitter/X thread content
- 🎬 **TikTok Scripts** - Generate TikTok video scripts (informative, event, hiring, culture, fun)
- 🌐 **URL Scraping** - Automatically extract and process content from web URLs
- 📊 **Brand Tone Checking** - Validate generated content against brand guidelines
- 💾 **History Tracking** - Keep records of all generated content
- 🎯 **Multi-Format Generation** - Generate all formats at once from a single input

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Google Generative AI (Gemini 2.0 Flash)** - AI-powered content generation
- **BeautifulSoup4** - Web scraping
- **PDFPlumber** - PDF text extraction
- **SQLite** - Local history database

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling
- **Vanilla JavaScript** - No external dependencies

## Project Structure

```
ALN-SocialMedia-Script-Generator/
├── backend/
│   ├── main.py              # FastAPI application & routes
│   ├── generator.py         # Gemini API integration & content generation
│   ├── scraper.py           # Web scraping & content extraction
│   ├── database.py          # SQLite database operations
│   ├── requirements.txt      # Python dependencies
│   └── __init__.py
├── frontend/
│   ├── index.html           # Main UI
│   ├── main.js              # Frontend logic
│   └── style.css            # Styling
├── aln_context.py           # ALN-specific prompts & context
├── .env                     # Environment variables (API keys)
└── README.md
```

## Installation

### Prerequisites
- Python 3.10+
- pip or conda
- Gemini API key from [aistudio.google.com](https://aistudio.google.com)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/RoshanKapali/ALN-SocialMedia-Script-Generator.git
   cd ALN-SocialMedia-Script-Generator
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

4. **Set up environment variables**
   ```bash
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```
   - Get your API key from [aistudio.google.com](https://aistudio.google.com)
   - Replace `your_api_key_here` with your actual Gemini API key

## Running the Application

### Start the Backend Server
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

### Open the Frontend
Open `frontend/index.html` in your web browser or use a local server:
```bash
python -m http.server 8080 --directory frontend
```
Then visit `http://localhost:8080`

## API Endpoints

### Text-based Generation
```
POST /generate/text
```
Body:
```json
{
  "text": "Article text here",
  "format_type": "linkedin",
  "tiktok_type": "informative",
  "run_brand_check": false
}
```

### URL-based Generation
```
POST /generate/url
```
Body:
```json
{
  "url": "https://example.com/article",
  "format_type": "newsletter",
  "run_brand_check": true
}
```

### Supported Formats
- `linkedin` - LinkedIn post
- `twitter` - Twitter/X thread
- `tiktok` - TikTok video script
- `newsletter` - Newsletter content
- `all` - Generate all formats at once

### TikTok Types
- `informative` - Educational content
- `event` - Event announcement
- `hiring` - Job posting
- `culture` - Company culture
- `fun` - Entertainment content

### Content History
```
GET /history
GET /history/{item_id}
DELETE /history/{item_id}
```

## Configuration

### .env File
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### System Prompts
Edit `aln_context.py` to customize:
- `get_system_prompt(format_type)` - System instructions for each content type
- `CURRENT_EPISODE` - Newsletter episode number
- `CURRENT_DATE` - Current publication date

## Usage Examples

### Generate a LinkedIn Post
1. Open the frontend
2. Select "Text" tab
3. Paste article text
4. Check "LinkedIn" checkbox
5. Click "Generate"

### Generate All Formats from a URL
1. Select "URL" tab
2. Paste article URL (e.g., from news websites)
3. Check "Generate All"
4. Click "Generate"
5. Review and copy content

### Run Brand Check
1. Generate content
2. Enable "Run Brand Check" before generating
3. Review brand tone feedback

## API Rate Limits

### Gemini Free Tier (Default)
- 15 requests per minute
- 1.5 million tokens per day
- Model: `gemini-2.0-flash`

### Upgrade Options
- Pay-as-you-go: [console.cloud.google.com](https://console.cloud.google.com)
- Higher limits with paid API tier

## Troubleshooting

### API Quota Exceeded
**Error**: `429 You exceeded your current quota`
- **Solution**: Wait for quota reset or upgrade to paid tier
- Monitor usage at [ai.dev/rate-limit](https://ai.dev/rate-limit)

### .env File Not Found
- **Solution**: Ensure `.env` is in the project root directory
- Check file permissions

### Backend Won't Start
- **Solution**: Ensure port 8000 is available
- Check Python version (3.10+)
- Verify all dependencies installed: `pip install -r backend/requirements.txt`

### API Key Invalid
- **Solution**: Regenerate key at [aistudio.google.com](https://aistudio.google.com)
- Update `.env` file
- Restart backend server

## Development

### Adding New Content Types
1. Create new system prompt in `aln_context.py`
2. Add generation function in `backend/generator.py`
3. Update API route in `backend/main.py`
4. Add UI option in `frontend/index.html`

### Customizing Prompts
Edit the `get_system_prompt()` function in `aln_context.py` to modify behavior for each content type.

## Features & Roadmap

### ✅ Completed
- Text-based content generation
- URL scraping and processing
- Multiple content formats
- Brand tone validation
- History tracking
- Gemini AI integration

### 🔄 Planned
- File upload support (PDF, DOCX)
- Batch processing
- Custom template creation
- Export to various formats
- Advanced analytics
- Multi-language support

## License

This project is open source and available under the MIT License.

## Support

For issues, feature requests, or contributions:
1. Open an issue on GitHub
2. Create a pull request with your changes
3. Contact: [Your contact info if needed]

## Author

**Roshan Kapali**
- GitHub: [RoshanKapali](https://github.com/RoshanKapali)
- Repository: [ALN-SocialMedia-Script-Generator](https://github.com/RoshanKapali/ALN-SocialMedia-Script-Generator)

## Acknowledgments

- Google Gemini API for AI-powered content generation
- FastAPI for the backend framework
- BeautifulSoup4 for web scraping

---

**Note**: This tool is designed for the ALN (Accountability and Localization Network) content team. Customize prompts and configurations as needed for your specific use case.
