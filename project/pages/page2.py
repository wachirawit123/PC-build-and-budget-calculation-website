# -*- coding: utf-8 -*-
"""pages/page2.py — เพิ่ม / ลบสินค้าในคลัง (ฟอร์ม + ตรวจข้อมูล + อัปโหลดรูป)
เจ้าของหน้า: นายกาจบัณฑิต ประทุมตรี
"""
import storage
from models import Product, CATEGORY_ORDER, category_name

TITLE = "เพิ่มสินค้า"

ALLOWED_CATEGORIES = CATEGORY_ORDER


def read_data():
    data = storage.load()
    if not isinstance(data, dict):
        data = {}
    return data


def next_id(rows, category):
    """หาเลข id ถัดไปของหมวดนั้น เช่น cpu-19"""
    biggest = 0
    for row in rows:
        if isinstance(row, dict):
            parts = str(row.get("id", "")).split("-")
            if len(parts) == 2 and parts[1].isdigit():
                number = int(parts[1])
                if number > biggest:
                    biggest = number
    return category + "-" + str(biggest + 1)


def build():
    data = read_data()

    categories = []
    for key in ALLOWED_CATEGORIES:
        rows = data.get(key, [])
        if isinstance(rows, list):
            amount = len(rows)
        else:
            amount = 0
        categories.append({"key": key, "label": category_name(key), "count": amount})

    # 8 รายการที่เพิ่งเพิ่มล่าสุด (ท้ายลิสต์ของแต่ละหมวด)
    latest = []
    for key, rows in data.items():
        if isinstance(rows, list):
            for row in rows[-3:]:
                if isinstance(row, dict):
                    latest.append(Product.from_dict(row, key).to_dict())
    latest = latest[-8:]
    latest.reverse()

    total_items = 0
    for rows in data.values():
        if isinstance(rows, list):
            total_items = total_items + len(rows)

    return {
        "categories": categories,
        "latest": latest,
        "total_items": total_items,
    }


def handle(form):
    """ทำงานเมื่อกดปุ่มในหน้า /page2 — คืนข้อความแจ้งเตือน 1 บรรทัด"""
    data = read_data()
    action = form.get("action", "add").strip()

    # ---------- ลบสินค้า ----------
    if action == "delete":
        target = form.get("id", "").strip()
        category = form.get("category", "").strip()
        rows = data.get(category, [])
        if not isinstance(rows, list):
            return "✗ ไม่พบหมวดหมู่ " + category
        kept = []
        removed = ""
        for row in rows:
            if isinstance(row, dict) and row.get("id", "") == target:
                removed = row.get("name", target)
            else:
                kept.append(row)
        if removed == "":
            return "✗ ไม่พบสินค้ารหัส " + target
        data[category] = kept
        storage.save(data)
        return "🗑 ลบ " + removed + " ออกจากคลังแล้ว"

    # ---------- เพิ่มสินค้า ----------
    name = form.get("name", "").strip()
    brand = form.get("brand", "").strip()
    category = form.get("category", "").strip()
    price_text = form.get("price", "").strip()
    wattage_text = form.get("wattage", "0").strip()
    stock_text = form.get("stock", "1").strip()
    photo = form.get("photo", "").strip()

    if name == "":
        return "✗ กรุณากรอกชื่อสินค้า"
    if len(name) < 3:
        return "✗ ชื่อสินค้าต้องยาวอย่างน้อย 3 ตัวอักษร"
    if category not in ALLOWED_CATEGORIES:
        return "✗ กรุณาเลือกหมวดหมู่สินค้าให้ถูกต้อง"

    try:
        price = float(price_text)
    except ValueError:
        return "✗ ราคาต้องเป็นตัวเลขเท่านั้น"
    if price <= 0:
        return "✗ ราคาต้องมากกว่า 0 บาท"
    if price > 500000:
        return "✗ ราคาสูงเกินจริง (ไม่เกิน 500,000 บาท)"

    try:
        wattage = float(wattage_text)
    except ValueError:
        wattage = 0.0
    if wattage < 0:
        wattage = 0.0

    try:
        stock = int(float(stock_text))
    except ValueError:
        stock = 0
    if stock < 0:
        stock = 0

    rows = data.get(category, [])
    if not isinstance(rows, list):
        rows = []

    # ชื่อซ้ำในหมวดเดียวกัน = ไม่เพิ่ม
    for row in rows:
        if isinstance(row, dict) and str(row.get("name", "")).lower() == name.lower():
            return "✗ มี " + name + " อยู่ในคลังแล้ว"

    if photo == "":
        image = ""
    else:
        image = photo

    rows.append({
        "id": next_id(rows, category),
        "name": name,
        "brand": brand,
        "price": price,
        "wattage": wattage,
        "stock": stock,
        "image": image,
    })
    data[category] = rows
    storage.save(data)
    return "✓ เพิ่ม " + name + " (" + category_name(category) + ") เรียบร้อยแล้ว"
