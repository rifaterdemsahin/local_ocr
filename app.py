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
