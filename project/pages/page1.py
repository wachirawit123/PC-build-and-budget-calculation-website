# -*- coding: utf-8 -*-
"""pages/page1.py — รายการสินค้าทั้งหมด (การ์ดสินค้า + รูป + ค้นหา + กรองหมวดหมู่)
เจ้าของหน้า: นายกิตติภูมิ จิตต์ประเสริฐ
"""
import storage
from models import Product, CATEGORY_ORDER, category_name

TITLE = "รายการสินค้า"


def one_value(query, key, default=""):
    """ค่าที่ส่งมากับ URL (?cat=cpu) อาจมาเป็น list — ดึงตัวแรกมาใช้"""
    value = query.get(key, default)
    if isinstance(value, list):
        if len(value) > 0:
            value = value[0]
        else:
            value = default
    return str(value).strip()


def all_products():
    """อ่าน data.json แล้วแปลงทุกแถวเป็นวัตถุ Product"""
    data = storage.load()
    products = []
    if isinstance(data, dict):
        for category, rows in data.items():
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, dict):
                        products.append(Product.from_dict(row, category))
    return products


def build(query):
    products = all_products()
    selected = one_value(query, "cat", "all")
    keyword = one_value(query, "q", "")
    sort_by = one_value(query, "sort", "name")

    # หมวดหมู่ที่มีจริงในคลัง + จำนวนชิ้นของแต่ละหมวด
    counts = {}
    for p in products:
        if p.category in counts:
            counts[p.category] = counts[p.category] + 1
        else:
            counts[p.category] = 1

    categories = []
    for key in CATEGORY_ORDER:
        if key in counts:
            categories.append({"key": key, "label": category_name(key), "count": counts[key]})
    for key in sorted(counts.keys()):
        if key not in CATEGORY_ORDER:
            categories.append({"key": key, "label": category_name(key), "count": counts[key]})

    # กรอง: หมวดหมู่ + คำค้นหา
    shown = []
    total_price = 0.0
    out_of_stock = 0
    for p in products:
        if selected != "all" and p.category != selected:
            continue
        if not p.matches(keyword):
            continue
        shown.append(p)
        total_price = total_price + p.price
        if not p.in_stock():
            out_of_stock = out_of_stock + 1

    # เรียงลำดับตามที่ผู้ใช้เลือก
    if sort_by == "price_low":
        shown.sort(key=lambda p: p.price)
    elif sort_by == "price_high":
        shown.sort(key=lambda p: p.price, reverse=True)
    elif sort_by == "watt":
        shown.sort(key=lambda p: p.wattage, reverse=True)
    else:
        shown.sort(key=lambda p: (p.category, p.name))

    items = []
    for p in shown:
        items.append(p.to_dict())

    if len(shown) > 0:
        average_price = total_price / len(shown)
    else:
        average_price = 0.0

    return {
        "items": items,
        "categories": categories,
        "selected": selected,
        "keyword": keyword,
        "sort": sort_by,
        "shown_count": len(items),
        "all_count": len(products),
        "total_price": "{:,.0f}".format(total_price),
        "average_price": "{:,.0f}".format(average_price),
        "out_of_stock": out_of_stock,
    }
