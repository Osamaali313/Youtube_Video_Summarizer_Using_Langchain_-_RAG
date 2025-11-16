# 🚀 AI-Powered YouTube Video Summarizer

> Transform YouTube videos into intelligence with state-of-the-art multi-agent AI system powered by LangGraph

<div align="center">

![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?style=for-the-badge&logo=typescript)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![LangChain](https://img.shields.io/badge/LangChain-Latest-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

[Features](#features) • [Demo](#demo) • [Installation](#installation) • [Architecture](#architecture) • [Deployment](#deployment)

</div>

---

## ✨ Features

### 🤖 Multi-Agent Intelligence
- **9+ Specialized AI Agents** powered by LangGraph
- **Supervisor Agent** orchestrates workflow and task routing
- **Extractor Agent** fetches YouTube transcripts with error handling
- **Summarizer Agent** creates context-aware summaries
- **Research Agent** performs web searches for additional context
- **Fact-Checker Agent** validates claims against knowledge bases
- **Q&A Agent** answers questions with RAG-powered responses
- **Citation Agent** adds timestamps and source references
- **Translation Agent** multi-lingual summary support
- **Export Agent** generates formatted outputs

### 🎨 Stunning UI/UX
- **3D Particle Galaxy** background with Three.js
- **Glassmorphism** design with blur effects
- **Smooth Animations** powered by Framer Motion
- **Real-time Agent Visualization** see agents work live
- **Responsive Design** works on all devices
- **Dark Mode** optimized for extended use

### ⚡ Multiple Backend Options
Choose the backend that fits your needs:
- **Python/FastAPI** - Full LangGraph support (recommended)
- **Node.js/Express** - LangGraph.js implementation
- **Go/Fiber** - High-performance RAG
- **Rust/Actix-web** - Ultra-fast processing
- **Ruby/Rails** - Full-featured with ActiveRecord

### 🔑 Flexible AI Providers
- **OpenRouter** - Access to 200+ AI models
- **Google AI Studio** - Gemini Pro/Flash
- **User-provided API keys** with encrypted storage

### 📊 Summary Modes
- **Quick** (2-3 min) - Fast bullet-point summary
- **Standard** (5-7 min) - Detailed analysis with sections
- **Deep Research** (15+ min) - Fact-checked with citations
- **Educational** - Study notes with Q&A

### 💬 Interactive Features
- **RAG-powered Q&A** - Ask questions about any video
- **Multi-hop Reasoning** - Complex question handling
- **Context-aware Responses** - Maintains conversation history
- **Source Citations** - Links back to video timestamps

### 📄 Export Options
- **PDF** with formatted sections
- **Markdown** with headers and links
- **JSON** structured data
- **Notion/Obsidian** ready format

---

## 🏗️ Architecture

### Frontend (Next.js 14)
```
apps/web/
├── app/
│   ├── (landing)/           # 3D landing page
│   ├── dashboard/           # Main app interface
│   │   ├── chat/           # Q&A interface
│   │   ├── history/        # Past summaries
│   │   └── settings/       # Configuration
│   └── api/                # API routes
├── components/
│   ├── 3d/                 # Three.js components
│   ├── ui/                 # Reusable UI components
│   ├── agents/             # Agent visualization
│   └── features/           # Feature components
└── lib/
    ├── stores/             # Zustand state management
    └── utils/              # Utilities
```

### Backend Options

#### Python/FastAPI (Primary)
```
apps/backends/python-fastapi/
├── app/
│   ├── agents/             # LangGraph agent definitions
│   │   ├── supervisor.py
│   │   ├── extractor.py
│   │   ├── summarizer.py
│   │   ├── qa_agent.py
│   │   └── ...
│   ├── graphs/             # LangGraph workflows
│   │   ├── summary_graph.py
│   │   └── qa_graph.py
│   ├── tools/              # Custom tools
│   ├── api/                # FastAPI routes
│   └── main.py
├── Dockerfile
└── requirements.txt
```

### Agent Workflow
```
User Input → Supervisor Agent
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
Extractor   Research    Q&A Agent
    ↓           ↓           ↓
Summarizer  Fact-Checker  Citation
    ↓           ↓           ↓
          Export Agent
                ↓
            Results
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+ (for Python backend)
- Docker & Docker Compose (optional)
- API keys (OpenRouter or Google AI Studio)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/youtube-ai-summarizer.git
cd youtube-ai-summarizer
```

2. **Install frontend dependencies**
```bash
cd apps/web
npm install
```

3. **Set up environment variables**
```bash
cp .env.example .env.local
# Edit .env.local with your API keys
```

4. **Run the development server**
```bash
npm run dev
```

5. **Open your browser**
```
http://localhost:3000
```

---

## 🔧 Configuration

### Environment Variables

Create `.env.local` in `apps/web/`:

```env
# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Backend Selection (python | nodejs | go | rust | ruby)
NEXT_PUBLIC_DEFAULT_BACKEND=python

# API Keys (stored encrypted in browser)
# Users will input these in the app UI
```

### Backend Setup

#### Python/FastAPI
```bash
cd apps/backends/python-fastapi
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Node.js/Express
```bash
cd apps/backends/nodejs-express
npm install
npm run dev
```

#### Go/Fiber
```bash
cd apps/backends/go-fiber
go mod download
go run main.go
```

---

## 🐳 Docker Deployment

### Using Docker Compose (All Services)
```bash
docker-compose up -d
```

This starts:
- Frontend (Next.js) on `http://localhost:3000`
- Python backend on `http://localhost:8000`
- Node.js backend on `http://localhost:8001`
- PostgreSQL database on `localhost:5432`
- Redis cache on `localhost:6379`

### Individual Services
```bash
# Frontend only
docker build -t youtube-summarizer-web -f apps/web/Dockerfile .
docker run -p 3000:3000 youtube-summarizer-web

# Python backend only
docker build -t youtube-summarizer-python -f apps/backends/python-fastapi/Dockerfile .
docker run -p 8000:8000 youtube-summarizer-python
```

---

## 🌐 Production Deployment

### Frontend (Vercel)
1. Push to GitHub
2. Import to Vercel
3. Set environment variables
4. Deploy

```bash
npm run build
```

### Backends (Railway/Render)
Each backend can be deployed independently:

**Python Backend to Railway:**
```bash
railway login
railway init
railway up
```

**Database (Supabase):**
1. Create project at [supabase.com](https://supabase.com)
2. Copy connection string
3. Add to backend environment variables

---

## 📊 Agent System Details

### LangGraph Workflows

#### Summary Workflow
```python
graph = StateGraph(SummaryState)

graph.add_node("extract", extractor_agent)
graph.add_node("summarize", summarizer_agent)
graph.add_node("fact_check", fact_checker_agent)
graph.add_node("cite", citation_agent)

graph.add_edge("extract", "summarize")
graph.add_edge("summarize", "fact_check")
graph.add_edge("fact_check", "cite")
```

#### Q&A Workflow
```python
graph = StateGraph(QAState)

graph.add_node("retrieve", retrieval_agent)
graph.add_node("answer", qa_agent)
graph.add_node("verify", verification_agent)

graph.add_conditional_edges("retrieve", route_to_agent)
```

---

## 🎨 UI Components

### Custom Components
- **ParticleGalaxy** - 3D particle background
- **AgentActivityGraph** - Real-time agent visualization
- **SummaryCard** - Animated summary display
- **ChatInterface** - Q&A conversation UI
- **VideoInput** - YouTube URL validation

### Design System
- **Colors**: Electric Blue/Purple gradient theme
- **Typography**: Geist Sans & Geist Mono
- **Animations**: Framer Motion powered
- **Effects**: Glassmorphism, gradients, glows

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangChain** & **LangGraph** for the amazing agent framework
- **Vercel** for Next.js and hosting
- **OpenRouter** for model access
- **Three.js** for 3D graphics
- **Framer Motion** for animations

---

## 📧 Contact

Project Link: [https://github.com/yourusername/youtube-ai-summarizer](https://github.com/yourusername/youtube-ai-summarizer)

---

<div align="center">

**Built with ❤️ using Next.js, LangGraph, and cutting-edge AI**

[⬆ back to top](#-ai-powered-youtube-video-summarizer)

</div>
