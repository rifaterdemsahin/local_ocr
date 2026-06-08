import requests
import json

def test_ocr():
    url = "http://localhost:8000/ocr"
    image_path = "test_image.png"
    
    print(f"Sending {image_path} to {url}...")
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files)
            
        print("Status Code:", response.status_code)
        if response.status_code == 200:
            result = response.json()
            print("OCR Result:")
            print(result)
            
            output_file = "output/result.json"
            with open(output_file, "w") as out:
                json.dump(result, out, indent=4)
            print(f"Saved result to {output_file}")
        else:
            print("Error:", response.text)
    except Exception as e:
        print("An error occurred during request:", e)

if __name__ == "__main__":
    test_ocr()
