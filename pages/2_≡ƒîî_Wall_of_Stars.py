"""
pages/2_🌌_Wall_of_Stars.py — Wall of Stars
=============================================
Trưng bày (ẩn danh) những Bức thư từ Vũ trụ mà người dùng đã đồng ý chia
sẻ công khai từ trang chính. Tính năng lan tỏa: tạo cảm giác cộng đồng và
khuyến khích người mới thử tạo bức thư của riêng mình.
"""

import streamlit as st

from core.storage import cache_db
from core.ui import styles

st.set_page_config(page_title="AstroBorn | Wall of Stars", page_icon="🌌", layout="centered")
styles.apply()
styles.header("🌌 Wall of Stars", "Những bức thư từ vũ trụ được cộng đồng chia sẻ")

cache_db.init_db()
entries = cache_db.get_wall_entries(limit=30)

if not entries:
    st.info(
        "Chưa có bức thư nào được chia sẻ. Hãy quay lại trang chính, khám phá bức ảnh vũ trụ "
        "của bạn và nhấn **'Chia sẻ lên Wall of Stars'** để trở thành người đầu tiên! ✨"
    )
else:
    st.caption(f"Đang hiển thị {len(entries)} bức thư gần nhất.")
    for entry in entries:
        st.markdown(
            f"""
            <div class="wall-entry">
                <div class="wall-meta">✦ {entry['snapshot_title']} · gửi bởi {entry['display_name']}</div>
                <div class="letter-box" style="border-left:none; background:transparent; padding:0;">
                    {entry['letter']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")
st.caption("Muốn góp mặt ở đây? Quay lại trang chính để tạo Bức thư từ Vũ trụ của riêng bạn.")
