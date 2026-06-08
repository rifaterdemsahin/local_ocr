import base64
import io
import numpy as np

import pytesseract
import easyocr
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from pydantic import BaseModel
from PIL import Image, ImageOps

app = FastAPI(title="Local OCR API", version="1.0.0")

# Initialize EasyOCR reader (keeps in memory)
easyocr_reader = easyocr.Reader(['en'])

def preprocess(img: Image.Image) -> Image.Image:
    """Grayscale + autocontrast + upscale small images. Improves screenshot OCR."""
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    if max(img.size) < 1000:
        img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    return img


def run_tesseract_ocr(img: Image.Image, lang: str = "eng", psm: int = 3) -> str:
    config = f"--oem 3 --psm {psm}"
    return pytesseract.image_to_string(preprocess(img), lang=lang, config=config).strip()


def run_easy_ocr(img: Image.Image) -> str:
    # Convert PIL Image to numpy array (RGB) for EasyOCR
    img_np = np.array(img.convert("RGB"))
    results = easyocr_reader.readtext(img_np, detail=0)
    return "\n".join(results).strip()


class Base64Request(BaseModel):
    image_base64: str
    engine: str = "easyocr"  # "easyocr" or "tesseract"
    lang: str = "eng"
    psm: int = 3


@app.get("/health")
def health():
    return {
        "status": "ok",
        "engines": ["tesseract", "easyocr"],
        "tesseract_version": str(pytesseract.get_tesseract_version()),
    }


@app.post("/ocr")
async def ocr_file(
    file: UploadFile = File(...), 
    engine: str = Query("easyocr", description="OCR Engine to use: 'easyocr' or 'tesseract'"),
    lang: str = "eng", 
    psm: int = 3
):
    try:
        data = await file.read()
        img = Image.open(io.BytesIO(data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")
    
    if engine.lower() == "easyocr":
        text = run_easy_ocr(img)
    else:
        text = run_tesseract_ocr(img, lang=lang, psm=psm)
        
    return {"text": text, "chars": len(text), "engine": engine}


@app.post("/ocr/base64")
def ocr_base64(req: Base64Request):
    try:
        raw = req.image_base64.split(",")[-1]  # tolerate data-URL prefix
        img = Image.open(io.BytesIO(base64.b64decode(raw)))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 image: {e}")
        
    if req.engine.lower() == "easyocr":
        text = run_easy_ocr(img)
    else:
        text = run_tesseract_ocr(img, lang=req.lang, psm=req.psm)
        
    return {"text": text, "chars": len(text), "engine": req.engine}
