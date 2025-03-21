import json
import unittest
from main_wip import Solution

class TestSolution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Đọc file JSON và khởi tạo Solution một lần cho tất cả test cases."""
        with open("data/public.json", "r", encoding="utf-8") as file:
            cls.test_cases = json.load(file)
        
        # Khởi tạo Solution nhưng chưa gọi prepare_database()
        cls.solution = Solution()

        # Cập nhật đường dẫn dữ liệu trước khi gọi prepare_database()
        cls.solution.province_path = "data/list_province.txt"
        cls.solution.district_path = "data/list_district.txt"
        cls.solution.ward_path = "data/list_ward.txt"
        cls.solution.province_path_internal = "data/list_province.csv"
        cls.solution.district_path_internal = "data/list_district.csv"
        cls.solution.ward_path_internal = "data/list_ward.csv"
        cls.solution.full_path_internal = "data/list_full.csv"

        # Gọi lại prepare_database() sau khi đã cập nhật đường dẫn
        cls.solution.prepare_database()

    def test_location_extraction(self):
        """Kiểm thử việc trích xuất địa danh từ đoạn text."""
        for i, case in enumerate(self.test_cases):
            text = case["text"]
            expected_result = case["result"]
            
            with self.subTest(test_case=i, input_text=text):
                output = self.solution.process(text)

                # So sánh kết quả trả về với kết quả mong đợi
                self.assertEqual(output, expected_result, f"Failed on test case {i}: {text}")

if __name__ == "__main__":
    unittest.main()
