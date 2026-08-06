"""
pages/1_💞_Cap_doi_Vu_tru.py — Cặp đôi vũ trụ
================================================
So sánh hai ngày sinh, lấy 2 bức ảnh thiên văn tương ứng và để AI viết
một bức thư về sự tương hợp giữa hai người. Phù hợp chia sẻ giữa bạn bè,
người yêu vào các dịp đặc biệt (Valentine, sinh nhật...).
"""

import datetime

import streamlit as st

from core.services.letter_generator import generate_pair_letter
from core.services.nasa_api import get_cosmic_snapshot
from core.ui import components, styles

st.set_page_config(page_title="AstroBorn | Cặp đôi vũ trụ", page_icon="💞", layout="centered")
styles.apply()
styles.header("💞 Cặp đôi Vũ trụ", "Hai vì sao, một bầu trời chung")

with st.form("pair_form"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Người thứ nhất**")
        name_a = st.text_input("Tên (không bắt buộc)", key="name_a", placeholder="Ví dụ: An")
        date_a = st.date_input(
            "Ngày sinh", value=datetime.date(2000, 1, 1),
            min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today(), key="date_a",
        )
    with col2:
        st.markdown("**Người thứ hai**")
        name_b = st.text_input("Tên (không bắt buộc)", key="name_b", placeholder="Ví dụ: Bình")
        date_b = st.date_input(
            "Ngày sinh", value=datetime.date(2000, 6, 15),
            min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today(), key="date_b",
        )
    submitted = st.form_submit_button("💫 Xem sự tương hợp vũ trụ")

if submitted:
    with st.spinner("Đang đối chiếu hai bầu trời..."):
        snapshot_a = get_cosmic_snapshot(date_a)
        snapshot_b = get_cosmic_snapshot(date_b)
        pair_letter = generate_pair_letter(snapshot_a, snapshot_b, name_a, name_b)

    st.session_state["pair_snapshot_a"] = snapshot_a
    st.session_state["pair_snapshot_b"] = snapshot_b
    st.session_state["pair_letter"] = pair_letter
    st.session_state["pair_names"] = (name_a or "Người thứ nhất", name_b or "Người thứ hai")

if "pair_letter" in st.session_state:
    st.markdown("---")
    name_a, name_b = st.session_state["pair_names"]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"##### 🌠 {name_a}")
        st.image(st.session_state["pair_snapshot_a"]["url"], use_container_width=True)
        st.caption(st.session_state["pair_snapshot_a"]["title"])
    with col2:
        st.markdown(f"##### 🌠 {name_b}")
        st.image(st.session_state["pair_snapshot_b"]["url"], use_container_width=True)
        st.caption(st.session_state["pair_snapshot_b"]["title"])

    st.markdown("##### 💌 Bức thư về sự tương hợp")
    st.markdown(f'<div class="letter-box">{st.session_state["pair_letter"]}</div>', unsafe_allow_html=True)

    st.markdown("### 📲 Chia sẻ khoảnh khắc này")
    try:
        import requests

        img_resp = requests.get(st.session_state["pair_snapshot_a"]["url"], timeout=10)
        img_resp.raise_for_status()
        components.render_download_and_share(
            img_resp.content,
            st.session_state["pair_snapshot_a"],
            st.session_state["pair_letter"],
            f"{name_a} & {name_b}",
            "",
            key_prefix="pair",
        )
    except Exception:
        st.info("Không thể tải ảnh để tạo file chia sẻ lúc này, vui lòng thử lại.")
