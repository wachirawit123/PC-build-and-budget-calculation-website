# PAGES.md — ทีม ทบทวน888

Topic: ร้านอุปกรณ์คอมพิวเตอร์ ทบทวน888
data.json: หมวดหมู่ → list ของสินค้า · ฟิลด์: id · name · brand · price · wattage · stock · image

## สมาชิกและหน้าที่
| # | ชื่อ | รหัส | หน้าที่รับผิดชอบ |
|---|------|------|------------------|
| 1 | นายกิตติภูมิ จิตต์ประเสริฐ | 69130740031 | Team Lead + page1 (รายการสินค้า) |
| 2 | นายกาจบัณฑิต ประทุมตรี | 69130740026 | page2 (ฟอร์มเพิ่ม/ลบสินค้า) |
| 3 | นายวชิรวิทย์ ซื่อตรง | 69130740242 | page3 (สถิติคลังสินค้า) |
| 4 | นายชยพล สืบสิมมา | 69130740419 | page4 (จัดสเปกคอม) + models.py + data.json |

## หน้า
- [x] page1 — รายการสินค้า · catalog type: list/gallery · เจ้าของ: กิตติภูมิ
  - [x] เปลี่ยน TITLE แล้ว
  - [x] build(query) อ่าน data.json → กรองหมวดหมู่ + ค้นหา + เรียงลำดับ
  - [x] มีรูปสินค้าทุกชิ้น (static/img/parts/)
  - [x] ไม่เหลือ TODO
- [x] page2 — เพิ่ม/ลบสินค้า · catalog type: form · เจ้าของ: กาจบัณฑิต
  - [x] handle(form) ตรวจชื่อว่าง · ชื่อซ้ำ · ราคาไม่ใช่ตัวเลข · ราคาเกินจริง
  - [x] อัปโหลดรูปสินค้าได้
  - [x] ลบสินค้าออกจากคลังได้
- [x] page3 — สถิติคลังสินค้า · catalog type: stats · เจ้าของ: วชิรวิทย์
  - [x] มูลค่ารวม · ราคาเฉลี่ย · กราฟแท่งต่อหมวดหมู่ · 5 อันดับราคาสูงสุด · สต็อกเหลือน้อย
- [x] page4 (โบนัส) — จัดสเปกคอม · catalog type: cart/calculator · เจ้าของ: ชยพล
  - [x] เลือกอุปกรณ์ทีละหมวด → ราคารวม · ไฟรวม · ขนาด PSU ที่แนะนำ · เตือนเมื่อสเปกไม่ครบ
- [x] models.py — class Product (8 เมธอด) + class PCBuildCalculator (9 เมธอด)

## Python foundations ที่ใช้
- if / else: pages/page1.py, page2.py, page3.py, page4.py, models.py
- loop: ทุกหน้า (วนอ่านสินค้าจาก data.json)
- function: one_value(), all_products(), next_id(), percent(), load_by_category() ...
- class: models.py → Product, PCBuildCalculator
