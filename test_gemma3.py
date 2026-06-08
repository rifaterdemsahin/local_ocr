import requests
import json

def test_ocr_with_gemma3(image_path: str, output_suffix: str):
    url = "http://localhost:8000/ocr"
    
    print(f"\n--- Testing {image_path} ---")
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files, params={"engine": "tesseract"})
            
        if response.status_code == 200:
            ocr_text = response.json().get("text", "")
            print("Raw OCR Output:")
            print(ocr_text)
            
            # Post-process using local Ollama (gemma3:12b)
            ollama_url = "http://localhost:11434/api/generate"
            prompt = (
                "You are an assistant that cleans up noisy OCR transcription data. "
                "Remove raw terminal styling, garbage characters, and window decorations "
                "to yield only the clean text structure. Here is the raw OCR output:\n\n"
                f"{ocr_text}\n\n"
                "Cleaned text:"
            )
            
            payload = {
                "model": "gemma3:12b",
                "prompt": prompt,
                "stream": False
            }
            
            print("Sending raw OCR text to local LLM (Ollama: gemma3:12b)...")
            ollama_response = requests.post(ollama_url, json=payload)
            
            if ollama_response.status_code == 200:
                cleaned_text = ollama_response.json().get("response", "").strip()
                print("Cleaned Gemma 3 Output:")
                print(cleaned_text)
                
                # Save results
                output_data = {
                    "image": image_path,
                    "raw_ocr": ocr_text,
                    "cleaned_gemma3": cleaned_text
                }
                output_file = f"output/result_gemma3_{output_suffix}.json"
                with open(output_file, "w") as out:
                    json.dump(output_data, out, indent=4)
                print(f"Saved result to {output_file}")
            else:
                print("Ollama Error:", ollama_response.text)
        else:
            print("OCR Error:", response.text)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    test_ocr_with_gemma3("test_image1.png", "img1")
    test_ocr_with_gemma3("test_image2.png", "img2")
