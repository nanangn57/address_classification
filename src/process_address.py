from src.trie import PrefixTree
import src.utils as u
import src.autocorrect as ac

def initialize_trie(data_list):
    """Initialize a PrefixTree and insert data into it."""
    trie = PrefixTree()
    for item in data_list:
        trie.insert(item)
    return trie


def process_address(input_string, ward_path, district_path, province_path):

    wards, wards_clean, wards_clean_en = u.process_ref(ward_path)
    districts, districts_clean, districts_clean_en = u.process_ref(district_path)
    provinces, provinces_clean, provinces_clean_en = u.process_ref(province_path)

    # Initialize Trie structures
    ward_trie = initialize_trie(wards_clean_en)
    district_trie = initialize_trie(districts_clean_en)
    province_trie = initialize_trie(provinces_clean_en)

    """Process input string to extract address components."""
    start_time = __import__('time').time()
    input_clean = u.process_input_string(input_string)

    # Search for ward
    ward_search_len = int(len(input_clean)/2.5) # only limit first half for ward search
    search_ward = input_clean[:ward_search_len]
    ward = u.search_loc(ward_trie, search_ward)
    input_clean = u.remove_up_to(input_clean, ward)

    if not ward:
        search_list = search_ward
        search_list_2gram = u.find_ngrams(search_list, 2)
        ward, target_used = ac.suggest_close_word(search_list, search_list_2gram, wards_clean_en, 5)
        input_clean = u.remove_up_to(input_clean, target_used)

    # Search for district
    district = u.search_loc(district_trie, input_clean)
    input_clean = u.remove_up_to(input_clean, district)

    if not district:
        search_list = input_clean[:-2] # leave out ~2 characters for district search
        search_list_2gram = u.find_ngrams(search_list, 2)
        district, target_used = ac.suggest_close_word(search_list, search_list_2gram, districts_clean_en, 5)
        input_clean = u.remove_up_to(input_clean, target_used)

    # Search for province
    province = u.search_loc(province_trie, input_clean)
    input_clean = u.remove_up_to(input_clean, district)

    if not province:
        search_list_2gram = u.find_ngrams(input_clean, 2)
        province, target_used = ac.suggest_close_word(input_clean, search_list_2gram, provinces_clean_en, 5)

    address = {
        "ward": u.remap_en_vn(ward, wards_clean_en, wards),
        "district": u.remap_en_vn(district, districts_clean_en, districts),
        "province": u.remap_en_vn(province, provinces_clean_en, provinces),
    }

    end_time = __import__('time').time()
    execution_time = round(end_time - start_time, 4)

    return address, execution_time