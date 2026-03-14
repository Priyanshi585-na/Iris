import asyncio
import base64
from playwright.async_api import async_playwright, Browser, Page


class BrowserController:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    async def start(self):
        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.connect_over_cdp("http://localhost:9222")

        contexts = self.browser.contexts
        if contexts and contexts[0].pages:
            self.page = contexts[0].pages[0]

        else:
            context = await self.browser.new_context()
            self.page = await context.new_page()

        await self.page.set_viewport_size({"width":1280, "height": 720})
        print("Connected")

    async def screenshot(self):
        return await self.page.screenshot(type="png")
    
    async def execute_action(self, action: dict) -> str:
        act = action.get("action")

        try:
            if act == "navigate":
                url = action.get("url")
                await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(2)
                return f"Navigate to {url}"

            elif act == "click":
                x = action.get("x")
                y = action.get("y")
                selector = action.get("selector")

                if x and y:
                    await self.page.mouse.click(x, y)
                    await asyncio.sleep(1)
                    return f"Clicked at ({x}, {y})"
                elif selector:
                    # Fallback to selector
                    await self.page.click(selector, timeout=5000)
                    await asyncio.sleep(1)
                    return f"Clicked {selector}"
                else:
                    return "No click target provided"

            elif act == "type":
                x = action.get("x")
                y = action.get("y")
                selector = action.get("selector")
                text = action.get("text", "")

                if x and y:
                    await self.page.mouse.click(x, y)
                    await asyncio.sleep(0.5)
                elif selector:
                    await self.page.click(selector, timeout=5000)
                    await asyncio.sleep(0.5)

                await self.page.keyboard.type(text, delay=50)
                await asyncio.sleep(0.5)
                await self.page.keyboard.press("Enter")
                await asyncio.sleep(2)
                return f"Typed '{text}' and pressed Enter"

            elif act == "scroll":
                direction = action.get("direction", "down")
                delta = 500 if direction == "down" else -500
                await self.page.mouse.wheel(0, delta)
                await asyncio.sleep(1)
                return f"Scrolled {direction}"

            elif act == "press_enter":
                await self.page.keyboard.press("Enter")
                await asyncio.sleep(2)
                return "Pressed Enter"

            elif act == "done":
                return "DONE"

            else:
                return f"Unknown action: {act}"

        except Exception as e:
            return f"Action failed {str(e)}"

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()