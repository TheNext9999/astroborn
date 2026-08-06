"""
core/services/letter_generator.py
Sinh "Bức thư từ Vũ trụ" - đoạn văn ngắn mang phong cách triết học/chữa lành,
kết nối hiện tượng thiên văn với tính cách ẩn giấu mang tính giả tưởng.

Mặc định dùng bộ sinh văn bản theo template (chạy offline 100%, không cần
API key). Nếu có ANTHROPIC_API_KEY hoặc OPENAI_API_KEY trong biến môi
trường, hệ thống sẽ ưu tiên gọi AI thật để văn phong tự nhiên hơn.

Ngoài thư cá nhân, module còn hỗ trợ sinh thư "Cặp đôi vũ trụ" - so sánh
hai hiện tượng thiên văn ứng với hai ngày sinh, viết về sự tương hợp.
"""

import os
import random

import requests

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

PAIR_OPENINGS = [
    "Hai ngọn đèn của các bạn được thắp lên ở hai thời khắc khác nhau của vũ trụ, nhưng ánh sáng ấy rồi cũng tìm đến nhau.",
    "Vũ trụ hiếm khi sắp đặt điều gì một cách tình cờ - và cuộc gặp gỡ của hai bạn cũng vậy.",
]
PAIR_CLOSINGS = [
    "Hai vì sao không cần giống nhau để cùng tỏa sáng trên một bầu trời.",
    "Có những quỹ đạo được sinh ra để giao nhau - có lẽ đây là một trong số đó.",
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

    return (
        f"{opening} Ánh sáng ấy đã du hành qua không gian và thời gian để chạm đến bạn{city_part}, "
        f"mang theo một thông điệp: bạn mang trong mình {trait}. "
        f"{closing}"
    )


def _template_pair_letter(snapshot_a: dict, snapshot_b: dict, name_a: str, name_b: str) -> str:
    trait_a = _find_trait(snapshot_a.get("explanation", ""), snapshot_a.get("title", ""))
    trait_b = _find_trait(snapshot_b.get("explanation", ""), snapshot_b.get("title", ""))
    opening = random.choice(PAIR_OPENINGS)
    closing = random.choice(PAIR_CLOSINGS)
    label_a = name_a or "Người thứ nhất"
    label_b = name_b or "Người thứ hai"

    return (
        f"{opening} {label_a} mang trong mình {trait_a}, còn {label_b} lại mang {trait_b}. "
        f"Khi {_extract_phenomenon(snapshot_a.get('title',''))} và {_extract_phenomenon(snapshot_b.get('title',''))} "
        f"cùng được nhắc đến trong một câu chuyện, đó là lúc hai nguồn năng lượng khác biệt học cách bổ khuyết cho nhau. "
        f"{closing}"
    )


def _call_anthropic(prompt: str):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
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
        text = "".join(
            block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
        ).strip()
        return text or None
    except Exception:
        return None


def _call_openai(prompt: str):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def generate_letter(snapshot: dict, city: str, birth_date_str: str) -> str:
    """Sinh Bức thư từ Vũ trụ cho một người. Ưu tiên AI thật nếu có key."""
    prompt = (
        "Viết một đoạn văn ngắn khoảng 100 chữ, tiếng Việt, phong cách triết học/chữa lành, "
        f"kết nối hiện tượng thiên văn '{snapshot.get('title')}' "
        f"(mô tả: {snapshot.get('explanation', '')[:300]}) "
        f"với một người sinh ngày {birth_date_str} tại {city or 'một nơi nào đó trên Trái Đất'}. "
        "Giọng văn ấm áp, giàu hình ảnh, kết thúc bằng một câu truyền cảm hứng."
    )
    ai_letter = _call_anthropic(prompt) or _call_openai(prompt)
    if ai_letter:
        return ai_letter
    return _template_letter(snapshot, city)


def generate_pair_letter(snapshot_a: dict, snapshot_b: dict, name_a: str, name_b: str) -> str:
    """Sinh Bức thư 'Cặp đôi vũ trụ' so sánh sự tương hợp giữa hai người."""
    prompt = (
        "Viết một đoạn văn ngắn khoảng 120 chữ, tiếng Việt, phong cách triết học/lãng mạn nhẹ nhàng, "
        f"so sánh hai hiện tượng thiên văn '{snapshot_a.get('title')}' (ứng với {name_a or 'người thứ nhất'}) "
        f"và '{snapshot_b.get('title')}' (ứng với {name_b or 'người thứ hai'}), "
        "nói về sự tương hợp, bổ khuyết giữa hai người, kết thúc bằng một câu truyền cảm hứng về mối quan hệ của họ."
    )
    ai_letter = _call_anthropic(prompt) or _call_openai(prompt)
    if ai_letter:
        return ai_letter
    return _template_pair_letter(snapshot_a, snapshot_b, name_a, name_b)
