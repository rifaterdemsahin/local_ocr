# OCR Accuracy Optimization Formula

To improve the accuracy of local OCR, we can optimize across three main dimensions: Preprocessing, Tesseract Configuration, and Alternative Engines.

---

## 🧪 Optimization Options & Formulas

### Option 1: Advanced Preprocessing Pipeline (Image Magic)
Tesseract performs poorly on raw screenshots. Enhancing image clarity before passing it to Tesseract yields the best performance increase for simple layouts.

*   **Pros:** Minimal performance footprint; does not require downloading heavy deep learning weights.
*   **Cons:** Needs custom tuning depending on the text size and contrast variation.
*   **Formula:**
    $$\text{Processed Image} = \text{Binarize}(\text{ContrastStretch}(\text{Scale}(\text{Grayscale}(\text{Input Image}), \text{factor}=2\times)))$$

---

### Option 2: Page Segmentation Modes (PSM) tuning
Tesseract segments blocks of text. Choosing the right layout analysis method completely changes the accuracy.

*   **Pros:** Built-in FastAPI parameter tuning; zero installation required.
*   **Cons:** Highly dependent on target text layout (e.g. table vs single line).
*   **Modes:**
    *   `psm = 3` (Default): Auto layout analysis.
    *   `psm = 6`: Single uniform block of text (highly recommended for code snippets or console outputs).
    *   `psm = 7`: Single text line (best for short input boxes/filenames).

---

### Option 3: Swap Engine to RapidOCR (ONNX Runtime)
RapidOCR uses an ONNX-runtime version of PaddleOCR. It runs natively on CPU, handles rotated text, and performs exceptionally well on diverse font families.

*   **Pros:** Deep-learning accuracy, highly robust on UI components, lightweight CPU execution.
*   **Cons:** Larger container build footprint (~150MB more).

---

### Option 4: Swap Engine to EasyOCR (PyTorch-based)
EasyOCR utilizes a CRAFT text detector combined with a ResNet/BiLSTM sequence generator.

*   **Pros:** State-of-the-art accuracy on stylized fonts and cluttered environments.
*   **Cons:** Slow execution on CPU (~1-2 seconds per call), large container size (~1GB dependencies).

---

## 📊 Summary Matrix

| Metric | Option 1 (Tesseract + Custom Prep) | Option 2 (Tesseract Tuning) | Option 3 (RapidOCR) | Option 4 (EasyOCR) |
|---|---|---|---|---|
| **Speed (Latency)** | 🏎️ High (~250-300ms) | 🏎️ Ultra-high (~200ms) | ⚡ Moderate (~400-600ms) | 🐌 Slow (~1-2s on CPU) |
| **Accuracy** | ⭐⭐ Moderate | ⭐⭐ Low-to-Moderate | ⭐⭐⭐⭐ High | ⭐⭐⭐⭐⭐ Maximum |
| **Setup Cost** | Low | None | Medium (Re-build Image) | High (Pip + PyTorch weights) |
