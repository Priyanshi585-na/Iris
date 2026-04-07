# Iris — Autonomous Browser Agent

Iris is an autonomous browser system that can **perceive, reason, and act** on web pages — similar to how a human interacts with a browser.

It combines browser automation, structured page understanding, and LLM-based decision making to execute tasks step-by-step.

---

##  Features

-  Connects to a real browser using Playwright (CDP)
-  Extracts structured interactive elements from the DOM
-  Uses visual context (screenshots) for reasoning
-  Executes actions: click, type, scroll, navigate
-  Runs an agent loop: observe → think → act
-  Streams live browser screen using noVNC

---

##  How It Works

### 1. Perception Layer
- Captures browser screenshots
- Extracts interactive elements (buttons, inputs, links)
- Builds a structured representation of the page

### 2. Reasoning Layer
- Sends context (DOM + screenshot) to an LLM
- Decides the next best action

### 3. Action Layer
- Executes actions using Playwright:
  - click
  - type
  - scroll
  - navigation

### 4. Feedback Loop

Observe → Understand → Decide → Act → Repeat

---

##  Architecture (V1)

User  
↓  
Backend (FastAPI)  
↓  
Playwright Browser (via CDP)  
↓  
DOM Extraction + Screenshot  
↓  
LLM (Vertex AI - Gemini Flash)  
↓  
Action Execution  
↓  
noVNC (Live Screen Streaming)

---

##  Current Limitations (V1)

- Single VM deployment (shared session across users)
- No per-user isolation
- Heavy reliance on vision (screenshots → higher cost)
- Uses coordinate-based clicking (can be fragile)

---

##  Roadmap (V2)

-  Per-user isolated browser sessions  
-  Containerized execution (Docker)  
-  Scalable architecture (multi-instance support)  
-  Voice input for natural interaction  
-  Hybrid reasoning (DOM-first, vision fallback)  
-  Reduced LLM cost via selective screenshot usage  

---

##  Design Insights

- Instead of raw pixel-based control, Iris builds a structured interaction map  
- LLM is used for decision making, not raw extraction  
- System follows a closed-loop agent architecture  
- Combines symbolic (DOM) + perceptual (vision) inputs  

---

##  Tech Stack

- Backend: FastAPI, Python  
- Browser Automation: Playwright (CDP)  
- LLM: Vertex AI (Gemini Flash)  
- Streaming: noVNC  
- Infra: Google Cloud VM (Compute Engine)  

---


## Future Direction

Iris is evolving toward a multi-user, scalable autonomous agent system, with:

- distributed browser sessions  
- intelligent routing  
- efficient multimodal reasoning  

---

##  Contributing

Open to ideas, improvements, and collaborations.

---

##  Note

This is an early version (V1) focused on validating the core idea of autonomous browser interaction.
