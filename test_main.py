import json
from main_wip import AddressParser

# Load dữ liệu test từ JSON file
with open("test_data.json", "r", encoding="utf-8") as file:
    test_cases = json.load(file)

# Khởi tạo trình phân tích địa chỉ
parser = AddressParser("province.txt", "district.txt", "ward.txt")

# Hàm kiểm thử
def run_tests():
    for i, case in enumerate(test_cases):
        input_text = case["text"]
        expected_result = case["result"]

        # Chạy parser trên đoạn text đầu vào
        output = parser.get_location_prediction_set(input_text)

        # Chuyển kết quả thành format mong muốn
        parsed_result = {
            "district": output["district"][0] if output["district"] else None,
            "ward": output["ward"][0] if output["ward"] else None,
            "province": output["province"][0] if output["province"] else None
        }

        # Kiểm tra kết quả
        print(f"Test case {i+1}:")
        print(f"Input: {input_text}")
        print(f"Expected: {expected_result}")
        print(f"Got: {parsed_result}")
        print("✅ Passed\n" if parsed_result == expected_result else "❌ Failed\n")

# Chạy tất cả test
if __name__ == "__main__":
    run_tests()
