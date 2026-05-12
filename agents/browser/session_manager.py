import asyncio
import logging
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

logger = logging.getLogger(__name__)

class BrowserSessionManager:
    """
    Manages Playwright browser instances, contexts, and pages.
    Supports session persistence and multi-tab workflows.
    """
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._contexts: dict[str, BrowserContext] = {}

    async def start(self):
        """Initializes the Playwright engine and browser."""
        if not self._playwright:
            self._playwright = await async_playwright().start()
            # Use chromium by default
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled"]
            )
            logger.info("Playwright browser started.")

    async def get_context(self, session_id: str = "default", persist_dir: Optional[str] = None) -> BrowserContext:
        """
        Retrieves or creates a browser context.
        Can persist state (cookies, local storage) if persist_dir is provided.
        """
        await self.start()
        
        if session_id not in self._contexts:
            logger.debug(f"Creating new browser context for session: {session_id}")
            if persist_dir:
                context = await self._playwright.chromium.launch_persistent_context(
                    user_data_dir=persist_dir,
                    headless=self.headless,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720}
                )
                self._contexts[session_id] = context
            else:
                context = await self._browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720}
                )
                self._contexts[session_id] = context
                
        return self._contexts[session_id]

    async def get_page(self, session_id: str = "default") -> Page:
        """Gets an active page for the session, creating one if needed."""
        context = await self.get_context(session_id)
        pages = context.pages
        if pages:
            return pages[-1] # Return the most recently opened tab
        return await context.new_page()

    async def new_tab(self, session_id: str = "default") -> Page:
        """Explicitly opens a new tab in the session context."""
        context = await self.get_context(session_id)
        return await context.new_page()

    async def close(self):
        """Cleans up all resources."""
        for ctx in self._contexts.values():
            await ctx.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info("Playwright browser stopped.")

# Singleton instance
browser_session_manager = BrowserSessionManager()
