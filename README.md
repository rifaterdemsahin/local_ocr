# Local OCR API — Dual-Engine Screenshot Reader for Agents

A self-contained, local-only OCR service. Runs **Tesseract OCR** and **EasyOCR (PyTorch)** inside Docker, exposes an HTTP endpoint, and returns extracted text as JSON. Perfect for feeding clean desktop/window text to local AI agents.

No cloud dependencies, no API keys, runs natively on Mac (Apple Silicon & Intel). Binds to `localhost:8000`.

---

## What you get

- `POST /ocr` — Upload a screenshot file, select engine (`easyocr` or `tesseract`), get clean text.
- `POST /ocr/base64` — Send base64 payload representation of screenshots.
- `GET /health` — Diagnostics and status check.

---

## Prerequisites

- **Docker Desktop for Mac** running.
- Local LLM Runner: **Ollama** (optional, for post-OCR text correction).

---

## Quick Start

### 1. Build and Run Container
```bash
docker compose up -d --build
```

### 2. Post OCR Request (EasyOCR default)
```bash
curl -s -X POST localhost:8000/ocr -F "file=@screenshot.png"
```

### 3. Post OCR Request (Tesseract engine)
```bash
curl -s -X POST "localhost:8000/ocr?engine=tesseract" -F "file=@screenshot.png"
```

---

## Multi-Engine Architecture & Performance

This project supports two execution paths:
1. **EasyOCR Engine (Default)**: Leverages deep learning CRAFT text detection. Essential for complex screenshots as it automatically ignores window frames and UI styling artifacts.
2. **Tesseract Engine**: CPU-based parser. Extremely fast but susceptible to layout noise (e.g. converting window borders to garbage characters).

See [performance.md](file:///Users/rifaterdemsahin/projects/local_ocr/performance.md) for full benchmarks.

---

## Local LLM Integration (OCR Corrections)

To get absolute accuracy on complicated UI screenshots, feed the raw OCR output into a local Ollama model to remove junk elements:

```python
import requests

def clean_ocr(raw_text: str) -> str:
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma3:12b",
            "prompt": f"Clean OCR transcription noise and terminal styling from:\n\n{raw_text}\n\nCleaned text:",
            "stream": False
        }
    )
    return r.json().get("response", "").strip()
```

Refer to [agents.md](file:///Users/rifaterdemsahin/projects/local_ocr/agents.md) for agent prompts and MCP skills.
