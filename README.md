# YouTube AI Tools (LangChain LCEL)

Python CLI to explore trending videos, search videos by keywords, pull transcripts, and generate AI summaries/hashtags/ideas using **LangChain + LCEL**.

## Features
- Trending videos by region (YouTube Data API v3)
- Search videos
- Get transcript (public captions) via `youtube-transcript-api`
- LCEL chains for summarization, hashtags, and follow-up ideas (parallel)

## Quickstart
1) Clone and install
```bash
git clone https://github.com/mujtaba-a-khan/youtube-ai-tools.git
cd youtube-ai-tools

# OpenAI only
pip install -e .            
# or, with IBM extras as well:
pip install -e ".[ibm]"
```

2) Set environment
```bash
cp .env.example .env
# fill in YOUTUBE_API_KEY (required) and LLM keys (OpenAI or watsonx)
```

3) Run commands
```bash
#Finds trending videos replace US by any of your desired region
python -m ytai.cli trending --region US --max-results 10

#Searching by Keyword
python -m ytai.cli search "langchain LCEL"

# Transcript by link
python -m ytai.cli transcript "https://www.youtube.com/watch?v=boJG84Jcf-4"
#or, by ID as well:
python -m ytai.cli transcript boJG84Jcf-4
```

## Notes
- **Transcripts** work only for videos with public captions.
- **Trending** uses `chart=mostPopular` (region-based quota applies).
- Default LLM provider is OpenAI; set `LLM_PROVIDER=watsonx` to use IBM.

## Credits
- **IBM Skill Network** where I learnt from.
- **Course** https://www.coursera.org/professional-certificates/ibm-rag-and-agentic-ai
