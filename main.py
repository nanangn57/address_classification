import src.process_address as pa
import json

# Load reference data
ward_path = 'data/list_wards.txt'
district_path = 'data/list_districts.txt'
province_path = 'data/list_provinces.txt'


# Run tests and measure max/average time
if __name__ == "__main__":

    # Load JSON data from file
    with open("data/public.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract required fields into test_cases
    test_cases = [(item["text"], item["result"]["ward"], item["result"]["district"], item["result"]["province"]) for
                  item in data]

    # Iterate over test_cases
    total_time = 0
    max_time = 0
    correct_count = 0

    for input_str, correct_ward, correct_district, correct_province in test_cases:
        predicted_address, exec_time = pa.process_address(input_str, ward_path, district_path, province_path)
        total_time += exec_time
        max_time = max(max_time, exec_time)

        if (predicted_address["ward"].strip() == correct_ward.strip() and
                predicted_address["district"].strip() == correct_district.strip() and
                predicted_address["province"].strip() == correct_province.strip()):
            correct_count += 1

        else:
            print("wrong predicted test case----")
            print(input_str, exec_time)
            print(predicted_address["ward"], "---", correct_ward)
            print(predicted_address["district"], "---", correct_district)
            print(predicted_address["province"], "---", correct_province)

    accuracy = round(correct_count / len(test_cases) * 100, 2)
    avg_time = round(total_time / len(test_cases), 6)

    print(f"✅ Accuracy: {accuracy}%")
    print(f"⏱️ Max Execution Time: {max_time} seconds")
    print(f"⏳ Average Execution Time: {avg_time} seconds")