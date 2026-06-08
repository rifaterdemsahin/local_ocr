# Local OCR API — Dockerized screenshot reader for agents

A self-contained, local-only OCR service. Runs Tesseract inside Docker, exposes an HTTP endpoint, and returns extracted text as JSON. Built for Apple Silicon / Intel MacBook Pro. No cloud, no API keys, no GPU required.

Everything you need is in this file. Copy each code block into the named file, then build and run.

---

## What you get

- `POST /ocr` — upload a screenshot file, get text back.
- `POST /ocr/base64` — send a base64 image (handy for agents that hold an image in memory).
- `GET /health` — liveness + Tesseract version.
- CPU-only, runs natively on arm64. Binds to `localhost:8000`.

---

## Prerequisites

- **Docker Desktop for Mac** installed and running. ([docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop))
- `jq` for pretty JSON in the test commands (optional): `brew install jq`

That's it. Tesseract and all Python deps are installed inside the image.

---

## Project layout

Create a folder and these four files:

```
local-ocr/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── app.py
```

```bash
mkdir local-ocr && cd local-ocr
```

---

## Step 1 — Create the files

### `requirements.txt`

```
fastapi==0.110.0
uvicorn[standard]==0.27.1
pytesseract==0.3.10
pillow==10.2.0
python-multipart==0.0.9
```

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

# Tesseract OCR engine (English language pack ships with it)
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `app.py`

```python
import base64
import io

import pytesseract
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from PIL import Image, ImageOps

app = FastAPI(title="Local OCR API", version="1.0.0")


def preprocess(img: Image.Image) -> Image.Image:
    """Grayscale + autocontrast + upscale small images. Improves screenshot OCR."""
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    if max(img.size) < 1000:
        img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    return img


def run_ocr(img: Image.Image, lang: str = "eng", psm: int = 3) -> str:
    config = f"--oem 3 --psm {psm}"
    return pytesseract.image_to_string(preprocess(img), lang=lang, config=config).strip()


class Base64Request(BaseModel):
    image_base64: str
    lang: str = "eng"
    psm: int = 3


@app.get("/health")
def health():
    return {
        "status": "ok",
        "engine": "tesseract",
        "version": str(pytesseract.get_tesseract_version()),
    }


@app.post("/ocr")
async def ocr_file(file: UploadFile = File(...), lang: str = "eng", psm: int = 3):
    try:
        data = await file.read()
        img = Image.open(io.BytesIO(data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")
    text = run_ocr(img, lang=lang, psm=psm)
    return {"text": text, "chars": len(text)}


@app.post("/ocr/base64")
def ocr_base64(req: Base64Request):
    try:
        raw = req.image_base64.split(",")[-1]  # tolerate data-URL prefix
        img = Image.open(io.BytesIO(base64.b64decode(raw)))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image: {e}")
    text = run_ocr(img, lang=req.lang, psm=req.psm)
    return {"text": text, "chars": len(text)}
```

### `docker-compose.yml`

```yaml
services:
  ocr:
    build: .
    container_name: local-ocr
    ports:
      - "127.0.0.1:8000:8000"   # localhost only — not exposed to your network
    restart: unless-stopped
```

---

## Step 2 — Build & run

```bash
docker compose up -d --build
```

First build pulls the Python base image and installs Tesseract (~1–2 min). Subsequent starts are instant.

---

## Step 3 — Test it

```bash
# Health check
curl -s localhost:8000/health | jq

# OCR a file
curl -s -X POST localhost:8000/ocr -F "file=@screenshot.png" | jq

# OCR via base64
B64=$(base64 -i screenshot.png)
curl -s -X POST localhost:8000/ocr/base64 \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\": \"$B64\"}" | jq
```

Interactive docs are auto-generated at **http://localhost:8000/docs**.

---

## Step 4 — Capture screenshots on Mac

```bash
screencapture -x shot.png      # full screen, no sound
screencapture -i shot.png      # interactive region/window select
```

Pipe straight into the API:

```bash
screencapture -i /tmp/shot.png && \
  curl -s -X POST localhost:8000/ocr -F "file=@/tmp/shot.png" | jq -r '.text'
```

---

## Step 5 — Call it from an agent

It's a plain HTTP endpoint, so any agent that can make a POST request can use it.

**Python:**

```python
import base64, requests

with open("shot.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

r = requests.post(
    "http://localhost:8000/ocr/base64",
    json={"image_base64": b64, "psm": 6},
)
print(r.json()["text"])
```

**Bash tool / Claude Code agent:** give the agent the `curl` one-liner from Step 4 as a callable command, or wrap the endpoint in an MCP tool that takes an image path and returns `.text`.

---

## Tuning

| Knob | What it does |
|------|--------------|
| `psm=3` (default) | Auto page segmentation — good for full pages/documents. |
| `psm=6` | Assume a single uniform block — better for dense UI / dialogs. |
| `psm=7` | Single line — good for one-line labels. |
| `lang=eng` | Default. Add more by installing packs (below) and passing e.g. `lang=eng+tur`. |

Add a language pack (example: Turkish), then rebuild:

```dockerfile
# in the apt-get install line, add:
        tesseract-ocr-tur \
```

---

## Upgrading accuracy (optional)

Tesseract is fast and fine for clean screenshots. If you need higher accuracy on noisy or stylized UI text, swap the engine — the API stays the same:

- **RapidOCR** (`pip install rapidocr-onnxruntime`) — ONNX, CPU-friendly, good accuracy, no system deps. Best drop-in upgrade.
- **EasyOCR** (`pip install easyocr`) — deep learning, heavier, slower on CPU, strong on varied fonts.

Only `run_ocr()` in `app.py` and `requirements.txt` change; endpoints and agent calls are unchanged.

---

## Operations

```bash
docker compose logs -f          # tail logs
docker compose restart          # restart
docker compose down             # stop & remove
docker compose up -d --build    # rebuild after editing files
```

---

## Security note

The compose file binds to `127.0.0.1` only, so the service is reachable from your Mac but **not** from your local network. There's no authentication — keep it that way unless you add an auth layer, and don't change the port mapping to `0.0.0.0`.
