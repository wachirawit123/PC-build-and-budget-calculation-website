# -*- coding: utf-8 -*-
"""models.py — คลาสของกลุ่ม ทบทวน888 (ร้านอุปกรณ์คอมพิวเตอร์)

Product            = สินค้า 1 ชิ้น (ซีพียู / การ์ดจอ / แรม / ...)
PCBuildCalculator  = ตัวคำนวณสเปกคอม: ราคารวม, ไฟรวม, ขนาด PSU ที่แนะนำ
"""

CATEGORY_TH = {
    "cpu": "ซีพียู (CPU)",
    "vga": "การ์ดจอ (VGA)",
    "mainboard": "เมนบอร์ด (Mainboard)",
    "ram": "แรม (RAM)",
    "ssd": "เอสเอสดี (SSD)",
    "hdd": "ฮาร์ดดิสก์ (HDD)",
    "aio": "ชุดน้ำปิด (AIO)",
    "aircooler": "ซิงก์ลม (Air Cooler)",
    "fan": "พัดลมระบายความร้อน (Fan)",
    "psu": "พาวเวอร์ซัพพลาย (PSU)",
    "case": "เคสคอมพิวเตอร์ (Case)",
}

CATEGORY_ORDER = ["cpu", "vga", "mainboard", "ram", "ssd", "hdd",
                  "aio", "aircooler", "fan", "psu", "case"]


def category_name(key):
    """คืนชื่อหมวดหมู่ภาษาไทย ถ้าไม่รู้จักก็คืนคีย์เดิม"""
    if key in CATEGORY_TH:
        return CATEGORY_TH[key]
    return str(key)


class Product:
    """สินค้า 1 ชิ้นในคลังของร้าน"""

    def __init__(self, item_id, name, price, category, wattage=0, brand="", image="", stock=0):
        self.id = str(item_id)
        self.name = str(name)
        self.brand = str(brand)
        self.category = str(category)
        self.image = str(image)
        try:
            self.price = float(price)
        except (ValueError, TypeError):
            self.price = 0.0
        try:
            self.wattage = float(wattage)
        except (ValueError, TypeError):
            self.wattage = 0.0
        try:
            self.stock = int(float(stock))
        except (ValueError, TypeError):
            self.stock = 0

    @staticmethod
    def from_dict(row, category):
        """สร้าง Product จาก dict 1 แถวใน data.json"""
        return Product(
            row.get("id", "-"),
            row.get("name", "ไม่ระบุชื่อ"),
            row.get("price", 0),
            category,
            row.get("wattage", 0),
            row.get("brand", ""),
            row.get("image", ""),
            row.get("stock", 0),
        )

    def get_formatted_price(self):
        return "{:,.0f} บาท".format(self.price)

    def category_label(self):
        return category_name(self.category)

    def picture(self):
        """ที่อยู่รูปใน static/ — ถ้าไม่มีรูปก็ใช้รูปสำรอง"""
        if self.image == "":
            return "img/placeholder.svg"
        import os
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        image_path = os.path.join(static_dir, "img", self.image)
        if os.path.isfile(image_path):
            return "img/" + self.image

        base, extension = os.path.splitext(self.image)
        if extension.lower() == ".svg":
            alternative = base + ".jpg"
        elif extension.lower() in (".jpg", ".jpeg"):
            alternative = base + ".svg"
        else:
            alternative = ""
        if alternative != "" and os.path.isfile(os.path.join(static_dir, "img", alternative)):
            return "img/" + alternative
        return "img/placeholder.svg"

    def is_high_power(self):
        return self.wattage > 100

    def in_stock(self):
        return self.stock > 0

    def stock_label(self):
        if self.stock <= 0:
            return "สินค้าหมด"
        elif self.stock <= 3:
            return "เหลือน้อย (" + str(self.stock) + ")"
        else:
            return "พร้อมส่ง (" + str(self.stock) + ")"

    def matches(self, keyword):
        """ค้นหาจากชื่อ / ยี่ห้อ / หมวดหมู่"""
        keyword = str(keyword).strip().lower()
        if keyword == "":
            return True
        haystack = (self.name + " " + self.brand + " " + self.category).lower()
        return keyword in haystack

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "category_label": self.category_label(),
            "price": self.price,
            "price_text": self.get_formatted_price(),
            "wattage": int(self.wattage),
            "stock": self.stock,
            "stock_label": self.stock_label(),
            "in_stock": self.in_stock(),
            "high_power": self.is_high_power(),
            "picture": self.picture(),
        }


class PCBuildCalculator:
    """รับรายการสินค้า (list ของ Product) แล้วคำนวณสรุปให้"""

    PSU_SIZES = [450, 550, 650, 750, 850, 1000, 1200, 1600]

    def __init__(self, products):
        if isinstance(products, list):
            self.products = products
        else:
            self.products = []

    def count(self):
        return len(self.products)

    def total_price(self):
        total = 0.0
        for p in self.products:
            total = total + p.price
        return total

    def total_wattage(self):
        total = 0.0
        for p in self.products:
            total = total + p.wattage
        return total

    def average_price(self):
        if self.count() == 0:
            return 0.0
        return self.total_price() / self.count()

    def most_expensive(self):
        best = None
        for p in self.products:
            if best is None or p.price > best.price:
                best = p
        return best

    def count_over(self, limit):
        """นับสินค้าที่ราคามากกว่า limit บาท"""
        n = 0
        for p in self.products:
            if p.price > limit:
                n = n + 1
        return n

    def total_by_category(self):
        """คืน dict: หมวดหมู่ -> {'count', 'price', 'wattage'}"""
        summary = {}
        for p in self.products:
            if p.category not in summary:
                summary[p.category] = {"count": 0, "price": 0.0, "wattage": 0.0}
            summary[p.category]["count"] += 1
            summary[p.category]["price"] += p.price
            summary[p.category]["wattage"] += p.wattage
        return summary

    def recommended_psu(self):
        """ไฟรวม + เผื่อ 30% แล้วปัดขึ้นเป็นขนาด PSU ที่มีขายจริง"""
        need = self.total_wattage() * 1.3
        for size in self.PSU_SIZES:
            if size >= need:
                return size
        return self.PSU_SIZES[-1]
