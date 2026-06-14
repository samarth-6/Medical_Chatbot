import asyncio
import aiohttp
import trafilatura

from backend.logger import logger


class CrawlerService:
    async def fetch_html(
        self,
        session,
        url: str
    ):

        try:

            async with session.get(
                url,
                timeout=30
            ) as response:

                if response.status != 200:
                    return None

                return await response.text()

        except Exception as e:

            logger.warning(
                f"Failed to fetch {url}: {e}"
            )

            return None

    async def extract_page(
        self,
        session,
        url: str
    ):

        html = await self.fetch_html(
            session,
            url
        )

        if not html:
            return None

        try:

            text = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=False
            )

            if not text:
                return None

            return text

        except Exception as e:

            logger.warning(
                f"Extraction failed: {url}: {e}"
            )

            return None

    async def extract_many(self, urls):

        async with aiohttp.ClientSession() as session:

            tasks = [
                self.extract_page(
                    session,
                    url
                )
                for url in urls
            ]

            return await asyncio.gather(
                *tasks,
                return_exceptions=True
            )