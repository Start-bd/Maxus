"""
LLM Service - Unified interface for OpenAI and Anthropic
"""
from typing import List, Dict, Any, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Unified LLM service supporting OpenAI and Anthropic"""

    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the LLM client based on provider"""
        try:
            if self.provider == "openai" and settings.OPENAI_API_KEY:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info(f"OpenAI client initialized with model: {self.model}")
            elif self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
                import anthropic
                self._client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info(f"Anthropic client initialized with model: {self.model}")
            else:
                logger.warning("No LLM API key configured. Using mock responses.")
        except ImportError as e:
            logger.warning(f"LLM library not installed: {e}. Using mock responses.")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Send chat messages and get a response"""
        if self._client is None:
            return self._mock_response(messages)

        try:
            if self.provider == "openai":
                return await self._openai_chat(messages, system_prompt, max_tokens, temperature)
            elif self.provider == "anthropic":
                return await self._anthropic_chat(messages, system_prompt, max_tokens, temperature)
        except Exception as e:
            logger.error(f"LLM chat error: {e}")
            raise

        return self._mock_response(messages)

    async def _openai_chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """OpenAI chat completion"""
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        response = await self._client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature if temperature is not None else self.temperature,
        )
        return response.choices[0].message.content

    async def _anthropic_chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Anthropic Claude chat completion"""
        response = await self._client.messages.create(
            model=self.model or "claude-3-haiku-20240307",
            max_tokens=max_tokens or self.max_tokens,
            system=system_prompt or "",
            messages=messages,
        )
        return response.content[0].text

    async def generate_article(
        self,
        topic: str,
        keywords: List[str] = None,
        style: str = "news",
        length: int = 800,
    ) -> Dict[str, Any]:
        """Generate a full article"""
        keywords = keywords or []
        system_prompt = f"""You are a professional {style} writer. Write high-quality, factual articles."""
        messages = [{
            "role": "user",
            "content": f"""Write a {style} article about: {topic}
Target keywords: {', '.join(keywords)}
Target length: approximately {length} words
Format: JSON with keys: title, content, summary, tags"""
        }]

        try:
            response = await self.chat(messages, system_prompt)
            import json
            # Try to parse JSON, fallback to plain text
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"title": topic, "content": response, "summary": "", "tags": keywords}
        except Exception as e:
            logger.error(f"Article generation error: {e}")
            return {"title": topic, "content": "", "summary": "", "tags": [], "error": str(e)}

    async def summarize_text(self, text: str, max_length: int = 150) -> str:
        """Summarize a piece of text"""
        messages = [{
            "role": "user",
            "content": f"Summarize the following text in under {max_length} words:\n\n{text}"
        }]
        return await self.chat(messages)

    async def extract_keywords(self, text: str, count: int = 5) -> List[str]:
        """Extract keywords from text"""
        messages = [{
            "role": "user",
            "content": f"Extract the top {count} keywords from this text. Return only a comma-separated list:\n\n{text}"
        }]
        response = await self.chat(messages)
        return [kw.strip() for kw in response.split(",")][:count]

    def _mock_response(self, messages: List[Dict[str, str]]) -> str:
        """Return a mock response when no API key is configured"""
        last_message = messages[-1].get("content", "") if messages else ""
        return f"[Mock response] No LLM API key configured. Query: {last_message[:100]}"
