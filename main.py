import src.utils as u
import src.process_address as pa

# Load reference data
ward_path = 'data/list_wards.txt'
district_path = 'data/list_districts.txt'
province_path = 'data/list_provinces.txt'


# Run tests and measure max/average time
if __name__ == "__main__":

    test_cases = []
    with open("test_cases.txt", "r", encoding="utf-8") as f:
        for line in f:
            input_str, correct_ward, correct_district, correct_province = line.strip().split("|")
            test_cases.append((input_str, correct_ward, correct_district, correct_province))

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
    avg_time = round(total_time / len(test_cases), 4)

    print(f"✅ Accuracy: {accuracy}%")
    print(f"⏱️ Max Execution Time: {max_time} seconds")
    print(f"⏳ Average Execution Time: {avg_time} seconds")