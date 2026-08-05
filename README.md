# AstroBorn — Cosmic Snapshot 🌌

Trang web **100% Python** (dùng [Streamlit](https://streamlit.io) — không cần viết HTML/CSS/JS tay),
dựa trên ý tưởng trong file `Idea_Futuret.docx`:

Người dùng nhập ngày/giờ sinh + thành phố → hệ thống lấy bức ảnh thiên văn NASA (APOD)
gần đúng với ngày sinh → AI viết "Bức thư từ Vũ trụ" → người dùng có thể tải ảnh
(kèm khung thông tin ngày sinh) hoặc đặt in làm quà tặng.

## Cấu trúc dự án

```
astroborn/
├── app.py                # Giao diện + luồng chính (Streamlit)
├── nasa_api.py            # Gọi NASA APOD API, xử lý ngày sinh
├── letter_generator.py    # Sinh "Bức thư từ Vũ trụ" (template + AI thật nếu có key)
├── requirements.txt
├── data/
│   └── orders.csv          # Đơn đặt in được lưu tại đây (tự tạo khi có đơn đầu tiên)
└── README.md
```

## Cài đặt

```bash
cd astroborn
pip install -r requirements.txt
```

## Chạy trang web

```bash
streamlit run app.py
```

Trình duyệt sẽ tự mở tại `http://localhost:8501`.

## Cấu hình (tuỳ chọn)

Trang vẫn chạy được ngay mà **không cần API key** (dùng `DEMO_KEY` của NASA + bộ sinh
thư bằng template). Để nâng cấp trải nghiệm, đặt các biến môi trường:

| Biến môi trường     | Mục đích                                                        |
|----------------------|-------------------------------------------------------------------|
| `NASA_API_KEY`       | Lấy miễn phí tại https://api.nasa.gov — tránh giới hạn của DEMO_KEY |
| `ANTHROPIC_API_KEY`  | Nếu có, "Bức thư từ Vũ trụ" sẽ do Claude viết thay vì template     |
| `OPENAI_API_KEY`     | Tương tự, dùng GPT nếu bạn không có key Anthropic                  |

Ví dụ trên macOS/Linux:

```bash
export NASA_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
streamlit run app.py
```

## Ghi chú triển khai theo lộ trình trong tài liệu gốc

- ✅ Bước 1 (UI/UX): giao diện dark-mode, chữ neon, đã dựng sẵn bằng CSS trong `app.py`.
- ✅ Bước 2 (Kết nối dữ liệu): tích hợp NASA APOD API trong `nasa_api.py`, có cơ chế
  dự phòng offline nếu API lỗi/hết quota.
- ✅ Bước 3 (Lập trình): toàn bộ Frontend + Backend đều bằng Python (Streamlit).
- 🔜 Bước 4 (Ra mắt): bạn có thể deploy miễn phí lên **Streamlit Community Cloud**,
  hoặc các nền tảng hỗ trợ Python như Render/Railway, rồi chia sẻ lên các hội nhóm
  yêu thiên văn/cung hoàng đạo.

## Ghi chú kỹ thuật khác

- Ảnh trước ngày 16/06/1995 (mốc NASA APOD bắt đầu) sẽ tự động quy đổi về
  cùng ngày/tháng ở năm gần nhất có dữ liệu.
- Đơn đặt in (canvas/ốp lưng/bưu thiếp) hiện được lưu vào `data/orders.csv` —
  đây là bản mô phỏng (MVP), bạn có thể thay bằng kết nối tới hệ thống thanh
  toán/CRM thật khi triển khai chính thức.
