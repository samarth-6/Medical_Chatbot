from backend.services.serp_service import (
    SerpService
)

from backend.services.crawler_service import (
    CrawlerService
)

from backend.logger import logger


class WebSearchAgent:
    def __init__(self):

        self.search_service = SerpService()

        self.crawler_service = CrawlerService()

    async def run(self, query: str):

        logger.info(
            f"WebSearchAgent running: {query}"
        )

        search_results = await self.search_service.search(
            query
        )

        if not search_results:

            return {
                "context": "",
                "sources": []
            }

        urls = [
    r["url"]
    for r in search_results[:5]
]

        extracted_pages = (
            await self.crawler_service.extract_many(
                urls
            )
        )

        contexts = []

        sources = []

        for result, text in zip(
            search_results,
            extracted_pages
        ):

            if not text:
                continue

            title = result["title"]
            url = result["url"]

            citation = (
                f"[{title}]({url})"
            )

            contexts.append(
                f"""
SOURCE:
{citation}

CONTENT:
{text[:5000]}
"""
            )

            sources.append(
                {
                    "title": title,
                    "url": url,
                    "citation": citation
                }
            )

        final_context = "\n\n".join(
            contexts
        )

        return {
            "context": final_context,
            "sources": sources
        }