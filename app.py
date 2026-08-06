"""
app.py — AstroBorn (trang chính: Khám phá của bạn)
=====================================================
Đây là điểm khởi chạy của ứng dụng multipage Streamlit. Các trang khác
(Cặp đôi vũ trụ, Wall of Stars) nằm trong thư mục pages/ và sẽ tự động
xuất hiện ở thanh điều hướng bên trái.

Toàn bộ logic nghiệp vụ (gọi NASA API, sinh thư, xử lý ảnh, cache) nằm
trong package core/ - app.py chỉ còn nhiệm vụ điều phối giao diện.

Chạy: streamlit run app.py
"""

import datetime

import streamlit as st

from core.services.letter_generator import generate_letter
from core.services.nasa_api import get_cosmic_snapshot
from core.storage import cache_db
from core.ui import components, styles

st.set_page_config(
    page_title="AstroBorn | Bức ảnh vũ trụ ngày bạn chào đời",
    page_icon="✨",
    layout="centered",
)
styles.apply()
styles.header("✨ AstroBorn ✨", "Vũ trụ đã thắp sáng vì sao nào khi bạn chào đời?")

cache_db.init_db()

# --------------------------------------------------------------------------
# THE LAUNCHPAD - Cổng nhập thông tin
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
    # reset ảnh share card cũ (nếu có) khi tra cứu mới
    st.session_state.pop("main_share_image", None)


# --------------------------------------------------------------------------
# Hiển thị kết quả + tải ảnh / chia sẻ / đặt in / góp vào Wall of Stars
# --------------------------------------------------------------------------
if "snapshot" in st.session_state:
    snapshot = st.session_state["snapshot"]
    letter = st.session_state["letter"]
    birth_date_str = st.session_state["birth_date_str"]
    city = st.session_state["city"]

    st.markdown("---")
    source_note = {"cache": "⚡ lấy từ cache", "fallback": "📦 dữ liệu dự phòng offline"}.get(
        snapshot.get("source"), ""
    )
    image_bytes = components.render_snapshot_result(snapshot, letter, extra_caption=source_note)

    st.markdown("### 🎁 Tải ảnh & Chia sẻ")
    components.render_download_and_share(image_bytes, snapshot, letter, birth_date_str, city, key_prefix="main")

    st.markdown("### 🌌 Góp vào Wall of Stars")
    with st.form("wall_form"):
        st.caption("Đồng ý chia sẻ ẩn danh Bức thư từ Vũ trụ của bạn lên trang công khai để lan tỏa cảm hứng.")
        display_name = st.text_input("Tên hiển thị (không bắt buộc)", placeholder="Ví dụ: một người mộng mơ")
        share_to_wall = st.form_submit_button("✨ Chia sẻ lên Wall of Stars")

    if share_to_wall:
        cache_db.add_wall_entry(display_name, letter, snapshot["title"], snapshot.get("url", ""))
        st.success("Đã thêm bức thư của bạn vào Wall of Stars! Ghé trang 'Wall of Stars' ở thanh bên để xem. 🌠")

    st.markdown("### 🖼️ Dịch vụ in ấn (Bưu thiếp / Canvas / Ốp lưng)")
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
            import csv
            import os

            data_dir = os.path.join(os.path.dirname(__file__), "data")
            os.makedirs(data_dir, exist_ok=True)
            orders_file = os.path.join(data_dir, "orders.csv")
            file_exists = os.path.isfile(orders_file)
            with open(orders_file, "a", newline="", encoding="utf-8") as f:
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
stats = cache_db.cache_stats()
st.caption(
    f"AstroBorn · {stats['cached_snapshots']} ngày đã cache · {stats['wall_entries']} thư trên Wall of Stars "
    "· Dữ liệu ảnh từ NASA APOD API · Made with Python & Streamlit"
)