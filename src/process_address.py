from src.trie import PrefixTree
import src.utils as u
import src.autocorrect as ac
import time

def initialize_trie(data_list):
    """Initialize a PrefixTree and insert data into it."""
    trie = PrefixTree()
    for item in data_list:
        trie.insert(item)
    return trie


def first_search_trie(clean_input, trie, look_up_dict, total_execution_time):
     # Start tracking execution time
    i = len(clean_input) - 1  # Start from the last index

    while i >= 0:
        start_time = time.time()
        if total_execution_time > 0.09:
            return "", total_execution_time   # Stop execution if time exceeds 0.099 seconds

        one_word = clean_input[i]

        if i - 1 >= 0:  # Check two-word combination
            two_word = "".join(clean_input[i - 1:i + 1])
            if trie.search(two_word):
                del clean_input[i - 1:i + 1]
                return look_up_dict.get(two_word, ""), total_execution_time

        if i - 2 >= 0:  # Check three-word combination
            three_word = "".join(clean_input[i - 2:i + 1])
            if trie.search(three_word):
                del clean_input[i - 2:i + 1]
                return look_up_dict.get(three_word, ""), total_execution_time

        if trie.search(one_word):  # Check single word
            word = clean_input.pop(i)
            return look_up_dict.get(word, ""), total_execution_time

        if i - 3 >= 0:  # Check 4-word combination
            four_word = "".join(clean_input[i - 3:i + 1])
            if trie.search(four_word):
                del clean_input[i - 3:i + 1]
                return look_up_dict.get(four_word, ""), total_execution_time

        i -= 1  # Move backward
        total_execution_time += (time.time() - start_time)

    return "", total_execution_time


def second_search(clean_input, source_ref, look_up_dict, total_execution_time):

    clean_input_en = [u.remove_vietnamese_accents(w) for w in clean_input]
    n2gram = u.find_ngrams(clean_input_en, 2)

    short_list_start = []
    for prefix in clean_input_en:
        start_time = time.time()
         # Stop if execution time exceeds limit
        short_list_start += ac.find_words_start_with(source_ref, prefix)
        total_execution_time += time.time() - start_time
        if total_execution_time > 0.07:
            return [], clean_input, total_execution_time

    short_list_end = []
    for suffix in clean_input_en:
        start_time = time.time()
        total_execution_time += (time.time() - start_time)
        short_list_end += ac.find_words_end_with(source_ref, suffix)

        total_execution_time += time.time() - start_time
        if total_execution_time > 0.07:
            return [], clean_input, total_execution_time


    suggested, target_used, total_execution_time = ac.suggest_close_word(n2gram, short_list_start, short_list_end, total_execution_time, limit=5)
    clean_input = [v for i, v in enumerate(clean_input) if clean_input_en[i] not in target_used.split()]

    return look_up_dict.get(suggested, ""), clean_input, total_execution_time


def initialize_dict_trie_search(ward_path, district_path, province_path):

    wards_lookup, wards_lookup_reverse, wards_trie_list, wards_clean_en = u.process_ref(ward_path)
    districts_lookup, districts_lookup_reverse, districts_trie_list, districts_clean_en = u.process_ref(district_path)
    provinces_lookup, provinces_lookup_reverse, provinces_trie_list, provinces_clean_en = u.process_ref(province_path)

    prefix_province = ["t", "tnh", "tỉnh", "tp", "p", "thphố", "thph", "phố", "thànhphố"]
    prefix_district = ["h", "thịtrấn", "thtrấn", "ttr", "tt", "thtr", 'huyện', "trấn"]
    prefix_ward = ["x", "xã"]

    provinces_lookup_reverse, provinces_trie_list = u.extend_trie_list(provinces_lookup, provinces_lookup_reverse,
                                                                       provinces_trie_list, prefix_province)
    districts_lookup_reverse, districts_trie_list = u.extend_trie_list(districts_lookup, districts_lookup_reverse,
                                                                       districts_trie_list, prefix_district)
    wards_lookup_reverse, wards_trie_list = u.extend_trie_list(wards_lookup, wards_lookup_reverse, wards_trie_list,
                                                               prefix_ward)

    # Initialize Trie structures
    wards_trie = initialize_trie(wards_trie_list)
    districts_trie = initialize_trie(districts_trie_list)
    provinces_trie = initialize_trie(provinces_trie_list)

    return [wards_trie, districts_trie, provinces_trie, provinces_clean_en, provinces_lookup_reverse,
            districts_clean_en, districts_lookup_reverse, wards_clean_en, wards_lookup_reverse]

def process_address(input_string, wards_trie, districts_trie, provinces_trie,
                    provinces_clean_en, provinces_lookup_reverse,
                    districts_clean_en, districts_lookup_reverse,
                    wards_clean_en, wards_lookup_reverse, total_execution_time):

    start_execution_time = time.time()

    clean_input, total_execution_time = u.process_input_string(input_string, total_execution_time)
    province_search, total_execution_time = first_search_trie(clean_input, provinces_trie,
                                                              provinces_lookup_reverse, total_execution_time)
    district_search, total_execution_time = first_search_trie(clean_input, districts_trie,
                                                              districts_lookup_reverse, total_execution_time)
    ward_search, total_execution_time = first_search_trie(clean_input, wards_trie,
                                                          wards_lookup_reverse, total_execution_time)

    if province_search == '' and total_execution_time < 0.05:
        province_search, clean_input, total_execution_time = second_search(clean_input, provinces_clean_en,
                                                                           provinces_lookup_reverse, total_execution_time)

    if district_search == '' and total_execution_time < 0.06:
        district_search, clean_input, total_execution_time = second_search(clean_input, districts_clean_en,
                                                                           districts_lookup_reverse, total_execution_time)

    if ward_search == '' and total_execution_time < 0.07:
        ward_search, clean_input, total_execution_time = second_search(clean_input, wards_clean_en,
                                                                       wards_lookup_reverse, total_execution_time)


    address = {
        "ward": ward_search,
        "district": district_search,
        "province": province_search
    }

    end_execution_time = time.time()
    execution_time = round(end_execution_time - start_execution_time, 6)

    return address, execution_time