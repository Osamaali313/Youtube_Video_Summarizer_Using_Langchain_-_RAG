"""
LangGraph workflow for video summarization
"""
from typing import Dict, Any, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from loguru import logger

from app.agents import ExtractorAgent, SummarizerAgent, CitationAgent, ResearchAgent, FactCheckerAgent
from app.config import settings, WORKFLOW_CONFIGS


class SummaryState(TypedDict):
    """State for the summary workflow"""
    # Input
    video_url: str
    mode: str
    features: Dict[str, bool]
    api_key: str | None

    # Intermediate state
    video_data: Dict[str, Any] | None
    summary: str | None
    research_findings: Dict[str, Any] | None
    fact_check_result: Dict[str, Any] | None
    cited_summary: str | None
    timestamps: list[Dict[str, str]] | None

    # Output
    result: Dict[str, Any] | None
    error: str | None
    current_agent: str | None


class SummaryWorkflow:
    """LangGraph workflow for video summarization"""

    def __init__(self, api_key: str | None = None):
        """Initialize the workflow"""
        self.api_key = api_key

        # Initialize agents
        self.extractor = ExtractorAgent(api_key=api_key)
        self.summarizer = SummarizerAgent(api_key=api_key)
        self.citation = CitationAgent(api_key=api_key)
        self.research = ResearchAgent(api_key=api_key)
        self.fact_checker = FactCheckerAgent(api_key=api_key)

        # Build graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(SummaryState)

        # Add nodes
        workflow.add_node("extract", self.extract_node)
        workflow.add_node("summarize", self.summarize_node)
        workflow.add_node("research", self.research_node)
        workflow.add_node("fact_check", self.fact_check_node)
        workflow.add_node("cite", self.cite_node)
        workflow.add_node("finalize", self.finalize_node)

        # Define edges
        workflow.set_entry_point("extract")
        workflow.add_edge("extract", "summarize")

        # After summarize, conditionally go to research or fact_check
        workflow.add_conditional_edges(
            "summarize",
            self.should_research,
            {
                "research": "research",
                "fact_check": "fact_check",
                "cite": "cite"
            }
        )

        # After research, go to fact_check
        workflow.add_conditional_edges(
            "research",
            self.should_fact_check,
            {
                "fact_check": "fact_check",
                "cite": "cite"
            }
        )

        # After fact_check, go to cite
        workflow.add_conditional_edges(
            "fact_check",
            self.should_add_citations,
            {
                "cite": "cite",
                "finalize": "finalize"
            }
        )

        workflow.add_edge("cite", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    async def extract_node(self, state: SummaryState) -> SummaryState:
        """Extract video transcript"""
        logger.info(f"[EXTRACT] Processing {state['video_url']}")

        state["current_agent"] = "extractor"

        result = await self.extractor.execute({
            "video_url": state["video_url"]
        })

        if result["success"]:
            state["video_data"] = result["data"]
            logger.info(f"[EXTRACT] Success: {result['data']['title']}")
        else:
            state["error"] = result.get("error", "Extraction failed")
            logger.error(f"[EXTRACT] Failed: {state['error']}")

        return state

    async def summarize_node(self, state: SummaryState) -> SummaryState:
        """Generate summary"""
        logger.info(f"[SUMMARIZE] Mode: {state['mode']}")

        state["current_agent"] = "summarizer"

        if not state.get("video_data"):
            state["error"] = "No video data available for summarization"
            return state

        video_data = state["video_data"]

        result = await self.summarizer.execute({
            "transcript": video_data["transcript"],
            "metadata": {
                "title": video_data.get("title", "Unknown"),
                "author": video_data.get("author", "Unknown"),
                "length": video_data.get("length", 0),
                "publish_date": video_data.get("publish_date"),
            },
            "mode": state["mode"]
        })

        if result["success"]:
            state["summary"] = result["data"]["summary"]
            logger.info(f"[SUMMARIZE] Generated {len(state['summary'])} chars")
        else:
            state["error"] = result.get("error", "Summarization failed")
            logger.error(f"[SUMMARIZE] Failed: {state['error']}")

        return state

    async def research_node(self, state: SummaryState) -> SummaryState:
        """Perform web research"""
        logger.info("[RESEARCH] Conducting web research")

        state["current_agent"] = "research"

        if not state.get("summary") or not state.get("video_data"):
            state["error"] = "Missing summary or video data for research"
            return state

        result = await self.research.execute({
            "summary": state["summary"],
            "video_title": state["video_data"]["title"],
            "video_url": state["video_url"]
        })

        if result["success"]:
            state["research_findings"] = result["data"]
            logger.info(f"[RESEARCH] Found {len(result['data'].get('findings', []))} research findings")
        else:
            state["research_findings"] = None
            logger.warning(f"[RESEARCH] Failed: {result.get('error')}")

        return state

    async def fact_check_node(self, state: SummaryState) -> SummaryState:
        """Fact-check the summary"""
        logger.info("[FACT_CHECK] Verifying claims")

        state["current_agent"] = "fact_checker"

        if not state.get("summary"):
            state["error"] = "Missing summary for fact-checking"
            return state

        # Get transcript for verification context
        transcript = state["video_data"]["transcript"] if state.get("video_data") else None

        result = await self.fact_checker.execute({
            "summary": state["summary"],
            "transcript": transcript,
            "research_findings": state.get("research_findings")
        })

        if result["success"]:
            state["fact_check_result"] = result["data"]
            logger.info(f"[FACT_CHECK] Credibility score: {result['data'].get('credibility_score', 0):.2f}")
        else:
            state["fact_check_result"] = None
            logger.warning(f"[FACT_CHECK] Failed: {result.get('error')}")

        return state

    async def cite_node(self, state: SummaryState) -> SummaryState:
        """Add citations"""
        logger.info("[CITE] Adding timestamps")

        state["current_agent"] = "citation"

        if not state.get("summary") or not state.get("video_data"):
            state["error"] = "Missing summary or video data for citation"
            return state

        result = await self.citation.execute({
            "summary": state["summary"],
            "transcript_data": state["video_data"]["raw_transcript"],
            "video_id": state["video_data"]["video_id"]
        })

        if result["success"]:
            state["cited_summary"] = result["data"]["cited_summary"]
            state["timestamps"] = result["data"]["timestamps"]
            logger.info(f"[CITE] Added {len(state['timestamps'])} citations")
        else:
            # If citation fails, just use original summary
            state["cited_summary"] = state["summary"]
            state["timestamps"] = []
            logger.warning(f"[CITE] Failed, using uncited summary")

        return state

    async def finalize_node(self, state: SummaryState) -> SummaryState:
        """Finalize and package result"""
        logger.info("[FINALIZE] Packaging results")

        state["current_agent"] = "finalize"

        if state.get("error"):
            state["result"] = {
                "success": False,
                "error": state["error"]
            }
            return state

        # Use cited summary if available, otherwise regular summary
        final_summary = state.get("cited_summary") or state.get("summary", "")

        # Build result with all data
        result_data = {
            "id": f"sum_{state['video_data']['video_id']}_{int(time.time())}",
            "video_id": state["video_data"]["video_id"],
            "video_title": state["video_data"]["title"],
            "video_url": state["video_url"],
            "thumbnail": state["video_data"].get("thumbnail_url"),
            "author": state["video_data"].get("author"),
            "content": final_summary,
            "mode": state["mode"],
            "timestamps": state.get("timestamps", []),
            "duration": state["video_data"].get("length", 0),
            "language": state["video_data"].get("language", "en"),
            "transcript": state["video_data"].get("transcript", ""),
            "created_at": int(time.time() * 1000),
        }

        # Add research findings if available
        if state.get("research_findings"):
            result_data["research"] = state["research_findings"]

        # Add fact-check results if available
        if state.get("fact_check_result"):
            result_data["fact_check"] = state["fact_check_result"]
            result_data["credibility_score"] = state["fact_check_result"].get("credibility_score")

        # Add citations if available
        if state.get("timestamps"):
            result_data["citations"] = [
                f"{ts['time']}: {ts['text']}" for ts in state["timestamps"]
            ]

        state["result"] = {
            "success": True,
            "summary": result_data
        }

        logger.info("[FINALIZE] Complete")
        return state

    def should_research(self, state: SummaryState) -> str:
        """Determine if web research should be performed"""
        features = state.get("features", {})
        web_research = features.get("webResearch", False)

        # Always research for research mode
        if state["mode"] == "research":
            return "research"

        # For educational mode with web research enabled
        if state["mode"] == "educational" and web_research:
            return "research"

        # Check if fact-checking is needed
        if self._should_fact_check_internal(state):
            return "fact_check"

        # Otherwise skip to citations
        return "cite"

    def should_fact_check(self, state: SummaryState) -> str:
        """Determine if fact-checking should be performed"""
        if self._should_fact_check_internal(state):
            return "fact_check"
        return "cite"

    def _should_fact_check_internal(self, state: SummaryState) -> bool:
        """Internal helper to check if fact-checking is needed"""
        features = state.get("features", {})
        fact_checking = features.get("factChecking", False)

        # Always fact-check for research mode
        if state["mode"] == "research":
            return True

        # For educational mode with fact-checking enabled
        if state["mode"] == "educational" and fact_checking:
            return True

        # If explicitly enabled
        if fact_checking:
            return True

        return False

    def should_add_citations(self, state: SummaryState) -> str:
        """Determine if citations should be added"""
        features = state.get("features", {})
        add_citations = features.get("citations", True)

        # Always add citations for standard, research, and educational modes
        if state["mode"] in ["standard", "research", "educational"]:
            return "cite"

        # For quick mode, only if explicitly requested
        if add_citations:
            return "cite"

        return "finalize"

    async def run(
        self,
        video_url: str,
        mode: str = "standard",
        features: Dict[str, bool] | None = None
    ) -> Dict[str, Any]:
        """
        Run the workflow

        Args:
            video_url: YouTube video URL
            mode: Summary mode (quick, standard, research, educational)
            features: Feature flags

        Returns:
            Result dictionary
        """
        initial_state: SummaryState = {
            "video_url": video_url,
            "mode": mode,
            "features": features or {},
            "api_key": self.api_key,
            "video_data": None,
            "summary": None,
            "research_findings": None,
            "fact_check_result": None,
            "cited_summary": None,
            "timestamps": None,
            "result": None,
            "error": None,
            "current_agent": None
        }

        logger.info(f"Starting workflow for {video_url} in {mode} mode")

        try:
            final_state = await self.graph.ainvoke(initial_state)
            return final_state["result"]
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


import time

# Factory function
def create_summary_workflow(api_key: str | None = None) -> SummaryWorkflow:
    """Create a new summary workflow instance"""
    return SummaryWorkflow(api_key=api_key)
