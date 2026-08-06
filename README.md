# AstroBorn — Cosmic Snapshot 🌌

Trang web **100% Python** (dùng [Streamlit](https://streamlit.io)), dựa trên ý tưởng
trong `Idea_Futuret.docx`: nhập ngày/giờ sinh → nhận bức ảnh thiên văn NASA gần
đúng ngày đó → AI viết "Bức thư từ Vũ trụ" → tải ảnh/chia sẻ/đặt in.

Dự án được tổ chức theo **package chuẩn**, tách riêng từng trang và từng nhóm
chức năng để dễ bảo trì, mở rộng.

## Cấu trúc dự án

```
astroborn/
├── app.py                          # Trang chính: Khám phá của bạn
├── pages/                          # Mỗi file = 1 trang (Streamlit multipage)
│   ├── 1_💞_Cap_doi_Vu_tru.py       # So sánh sự tương hợp giữa 2 ngày sinh
│   └── 2_🌌_Wall_of_Stars.py        # Tường thư vũ trụ công khai (ẩn danh)
├── core/                            # Package lõi - toàn bộ logic nghiệp vụ
│   ├── services/
│   │   ├── nasa_api.py              # Gọi NASA APOD API + fallback offline
│   │   ├── letter_generator.py      # Sinh thư cá nhân & thư cặp đôi (AI hoặc template)
│   │   └── social_card.py           # Xử lý ảnh: ảnh quà tặng + ảnh chia sẻ mạng xã hội
│   ├── storage/
│   │   └── cache_db.py              # Cache SQLite (ảnh NASA) + lưu Wall of Stars
│   └── ui/
│       ├── styles.py                 # CSS "vũ trụ" dùng chung mọi trang
│       └── components.py             # Khối giao diện tái sử dụng (kết quả, nút tải/chia sẻ)
├── data/                             # Nơi lưu astroborn.db (SQLite) và orders.csv
├── requirements.txt
└── README.md
```

Nhờ tách theo package, `streamlit run app.py` sẽ **tự động tạo thanh điều
hướng bên trái** với 3 trang: *Khám phá của bạn*, *Cặp đôi Vũ trụ*, *Wall of
Stars* — không cần code thêm gì để có multipage.

## Cài đặt & chạy

```bash
cd astroborn
pip install -r requirements.txt
streamlit run app.py
```

Trình duyệt tự mở tại `http://localhost:8501`.

> Nếu Windows PowerShell báo "streamlit không được nhận dạng", dùng thay:
> `python -m streamlit run app.py`

## Các tính năng đã có

### 🌠 Trải nghiệm & cá nhân hoá
- **Khám phá của bạn**: ảnh NASA APOD gần ngày sinh + Bức thư từ Vũ trụ.
- **Cặp đôi Vũ trụ**: nhập 2 ngày sinh, nhận thư về sự tương hợp giữa hai người.

### 📣 Lan tỏa & viral
- **Ảnh chia sẻ mạng xã hội**: tạo ảnh vuông 1080×1080 có trích đoạn thư đè
  lên ảnh nền, tối ưu để đăng Instagram/Facebook (module `social_card.py`).
- **Wall of Stars**: người dùng có thể chia sẻ ẩn danh bức thư của mình lên
  tường công khai, khuyến khích người mới ghé thăm tự tạo thư của họ.

### ⚙️ Kỹ thuật
- **Cache SQLite** (`cache_db.py`): mỗi ngày chỉ gọi NASA API thật một lần,
  các lượt tra cứu sau (cùng ngày) được phục vụ từ cache — nhanh hơn và tiết
  kiệm quota API.
- **Kiến trúc package** rõ ràng: `services` (nghiệp vụ) / `storage` (dữ liệu)
  / `ui` (giao diện dùng chung), giúp thêm trang mới hoặc chức năng mới dễ
  dàng mà không phải sửa các phần không liên quan.

## Cấu hình (tuỳ chọn)

Trang chạy được ngay **không cần API key** (dùng `DEMO_KEY` của NASA + bộ
sinh thư bằng template). Để nâng cấp:

| Biến môi trường     | Mục đích                                                        |
|----------------------|-------------------------------------------------------------------|
| `NASA_API_KEY`       | Lấy miễn phí tại https://api.nasa.gov — tránh giới hạn DEMO_KEY    |
| `ANTHROPIC_API_KEY`  | Nếu có, thư sẽ do Claude viết thay vì dùng template                |
| `OPENAI_API_KEY`     | Tương tự, dùng GPT nếu không có key Anthropic                     |

```bash
export NASA_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
streamlit run app.py
```

## Hướng phát triển tiếp theo

- Bản đồ sao (star chart) thật tại thời điểm/toạ độ sinh (dùng `skyfield`/`astropy`).
- Đa ngôn ngữ (Việt/Anh) để mở rộng ra thị trường quốc tế.
- Gói Premium (khung ảnh cao cấp, thư dài hơn) + tích hợp API in ấn thật
  (Printful/Printify) để tự động hoá từ đặt hàng đến giao hàng.
- Nhắc lại "bức ảnh vũ trụ" mỗi năm vào đúng ngày sinh (qua email).
