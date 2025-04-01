from src.process_address import Solution
import json

# Load reference data
ward_path = 'data/list_wards.txt'
district_path = 'data/list_districts.txt'
province_path = 'data/list_provinces.txt'

ward_db_path = 'data/list_ward.csv'
district_db_path = 'data/list_district.csv'
province_db_path = 'data/list_province.csv'
full_address_db_path = 'data/list_full.csv'


# Run tests and measure max/average time
if __name__ == "__main__":

    # Load JSON data from file
    with open("data/public1.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract required fields into test_cases
    test_cases = [(item["text"], item["result"]["ward"], item["result"]["district"], item["result"]["province"]) for
                  item in data]

    # Iterate over test_cases
    total_time = 0
    max_time = 0
    correct_count = 0

    solution = Solution()

    for input_str, correct_ward, correct_district, correct_province in test_cases:
        predicted_address, exec_time = solution.process(input_str)
        total_time += exec_time
        max_time = max(max_time, exec_time)

        # if (predicted_address["ward"].strip() == correct_ward.strip() 
        #         predicted_address["district"].strip() == correct_district.strip() and
        #         predicted_address["province"].strip() == correct_province.strip()):
        #     correct_count += 1

        # else:
        #     print("wrong predicted test case----")
        #     print(input_str, exec_time)
        #     print(predicted_address["ward"], "---", correct_ward)
        #     print(predicted_address["district"], "---", correct_district)
        #     print(predicted_address["province"], "---", correct_province)

        #     print(predicted_address["ward"], "---", correct_ward)
        #     print(predicted_address["district"], "---", correct_district)
        if (predicted_address["province"].strip() == correct_province.strip()):
            correct_count += 1
        if (predicted_address["district"].strip() == correct_district.strip()):
            correct_count +=1
        if (predicted_address["ward"].strip() == correct_ward.strip()):
            correct_count +=1
        if (
                predicted_address["ward"].strip() != correct_ward.strip() or
                predicted_address["district"].strip() != correct_district.strip() or
                predicted_address["province"].strip() != correct_province.strip()):
            print(input_str, exec_time)
            print(predicted_address["ward"], "---", correct_ward)
            print(predicted_address["district"], "---", correct_district)
            print(predicted_address["province"], "---", correct_province ,"\n")

    accuracy = round(correct_count / len(test_cases * 3) * 100, 2)
    avg_time = round(total_time / len(test_cases), 6)

    print(f"✅ Accuracy: {accuracy}%")
    print(f"⏱️ Max Execution Time: {max_time} seconds")
    print(f"⏳ Average Execution Time: {avg_time} seconds")