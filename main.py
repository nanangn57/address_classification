import src.utils as u
import src.process_address as pa

# Load reference data
ward_path = 'data/list_wards.txt'
district_path = 'data/list_districts.txt'
province_path = 'data/list_provinces.txt'


# Run tests and measure max/average time
if __name__ == "__main__":
    with open("test_cases.txt", "r", encoding="utf-8") as file:
        test_cases = file.readlines()

    execution_times = []
    results = []

    for test in test_cases:
        result, exec_time = pa.process_address(test, ward_path, district_path, province_path)
        execution_times.append(exec_time)
        results.append((test, result, exec_time))

    # Print results
    for test, result, exec_time in results:
        print(f"Input: {test}\nOutput: {result}\nExecution Time: {exec_time:.4f} seconds\n")

    # Calculate statistics
    max_time = max(execution_times)
    avg_time = sum(execution_times) / len(execution_times)

    print(f"Max Execution Time: {max_time:.4f} seconds")
    print(f"Average Execution Time: {avg_time:.4f} seconds")