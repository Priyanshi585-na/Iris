import google.genai as genai
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_screenshot(screenshot_bytes, task, step_history):
    image_data = base64.b64encode(screenshot_bytes).decode("utf-8")
    history_text = "\n".join(step_history[-5:]) if step_history else "No steps yet"

    prompt = f"""You are Iris, an AI web agent. You control a real browser to complete tasks.

CURRENT TASK: {task}

STEPS TAKEN SO FAR:
{history_text}

Look at this screenshot and decide the NEXT single action to take.

Respond ONLY with a JSON object like this:
{{
  "thought": "what you see and why you're taking this action",
  "action": "click" | "type" | "navigate" | "scroll" | "done",
  "selector": "CSS selector of element to interact with (if click/type)",
  "text": "text to type (if action is type)",
  "url": "full url (if action is navigate)",
  "direction": "up" | "down" (if action is scroll),
  "result": "final answer to user (if action is done)"
}}

RULES:
- One action at a time
- If task is complete, use action "done"
- For search bars use action "type" then a separate "click" for the button
- Maximum 15 steps total
- Be precise with CSS selectors
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            genai.types.Part.from_bytes(data=screenshot_bytes, mime_type="image/png"),
            prompt
        ]
    )

    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)
