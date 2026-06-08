import requests
import json

def test_ocr_with_llm_fix():
    url = "http://localhost:8000/ocr"
    image_path = "test_image.png"
    
    # Step 1: Run OCR on image (using Tesseract to intentionally show LLM correction capabilities on raw/noisy output)
    print(f"Sending {image_path} to {url} using Tesseract engine...")
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files, params={"engine": "tesseract"})
            
        if response.status_code == 200:
            ocr_text = response.json().get("text", "")
            print("\n--- Raw OCR Output ---")
            print(ocr_text)
            
            # Step 2: Query local LLM (Ollama) to clean up layout noise and yield meaningful outputs
            ollama_url = "http://localhost:11434/api/generate"
            prompt = (
                "You are an assistant that cleans up noisy OCR transcription data. "
                "Remove raw terminal styling, garbage characters, and window decorations "
                "to yield only the clean text structure. Here is the raw OCR output:\n\n"
                f"{ocr_text}\n\n"
                "Cleaned text:"
            )
            
            payload = {
                "model": "llama3:latest",
                "prompt": prompt,
                "stream": False
            }
            
            print("\nSending OCR text to local LLM (Ollama: llama3)...")
            ollama_response = requests.post(ollama_url, json=payload)
            
            if ollama_response.status_code == 200:
                cleaned_text = ollama_response.json().get("response", "").strip()
                print("\n--- Cleaned LLM Output ---")
                print(cleaned_text)
                
                # Save results
                output_data = {
                    "raw_ocr": ocr_text,
                    "cleaned_llm": cleaned_text
                }
                output_file = "output/result_llm.json"
                with open(output_file, "w") as out:
                    json.dump(output_data, out, indent=4)
                print(f"\nSaved combined result to {output_file}")
            else:
                print("Ollama Error:", ollama_response.text)
        else:
            print("OCR Error:", response.text)
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    test_ocr_with_llm_fix()
