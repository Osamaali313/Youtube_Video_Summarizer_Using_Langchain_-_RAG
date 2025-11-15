"""
FastAPI Main Application
AI-Powered YouTube Video Summarizer with LangGraph Multi-Agent System
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from loguru import logger
import sys
import time

from app.config import settings
from app.graphs.summary_graph import create_summary_workflow

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format=settings.LOG_FORMAT,
    level=settings.LOG_LEVEL
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Multi-agent YouTube video summarizer powered by LangGraph",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Request/Response Models
# =============================================================================

class SummarizeRequest(BaseModel):
    """Request model for summarization"""
    video_url: str = Field(..., description="YouTube video URL")
    mode: str = Field(
        default="standard",
        description="Summary mode: quick, standard, research, educational"
    )
    features: Optional[Dict[str, bool]] = Field(
        default_factory=lambda: {
            "factChecking": False,
            "webResearch": False,
            "citations": True,
            "translation": False
        },
        description="Feature flags"
    )
    api_key: Optional[str] = Field(None, description="Optional user API key")


class SummarizeResponse(BaseModel):
    """Response model for summarization"""
    success: bool
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


class QuestionRequest(BaseModel):
    """Request model for Q&A"""
    summary_id: str = Field(..., description="Summary ID")
    question: str = Field(..., description="User question")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Conversation history"
    )


class QuestionResponse(BaseModel):
    """Response model for Q&A"""
    answer: str
    citations: Optional[List[Dict[str, str]]] = None
    sources: Optional[List[str]] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    backend: str
    version: str
    timestamp: int


# =============================================================================
# Routes
# =============================================================================

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "AI-Powered YouTube Summarizer API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        backend="python-fastapi",
        version=settings.APP_VERSION,
        timestamp=int(time.time() * 1000)
    )


@app.post("/api/summarize", response_model=SummarizeResponse)
async def summarize_video(request: SummarizeRequest):
    """
    Summarize a YouTube video

    This endpoint processes a YouTube video through our multi-agent system:
    1. Extractor Agent: Fetches transcript
    2. Summarizer Agent: Creates intelligent summary
    3. Citation Agent: Adds timestamps (if enabled)

    Returns a comprehensive summary with metadata.
    """
    start_time = time.time()

    try:
        logger.info(f"Summarize request: {request.video_url} [{request.mode}]")

        # Create workflow
        workflow = create_summary_workflow(api_key=request.api_key)

        # Run workflow
        result = await workflow.run(
            video_url=request.video_url,
            mode=request.mode,
            features=request.features
        )

        processing_time = time.time() - start_time

        if result.get("success"):
            logger.info(f"Summarization complete in {processing_time:.2f}s")
            return SummarizeResponse(
                success=True,
                summary=result.get("summary"),
                processing_time=processing_time
            )
        else:
            error_msg = result.get("error", "Unknown error occurred")
            logger.error(f"Summarization failed: {error_msg}")
            return SummarizeResponse(
                success=False,
                error=error_msg,
                processing_time=processing_time
            )

    except Exception as e:
        logger.error(f"Summarization error: {e}")
        processing_time = time.time() - start_time
        return SummarizeResponse(
            success=False,
            error=str(e),
            processing_time=processing_time
        )


@app.post("/api/question", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about a summarized video

    Uses RAG (Retrieval-Augmented Generation) to answer questions based on
    the video transcript. Returns answer with citations.
    """
    try:
        logger.info(f"Q&A request for {request.summary_id}: {request.question}")

        # TODO: Implement Q&A agent with RAG
        # For now, return a placeholder response
        return QuestionResponse(
            answer="Q&A functionality will be available once the RAG system is implemented. "
                   "This will use vector storage to retrieve relevant context from the video "
                   "and provide accurate, cited answers.",
            citations=[],
            sources=[]
        )

    except Exception as e:
        logger.error(f"Q&A error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
async def get_available_models():
    """Get list of available AI models"""
    models = {
        "openrouter": [
            "anthropic/claude-3.5-sonnet",
            "anthropic/claude-3-opus",
            "openai/gpt-4-turbo",
            "openai/gpt-4",
            "google/gemini-pro-1.5",
            "meta-llama/llama-3.1-70b-instruct",
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

    return {"models": models}


# =============================================================================
# WebSocket for Real-Time Updates
# =============================================================================

class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")

    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")


manager = ConnectionManager()


@app.websocket("/ws/summarize")
async def websocket_summarize(websocket: WebSocket):
    """
    WebSocket endpoint for real-time summarization updates

    Sends progress updates as agents execute:
    - Agent status changes
    - Progress percentages
    - Intermediate results
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive request
            data = await websocket.receive_json()

            video_url = data.get("video_url")
            mode = data.get("mode", "standard")
            features = data.get("features", {})
            api_key = data.get("api_key")

            if not video_url:
                await manager.send_message({
                    "type": "error",
                    "message": "No video URL provided"
                }, websocket)
                continue

            # Send start message
            await manager.send_message({
                "type": "start",
                "message": "Starting summarization..."
            }, websocket)

            # Create workflow
            workflow = create_summary_workflow(api_key=api_key)

            # TODO: Implement streaming updates from workflow
            # For now, just run and send final result

            await manager.send_message({
                "type": "agent_update",
                "agent": "extractor",
                "status": "running",
                "progress": 33
            }, websocket)

            result = await workflow.run(video_url, mode, features)

            await manager.send_message({
                "type": "agent_update",
                "agent": "summarizer",
                "status": "running",
                "progress": 66
            }, websocket)

            await manager.send_message({
                "type": "agent_update",
                "agent": "citation",
                "status": "running",
                "progress": 90
            }, websocket)

            # Send final result
            if result.get("success"):
                await manager.send_message({
                    "type": "complete",
                    "result": result
                }, websocket)
            else:
                await manager.send_message({
                    "type": "error",
                    "message": result.get("error", "Unknown error")
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await manager.send_message({
                "type": "error",
                "message": str(e)
            }, websocket)
        except:
            pass
        manager.disconnect(websocket)


# =============================================================================
# Error Handlers
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


# =============================================================================
# Startup/Shutdown Events
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Default LLM: {settings.DEFAULT_LLM_PROVIDER}/{settings.DEFAULT_MODEL}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down application")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
