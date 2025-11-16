"""
Base Agent class for all specialized agents
"""
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from loguru import logger

from app.config import settings, AGENT_PROMPTS, LLM_CONFIGS


class BaseAgent(ABC):
    """Base class for all agents in the system"""

    def __init__(
        self,
        agent_name: str,
        llm_provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize base agent

        Args:
            agent_name: Name of the agent (must match key in AGENT_PROMPTS)
            llm_provider: LLM provider to use (openai, anthropic, google, openrouter)
            model: Specific model to use
            api_key: Optional API key override
            **kwargs: Additional configuration
        """
        self.agent_name = agent_name
        self.system_prompt = AGENT_PROMPTS.get(agent_name, "")

        # LLM Configuration
        self.llm_provider = llm_provider or settings.DEFAULT_LLM_PROVIDER
        self.model = model or LLM_CONFIGS[self.llm_provider]["model"]
        self.api_key = api_key

        # Initialize LLM
        self.llm = self._initialize_llm()

        logger.info(f"Initialized {agent_name} agent with {self.llm_provider}/{self.model}")

    def _initialize_llm(self):
        """Initialize the appropriate LLM based on provider"""
        config = LLM_CONFIGS[self.llm_provider].copy()
        config["model"] = self.model

        if self.llm_provider == "openai":
            return ChatOpenAI(
                api_key=self.api_key or settings.OPENAI_API_KEY,
                **config
            )

        elif self.llm_provider == "google":
            return ChatGoogleGenerativeAI(
                google_api_key=self.api_key or settings.GOOGLE_AI_API_KEY,
                **config
            )

        elif self.llm_provider == "openrouter":
            return ChatOpenAI(
                api_key=self.api_key or settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
                **config
            )

        else:
            # Default to OpenRouter
            return ChatOpenAI(
                api_key=self.api_key or settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
                **config
            )

    def create_messages(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List:
        """
        Create message list with system prompt and context

        Args:
            user_message: The user's message/query
            context: Optional context dictionary

        Returns:
            List of messages for the LLM
        """
        messages = [SystemMessage(content=self.system_prompt)]

        # Add context if provided
        if context:
            context_str = self._format_context(context)
            if context_str:
                messages.append(HumanMessage(content=f"Context:\n{context_str}"))

        # Add user message
        messages.append(HumanMessage(content=user_message))

        return messages

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary into a string"""
        parts = []
        for key, value in context.items():
            if value is not None:
                parts.append(f"{key}: {value}")
        return "\n".join(parts)

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main task

        Args:
            input_data: Input data for the agent

        Returns:
            Result dictionary
        """
        pass

    async def invoke(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Invoke the LLM with a message

        Args:
            user_message: The message to send
            context: Optional context

        Returns:
            LLM response string
        """
        try:
            messages = self.create_messages(user_message, context)
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error invoking {self.agent_name}: {e}")
            raise

    def log_execution(self, step: str, data: Any):
        """Log agent execution step"""
        logger.info(f"[{self.agent_name}] {step}: {str(data)[:100]}")

    def format_output(
        self,
        success: bool,
        data: Any,
        error: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Format agent output consistently

        Args:
            success: Whether execution was successful
            data: The output data
            error: Optional error message
            metadata: Optional metadata

        Returns:
            Formatted output dictionary
        """
        output = {
            "agent": self.agent_name,
            "success": success,
            "data": data,
        }

        if error:
            output["error"] = error

        if metadata:
            output["metadata"] = metadata

        return output
