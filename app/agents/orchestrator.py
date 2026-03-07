"""
Orchestrator Agent - Main coordinator for all specialized agents
"""
from typing import Dict, Any, Optional
import logging

from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Main orchestrator that coordinates specialized agents"""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self._content_agent = None
        self._news_agent = None
        self._seo_agent = None
        logger.info("OrchestratorAgent initialized")

    @property
    def content_agent(self):
        if self._content_agent is None:
            from app.agents.content_agent import ContentAgent
            self._content_agent = ContentAgent(self.llm_service)
        return self._content_agent

    @property
    def news_agent(self):
        if self._news_agent is None:
            from app.agents.news_agent import NewsAgent
            self._news_agent = NewsAgent(self.llm_service)
        return self._news_agent

    @property
    def seo_agent(self):
        if self._seo_agent is None:
            from app.agents.seo_agent import SEOAgent
            self._seo_agent = SEOAgent(self.llm_service)
        return self._seo_agent

    async def run(
        self,
        task: str,
        project_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze the task and delegate to the appropriate specialized agent.

        Args:
            task: Task description string
            project_context: Optional context dictionary

        Returns:
            Result dictionary
        """
        context = project_context or {}
        logger.info(f"Orchestrator running task: {task}")

        try:
            task_lower = task.lower()

            # Route to appropriate agent
            if any(kw in task_lower for kw in ["news", "fetch", "article", "breaking"]):
                logger.info("Routing to NewsAgent")
                return await self.news_agent.execute(task=task, context=context)

            elif any(kw in task_lower for kw in ["seo", "optimize", "keyword", "meta", "rank"]):
                logger.info("Routing to SEOAgent")
                return await self.seo_agent.execute(task=task, context=context)

            elif any(kw in task_lower for kw in ["write", "content", "blog", "post", "social", "rewrite"]):
                logger.info("Routing to ContentAgent")
                return await self.content_agent.execute(task=task, context=context)

            else:
                # Default: use LLM directly
                logger.info("No specific agent matched, using LLM directly")
                messages = [{"role": "user", "content": task}]
                system_prompt = """You are a helpful AI assistant specializing in content, news and SEO tasks."""
                response = await self.llm_service.chat(
                    messages=messages,
                    system_prompt=system_prompt,
                )
                return {
                    "success": True,
                    "agent": "orchestrator",
                    "task": task,
                    "result": response,
                }

        except Exception as e:
            logger.error(f"OrchestratorAgent error: {e}")
            return {"error": str(e), "task": task}
