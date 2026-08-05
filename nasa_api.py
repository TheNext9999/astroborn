"""
nasa_api.py
Kết nối với NASA Open API (APOD - Astronomy Picture of the Day) để lấy
bức ảnh thiên văn gần đúng với ngày sinh của người dùng.

NASA APOD chỉ có dữ liệu từ 16/06/1995 trở đi. Nếu ngày sinh trước mốc
này, hệ thống sẽ tự động quy đổi về năm gần nhất có cùng ngày/tháng.
"""

import os
import datetime
import requests

APOD_START_DATE = datetime.date(1995, 6, 16)
NASA_API_URL = "https://api.nasa.gov/planetary/apod"

# Dữ liệu dự phòng (offline fallback) - dùng khi không có mạng hoặc API lỗi,
# để trang web vẫn demo được với vài "bức ảnh vũ trụ" mẫu.
FALLBACK_SNAPSHOTS = [
    {
        "title": "Tinh vân Đại Bàng - Cột trụ Sáng Tạo",
        "explanation": (
            "Những cột khí và bụi khổng lồ trong tinh vân Đại Bàng là nơi "
            "các ngôi sao mới đang được sinh ra từ vật chất nguyên thủy của vũ trụ."
        ),
        "url": "https://apod.nasa.gov/apod/image/1501/pillars_hst.jpg",
        "media_type": "image",
        "date": "1995-06-16",
        "copyright": "NASA, ESA, Hubble Heritage Team",
    },
    {
        "title": "Thiên hà Xoáy Ốc NGC 1300",
        "explanation": (
            "Một thiên hà xoắn ốc có thanh chắn ngoạn mục, nơi hàng tỷ ngôi sao "
            "quay quanh trung tâm trong một điệu vũ vũ trụ kéo dài hàng triệu năm."
        ),
        "url": "https://apod.nasa.gov/apod/image/0503/ngc1300_hst_big.jpg",
        "media_type": "image",
        "date": "2005-03-02",
        "copyright": "NASA, ESA, Hubble Heritage Team",
    },
    {
        "title": "Hố Đen Nuốt Vật Chất",
        "explanation": (
            "Ở trung tâm nhiều thiên hà, những hố đen siêu khối lượng âm thầm "
            "hút vật chất xung quanh, giải phóng năng lượng khổng lồ ra không gian."
        ),
        "url": "https://apod.nasa.gov/apod/image/2105/M87_EHT_1080.jpg",
        "media_type": "image",
        "date": "2021-05-01",
        "copyright": "Event Horizon Telescope Collaboration",
    },
]


def _closest_valid_date(birth_date: datetime.date) -> datetime.date:
    """Quy đổi ngày sinh về một ngày mà NASA APOD chắc chắn có dữ liệu.

    - Nếu ngày sinh nằm trong khoảng APOD có dữ liệu (16/06/1995 -> hôm qua) -> giữ nguyên.
    - Nếu trước 16/06/1995 -> lấy cùng ngày/tháng nhưng ở năm 1995 trở đi
      (nếu ngày/tháng đó nhỏ hơn 16/06 thì lùi sang 1996 để chắc chắn có dữ liệu).
    - Nếu ngày sinh ở tương lai / hôm nay -> lấy ngày hôm qua (APOD publish trễ 1 ngày).
    """
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    if birth_date > yesterday:
        return yesterday

    if birth_date >= APOD_START_DATE:
        return birth_date

    # Ngày sinh trước khi APOD bắt đầu -> tìm năm gần nhất có cùng ngày/tháng
    for year in (1995, 1996):
        try:
            candidate = birth_date.replace(year=year)
        except ValueError:
            # xử lý 29/02 vào năm không nhuận
            candidate = birth_date.replace(year=year, day=28)
        if candidate >= APOD_START_DATE:
            return candidate
    return birth_date.replace(year=1996)


def get_cosmic_snapshot(birth_date: datetime.date) -> dict:
    """Trả về dict thông tin ảnh thiên văn gần nhất với ngày sinh.

    Nếu gọi API thất bại (không có mạng, hết quota, v.v.) sẽ dùng dữ liệu
    dự phòng để trang web vẫn hoạt động được.
    """
    api_key = os.environ.get("NASA_API_KEY", "DEMO_KEY")
    target_date = _closest_valid_date(birth_date)

    try:
        resp = requests.get(
            NASA_API_URL,
            params={"api_key": api_key, "date": target_date.isoformat()},
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("media_type") == "image" and data.get("url"):
            return {
                "title": data.get("title", "Khoảnh khắc vũ trụ"),
                "explanation": data.get("explanation", ""),
                "url": data.get("hdurl") or data.get("url"),
                "media_type": data.get("media_type"),
                "date": data.get("date"),
                "copyright": data.get("copyright", "NASA / APOD"),
                "source": "live",
            }
        # Nếu hôm đó là video, thử lùi lại 1 ngày để tìm ảnh
        prev_day = target_date - datetime.timedelta(days=1)
        resp2 = requests.get(
            NASA_API_URL,
            params={"api_key": api_key, "date": prev_day.isoformat()},
            timeout=8,
        )
        resp2.raise_for_status()
        data2 = resp2.json()
        if data2.get("media_type") == "image" and data2.get("url"):
            return {
                "title": data2.get("title", "Khoảnh khắc vũ trụ"),
                "explanation": data2.get("explanation", ""),
                "url": data2.get("hdurl") or data2.get("url"),
                "media_type": data2.get("media_type"),
                "date": data2.get("date"),
                "copyright": data2.get("copyright", "NASA / APOD"),
                "source": "live",
            }
    except Exception:
        pass

    # --- Fallback offline: chọn theo tổng ngày/tháng/năm sinh để có tính "cá nhân hoá" ---
    idx = (birth_date.day + birth_date.month + birth_date.year) % len(FALLBACK_SNAPSHOTS)
    fallback = dict(FALLBACK_SNAPSHOTS[idx])
    fallback["source"] = "fallback"
    return fallback
