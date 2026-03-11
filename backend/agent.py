import asyncio
from browser import BrowserController
from vision import analyze_screenshot

class IrisAgent:
    def __int__(self):
        self.browser = BrowserController()
        self.step_history = []
        self.max_steps = 15
        self.running = False

    async def start(self):
        await self.browser.start()
        print("Iris Agent running!")

    async def run_task(self, task, on_step = None):
        self.running = True
        self.step_history = []
        result = None

        print(f"Task:{task}")

        for step in range(self.max_steps):
            if not self.running:
                break

            screenshot = await self.browser.screenshot()

            try:
                action = analyze_screenshot(screenshot, task, self.step_history)
            
            except Exception as e:
                print(f"Error {e}")
                break

            thought = action.get("thought")
            act = action.get("action")

            if on_step:
                await on_step({
                    "step": step+1,
                    "thought": thought,
                    "act": act,
                    "screenshot": screenshot
                })
            
            self.step_history.append(f"{step + 1}. {act}")

            if act == "done":
                result = action.get("result")
                if on_step:
                    await on_step({
                        "step": step + 1,
                        "thought": thought,
                        "action": "done",
                        "result": result,
                        "screenshot": screenshot
                    })
                break

            outcome = await self.browser.execute_action(action)
            print(f"Outcome: {outcome}")
            await asyncio.sleep(1)
        
        self.running = False
        return result
    
    def stop(self):
        self.running = False
        print("Iris stopped!")

    async def close(self):
        await self.browser.close()