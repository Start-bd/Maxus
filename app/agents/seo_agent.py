"""
SEO Agent - Optimizes content for search engines
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class SEOAgent:
    """Agent for SEO optimization tasks"""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        logger.info("SEOAgent initialized")

    async def execute(self, task: str, context: Dict[str, Any]) -> Dict:
        """Execute SEO-related task"""
        logger.info(f"SEOAgent executing: {task}")
        try:
            task_lower = task.lower()
            if "optimize" in task_lower:
                return await self.optimize_content(task, context)
            elif "keyword" in task_lower:
                content = context.get("content", "")
                count = context.get("count", 10)
                keywords = await self.llm_service.extract_keywords(content, count=count)
                return {"success": True, "keywords": keywords}
            elif "meta" in task_lower:
                title = context.get("title", "")
                content = context.get("content", "")
                keywords = context.get("keywords", [])
                return await self.generate_meta_tags(title=title, content=content, keywords=keywords)
            else:
                return await self.optimize_content(task, context)
        except Exception as e:
            logger.error(f"SEOAgent error: {e}")
            return {"error": str(e), "success": False}

    async def optimize_content(self, task: str, context: Dict[str, Any]) -> Dict:
        """Optimize content for SEO"""
        content = context.get("content", "")
        keywords = context.get("keywords", [])

        system_prompt = """You are an SEO expert. Optimize content for search engines while maintaining quality.
Focus on:
- Natural keyword integration
- Proper heading structure
- Readability improvements
- Internal linking suggestions"""

        messages = [{
            "role": "user",
            "content": f"""Optimize this content for SEO:
Target keywords: {', '.join(keywords)}

Content:
{content}"""
        }]

        optimized = await self.llm_service.chat(messages=messages, system_prompt=system_prompt)

        return {
            "success": True,
            "optimization": optimized,
            "keywords_used": keywords,
            "optimized_at": datetime.utcnow().isoformat(),
        }

    async def generate_meta_tags(
        self,
        title: str,
        content: str,
        keywords: List[str] = None,
    ) -> Dict:
        """Generate SEO meta tags for content"""
        keywords = keywords or []
        system_prompt = """You are an SEO expert. Generate optimal meta tags.
Return JSON with keys: meta_title, meta_description, og_title, og_description, keywords"""

        messages = [{
            "role": "user",
            "content": f"""Generate meta tags for:
Title: {title}
Keywords: {', '.join(keywords)}
Content preview: {content[:500]}"""
        }]

        response = await self.llm_service.chat(messages=messages, system_prompt=system_prompt)

        # Try to parse JSON
        try:
            import json
            meta_tags = json.loads(response)
        except (json.JSONDecodeError, ValueError):
            meta_tags = {
                "meta_title": title[:60],
                "meta_description": content[:160],
                "keywords": ", ".join(keywords),
            }

        return {
            "success": True,
            "meta_tags": meta_tags,
            "generated_at": datetime.utcnow().isoformat(),
        }
