import json
import unittest
from main_wip import Solution

class TestSolution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Đọc file JSON và khởi tạo Solution một lần cho tất cả test cases."""
        with open("data/public.json", "r", encoding="utf-8") as file:
            cls.test_cases = json.load(file)

        # Khởi tạo Solution và cập nhật đường dẫn dữ liệu
        cls.solution = Solution()
        cls.solution.province_path = "list_province.txt"
        cls.solution.district_path = "list_district.txt"
        cls.solution.ward_path = "list_ward.txt"
        cls.solution.province_path_internal = "list_province.csv"
        cls.solution.district_path_internal = "list_district.csv"
        cls.solution.ward_path_internal = "list_ward.csv"
        cls.solution.full_path_internal = "list_full.csv"
        cls.solution.prepare_database()

    def test_location_extraction(self):
        """Kiểm thử việc trích xuất địa danh từ đoạn text và tính độ chính xác."""
        total_tests = len(self.test_cases)
        passed_tests = 0

        for i, case in enumerate(self.test_cases):
            text = case["text"]
            expected_result = case["result"]
            
            with self.subTest(test_case=i, input_text=text):
                output = self.solution.process(text)

                # Kiểm tra kết quả có khớp với mong đợi không
                if output == expected_result:
                    passed_tests += 1  # Đếm số test đúng
                
                # So sánh kết quả trả về với kết quả mong đợi
                self.assertEqual(output, expected_result, f"Failed on test case {i}: {text}")

        # Tính độ chính xác (accuracy)
        accuracy = (passed_tests / total_tests) * 100
        print(f"\n✅ Accuracy: {accuracy:.2f}% ({passed_tests}/{total_tests} test cases passed)")

if __name__ == "__main__":
    unittest.main()
