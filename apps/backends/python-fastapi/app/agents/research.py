"""
Research Agent - Performs web searches for additional context
"""
from typing import Dict, Any, List, Optional
from loguru import logger
import asyncio

from app.agents.base import BaseAgent
from app.config import settings


class ResearchAgent(BaseAgent):
    """Agent specialized in web research and context gathering"""

    def __init__(self, **kwargs):
        super().__init__(agent_name="research", **kwargs)
        self.search_tool = self._initialize_search_tool()

    def _initialize_search_tool(self):
        """Initialize web search tool"""
        try:
            # Try Tavily first (best quality)
            if settings.TAVILY_API_KEY:
                from langchain_community.tools.tavily_search import TavilySearchResults
                return TavilySearchResults(
                    api_key=settings.TAVILY_API_KEY,
                    max_results=settings.MAX_SEARCH_RESULTS
                )
        except Exception as e:
            logger.warning(f"Tavily not available: {e}")

        # Fallback to DuckDuckGo (free, no API key needed)
        try:
            from langchain_community.tools import DuckDuckGoSearchResults
            return DuckDuckGoSearchResults(max_results=settings.MAX_SEARCH_RESULTS)
        except Exception as e:
            logger.warning(f"DuckDuckGo not available: {e}")

        return None

    async def research_topic(
        self,
        topic: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Research a topic using web search

        Args:
            topic: Topic to research
            context: Optional context from video

        Returns:
            Dictionary with research findings
        """
        try:
            if not self.search_tool:
                return {
                    "findings": [],
                    "summary": "Web search is not configured. Please set TAVILY_API_KEY or install DuckDuckGo search.",
                    "sources": []
                }

            self.log_execution("Researching topic", topic)

            # Generate search query
            search_query = await self._generate_search_query(topic, context)

            # Perform search
            search_results = await self._perform_search(search_query)

            # Synthesize findings
            synthesis = await self._synthesize_findings(
                topic=topic,
                search_results=search_results,
                context=context
            )

            return {
                "findings": search_results,
                "summary": synthesis,
                "sources": [r.get("url", "") for r in search_results if r.get("url")],
                "search_query": search_query
            }

        except Exception as e:
            logger.error(f"Research error: {e}")
            return {
                "findings": [],
                "summary": f"Research failed: {str(e)}",
                "sources": []
            }

    async def _generate_search_query(
        self,
        topic: str,
        context: Optional[str]
    ) -> str:
        """Generate optimized search query"""
        if not context:
            return topic

        prompt = f"""Generate a focused web search query to find reliable information about this topic.

Topic: {topic}

Context from video:
{context[:500]}

Generate a concise search query (1-2 sentences max) that will find:
1. Authoritative sources
2. Recent information
3. Factual data

Search Query:"""

        query = await self.invoke(prompt)
        return query.strip()

    async def _perform_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform web search"""
        try:
            # Run search in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self.search_tool.invoke(query)
            )

            # Parse results
            parsed_results = self._parse_search_results(results)

            self.log_execution("Search complete", f"{len(parsed_results)} results")
            return parsed_results

        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def _parse_search_results(self, raw_results: Any) -> List[Dict[str, Any]]:
        """Parse search results into standard format"""
        parsed = []

        if isinstance(raw_results, str):
            # DuckDuckGo returns string
            # Parse the string format
            import re
            matches = re.findall(r'\[snippet: (.*?), title: (.*?), link: (.*?)\]', raw_results)

            for snippet, title, link in matches:
                parsed.append({
                    "title": title,
                    "snippet": snippet,
                    "url": link
                })

        elif isinstance(raw_results, list):
            # Tavily returns list of dicts
            for result in raw_results:
                if isinstance(result, dict):
                    parsed.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("content", result.get("snippet", "")),
                        "url": result.get("url", "")
                    })

        return parsed[:settings.MAX_SEARCH_RESULTS]

    async def _synthesize_findings(
        self,
        topic: str,
        search_results: List[Dict[str, Any]],
        context: Optional[str]
    ) -> str:
        """Synthesize search results into coherent summary"""
        if not search_results:
            return "No relevant information found."

        # Format search results
        results_text = self._format_search_results(search_results)

        prompt = f"""Synthesize these web search results into a brief, informative summary.

Topic: {topic}

{f"Context from video: {context[:300]}" if context else ""}

Search Results:
{results_text}

Create a synthesis that:
1. Summarizes key findings
2. Notes source credibility where mentioned
3. Highlights any consensus or disagreements
4. Identifies the most authoritative information
5. Stays objective and factual

Synthesis:"""

        synthesis = await self.invoke(prompt)
        return synthesis

    def _format_search_results(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for prompt"""
        formatted = []

        for i, result in enumerate(results, 1):
            formatted.append(
                f"[{i}] {result.get('title', 'Untitled')}\n"
                f"    {result.get('snippet', 'No description')}\n"
                f"    Source: {result.get('url', 'No URL')}"
            )

        return "\n\n".join(formatted)

    async def extract_research_topics(
        self,
        summary: str,
        max_topics: int = 5
    ) -> List[str]:
        """
        Extract topics from summary that need research

        Args:
            summary: Video summary
            max_topics: Maximum topics to extract

        Returns:
            List of research topics
        """
        prompt = f"""Identify key claims or topics from this summary that would benefit from external research or verification.

Summary:
{summary}

Extract up to {max_topics} specific claims, statistics, or topics that:
1. Make factual assertions
2. Could be verified or expanded with external sources
3. Would add valuable context
4. Are specific enough to research

Format: Return only the topics, one per line, without numbering.

Topics:"""

        response = await self.invoke(prompt)

        # Parse topics
        topics = [
            line.strip()
            for line in response.split('\n')
            if line.strip() and not line.strip().startswith(('#', '-', '*'))
        ]

        return topics[:max_topics]

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the research agent

        Args:
            input_data: {
                "topic": str OR "summary": str (to extract topics),
                "context": Optional[str],
                "auto_extract": Optional[bool]
            }

        Returns:
            Dictionary with research results
        """
        try:
            topic = input_data.get("topic")
            summary = input_data.get("summary")
            context = input_data.get("context")
            auto_extract = input_data.get("auto_extract", False)

            # Extract topics from summary if requested
            if auto_extract and summary and not topic:
                topics = await self.extract_research_topics(summary)

                if not topics:
                    return self.format_output(
                        success=True,
                        data={
                            "findings": [],
                            "summary": "No researchable topics found in summary.",
                            "sources": []
                        }
                    )

                # Research first topic
                topic = topics[0]
                self.log_execution("Auto-extracted topic", topic)

            if not topic:
                return self.format_output(
                    success=False,
                    data=None,
                    error="No topic provided and auto-extract failed"
                )

            self.log_execution("Starting research", topic)

            # Perform research
            result = await self.research_topic(topic, context)

            self.log_execution(
                "Research complete",
                f"{len(result['findings'])} findings"
            )

            return self.format_output(
                success=True,
                data=result,
                metadata={
                    "topic": topic,
                    "source_count": len(result["sources"])
                }
            )

        except Exception as e:
            logger.error(f"Research agent error: {e}")
            return self.format_output(
                success=False,
                data=None,
                error=str(e)
            )
