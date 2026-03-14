from google import genai
from google.genai import types
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    vertexai=True,
    project="iris-agent-489709",
    location="global"
)

def analyze_screenshot(screenshot_bytes: bytes, task: str, step_history: list) -> dict:
    history_text = "\n".join(step_history[-5:]) if step_history else "No steps yet"

    prompt = f"""You are Iris, an AI web agent. You control a real browser to complete tasks.

CURRENT TASK: {task}

STEPS TAKEN SO FAR:
{history_text}

Look at this screenshot and decide the NEXT single action to take.

Respond ONLY with a JSON object like this:
{{
  "thought": "what you see and why you're taking this action",
  "action": "click" | "type" | "navigate" | "scroll" | "done" | "press_enter",
  "selector": "CSS selector (optional, use if obvious)",
  "x": 640,
  "y": 360,
  "text": "text to type (if action is type)",
  "url": "full url (if action is navigate)",
  "direction": "up" | "down" (if action is scroll),
  "result": "final answer to user (if action is done)"
}}

RULES:
- One action at a time
- ALWAYS navigate directly to the website URL, never use Google search
- For Flipkart tasks start with action "navigate" to "https://www.flipkart.com"
- For Amazon tasks start with action "navigate" to "https://www.amazon.in"
- For clicks, ALWAYS provide x and y coordinates of the element center
- x and y are pixel coordinates on a 1280x720 screen
- CSS selector is optional backup only
- For typing, click the element first using coordinates, then type
- If task is complete, use action "done"
- For search bars use action "type" then press Enter key
- You can use "scroll" if some buttons are not or partially visible to you.
- Maximum 15 steps total
- Be precise with CSS selectors
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=screenshot_bytes, mime_type="image/png"),
            prompt
        ]
    )

    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    
    start = text.find('{')
    end = text.rfind('}') + 1
    text = text[start:end]
    return json.loads(text)