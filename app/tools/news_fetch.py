"""
News Fetch Tool - Fetches news from NewsAPI
"""
from typing import Optional
from app.tools.base import BaseTool, ToolResult
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class NewsFetchTool(BaseTool):
    """Tool for fetching news articles"""

    @property
    def name(self) -> str:
        return "news_fetch"

    @property
    def description(self) -> str:
        return "Fetches news articles from NewsAPI by category and keywords"

    async def execute(
        self,
        category: str = "technology",
        keywords: str = "",
        limit: int = 10,
    ) -> ToolResult:
        """Fetch news articles"""
        if not settings.NEWS_API_KEY:
            # Return mock data
            from datetime import datetime
            mock_articles = [
                {
                    "title": f"Tech News {i+1}",
                    "description": f"News about {category}",
                    "url": f"https://example.com/{i+1}",
                    "publishedAt": datetime.utcnow().isoformat(),
                }
                for i in range(min(limit, 3))
            ]
            return ToolResult(
                success=True,
                data={"articles": mock_articles, "note": "Mock data - configure NEWS_API_KEY"},
            )

        try:
            import httpx
            params = {
                "category": category,
                "language": "en",
                "pageSize": limit,
                "apiKey": settings.NEWS_API_KEY,
            }
            if keywords:
                params["q"] = keywords

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://newsapi.org/v2/top-headlines",
                    params=params,
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()

            return ToolResult(
                success=True,
                data={
                    "articles": data.get("articles", [])[:limit],
                    "total_results": data.get("totalResults", 0),
                },
            )
        except Exception as e:
            logger.error(f"NewsFetchTool error: {e}")
            return ToolResult(success=False, error=str(e))
