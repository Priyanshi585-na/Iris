from dotenv import load_dotenv
import base64
import os
import json
import google.generativeai as genai


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def analyze_screenshot(ss_bytes, task, step_history):
    image_data = base64.b64encode(ss_bytes).decode('utf-8')
    history_text = "\n".join(step_history[-5:]) if step_history else "No steps yet"
    prompt = f"""

You are Iris, an AI web agent. You can control a real browser to complete tasks.

CURRENT TASK : {task}

STEPS TAKEN SO FAR: {history_text}

Look at this screenshot and decide the NEXT single action to take.

Respond ONLY with JSON object in the following format:
{{
"thought" : "what you see and why you're taking this action",
"action" : "click" | "type" | "navigate" | "scroll" | "done",
"selector": "CSS selector of element to interact with (if action is click/type)",
"text" : "text to type (if action is type)",
"url" : "full url (if action is navigate)",
"direction" : "up" | "down" (if action is scroll)
"result":"final answer to user (if action is done)"
}}

RULES:
- One action at a time.
- If a task is complete, use action "done"
- For search bars use action "type", then separate "click" for button
- Maximum 15 steps total
- Be precise with CSS selector

"""
    
    response = model.generate_content([
        {"mime_type":"image/png",
         "data": image_data},
         prompt
    ])

    text = response.text.strip()
    text = text.replace("```json", ""). replace("```","").strip()

    return json.loads(text)
