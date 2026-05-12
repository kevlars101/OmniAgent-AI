import logging
from typing import Dict, List, Any
from playwright.async_api import Page

logger = logging.getLogger(__name__)

class DOMAnalyzer:
    """
    Analyzes the Document Object Model to extract interactive elements,
    text content, and layout structure for agent decision-making.
    """
    
    @staticmethod
    async def extract_interactable_elements(page: Page) -> List[Dict[str, Any]]:
        """
        Extracts buttons, links, inputs, and their bounding boxes.
        Injects a small script into the page to tag elements with unique IDs.
        """
        logger.debug("Extracting interactable elements from DOM...")
        
        # Inject JavaScript to find and tag interactable elements
        script = """
        () => {
            let elements = [];
            let interactables = document.querySelectorAll('a, button, input, textarea, select, [role="button"], [tabindex]:not([tabindex="-1"])');
            
            interactables.forEach((el, index) => {
                const rect = el.getBoundingClientRect();
                // Filter out hidden or 0-sized elements
                if (rect.width > 0 && rect.height > 0 && window.getComputedStyle(el).visibility !== 'hidden') {
                    const omniId = `omni-el-${index}`;
                    el.setAttribute('data-omni-id', omniId);
                    
                    elements.push({
                        id: omniId,
                        tag: el.tagName.toLowerCase(),
                        text: el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || '',
                        type: el.type || '',
                        href: el.href || '',
                        rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height }
                    });
                }
            });
            return elements;
        }
        """
        elements = await page.evaluate(script)
        return elements

    @staticmethod
    async def extract_main_content(page: Page) -> str:
        """
        Extracts the main readable text from the page, stripping navs and footers.
        Uses Readability.js logic or similar heuristics (simplified here).
        """
        # Simplified: Get all text from body
        # In a robust implementation, use Mozilla's Readability or similar
        content = await page.evaluate("() => document.body.innerText")
        return content
