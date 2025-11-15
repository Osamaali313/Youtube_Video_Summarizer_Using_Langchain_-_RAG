# Python/FastAPI Backend - AI YouTube Summarizer

> Multi-agent YouTube video summarization system powered by LangGraph, LangChain, and FastAPI with RAG, Research, and Fact-Checking

## 🌟 Features

### Multi-Agent System
- ✅ **Extractor Agent**: Fetches YouTube transcripts with multi-language support
- ✅ **Summarizer Agent**: Creates intelligent summaries in 4 modes (quick, standard, research, educational)
- ✅ **Citation Agent**: Adds intelligent timestamp citations to summaries
- ✅ **Q&A Agent**: RAG-powered question answering with vector search
- ✅ **Research Agent**: Web search for additional context using Tavily/DuckDuckGo
- ✅ **Fact-Checker Agent**: Validates claims with credibility scoring

### Advanced Features
- 🔍 **RAG System**: Vector storage with Chroma for intelligent Q&A
- ⚡ **Redis Caching**: High-performance caching for summaries and rate limiting
- 💾 **PostgreSQL Database**: Persistent storage for summaries, conversations, and analytics
- 🛡️ **Rate Limiting**: IP-based rate limiting with configurable thresholds
- 🔌 **WebSocket Support**: Real-time agent progress updates
- 🌐 **Multi-Language**: Support for transcripts in multiple languages

### AI Provider Support
- **OpenRouter**: Access to 200+ models (Claude, GPT-4, Gemini, Llama, etc.)
- **Google AI Studio**: Gemini models
- **OpenAI**: GPT-4 and GPT-3.5 Turbo
- **User API Keys**: Users can provide their own API keys

### Summary Modes
1. **Quick** - Fast 5-7 bullet points (Extractor + Summarizer)
2. **Standard** - Comprehensive summary with sections (+ Citations)
3. **Research** - In-depth analysis with web research and fact-checking (All agents)
4. **Educational** - Learning-focused with concepts and practice questions (+ Citations)

---

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL database
- Redis server
- API keys for LLM providers (OpenRouter, Google AI Studio, or OpenAI)

---

## 🔧 Installation

### 1. Navigate to Backend Directory
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
# Edit .env with your configuration
```

**Required Environment Variables:**
```env
# Application
APP_NAME="YouTube Summarizer API"
APP_VERSION="1.0.0"
ENVIRONMENT="development"
HOST="0.0.0.0"
PORT=8000
DEBUG=true

# Database
DATABASE_URL="postgresql://user:password@localhost:5432/youtube_summarizer"

# Redis
REDIS_URL="redis://localhost:6379/0"

# LLM Providers
DEFAULT_LLM_PROVIDER="openrouter"
DEFAULT_MODEL="anthropic/claude-3.5-sonnet"

# API Keys (optional - users can provide their own)
OPENROUTER_API_KEY="sk-or-..."
GOOGLE_API_KEY="..."
OPENAI_API_KEY="sk-..."

# Vector Store
CHROMA_PERSIST_DIR="./data/chroma"

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]

# Web Search (optional)
TAVILY_API_KEY="tvly-..."  # For research agent

# Logging
LOG_LEVEL="INFO"
LOG_FORMAT="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
```

### 5. Initialize Database
The database will be automatically initialized on first startup. Tables will be created for:
- Summaries
- Conversations
- Fact-checks
- Research results
- API usage tracking

---

## 🏃 Running the Server

### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e REDIS_URL="redis://..." \
  -e OPENROUTER_API_KEY="..." \
  youtube-summarizer-api
```

The API will be available at:
- **API**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 📡 API Endpoints

### POST /api/summarize

Summarize a YouTube video with optional research and fact-checking.

**Request:**
```bash
curl -X POST http://localhost:8000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "mode": "research",
    "features": {
      "citations": true,
      "factChecking": true,
      "webResearch": true,
      "translation": false
    },
    "api_key": "optional-user-api-key"
  }'
```

**Response:**
```json
{
  "success": true,
  "summary": {
    "id": "sum_VIDEO_ID_1234567890",
    "video_id": "VIDEO_ID",
    "video_title": "Example Video Title",
    "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "content": "Comprehensive summary content...",
    "mode": "research",
    "timestamps": [
      {"time": "00:30", "text": "Introduction to main topic"},
      {"time": "02:15", "text": "Key point discussed"}
    ],
    "citations": ["00:30: Introduction to main topic", "02:15: Key point discussed"],
    "credibility_score": 0.85,
    "research": {
      "topic": "Main topic of the video",
      "findings": [...],
      "sources": ["https://...", "https://..."]
    },
    "fact_check": {
      "claims": [
        {
          "claim": "Specific claim from video",
          "verification_status": "VERIFIED",
          "sources": ["https://..."],
          "confidence": 0.9
        }
      ],
      "credibility_score": 0.85,
      "overall_assessment": "Overall analysis..."
    },
    "duration": 600,
    "language": "en",
    "created_at": 1234567890000
  },
  "processing_time": 45.3
}
```

### POST /api/question

Ask questions about a summarized video using RAG (Retrieval-Augmented Generation).

**Request:**
```bash
curl -X POST http://localhost:8000/api/question \
  -H "Content-Type: application/json" \
  -d '{
    "summary_id": "sum_VIDEO_ID_1234567890",
    "question": "What are the main points discussed in the video?",
    "conversation_history": [
      {"role": "user", "content": "Tell me about the introduction"},
      {"role": "assistant", "content": "The introduction covers..."}
    ]
  }'
```

**Response:**
```json
{
  "answer": "The main points discussed in the video are: 1) Introduction to the topic at 00:30, 2) Key findings at 02:15...",
  "citations": [
    {"timestamp": "00:30", "text": "Relevant excerpt from transcript"},
    {"timestamp": "02:15", "text": "Another relevant excerpt"}
  ],
  "sources": ["00:30", "02:15", "05:45"]
}
```

### GET /api/models

Get list of available AI models from all providers.

**Response:**
```json
{
  "models": {
    "openrouter": [
      "anthropic/claude-3.5-sonnet",
      "anthropic/claude-3-opus",
      "openai/gpt-4-turbo",
      "google/gemini-pro-1.5",
      "meta-llama/llama-3.1-70b-instruct"
    ],
    "google": [
      "gemini-1.5-pro",
      "gemini-1.5-flash",
      "gemini-1.0-pro"
    ],
    "openai": [
      "gpt-4-turbo-preview",
      "gpt-4",
      "gpt-3.5-turbo"
    ]
  }
}
```

### GET /health

Health check endpoint to verify service status.

**Response:**
```json
{
  "status": "healthy",
  "backend": "python-fastapi",
  "version": "1.0.0",
  "timestamp": 1234567890000
}
```

### WebSocket /ws/summarize

Real-time summarization with live agent progress updates.

**Connect:** `ws://localhost:8000/ws/summarize`

**Send:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "mode": "research",
  "features": {
    "citations": true,
    "factChecking": true,
    "webResearch": true
  },
  "api_key": "optional-user-key"
}
```

**Receive (multiple messages):**
```json
{"type": "start", "message": "Starting summarization..."}
{"type": "agent_update", "agent": "extractor", "status": "running", "progress": 20}
{"type": "agent_update", "agent": "summarizer", "status": "running", "progress": 40}
{"type": "agent_update", "agent": "research", "status": "running", "progress": 60}
{"type": "agent_update", "agent": "fact_checker", "status": "running", "progress": 80}
{"type": "agent_update", "agent": "citation", "status": "running", "progress": 90}
{"type": "complete", "result": {"success": true, "summary": {...}}}
```

---

## 🏗️ Architecture

### LangGraph Workflow

```
┌──────────┐
│ Extract  │ → Fetch YouTube transcript with metadata
└────┬─────┘
     │
┌────▼──────┐
│ Summarize │ → Generate intelligent summary based on mode
└────┬──────┘
     │
     ├─────→ Research (if mode=research or webResearch=true)
     │       └─→ Web search for additional context
     │           └─→ Fact Check (if factChecking=true)
     │               └─→ Verify claims with credibility scoring
     │                   └─→ Citation → Add timestamps
     │                       └─→ Finalize → Package results
     │
     ├─────→ Fact Check (if factChecking=true and no research)
     │       └─→ Citation → Finalize
     │
     └─────→ Citation (default)
             └─→ Finalize
```

### Project Structure
```
app/
├── agents/                  # Agent implementations
│   ├── __init__.py         # Agent exports
│   ├── base.py             # Base agent class with LLM support
│   ├── extractor.py        # YouTube transcript extractor
│   ├── summarizer.py       # Summary generator (4 modes)
│   ├── citation.py         # Timestamp citation adder
│   ├── qa_agent.py         # RAG-powered Q&A agent
│   ├── research.py         # Web research agent
│   └── fact_checker.py     # Claim verification agent
│
├── graphs/                  # LangGraph workflows
│   └── summary_graph.py    # Main summarization workflow
│
├── models/                  # Database models
│   └── database.py         # PostgreSQL models (Summary, Conversation, etc.)
│
├── tools/                   # Utility tools
│   ├── cache.py            # Redis caching (VideoCache, RateLimitCache)
│   ├── vector_store.py     # Chroma vector store for RAG
│   └── youtube.py          # YouTube utility functions
│
├── middleware/              # FastAPI middleware
│   └── rate_limit.py       # Rate limiting middleware
│
├── config.py               # Configuration and system prompts
└── main.py                 # FastAPI application
```

### Agent System Prompts

Each agent has a comprehensive system prompt in `app/config.py` defining:

1. **Supervisor Agent**: Orchestrates multi-agent workflow based on mode
2. **Extractor Agent**: Retrieves YouTube transcripts with quality standards
3. **Summarizer Agent**: Creates summaries with mode-specific behavior:
   - Quick: 5-7 bullet points
   - Standard: Introduction, sections, conclusion
   - Research: Comprehensive analysis with evidence
   - Educational: Learning objectives, concepts, practice questions
4. **Research Agent**: Conducts web searches and synthesizes findings
5. **Fact-Checker Agent**: Extracts and verifies claims with credibility scoring
6. **Q&A Agent**: Answers questions using RAG with context retrieval
7. **Citation Agent**: Adds intelligent timestamp citations
8. **Translation Agent**: Translates summaries to other languages
9. **Export Agent**: Formats summaries for various platforms

---

## 🔍 RAG System

The Q&A agent uses RAG (Retrieval-Augmented Generation) for accurate answers:

### How It Works

1. **Document Creation**: Video transcripts are chunked into overlapping segments
2. **Embedding**: Each chunk is embedded using OpenAI's `text-embedding-3-small`
3. **Vector Storage**: Embeddings stored in Chroma with metadata
4. **Similarity Search**: Retrieves relevant chunks for user questions
5. **LLM Generation**: Generates answers with citations from retrieved context

### Configuration

```python
# app/tools/vector_store.py
chunk_size = 1000           # Characters per chunk
chunk_overlap = 200         # Overlap between chunks
embedding_model = "text-embedding-3-small"
collection_prefix = "video_"
k_results = 5               # Number of chunks to retrieve
score_threshold = 0.3       # Minimum similarity score
```

### Example Usage

After summarizing a video, the transcript is automatically indexed in the vector store. Users can then ask questions:

```python
# Question is answered using relevant chunks from transcript
question = "What did the speaker say about machine learning?"
# -> Retrieves 5 most relevant chunks
# -> Generates answer with citations
# -> Returns answer with timestamp sources
```

---

## 🗄️ Database Schema

### Summary Table
```sql
CREATE TABLE summaries (
  id VARCHAR PRIMARY KEY,
  video_id VARCHAR NOT NULL,
  video_url VARCHAR NOT NULL,
  video_title VARCHAR,
  video_author VARCHAR,
  video_duration INTEGER,
  thumbnail_url VARCHAR,
  content TEXT NOT NULL,
  mode VARCHAR NOT NULL,
  language VARCHAR DEFAULT 'en',
  timestamps JSON,
  citations JSON,
  processing_time FLOAT,
  credibility_score FLOAT,
  features JSON,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Conversation Table
```sql
CREATE TABLE conversations (
  id VARCHAR PRIMARY KEY,
  summary_id VARCHAR NOT NULL,
  video_id VARCHAR NOT NULL,
  messages JSON NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### FactCheck Table
```sql
CREATE TABLE fact_checks (
  id VARCHAR PRIMARY KEY,
  summary_id VARCHAR NOT NULL,
  video_id VARCHAR NOT NULL,
  claims JSON NOT NULL,
  overall_assessment TEXT,
  credibility_score FLOAT,
  total_claims INTEGER,
  checked_claims INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### ResearchResult Table
```sql
CREATE TABLE research_results (
  id VARCHAR PRIMARY KEY,
  summary_id VARCHAR NOT NULL,
  video_id VARCHAR NOT NULL,
  topic VARCHAR NOT NULL,
  findings JSON,
  summary TEXT,
  sources JSON,
  search_query VARCHAR,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### APIUsage Table
```sql
CREATE TABLE api_usage (
  id SERIAL PRIMARY KEY,
  endpoint VARCHAR NOT NULL,
  ip_address VARCHAR,
  user_agent VARCHAR,
  video_id VARCHAR,
  mode VARCHAR,
  processing_time FLOAT,
  success BOOLEAN DEFAULT TRUE,
  error_message TEXT,
  timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## ⚙️ Configuration

### Workflow Configs

Defined in `app/config.py`:

```python
WORKFLOW_CONFIGS = {
    "quick": {
        "agents": ["extractor", "summarizer"],
        "max_length": 500,
        "timeout": 30
    },
    "standard": {
        "agents": ["extractor", "summarizer", "citation"],
        "max_length": 2000,
        "timeout": 60
    },
    "research": {
        "agents": ["extractor", "summarizer", "research", "fact_checker", "citation"],
        "max_length": 5000,
        "timeout": 180
    },
    "educational": {
        "agents": ["extractor", "summarizer", "citation"],
        "max_length": 3000,
        "timeout": 120
    }
}
```

### Rate Limiting

Configure globally in environment:
```env
RATE_LIMIT_REQUESTS=100  # Max requests per period
RATE_LIMIT_PERIOD=3600   # Period in seconds (1 hour)
```

Apply custom rate limits to specific endpoints:
```python
from app.middleware.rate_limit import rate_limit

@app.post("/api/summarize")
@rate_limit(max_requests=10, window_seconds=60)
async def summarize_video(...):
    ...
```

### Caching Strategy

Redis caching is applied to:
- **Video summaries**: Cached by video_id + mode + features hash
- **Rate limiting**: IP-based request counting
- **Vector store queries**: Cached similarity searches

**Cache TTLs**:
- Video summaries: 1 hour
- Rate limit windows: Configurable (default 1 hour)
- Vector searches: 30 minutes

---

## 🐳 Docker Deployment

### Dockerfile

The included Dockerfile uses multi-stage builds for optimization:

```dockerfile
FROM python:3.11-slim as base
# ... install dependencies ...
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

Example `docker-compose.yml` for full stack:

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/youtube_summarizer
      - REDIS_URL=redis://redis:6379/0
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./data:/app/data

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: youtube_summarizer
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

Run with:
```bash
docker-compose up -d
```

---

## 📊 Monitoring & Logging

### Structured Logging

Uses Loguru for beautiful, structured logs:

```python
logger.info(f"Summarize request: {video_url} [{mode}]")
logger.error(f"Summarization failed: {error_msg}")
```

Configure log level:
```env
LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### API Usage Tracking

All requests are logged to the `api_usage` table. Query statistics:

```sql
SELECT
  endpoint,
  COUNT(*) as requests,
  AVG(processing_time) as avg_time,
  SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
  SUM(CASE WHEN success THEN 0 ELSE 1 END) as failed
FROM api_usage
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY endpoint;
```

### LangSmith Tracing

Enable LangSmith for debugging agent workflows:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=youtube-summarizer
```

View traces at [LangSmith](https://smith.langchain.com)

---

## 🧪 Testing

### Install Test Dependencies
```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

### Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=app --cov-report=html tests/

# Run specific test file
pytest tests/test_agents.py -v

# Run specific test
pytest tests/test_agents.py::test_extractor_agent -v
```

### Test Structure
```
tests/
├── test_agents.py          # Agent unit tests
├── test_workflow.py        # Workflow integration tests
├── test_api.py             # API endpoint tests
├── test_vector_store.py    # RAG system tests
└── test_cache.py           # Caching tests
```

---

## 🔐 Security

### Best Practices Implemented

- ✅ **API Key Encryption**: User API keys are not stored, only used in-memory
- ✅ **Rate Limiting**: IP-based throttling prevents abuse
- ✅ **CORS**: Configurable allowed origins
- ✅ **Input Validation**: Pydantic models validate all inputs
- ✅ **SQL Injection**: SQLAlchemy ORM prevents SQL injection
- ✅ **XSS Prevention**: FastAPI automatically escapes responses
- ✅ **Environment Variables**: Sensitive data in .env files
- ✅ **HTTPS**: Recommended for production deployments

### Security Headers

Add security headers in production:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
app.add_middleware(HTTPSRedirectMiddleware)
```

---

## 🚀 Deployment

### Railway

```bash
railway login
railway init
railway up
```

Set environment variables in Railway dashboard.

### Render

1. Connect your GitHub repository
2. Create a new Web Service
3. Set environment variables
4. Deploy

### Vercel (Serverless)

Note: Requires serverless-compatible setup. Use Railway or Render for full backend.

---

## 🐛 Troubleshooting

### No transcript available
- Check if video has captions enabled
- Try specifying different languages
- Some videos disable transcripts entirely

### API key errors
- Verify API keys in `.env` are correct
- Check API key permissions and quotas
- Ensure sufficient credits for LLM provider

### Database connection errors
- Verify DATABASE_URL is correct
- Ensure PostgreSQL server is running
- Check network connectivity

### Redis connection errors
- Verify REDIS_URL is correct
- Ensure Redis server is running
- Check if Redis requires authentication

### Slow processing
- Large videos (>1 hour) take longer
- Use "quick" mode for faster results
- Enable caching to speed up repeated requests
- Consider increasing timeouts in config

### Rate limit exceeded
- Wait for rate limit window to reset
- Increase RATE_LIMIT_REQUESTS if needed
- Check IP address detection is working

---

## 📝 License

See root LICENSE file

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## 📧 Support

For issues or questions:
- **GitHub Issues**: [Create an issue](https://github.com/yourusername/repo/issues)
- **Documentation**: `/docs` endpoint
- **Email**: support@example.com

---

## 📚 Technology Stack

- **FastAPI** - Modern Python web framework
- **LangChain** - LLM application framework
- **LangGraph** - Multi-agent workflow orchestration
- **Chroma** - Vector database for RAG
- **PostgreSQL** - Persistent data storage
- **Redis** - Caching and rate limiting
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **Loguru** - Advanced logging
- **Pytube** - YouTube metadata extraction
- **youtube-transcript-api** - Transcript fetching
- **Tavily/DuckDuckGo** - Web search for research

---

**Built with ❤️ using LangGraph, LangChain, and FastAPI** 🚀
