# -*- coding: utf-8 -*-
"""pages/detail.py — หน้ารายละเอียดสินค้า 1 ชิ้น เลือกด้วย ?id=...
เปิดจากการกดที่การ์ดสินค้าในหน้า page1 (รายการสินค้า)
"""
import json
import os
import storage
from models import Product, CATEGORY_ORDER, category_name

TITLE = "รายละเอียดสินค้า"


def all_products():
    """อ่าน data.json แล้วแปลงทุกแถวเป็นวัตถุ Product (เหมือน page1.py)"""
    data = storage.load()
    products = []
    if isinstance(data, dict):
        for category, rows in data.items():
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, dict):
                        products.append(Product.from_dict(row, category))
    return products


def product_spec_rows(category, product_id):
    """อ่านคุณสมบัติเฉพาะของสินค้าจากไฟล์สเปกตามหมวด"""
    spec_files = {
        "cpu": "cpu_specs.json",
        "vga": "vga_specs.json",
        "ram": "ram_specs.json",
        "mainboard": "mainboard_specs.json",
    }
    spec_fields = {
        "cpu": [
            ("cores", "จำนวนคอร์", " คอร์"),
            ("cores_detail", "รูปแบบคอร์", ""),
            ("threads", "จำนวนเธรด", " เธรด"),
            ("base_clock_ghz", "ความเร็วพื้นฐาน", " GHz"),
            ("boost_clock_ghz", "ความเร็วสูงสุด", " GHz"),
            ("socket", "ซ็อกเก็ต", ""),
            ("cache_l3_mb", "แคช L3", " MB"),
            ("tdp_w", "TDP", " วัตต์"),
            ("pl2_w", "กำลังไฟสูงสุด PL2", " วัตต์"),
            ("igpu", "กราฟิกในตัว", ""),
        ],
        "vga": [
            ("cuda_cores", "CUDA Cores", " คอร์"),
            ("stream_processors", "Stream Processors", " หน่วย"),
            ("xe_cores", "Xe Cores", " คอร์"),
            ("memory_gb", "หน่วยความจำการ์ดจอ", " GB"),
            ("memory_type", "ชนิดหน่วยความจำ", ""),
            ("memory_bus_bit", "Memory Bus", " bit"),
            ("tbp_w", "กำลังไฟการ์ดจอ (TBP)", " วัตต์"),
        ],
        "ram": [
            ("capacity_gb", "ความจุ", " GB"),
            ("modules", "จำนวนแถวแรม", ""),
            ("type", "ชนิดแรม", ""),
            ("speed_mts", "ความเร็ว", " MT/s"),
            ("cl_latency", "ค่า CL", ""),
            ("rgb", "ไฟ RGB", ""),
            ("amd_expo", "รองรับ AMD EXPO", ""),
        ],
        "mainboard": [
            ("socket", "ซ็อกเก็ต", ""),
            ("chipset", "ชิปเซ็ต", ""),
            ("form_factor", "ขนาดเมนบอร์ด", ""),
            ("memory_type", "ชนิดแรมที่รองรับ", ""),
        ],
    }

    if category not in spec_files:
        return []

    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    specs_path = os.path.join(project_dir, spec_files[category])
    with open(specs_path, encoding="utf-8") as file:
        data = json.load(file)

    specs_list = data.get(category, [])
    for specs in specs_list:
        if isinstance(specs, dict) and str(specs.get("id", "")) == product_id:
            rows = []
            for key, label, unit in spec_fields[category]:
                if key in specs:
                    value = specs[key]
                    if isinstance(value, bool):
                        if value:
                            value = "รองรับ"
                        else:
                            value = "ไม่รองรับ"
                    rows.append({"label": label, "value": str(value) + unit})
            return rows
    return []


def build(query):
    products = all_products()

    product_id = query.get("id", "")
    if isinstance(product_id, list):
        product_id = product_id[0] if product_id else ""
    product_id = str(product_id).strip()

    found = None
    for p in products:
        if p.id == product_id:
            found = p
            break

    if found is None:
        return {"item": None}

    # สินค้าอื่นในหมวดเดียวกัน (ไม่รวมชิ้นนี้) ไว้แนะนำต่อ
    related = []
    for p in products:
        if p.category == found.category and p.id != found.id:
            related.append(p.to_dict())
    related = related[:4]

    product_specs = product_spec_rows(found.category, found.id)

    return {
        "item": found.to_dict(),
        "related": related,
        "product_specs": product_specs,
    }
