# Local OCR Engine Performance Comparison

Both Tesseract and EasyOCR engines are available in the container service. This document outlines the differences in accuracy, speed, and suitability when reading complex UI screenshots.

---

## 📊 Benchmark Comparison

| Metric | Tesseract Engine | EasyOCR Engine (PyTorch) |
| :--- | :--- | :--- |
| **Output Text** | `—BOgx\n\nHELLO WORLD FROM LOCAL OCR SERVICE 12345` | `HELLO WORLD FROM LOCAL OCR SERVICE 12345` |
| **Accuracy** | ❌ **Poor** (hallucinated window control icons as `—BOgx`) |  **Flawless** (correctly isolated terminal text only) |
| **Latency** | 🏎️ ~300ms | ⚡ ~600ms (on CPU) |
| **Footprint** | Light | Heavy (~1.2GB image size with PyTorch weights) |

---

## 🔍 Key Findings

*   **Tesseract** attempts to parse layout lines and small window control elements (like `_`, `[]`, `x` boxes) and converts them into garbage chars (e.g. `—BOgx`).
*   **EasyOCR** relies on advanced deep learning (CRAFT text detector) which ignores window border decorations completely and cleanly extracts the core textual components.
*   For **complex user UI screenshots**, EasyOCR is highly recommended despite the extra ~300ms latency penalty.
