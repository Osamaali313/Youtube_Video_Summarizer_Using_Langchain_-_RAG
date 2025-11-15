# Python/FastAPI Backend - YouTube AI Summarizer

> Multi-agent YouTube video summarizer powered by LangGraph and LangChain

## 🚀 Features

### Multi-Agent System
- **Extractor Agent**: Fetches YouTube transcripts with metadata
- **Summarizer Agent**: Creates intelligent summaries (4 modes)
- **Citation Agent**: Adds timestamps and source references
- **Q&A Agent**: RAG-powered question answering *(coming soon)*
- **Research Agent**: Web search for context *(coming soon)*
- **Fact-Checker Agent**: Validates claims *(coming soon)*

### Summary Modes
1. **Quick** - Fast bullet-point summary
2. **Standard** - Detailed analysis with sections
3. **Research** - Comprehensive with fact-checking
4. **Educational** - Learning-focused with Q&A

### API Endpoints
- `POST /api/summarize` - Summarize a YouTube video
- `POST /api/question` - Ask questions about videos
- `GET /api/models` - List available AI models
- `GET /health` - Health check
- `WS /ws/summarize` - WebSocket for real-time updates

---

## 📋 Prerequisites

- Python 3.11+
- pip or poetry
- API keys for AI providers (OpenRouter, Google AI, etc.)

---

## 🔧 Installation

### 1. Clone and Navigate
```bash
cd apps/backends/python-fastapi
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your API keys
```

**Required API Keys:**
- `OPENROUTER_API_KEY` - Get from [OpenRouter](https://openrouter.ai/keys)
- `GOOGLE_AI_API_KEY` - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## 🏃 Running the Server

### Development Mode
```bash
uvicorn app.main:app --reload --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker
```bash
# Build image
docker build -t youtube-summarizer-api .

# Run container
docker run -p 8000:8000 --env-file .env youtube-summarizer-api
```

The API will be available at:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📚 API Usage

### Summarize a Video

```bash
curl -X POST http://localhost:8000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "mode": "standard",
    "features": {
      "citations": true,
      "factChecking": false,
      "webResearch": false
    }
  }'
```

### Response
```json
{
  "success": true,
  "summary": {
    "id": "sum_VIDEO_ID_1234567890",
    "video_id": "VIDEO_ID",
    "video_title": "Video Title",
    "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "content": "Summary content here...",
    "mode": "standard",
    "timestamps": [
      {"time": "00:30", "text": "Introduction"},
      {"time": "02:15", "text": "Main topic"}
    ],
    "duration": 600,
    "created_at": 1234567890000
  },
  "processing_time": 45.3
}
```

### Ask a Question
```bash
curl -X POST http://localhost:8000/api/question \
  -H "Content-Type: application/json" \
  -d '{
    "summary_id": "sum_VIDEO_ID_1234567890",
    "question": "What are the main topics covered?"
  }'
```

---

## 🏗️ Architecture

### Project Structure
```
app/
├── agents/              # Agent implementations
│   ├── base.py         # Base agent class
│   ├── extractor.py    # YouTube transcript extractor
│   ├── summarizer.py   # Summary generator
│   └── citation.py     # Citation adder
├── graphs/              # LangGraph workflows
│   └── summary_graph.py # Main summarization workflow
├── config.py            # Configuration and system prompts
└── main.py              # FastAPI application
```

### Agent System Prompts

Each agent has a comprehensive system prompt defining:
- Responsibilities and capabilities
- Quality standards
- Output formats
- Error handling

See `app/config.py` for all system prompts.

### Workflow

```
User Request
    ↓
Extractor Agent (fetch transcript)
    ↓
Summarizer Agent (create summary)
    ↓
Citation Agent (add timestamps)
    ↓
Response
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `DEFAULT_LLM_PROVIDER` | AI provider | `openrouter` |
| `DEFAULT_MODEL` | Model name | `anthropic/claude-3.5-sonnet` |
| `CHUNK_SIZE` | Text chunk size | `1000` |
| `MAX_VIDEO_LENGTH` | Max video duration (seconds) | `7200` |

### Workflow Configs

Defined in `app/config.py`:
- **Quick**: Extractor + Summarizer (2 min)
- **Standard**: + Citation Agent (5 min)
- **Research**: + Research + Fact-Checker (15 min)
- **Educational**: + Q&A Agent (10 min)

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# With coverage
pytest --cov=app tests/
```

---

## 📊 Monitoring

### LangSmith Integration

Enable tracing for debugging:
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=youtube-summarizer
```

View traces at [LangSmith](https://smith.langchain.com)

---

## 🚀 Deployment

### Railway
```bash
railway login
railway init
railway up
```

### Render
```bash
# Use Render.yaml or dashboard
# Set environment variables in Render dashboard
```

### Docker Compose
See root `docker-compose.yml` for full stack deployment.

---

## 🔐 Security

- API keys stored securely in environment
- CORS configured for allowed origins
- Rate limiting recommended (add middleware)
- Input validation on all endpoints

---

## 🐛 Troubleshooting

### No transcript available
- Check if video has captions
- Try different languages
- Some videos disable transcripts

### API key errors
- Verify API keys in `.env`
- Check API key permissions
- Ensure sufficient credits

### Slow processing
- Large videos take longer
- Use "quick" mode for speed
- Consider caching results

---

## 📝 License

See root LICENSE file

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

---

## 📧 Support

For issues or questions:
- GitHub Issues
- Documentation at `/docs`

---

**Built with LangChain, LangGraph, and FastAPI** 🚀
