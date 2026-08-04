"""Lịch sinh hoạt cố định, được trả lời không qua bước truy xuất RAG."""

from datetime import datetime
import re
import unicodedata
from typing import Optional


EVENING_SCHEDULE = {
    0: ("Thứ 2", "Office Hours 02", "Trên kênh OFFICE HOURS - KÊNH 01"),
    2: ("Thứ 4", "Mentor Duty", "Sinh hoạt theo nhóm trong Zoom"),
    3: ("Thứ 5", "Workshop 3", "Buổi workshop chung"),
    4: ("Thứ 6", "Office Hours 03", "Trên kênh OFFICE HOURS - KÊNH 01"),
    5: ("Thứ 7", "Mentor Duty", "Sinh hoạt theo nhóm trong Zoom"),
    6: ("Chủ nhật", "Workshop 4", "Buổi workshop chung"),
}

SCHEDULE_KEYWORDS = (
    "lich", "hoat dong", "sinh hoat", "cuoc hop", "hop", "meeting",
    "workshop", "mentor duty", "office hours", "buoi toi", "toi nay",
)


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text.lower())
    normalized = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return normalized.replace("đ", "d")


def _weekday_from_question(question: str) -> Optional[int]:
    text = _normalize(question)
    if "chu nhat" in text:
        return 6

    match = re.search(r"\bthu\s*([2-7])\b", text)
    if match:
        return int(match.group(1)) - 2
    return None


def _format_event(weekday: int) -> str:
    day, title, detail = EVENING_SCHEDULE[weekday]
    return f"**{day} — {title}**\n- {detail}\n- Thời gian: **20:00**"


def get_schedule_answer(question: str, now: Optional[datetime] = None) -> Optional[str]:
    """Trả về lịch tối nếu câu hỏi thuộc ý định hỏi lịch; ngược lại trả về ``None``."""
    text = _normalize(question)
    is_schedule_question = any(keyword in text for keyword in SCHEDULE_KEYWORDS)
    requested_day = _weekday_from_question(question)

    # Chỉ một thứ cụ thể chưa đủ để suy ra người dùng đang hỏi lịch.
    if not is_schedule_question:
        return None

    if requested_day is not None:
        event = EVENING_SCHEDULE.get(requested_day)
        if event:
            return "📅 Lịch buổi tối:\n" + _format_event(requested_day)
        return "📅 Theo lịch cố định, **Thứ 3 không có hoạt động chung lúc 20:00**."

    if "toi nay" in text:
        current_weekday = (now or datetime.now()).weekday()
        event = EVENING_SCHEDULE.get(current_weekday)
        if event:
            return "📅 Hoạt động tối nay:\n" + _format_event(current_weekday)
        return "📅 Theo lịch cố định, **tối nay không có hoạt động chung lúc 20:00**."

    events = "\n\n".join(_format_event(day) for day in EVENING_SCHEDULE)
    return "📅 **Lịch hoạt động cố định buổi tối (20:00)**\n\n" + events
