import json
import time
from main_wip import Solution

if __name__ == "__main__":
    # Load test data
    with open("data/public.json", "r", encoding="utf-8") as file:
        test_cases = json.load(file)

    # Initialize solution
    solution = Solution()
    solution.province_path = "list_province.txt"
    solution.district_path = "list_district.txt"
    solution.ward_path = "list_ward.txt"
    solution.province_path_internal = "list_province.csv"
    solution.district_path_internal = "list_district.csv"
    solution.ward_path_internal = "list_ward.csv"
    solution.full_path_internal = "list_full.csv"
    solution.prepare_database()

    total_tests = len(test_cases)
    correct_tests = 0
    total_time = 0
    max_time = 0

    # Iterate over test cases
    for case in test_cases:
        text = case["text"]
        expected_result = case["result"]

        start_time = time.time()
        output = solution.process(text)
        exec_time = time.time() - start_time
        
        total_time += exec_time
        max_time = max(max_time, exec_time)

        if output == expected_result:
            correct_tests += 1

    # Calculate accuracy and execution time stats
    accuracy = round((correct_tests / total_tests) * 100, 2)
    avg_time = round(total_time / total_tests, 6)

    print(f"✅ Accuracy: {accuracy}%")
    print(f"⏱️ Max Execution Time: {max_time} seconds")
    print(f"⏳ Average Execution Time: {avg_time} seconds")
