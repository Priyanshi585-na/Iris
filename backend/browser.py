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
    
    async def get_current_url(self):
        return self.page.url


    async def get_ax_tree(self):
        elements = await self.page.evaluate(
            """
    () => {
      const interactive = [];
      const selector = 'a,button, input, textarea, select, [role="button"],[role="link"],[role="textbox], [onclick]';
      const els = document.querySelectorAll(selector);
      
      els.forEach((el, i) => {
      const rect = el.getBoundingClientRect();
      if(rect.width > 0 && rect.height > 0 && rect.top>=0 && rect.top <= window.innerHeight){

      const label = el.getAttribute('aria-label')|| el.getAttribute('placeholder') || el.getAttribute('title') || el.getAttribute('name') || el.innerText?.trim().slice(0,50) || el.tagName.toLowerCase();

      interactive.push({
        id: i+1,
        tag: el.tagName.toLowerCase(),
        label: label,
        x: Math.round(rect.x + rect.width/2),
        y: Math.round(rect.y + rect.height/2),
        type: el.getAttribute('type') || ''
      });
      }
    });
    return interactive;
    }
""")
        
        tree = "INTERACTIVE ELEMENTS ON PAGE:\n"
        for el in elements[:50]:
            tree += f"[{el['id']}] {el['tag']} \"{el['label']}\" at (et{el['x']}, {el['y']})\n"

        return tree, elements


    
    async def execute_action(self, action, elements):
        act = action.get("action")
        element_id = action.get("element_id")

        try:
            if element_id and elements:
                el = next((e for e in elements if e['id'] == element_id), None)
                if el:
                    x, y = el['x'], el['y']
            else:
                x = action.get("x")
                y = action.get("y")

            if act == "navigate":
                url = action.get("url")
                await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(2)
                return f"Navigate to {url}"
            

            elif act == "click":
                await self.page.mouse.click(x,y)
                await asyncio.sleep(1)
                return f"Clicked [{element_id} at ({x},{y})]"

            elif act == "type":
                await self.page.mouse.click(x,y)
                await asyncio.sleep(0.5)
                text = action.get("text", "")
                await self.page.keyboard.type(text)
                await asyncio.sleep(0.5)
                await self.page.keyboard.press("Enter")
                await asyncio.sleep(2)
                return f"Typed '{text}'"

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