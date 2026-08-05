"""
AstroBorn - Cosmic Snapshot
============================
Trang web 100% Python (Streamlit) cho phép người dùng nhập ngày giờ sinh
và nhận về:
  1. Bức ảnh thiên văn (NASA APOD) gần đúng với thời khắc họ chào đời.
  2. "Bức thư từ Vũ trụ" do AI viết, mang phong cách triết học/chữa lành.
  3. Ảnh có thể tải về (đã in kèm thông tin ngày sinh) để làm quà tặng.
  4. Form đặt in (canvas / ốp lưng / bưu thiếp vũ trụ) - mô phỏng đơn hàng.

Chạy: streamlit run app.py
"""

import csv
import datetime
import io
import os

import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from letter_generator import generate_letter
from nasa_api import get_cosmic_snapshot

# --------------------------------------------------------------------------
# Cấu hình trang & CSS "vũ trụ" (dark mode, chữ neon, nền sao lấp lánh)
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="AstroBorn | Bức ảnh vũ trụ ngày bạn chào đời",
    page_icon="✨",
    layout="centered",
)

CUSTOM_CSS = """
<style>
@keyframes twinkle {
    0% { opacity: 0.2; }
    50% { opacity: 1; }
    100% { opacity: 0.2; }
}
.stApp {
    background: radial-gradient(ellipse at top, #0d1b3e 0%, #05060f 60%, #000000 100%);
    color: #eae6ff;
}
.astro-title {
    text-align: center;
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #7dd3fc, #c084fc, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
    letter-spacing: 2px;
}
.astro-slogan {
    text-align: center;
    color: #a5b4fc;
    font-style: italic;
    margin-top: 4px;
    margin-bottom: 28px;
}
.cosmic-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(196,181,253,0.25);
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 0 30px rgba(139,92,246,0.15);
}
.letter-box {
    background: rgba(124, 58, 237, 0.08);
    border-left: 3px solid #c084fc;
    padding: 18px 22px;
    border-radius: 8px;
    font-style: italic;
    line-height: 1.7;
    color: #ede9fe;
}
.star {
    position: fixed;
    background: white;
    border-radius: 50%;
    animation: twinkle 3s infinite ease-in-out;
    z-index: 0;
}
div.stButton > button {
    background: linear-gradient(90deg, #7c3aed, #db2777);
    color: white;
    border: none;
    border-radius: 999px;
    padding: 10px 26px;
    font-weight: 600;
}
div.stButton > button:hover {
    filter: brightness(1.15);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown('<div class="astro-title">✨ AstroBorn ✨</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="astro-slogan">Vũ trụ đã thắp sáng vì sao nào khi bạn chào đời?</div>',
    unsafe_allow_html=True,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
ORDERS_FILE = os.path.join(DATA_DIR, "orders.csv")


# --------------------------------------------------------------------------
# 1. THE LAUNCHPAD - Cổng nhập thông tin
# --------------------------------------------------------------------------
with st.form("launchpad_form"):
    st.markdown("### 🚀 The Launchpad — Nhập khoảnh khắc bạn chào đời")
    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input(
            "Ngày sinh",
            value=datetime.date(2000, 1, 1),
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today(),
        )
    with col2:
        birth_time = st.time_input("Giờ sinh", value=datetime.time(0, 0))

    city = st.text_input("Thành phố bạn sinh ra", placeholder="Ví dụ: Hà Nội")
    submitted = st.form_submit_button("🌌 Khám phá bức ảnh vũ trụ của tôi")

if submitted:
    with st.spinner("Đang quét kho dữ liệu thiên văn NASA..."):
        snapshot = get_cosmic_snapshot(birth_date)
        birth_date_str = birth_date.strftime("%d/%m/%Y") + f" lúc {birth_time.strftime('%H:%M')}"
        letter = generate_letter(snapshot, city, birth_date_str)

    st.session_state["snapshot"] = snapshot
    st.session_state["letter"] = letter
    st.session_state["birth_date_str"] = birth_date_str
    st.session_state["city"] = city


# --------------------------------------------------------------------------
# 2 & 3. THE COSMIC ENGINE + COSMIC SNAPSHOT - Hiển thị kết quả
# --------------------------------------------------------------------------
def build_downloadable_image(image_bytes: bytes, birth_date_str: str, city: str) -> bytes:
    """Ghép khung thông tin ngày sinh vào dưới ảnh, trả về bytes PNG."""
    base = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    banner_h = 90
    canvas = Image.new("RGB", (base.width, base.height + banner_h), (5, 6, 15))
    canvas.paste(base, (0, 0))

    draw = ImageDraw.Draw(canvas)
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except Exception:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    title_line = "AstroBorn — Cosmic Snapshot"
    sub_line = f"{birth_date_str}" + (f"  ·  {city}" if city else "")

    draw.text((24, base.height + 14), title_line, fill=(200, 170, 255), font=font_big)
    draw.text((24, base.height + 52), sub_line, fill=(180, 180, 220), font=font_small)

    out = io.BytesIO()
    canvas.save(out, format="PNG")
    return out.getvalue()


if "snapshot" in st.session_state:
    snapshot = st.session_state["snapshot"]
    letter = st.session_state["letter"]
    birth_date_str = st.session_state["birth_date_str"]
    city = st.session_state["city"]

    st.markdown("---")
    st.markdown('<div class="cosmic-card">', unsafe_allow_html=True)

    st.markdown(f"#### 🌠 {snapshot['title']}")
    st.caption(f"Ảnh chụp ngày {snapshot['date']} · Nguồn: {snapshot.get('copyright', 'NASA')}")

    image_bytes = None
    try:
        img_resp = requests.get(snapshot["url"], timeout=10)
        img_resp.raise_for_status()
        image_bytes = img_resp.content
        st.image(image_bytes, use_container_width=True)
    except Exception:
        st.info("Không thể tải ảnh trực tiếp (có thể do mạng bị chặn). Đây là mô tả ảnh:")

    with st.expander("📖 Mô tả thiên văn (từ NASA)"):
        st.write(snapshot.get("explanation", ""))

    st.markdown("##### 💌 Bức thư từ Vũ trụ")
    st.markdown(f'<div class="letter-box">{letter}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- 4. Tính năng thương mại & lan tỏa -------------------
    st.markdown("### 🎁 Tải ảnh & Đặt làm quà tặng")

    if image_bytes:
        downloadable = build_downloadable_image(image_bytes, birth_date_str, city)
        st.download_button(
            "⬇️ Tải ảnh bản quyền (kèm thông tin ngày sinh)",
            data=downloadable,
            file_name="astroborn_cosmic_snapshot.png",
            mime="image/png",
        )

    st.markdown("##### 🖼️ Dịch vụ in ấn (Bưu thiếp / Canvas / Ốp lưng)")
    with st.form("order_form"):
        product = st.selectbox(
            "Chọn sản phẩm muốn đặt in",
            ["Bưu thiếp Vũ trụ", "Tranh canvas treo tường", "Ốp lưng điện thoại"],
        )
        contact = st.text_input("Email hoặc số điện thoại để liên hệ giao hàng")
        order_submitted = st.form_submit_button("📦 Gửi yêu cầu đặt in")

    if order_submitted:
        if not contact.strip():
            st.warning("Vui lòng nhập thông tin liên hệ để chúng tôi gửi báo giá.")
        else:
            file_exists = os.path.isfile(ORDERS_FILE)
            with open(ORDERS_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["timestamp", "product", "contact", "birth_date", "city", "image_title"])
                writer.writerow(
                    [
                        datetime.datetime.now().isoformat(timespec="seconds"),
                        product,
                        contact,
                        birth_date_str,
                        city,
                        snapshot["title"],
                    ]
                )
            st.success("Đã ghi nhận yêu cầu! Đội ngũ AstroBorn sẽ liên hệ bạn sớm. 🚀")

st.markdown("---")
st.caption("AstroBorn · Dữ liệu ảnh thiên văn từ NASA APOD API · Made with Python & Streamlit")
