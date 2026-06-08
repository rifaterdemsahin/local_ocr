# Agent Integrations

This document describes how to configure various AI agents and frameworks to leverage this local OCR endpoint.

## Prompt Definition (System Skill)

Feed the following prompt to your agent:

```markdown
# System Skill: Read User Screenshot
You are equipped with a local OCR tool to view the user's screen.
When you need to read a screenshot or image file, invoke the local OCR API by sending a HTTP POST request.

- Endpoint: http://localhost:8000/ocr
- Method: POST
- Body Format: Multipart Form-Data
- Parameter Name: "file" (The binary image file)

Alternatively, if you hold the image in memory as a base64 encoded string, use:
- Endpoint: http://localhost:8000/ocr/base64
- Method: POST
- Body Format: JSON
- Payload Structure: {"image_base64": "YOUR_BASE64_STRING"}
```

## Python Agent Example (LangChain / AutoGen / CrewAI)

```python
import base64
import requests

def local_ocr(image_path: str) -> str:
    """Invokes local OCR service to extract text from a file."""
    url = "http://localhost:8000/ocr"
    with open(image_path, "rb") as f:
        files = {"file": f}
        r = requests.post(url, files=files)
    return r.json().get("text", "")
```

## LLM Correction (Post-Processing)

We use **`llama3:latest`** (Meta Llama 3 8B) running on **Ollama** locally to correct transcription errors, delete hallucinated window margins, and rebuild logical output structures.

### Recommended Models for correction:
1. **`llama3:latest`** (Default) — Balanced performance, very fast local CPU inference.
2. **`deepseek-r1:latest`** — Great reasoning capabilities for cleaning complex layouts.
3. **`gemma3:12b`** / **`gemma3:27b`** — High accuracy formatting.

