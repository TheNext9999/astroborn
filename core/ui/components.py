"""
core/ui/components.py
Các khối giao diện tái sử dụng giữa nhiều trang (hiển thị kết quả ảnh vũ
trụ + thư, nút tải ảnh/chia sẻ...), để app.py và các file trong pages/
không phải lặp lại code.
"""

import requests
import streamlit as st

from core.services import social_card


def render_snapshot_result(snapshot: dict, letter: str, extra_caption: str = ""):
    """Hiển thị ảnh + mô tả + Bức thư từ Vũ trụ. Trả về image_bytes (hoặc None)."""
    st.markdown('<div class="cosmic-card">', unsafe_allow_html=True)
    st.markdown(f"#### 🌠 {snapshot['title']}")
    caption = f"Ảnh chụp ngày {snapshot['date']} · Nguồn: {snapshot.get('copyright', 'NASA')}"
    if extra_caption:
        caption += f" · {extra_caption}"
    st.caption(caption)

    image_bytes = None
    try:
        img_resp = requests.get(snapshot["url"], timeout=10)
        img_resp.raise_for_status()
        image_bytes = img_resp.content
        st.image(image_bytes, use_container_width=True)
    except Exception:
        st.info("Không thể tải ảnh trực tiếp (có thể do mạng bị chặn). Xem mô tả bên dưới:")

    with st.expander("📖 Mô tả thiên văn (từ NASA)"):
        st.write(snapshot.get("explanation", ""))

    st.markdown("##### 💌 Bức thư từ Vũ trụ")
    st.markdown(f'<div class="letter-box">{letter}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    return image_bytes


def render_download_and_share(image_bytes: bytes, snapshot: dict, letter: str, birth_date_str: str, city: str, key_prefix: str = ""):
    """Nút tải ảnh quà tặng + nút tạo ảnh chia sẻ mạng xã hội (vuông)."""
    if not image_bytes:
        return

    col1, col2 = st.columns(2)
    with col1:
        gift_image = social_card.build_gift_image(image_bytes, birth_date_str, city)
        st.download_button(
            "⬇️ Tải ảnh bản quyền (kèm ngày sinh)",
            data=gift_image,
            file_name="astroborn_cosmic_snapshot.png",
            mime="image/png",
            key=f"{key_prefix}_gift",
        )
    with col2:
        if st.button("📲 Tạo ảnh chia sẻ mạng xã hội", key=f"{key_prefix}_share_btn"):
            share_image = social_card.build_share_card(image_bytes, letter, snapshot["title"])
            st.session_state[f"{key_prefix}_share_image"] = share_image

    share_image = st.session_state.get(f"{key_prefix}_share_image")
    if share_image:
        st.image(share_image, caption="Ảnh vuông sẵn sàng đăng Instagram/Facebook", width=320)
        st.download_button(
            "⬇️ Tải ảnh chia sẻ (1080x1080)",
            data=share_image,
            file_name="astroborn_share_card.png",
            mime="image/png",
            key=f"{key_prefix}_share_download",
        )
