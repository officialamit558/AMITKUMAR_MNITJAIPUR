
# app.py
from flask import Flask, request, jsonify
from model.model_inference import InvoiceExtractor
from utils.download import download_file
import os

app = Flask(__name__)
MODEL_CACHE_DIR = os.environ.get("MODEL_CACHE_DIR", "./model_cache")

# Initialize model (loads HF Donut model + processor)
extractor = InvoiceExtractor(model_name_or_path="naver-clova-ix/donut-base-finetuned-cord-v2", device="cpu")

@app.route("/extract-bill-data", methods=["POST"])
def extract_bill_data():
    payload = request.get_json(force=True)
    if not payload or "document" not in payload:
        return jsonify({"is_success": False, "error": "Missing 'document' field"}), 400

    doc_url = payload["document"]
    try:
        local_path = download_file(doc_url)
    except Exception as e:
        return jsonify({"is_success": False, "error": f"Failed to download: {str(e)}"}), 400

    try:
        result = extractor.process_document(local_path)
        # result should match required schema
        resp = {
            "is_success": True,
            "token_usage": {
                "total_tokens": 0, "input_tokens": 0, "output_tokens": 0
            },
            "data": result
        }
        return jsonify(resp), 200
    except Exception as e:
        return jsonify({"is_success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
