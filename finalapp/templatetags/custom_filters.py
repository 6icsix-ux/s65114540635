from django import template

register = template.Library()

# Map เดือนเป็นภาษาไทย
MONTHS_THAI = {
    1: "มกราคม",
    2: "กุมภาพันธ์",
    3: "มีนาคม",
    4: "เมษายน",
    5: "พฤษภาคม",
    6: "มิถุนายน",
    7: "กรกฎาคม",
    8: "สิงหาคม",
    9: "กันยายน",
    10: "ตุลาคม",
    11: "พฤศจิกายน",
    12: "ธันวาคม"
}

@register.filter
def thai_month_year(value):
    """ แปลง '2025-05' เป็น 'พฤษภาคม 2025' """
    if not value:
        return ""
    try:
        year, month = map(int, str(value).split('-'))
        return f"{MONTHS_THAI.get(month, '')} {year}"
    except (ValueError, AttributeError):
        return value

FACILITY_MAP = {
    'bed': '🛏 เตียง',
    'wifi': '📶 Wi-Fi',
    'water_heater': '🚿 เครื่องทำน้ำอุ่น',
    'parking': '🅿️ ที่จอดรถ',
    'kettle': '☕ กาน้ำร้อน',
    'kitchen': '🍳 ครัว/ไมโครเวฟ',
    'balcony': '🌅 ระเบียง',
    'no_smoking': '🚭 ห้ามสูบบุหรี่',
    'smoking_area': '🚬 สูบบุหรี่ (ภายนอก)',
    'pet_allowed': '🐶🐱 นำสัตว์เลี้ยงเข้าได้',
    'fridge': '🧊 ตู้เย็น',
}

@register.filter
def facility_label(code):
    """ แปลงรหัสสิ่งอำนวยความสะดวกเป็นชื่อพร้อมอีโมจิ """
    return FACILITY_MAP.get(code, code)