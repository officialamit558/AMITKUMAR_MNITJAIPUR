
# model/parser.py

import re
from typing import List, Dict

# Regex to detect numeric values
NUMERIC = r"([0-9]+(?:\.[0-9]+)?)"


def extract_last_numbers(tokens):
    """Extract the last numeric values in order: qty, rate, amount"""
    numbers = [t for t in tokens if re.fullmatch(NUMERIC, t)]
    return numbers[-3:] if len(numbers) >= 3 else None


def clean_name(tokens):
    """Remove last numeric fields & return the name."""
    name_tokens = []
    for t in tokens:
        if re.fullmatch(NUMERIC, t):
            continue
        if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", t):
            continue
        name_tokens.append(t)
    return " ".join(name_tokens).strip()


def parse_line_items_from_text(lines: List[str]) -> List[Dict]:
    items = []

    for line in lines:
        tokens = line.split()

        # At least name, qty, rate, amount
        if len(tokens) < 4:
            continue

        last_three = extract_last_numbers(tokens)
        if not last_three:
            continue

        qty, rate, amount = last_three

        qty = float(qty)
        rate = float(rate)
        amount = float(amount)

        name = clean_name(tokens)

        if not name or "total" in name.lower():
            continue

        # Calculate correct item_amount as quantity * rate
        calculated_amount = qty * rate

        items.append({
            "item_name": name,
            "item_quantity": qty,
            "item_rate": rate,
            "item_amount": calculated_amount
        })

    return items


def reconcile_items(items: List[Dict]) -> float:
    """Calculate total reconciled amount by summing all item_amounts (quantity * rate)."""
    total = 0.0

    for it in items:
        # Calculate item_amount if not already calculated
        item_amount = it.get("item_amount", 0.0)
        if item_amount == 0.0:
            item_amount = float(it.get("item_quantity", 0)) * float(it.get("item_rate", 0))
        total += item_amount

    return round(total, 2)
