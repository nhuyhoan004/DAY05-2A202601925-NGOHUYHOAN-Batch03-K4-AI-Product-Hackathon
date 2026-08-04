from datetime import datetime
import unittest

from src.schedule import get_schedule_answer


class FixedScheduleTests(unittest.TestCase):
    def test_returns_full_evening_schedule(self):
        answer = get_schedule_answer("Lịch hoạt động buổi tối như thế nào?")
        self.assertIn("Office Hours 02", answer)
        self.assertIn("Workshop 4", answer)
        self.assertIn("20:00", answer)

    def test_returns_requested_day(self):
        answer = get_schedule_answer("Tối thứ 5 có cuộc họp gì?")
        self.assertIn("Workshop 3", answer)
        self.assertNotIn("Workshop 4", answer)

    def test_resolves_tonight_from_date(self):
        answer = get_schedule_answer("Tối nay có hoạt động gì?", datetime(2026, 8, 3))
        self.assertIn("Office Hours 02", answer)

    def test_ignores_unrelated_question(self):
        self.assertIsNone(get_schedule_answer("Lab thứ 5 phải nộp lúc nào?"))


if __name__ == "__main__":
    unittest.main()
