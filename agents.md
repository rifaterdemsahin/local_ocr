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
