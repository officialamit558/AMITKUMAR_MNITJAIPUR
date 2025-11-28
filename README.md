# Invoice / Bill Extraction API (Bajaj Datathon)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-API-green)
![Donut](https://img.shields.io/badge/Model-Donut-orange)
![Status](https://img.shields.io/badge/Status-Production--Ready-brightgreen)

This project implements a production-ready solution for extracting **line item details**, **sub-totals**, and **final totals** from multi-page invoices and bills. 

The system supports **PDF + Images**, utilizes the **Donut model (OCR-free)** as the primary extractor, and seamlessly falls back to **OCR + rule-based parsing** when necessary.

---

## Problem Statement

Given a set of **bills (multi-page invoices)**, the system must extract:
- Line item details (name, quantity, rate, amount)
- Sub-totals (if present)
- Final item-wise total
- **Sum without double counting** across all pages.

### Requirements
- Do **NOT** miss any items.
- Do **NOT** double count.
- The score is calculated based on how closely the **AI extracted total** matches the **Actual Bill Total**.

---

## Tools & Tech Stack

| Component | Tool / Library |
| :--- | :--- |
| **Language** | Python 3.10+ |
| **API Framework** | Flask |
| **Primary Model** | Donut (`naver-clova-ix/donut-base-finetuned-cord-v2`) |
| **Fallback OCR** | Tesseract OCR |
| **PDF Handling** | `pdf2image` (Poppler backend) |
| **Logic** | Custom Rule-based parser for reconciliation |

---

## Repository Structure

```bash
invoice-extractor/
├── app.py                  
├── requirements.txt        
├── Dockerfile              
├── Procfile                
├── README.md               
│
├── model/
│   ├── model_inference.py  
│   ├── ocr_utils.py        
│   └── parser.py           
│
├── utils/
│   └── download.py         
│
└── test_samples/        

# API Endpoint
POST /extract-bill-data
## Request Headers
Content-Type: application/json

## Request Body
{
  "document": "[https://your-bill-or-pdf-url.com/file.png](https://your-bill-or-pdf-url.com/file.png)"
}

## Response formate
{
  "is_success": true,
  "token_usage": {
    "total_tokens": 0,
    "input_tokens": 0,
    "output_tokens": 0
  },
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "1",
        "page_type": "Bill Detail | Final Bill | Pharmacy",
        "bill_items": [
          {
            "item_name": "Livi 300mg Tab",
            "item_amount": 448.00,
            "item_rate": 32.00,
            "item_quantity": 14.00
          }
        ]
      }
    ],
    "total_item_count": 4,
    "reconciled_amount": 1699.84
  }
}

# Setup Instructions
python -m venv .venv
# Activate Virtual Environment
.\.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Mac/Linux

pip install -r requirements.txt

# Running the API
1) Running the API
2) The server will run at: http://localhost:5000/extract-bill-data

# Testing with cURL:
curl -X POST http://localhost:5000/extract-bill-data \
-H "Content-Type: application/json" \
-d "{\"document\":\"[https://your-url.com/bill.png](https://your-url.com/bill.png)\"}"

# Author
Amit Kumar and hackrxbot for  Bill Extraction Challenge
