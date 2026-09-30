# -*- coding: utf-8 -*-
"""pages/page3.py — สถิติคลังสินค้า (มูลค่ารวม · กราฟแท่งต่อหมวดหมู่ · สินค้าราคาสูงสุด)
เจ้าของหน้า: นายวชิรวิทย์ ซื่อตรง
"""
import storage
from models import Product, PCBuildCalculator, CATEGORY_ORDER, category_name

TITLE = "สถิติคลังสินค้า"

EXPENSIVE_LIMIT = 10000


def load_products():
    data = storage.load()
    products = []
    if isinstance(data, dict):
        for category, rows in data.items():
            if isinstance(rows, list):
                for row in rows:
                    if isinstance(row, dict):
                        products.append(Product.from_dict(row, category))
    return products


def percent(value, biggest):
    if biggest <= 0:
        return 0
    return int(round(value * 100.0 / biggest))


def build():
    products = load_products()
    calc = PCBuildCalculator(products)
    summary = calc.total_by_category()

    # หามูลค่าหมวดที่สูงสุด เพื่อคิดความยาวของแท่งกราฟเป็นเปอร์เซ็นต์
    biggest = 0.0
    for info in summary.values():
        if info["price"] > biggest:
            biggest = info["price"]

    keys = []
    for key in CATEGORY_ORDER:
        if key in summary:
            keys.append(key)
    for key in sorted(summary.keys()):
        if key not in keys:
            keys.append(key)

    rows = []
    for key in keys:
        info = summary[key]
        if info["count"] > 0:
            average = info["price"] / info["count"]
        else:
            average = 0.0
        rows.append({
            "key": key,
            "label": category_name(key),
            "count": info["count"],
            "price": "{:,.0f}".format(info["price"]),
            "average": "{:,.0f}".format(average),
            "percent": percent(info["price"], biggest),
        })

    top = calc.most_expensive()
    if top is None:
        top_item = None
    else:
        top_item = top.to_dict()

    # 5 อันดับสินค้าที่แพงที่สุดในร้าน
    ranking = []
    ordered = sorted(products, key=lambda p: p.price, reverse=True)
    place = 0
    for p in ordered[:5]:
        place = place + 1
        row = p.to_dict()
        row["rank"] = place
        ranking.append(row)

    low_stock = []
    for p in products:
        if p.stock <= 3:
            low_stock.append(p.to_dict())
    low_stock.sort(key=lambda r: r["stock"])

    return {
        "total_items": calc.count(),
        "total_price": "{:,.0f}".format(calc.total_price()),
        "average_price": "{:,.0f}".format(calc.average_price()),
        "total_wattage": int(calc.total_wattage()),
        "expensive_count": calc.count_over(EXPENSIVE_LIMIT),
        "expensive_limit": "{:,.0f}".format(EXPENSIVE_LIMIT),
        "category_count": len(rows),
        "rows": rows,
        "top_item": top_item,
        "ranking": ranking,
        "low_stock": low_stock[:6],
        "low_stock_count": len(low_stock),
    }
