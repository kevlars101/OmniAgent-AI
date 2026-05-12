import logging
import asyncio
from typing import Dict, Any, List
from playwright.async_api import Page

from agents.browser.dom_analyzer import DOMAnalyzer

logger = logging.getLogger(__name__)

class ActionExecutor:
    """
    Executes specific actions on the DOM based on element IDs mapped by DOMAnalyzer.
    """
    @staticmethod
    async def click(page: Page, element_id: str) -> bool:
        logger.debug(f"Attempting to click element: {element_id}")
        try:
            # Wait for element with the specific injected ID
            selector = f'[data-omni-id="{element_id}"]'
            await page.wait_for_selector(selector, timeout=5000)
            await page.click(selector)
            await page.wait_for_load_state("networkidle", timeout=5000)
            return True
        except Exception as e:
            logger.error(f"Failed to click {element_id}: {e}")
            return False

    @staticmethod
    async def type_text(page: Page, element_id: str, text: str) -> bool:
        logger.debug(f"Attempting to type into element: {element_id}")
        try:
            selector = f'[data-omni-id="{element_id}"]'
            await page.wait_for_selector(selector, timeout=5000)
            await page.fill(selector, text)
            return True
        except Exception as e:
            logger.error(f"Failed to type into {element_id}: {e}")
            return False


class WebNavigator:
    """
    High-level navigation and interaction orchestrator.
    Handles page transitions, waits, and action verification.
    """
    def __init__(self, page: Page):
        self.page = page

    async def goto(self, url: str) -> bool:
        """Navigates to a URL and waits for it to settle."""
        logger.info(f"Navigating to {url}")
        try:
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
            return True
        except Exception as e:
            logger.error(f"Navigation failed for {url}: {e}")
            return False

    async def get_state(self) -> Dict[str, Any]:
        """Returns the current state of the page including DOM elements and screenshot."""
        elements = await DOMAnalyzer.extract_interactable_elements(self.page)
        
        # Take a screenshot as bytes
        screenshot_bytes = await self.page.screenshot(type="jpeg", quality=70)
        
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "elements": elements,
            "screenshot": screenshot_bytes
        }
    
    async def perform_action(self, action: Dict[str, Any]) -> bool:
        """
        Parses an agent action dict and executes it.
        Example action: {"type": "click", "element_id": "omni-el-5"}
        """
        action_type = action.get("type")
        element_id = action.get("element_id")
        
        if action_type == "click":
            return await ActionExecutor.click(self.page, element_id)
        elif action_type == "type":
            text = action.get("text", "")
            return await ActionExecutor.type_text(self.page, element_id, text)
        elif action_type == "scroll":
            # Simple scroll down
            await self.page.evaluate("window.scrollBy(0, window.innerHeight)")
            await asyncio.sleep(1)
            return True
        elif action_type == "wait":
            await asyncio.sleep(action.get("duration", 2))
            return True
            
        logger.warning(f"Unknown action type: {action_type}")
        return False
