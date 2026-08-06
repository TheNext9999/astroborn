"""
core/services/social_card.py
Xử lý ảnh bằng Pillow cho 2 mục đích:

1. build_gift_image(): ghép khung thông tin ngày sinh vào dưới ảnh gốc -
   dùng cho nút "Tải ảnh bản quyền" (giữ nguyên tỉ lệ ảnh gốc).
2. build_share_card(): tạo ảnh vuông (1080x1080) có trích đoạn Bức thư từ
   Vũ trụ đè lên ảnh nền - tối ưu để đăng lên Instagram/Facebook, tăng khả
   năng lan tỏa (viral) của trang.
"""

import io
import textwrap

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_ITALIC = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"


def _load_font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def build_gift_image(image_bytes: bytes, birth_date_str: str, city: str) -> bytes:
    """Ghép khung thông tin ngày sinh vào dưới ảnh, trả về bytes PNG."""
    base = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    banner_h = 90
    canvas = Image.new("RGB", (base.width, base.height + banner_h), (5, 6, 15))
    canvas.paste(base, (0, 0))

    draw = ImageDraw.Draw(canvas)
    font_big = _load_font(FONT_BOLD, 26)
    font_small = _load_font(FONT_REGULAR, 18)

    draw.text((24, base.height + 14), "AstroBorn — Cosmic Snapshot", fill=(200, 170, 255), font=font_big)
    sub_line = f"{birth_date_str}" + (f"  ·  {city}" if city else "")
    draw.text((24, base.height + 52), sub_line, fill=(180, 180, 220), font=font_small)

    out = io.BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()


def build_share_card(image_bytes: bytes, quote: str, title: str) -> bytes:
    """Tạo ảnh vuông 1080x1080 để chia sẻ mạng xã hội, có trích đoạn thư đè lên."""
    SIZE = 1080
    base = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Crop ảnh gốc thành hình vuông (lấy phần giữa) rồi resize về 1080x1080
    w, h = base.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    square = base.crop((left, top, left + side, top + side)).resize((SIZE, SIZE))

    # Làm tối nhẹ + blur lớp nền dưới để chữ dễ đọc
    darkened = ImageEnhance.Brightness(square).enhance(0.55)
    canvas = darkened.filter(ImageFilter.GaussianBlur(1))

    draw = ImageDraw.Draw(canvas, "RGBA")
    # Lớp gradient tối phía dưới để chữ nổi bật
    overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for i in range(SIZE // 2):
        alpha = int(180 * (i / (SIZE // 2)))
        overlay_draw.line([(0, SIZE - i), (SIZE, SIZE - i)], fill=(5, 6, 15, alpha))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(canvas)

    font_quote = _load_font(FONT_ITALIC, 40)
    font_title = _load_font(FONT_BOLD, 30)
    font_brand = _load_font(FONT_BOLD, 26)

    # Wrap trích đoạn thư (giới hạn ~220 ký tự để vừa khung ảnh)
    snippet = quote.strip()
    if len(snippet) > 220:
        snippet = snippet[:217].rsplit(" ", 1)[0] + "..."
    wrapped = textwrap.wrap(snippet, width=34)

    y = SIZE - 90 - (len(wrapped) * 50)
    for line in wrapped:
        line_w = draw.textlength(line, font=font_quote)
        draw.text(((SIZE - line_w) / 2, y), line, font=font_quote, fill=(240, 235, 255))
        y += 50

    # Tên hiện tượng thiên văn (nhỏ, phía trên trích đoạn)
    title_line = f"✦ {title} ✦"
    title_w = draw.textlength(title_line, font=font_title)
    draw.text(((SIZE - title_w) / 2, y + 10), title_line, font=font_title, fill=(196, 132, 252))

    # Thương hiệu ở góc dưới
    brand = "AstroBorn.app"
    draw.text((30, SIZE - 50), brand, font=font_brand, fill=(180, 180, 220))

    out = io.BytesIO()
    canvas.convert("RGB").save(out, format="PNG")
    return out.getvalue()
