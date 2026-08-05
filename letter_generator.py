"""
letter_generator.py
Sinh "Bức thư từ Vũ trụ" - một đoạn văn ngắn (~100 chữ) mang phong cách
triết học / chữa lành, kết nối hiện tượng thiên văn với tính cách ẩn giấu
mang tính giả tưởng của người dùng.

Mặc định dùng bộ sinh văn bản theo template (không cần API key, chạy
offline 100%). Nếu bạn có ANTHROPIC_API_KEY hoặc OPENAI_API_KEY trong biến
môi trường, hệ thống sẽ ưu tiên gọi AI thật để văn phong tự nhiên hơn.
"""

import os
import random

# Từ khoá thiên văn -> nét tính cách "giả tưởng" tương ứng
TRAIT_MAP = {
    "nebula": "một tâm hồn giàu trí tưởng tượng, luôn ấp ủ những điều mới mẻ trước khi chúng thành hình",
    "tinh vân": "một tâm hồn giàu trí tưởng tượng, luôn ấp ủ những điều mới mẻ trước khi chúng thành hình",
    "galaxy": "khả năng kết nối vạn vật, nhìn thấy mối liên hệ mà người khác bỏ lỡ",
    "thiên hà": "khả năng kết nối vạn vật, nhìn thấy mối liên hệ mà người khác bỏ lỡ",
    "black hole": "chiều sâu nội tâm bí ẩn, sức hút âm thầm nhưng mãnh liệt",
    "hố đen": "chiều sâu nội tâm bí ẩn, sức hút âm thầm nhưng mãnh liệt",
    "supernova": "năng lượng bứt phá, sẵn sàng bùng cháy để tỏa sáng theo cách riêng",
    "sao": "năng lượng bứt phá, sẵn sàng bùng cháy để tỏa sáng theo cách riêng",
    "star": "năng lượng bứt phá, sẵn sàng bùng cháy để tỏa sáng theo cách riêng",
    "comet": "tinh thần tự do, luôn di chuyển và không ngại những hành trình dài",
    "sao chổi": "tinh thần tự do, luôn di chuyển và không ngại những hành trình dài",
    "cluster": "khả năng gắn kết cộng đồng, tỏa sáng đẹp nhất khi ở cùng những người thân thuộc",
    "cụm sao": "khả năng gắn kết cộng đồng, tỏa sáng đẹp nhất khi ở cùng những người thân thuộc",
}

DEFAULT_TRAIT = "một ngọn lửa lặng lẽ nhưng bền bỉ, âm thầm soi sáng những người xung quanh"

OPENINGS = [
    "Vào chính khoảnh khắc bạn cất tiếng khóc chào đời, {phenomenon} đang diễn ra ngoài kia, cách bạn hàng triệu năm ánh sáng.",
    "Ở một góc xa xôi của vũ trụ, đúng lúc bạn mở mắt lần đầu tiên, {phenomenon} vẫn lặng lẽ tiếp diễn.",
    "Vũ trụ đã chọn cách chào đón bạn bằng {phenomenon} - một sự trùng hợp không hề ngẫu nhiên.",
]

CLOSINGS = [
    "Hãy tin rằng, bạn không đến từ hư không - bạn là một mảnh vỡ nhỏ của những vì sao.",
    "Dù đôi khi lạc lối, hãy nhớ: ánh sáng bên trong bạn đã đi một hành trình rất dài để đến được đây.",
    "Vũ trụ không tạo ra bạn một cách tình cờ. Bạn là một phần tất yếu của bản giao hưởng vô tận này.",
]


def _extract_phenomenon(title: str) -> str:
    t = title.strip()
    return t[0].lower() + t[1:] if t else "một hiện tượng thiên văn kỳ diệu"


def _find_trait(explanation: str, title: str) -> str:
    text = f"{title} {explanation}".lower()
    for keyword, trait in TRAIT_MAP.items():
        if keyword in text:
            return trait
    return DEFAULT_TRAIT


def _template_letter(snapshot: dict, city: str) -> str:
    phenomenon = _extract_phenomenon(snapshot.get("title", "một hiện tượng thiên văn"))
    trait = _find_trait(snapshot.get("explanation", ""), snapshot.get("title", ""))
    opening = random.choice(OPENINGS).format(phenomenon=phenomenon)
    closing = random.choice(CLOSINGS)
    city_part = f" từ {city}" if city else ""

    letter = (
        f"{opening} Ánh sáng ấy đã du hành qua không gian và thời gian để chạm đến bạn{city_part}, "
        f"mang theo một thông điệp: bạn mang trong mình {trait}. "
        f"{closing}"
    )
    return letter


def _try_real_ai(snapshot: dict, city: str, birth_date_str: str) -> str | None:
    """Thử gọi AI thật (Anthropic hoặc OpenAI) nếu có API key trong môi trường.
    Trả về None nếu không có key hoặc gọi lỗi, để tự động fallback sang template.
    """
    prompt = (
        "Viết một đoạn văn ngắn khoảng 100 chữ, tiếng Việt, phong cách triết học/chữa lành, "
        f"kết nối hiện tượng thiên văn '{snapshot.get('title')}' "
        f"(mô tả: {snapshot.get('explanation', '')[:300]}) "
        f"với một người sinh ngày {birth_date_str} tại {city or 'một nơi nào đó trên Trái Đất'}. "
        "Giọng văn ấm áp, giàu hình ảnh, kết thúc bằng một câu truyền cảm hứng."
    )

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            import requests

            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": anthropic_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-6",
                    "max_tokens": 300,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            return "".join(
                block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
            ).strip() or None
        except Exception:
            return None

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            import requests

            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {openai_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                },
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            return None

    return None


def generate_letter(snapshot: dict, city: str, birth_date_str: str) -> str:
    """Sinh Bức thư từ Vũ trụ. Ưu tiên AI thật nếu có key, ngược lại dùng template."""
    ai_letter = _try_real_ai(snapshot, city, birth_date_str)
    if ai_letter:
        return ai_letter
    return _template_letter(snapshot, city)
