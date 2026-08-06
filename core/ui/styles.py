"""
core/ui/styles.py
CSS "vũ trụ" (dark mode, chữ neon) dùng chung cho mọi trang trong app.
Import và gọi apply() ở đầu mỗi file trang để đồng bộ giao diện.
"""

import streamlit as st

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
.wall-entry {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(196,181,253,0.18);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 14px;
}
.wall-meta {
    color: #a5b4fc;
    font-size: 0.85rem;
    margin-bottom: 6px;
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


def apply():
    """Áp dụng CSS chung + cấu hình trang. Gọi ở đầu mỗi file trang."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def header(title: str, slogan: str):
    st.markdown(f'<div class="astro-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="astro-slogan">{slogan}</div>', unsafe_allow_html=True)
