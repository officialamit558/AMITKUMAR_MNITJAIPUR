# model/model_inference.py
import torch
from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image
import json, os
from .ocr_utils import ocr_image_text_lines
from .parser import parse_line_items_from_text, reconcile_items
from typing import Dict, List
from pdf2image import convert_from_path
import tempfile

class InvoiceExtractor:
    def __init__(self, model_name_or_path="naver-clova-ix/donut-base-finetuned-cord-v2", device="cpu"):
        self.device = torch.device(device)

        self.processor = DonutProcessor.from_pretrained(model_name_or_path)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name_or_path)
        self.model.to(self.device)
        self.model.eval()

    def _donut_infer(self, image_path: str, task_prompt: str = "<s_invoice>"):
        
        img = Image.open(image_path).convert("RGB")
        pixel_values = self.processor(img, return_tensors="pt").pixel_values.to(self.device)
        # prepare decoder input ids as required by some donut setups
        decoder_input_ids = self.processor.tokenizer(task_prompt, add_special_tokens=False, return_tensors="pt").input_ids.to(self.device)

        outputs = self.model.generate(pixel_values,
                                      decoder_input_ids=decoder_input_ids,
                                      max_length=1024,
                                      num_beams=3,
                                      early_stopping=True)
        decoded = self.processor.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return decoded

    def _convert_pdf_to_images(self, pdf_path):
        """
        Converts PDF into images safely using OS-specific temp folder.
        """
        pages = convert_from_path(pdf_path, dpi=300)
        converted_images = []

        temp_dir = tempfile.gettempdir()  # Windows & Linux compatible

        for idx, page in enumerate(pages):
            out_path = os.path.join(temp_dir, f"invoice_page_{idx + 1}.png")
            page.save(out_path, "PNG")
            converted_images.append(out_path)

        return converted_images
    
    def process_document(self, file_path: str):
        
        # 1. Handle PDF or images
        ext = file_path.lower().split(".")[-1]
        if ext == "pdf":
            page_images = self._convert_pdf_to_images(file_path)
        else:
            page_images = [file_path]

        all_items = []
        pagewise_output = []

        page_no = 1

        for img_path in page_images:
            # Try Donut
            parsed_json = None
            try:
                donut_raw = self._donut_infer(img_path)
                parsed_json = json.loads(donut_raw)
            except Exception:
                parsed_json = None

            if parsed_json and "line_items" in parsed_json:
                bill_items = []
                for item in parsed_json["line_items"]:
                    bill_items.append({
                        "item_name": item.get("name", "").strip(),
                        "item_amount": float(item.get("amount", 0) or 0),
                        "item_rate": float(item.get("rate", 0) or 0),
                        "item_quantity": float(item.get("qty", 0) or 0)
                    })
            else:
                # OCR fallback
                text_lines = ocr_image_text_lines(img_path)
                bill_items = parse_line_items_from_text(text_lines)

            pagewise_output.append({
                "page_no": str(page_no),
                "bill_items": bill_items
            })

            all_items.extend(bill_items)
            page_no += 1

        reconciled_amount = reconcile_items(all_items)

        return {
            "pagewise_line_items": pagewise_output,
            "total_item_count": len(all_items),
            "reconciled_amount": reconciled_amount
        }