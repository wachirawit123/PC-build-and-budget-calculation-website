# -*- coding: utf-8 -*-
"""pages/page4.py — จัดสเปกคอม: เลือกอุปกรณ์ทีละหมวด แล้วคำนวณราคารวม/ไฟรวม/PSU ที่ควรใช้
เจ้าของหน้า: นายชยพล สืบสิมมา
"""
import storage
from models import Product, PCBuildCalculator, CATEGORY_ORDER, category_name

TITLE = "จัดสเปกคอม"

# หมวดที่ต้องมีในคอม 1 เครื่อง (ถ้าขาด จะเตือน)
REQUIRED = ["cpu", "mainboard", "ram", "ssd", "psu", "case"]


def one_value(query, key, default=""):
    value = query.get(key, default)
    if isinstance(value, list):
        if len(value) > 0:
            value = value[0]
        else:
            value = default
    return str(value).strip()


def load_by_category():
    data = storage.load()
    shelves = {}
    if isinstance(data, dict):
        for category, rows in data.items():
            if isinstance(rows, list):
                products = []
                for row in rows:
                    if isinstance(row, dict):
                        products.append(Product.from_dict(row, category))
                products.sort(key=lambda p: p.price)
                shelves[category] = products
    return shelves


def build(query):
    shelves = load_by_category()

    keys = []
    for key in CATEGORY_ORDER:
        if key in shelves:
            keys.append(key)
    for key in sorted(shelves.keys()):
        if key not in keys:
            keys.append(key)

    picker = []
    chosen = []
    for key in keys:
        wanted = one_value(query, key, "")
        options = []
        picked = None
        for p in shelves[key]:
            options.append({"id": p.id, "name": p.name, "price": "{:,.0f}".format(p.price),
                            "selected": p.id == wanted})
            if p.id == wanted:
                picked = p
        if picked is not None:
            chosen.append(picked)
        if picked is None:
            picked_row = None
        else:
            picked_row = picked.to_dict()
        picker.append({
            "key": key,
            "label": category_name(key),
            "required": key in REQUIRED,
            "options": options,
            "picked": picked_row,
        })

    calc = PCBuildCalculator(chosen)
    total_price = calc.total_price()
    total_wattage = calc.total_wattage()
    psu_size = calc.recommended_psu()

    # เตือนเมื่อสเปกยังไม่ครบ หรือ PSU ที่เลือกจ่ายไฟไม่พอ
    warnings = []
    for key in REQUIRED:
        found = False
        for p in chosen:
            if p.category == key:
                found = True
        if not found:
            warnings.append("ยังไม่ได้เลือก " + category_name(key))

    has_cooler = False
    for p in chosen:
        if p.category == "aio" or p.category == "aircooler":
            has_cooler = True
    if not has_cooler and len(chosen) > 0:
        warnings.append("ยังไม่ได้เลือกชุดระบายความร้อน (ชุดน้ำปิด หรือ ซิงก์ลม)")

    rows = []
    for p in chosen:
        rows.append(p.to_dict())

    if total_price > 0:
        budget_percent = min(100, int(total_price * 100 / 100000))
    else:
        budget_percent = 0

    return {
        "picker": picker,
        "rows": rows,
        "chosen_count": len(chosen),
        "total_price": "{:,.0f}".format(total_price),
        "total_wattage": int(total_wattage),
        "psu_size": psu_size,
        "warnings": warnings,
        "is_complete": len(warnings) == 0 and len(chosen) > 0,
        "budget_percent": budget_percent,
    }
