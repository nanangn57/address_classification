import os

files = ["list_province.txt", "list_district.txt", "list_ward.txt",
         "list_province.csv", "list_district.csv", "list_ward.csv", "list_full.csv"]

for file in files:
    print(f"{file}: {'✅ Tồn tại' if os.path.exists(file) else '❌ Không tồn tại'}")