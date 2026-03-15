import asyncio
from browser import BrowserController
from vision import analyze_screenshot

class IrisAgent:
    def __init__(self):
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
            ax_tree, elements = await self.browser.get_ax_tree()

            try:
                action = analyze_screenshot(screenshot, task, self.step_history, ax_tree)
            
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

            outcome = await self.browser.execute_action(action, elements)
            print(f"Outcome: {outcome}")

            self.step_history.append(
                f"Step {step + 1}: {thought} → {act} → Result: {outcome}"
            )

            if(len(self.step_history)>=4):
                last_4 = []
                for h in self.step_history[-4:]:
                   parts = h.split('→')
                   if len(parts) > 1:
                       last_4.append(parts[1].strip())

                if len(set(last_4)) == 1:
                    print("Loop detected, forcing navigate to restart")
                    await self.browser.execute_action({
                        "action":"navigate",
                        "url": await self.browser.get_current_url()
                    })
                    self.step_history.append("Loop detected - page refreshed")
                    
            await asyncio.sleep(1)
        
        self.running = False
        return result
    
    def stop(self):
        self.running = False
        print("Iris stopped!")

    async def close(self):
        await self.browser.close()