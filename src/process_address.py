from src.trie import PrefixTree
import src.utils as u
import src.autocorrect as ac

def initialize_trie(data_list):
    """Initialize a PrefixTree and insert data into it."""
    trie = PrefixTree()
    for item in data_list:
        trie.insert(item)
    return trie


def first_search_trie(clean_input, trie):
    i = 0
    while i < len(clean_input):
        one_word = clean_input[i]
        if trie.search(one_word) or trie.search(u.remove_vietnamese_accents(one_word)):
            word = clean_input.pop(i)
            return word

        elif i + 1 < len(clean_input):
            two_word = "".join(clean_input[i:i + 2])
            if trie.search(two_word) or trie.search(u.remove_vietnamese_accents(two_word)):
                del clean_input[i:i + 2]
                return two_word


        elif i + 2 < len(clean_input):
            three_word = "".join(clean_input[i:i + 3])
            if trie.search(three_word) or trie.search(u.remove_vietnamese_accents(three_word)):
                del clean_input[i:i + 3]
                return three_word
        i += 1

    return "Unknown"


def second_search(clean_input, source_ref, source_trie):
    clean_input_en = [u.remove_vietnamese_accents(w) for w in clean_input]
    n2gram = u.find_ngrams(clean_input, 2)

    valid_prefix = []

    for w in clean_input:
        valid_prefix.append(source_trie.getprefixstring(w.replace(" ", "")))

    valid_substring = [u.remove_vietnamese_accents(p) for p in valid_prefix if len(p) >= 2]

    short_list_start = []
    for prefix in valid_substring:
        short_list_start += ac.find_words_start_with(source_ref, prefix)

    short_list_end = []
    for suffix in valid_substring:
        short_list_end += ac.find_words_end_with(source_ref, suffix)

    suggested, target_used = ac.suggest_close_word(n2gram, short_list_start, short_list_end, limit=5)

    clean_input = [v for i, v in enumerate(clean_input) if clean_input_en[i] not in target_used.split()]

    return suggested, clean_input


def process_address(input_string, ward_path, district_path, province_path):

    wards_lookup, wards_lookup_reverse, wards_trie_list, wards_clean_en = u.process_ref(ward_path)
    districts_lookup, districts_lookup_reverse, districts_trie_list, districts_clean_en = u.process_ref(district_path)
    provinces_lookup, provinces_lookup_reverse, provinces_trie_list, provinces_clean_en = u.process_ref(province_path)

    # Initialize Trie structures
    wards_trie = initialize_trie(wards_trie_list)
    districts_trie = initialize_trie(districts_trie_list)
    provinces_trie = initialize_trie(provinces_trie_list)

    """Process input string to extract address components."""
    start_time = __import__('time').time()

    clean_input = u.process_input_string(input_string)
    province_search = first_search_trie(clean_input, provinces_trie)
    if province_search == 'Unknown':
        province_search, clean_input = second_search(clean_input, provinces_clean_en, provinces_trie)

    ward_search = first_search_trie(clean_input, wards_trie)
    if ward_search == 'Unknown':
        ward_search, clean_input = second_search(clean_input, wards_clean_en, wards_trie)

    district_search = first_search_trie(clean_input, districts_trie)
    if district_search == 'Unknown':
        district_search, clean_input = second_search(clean_input, districts_clean_en, districts_trie)


    address = {
        "ward": wards_lookup_reverse.get(ward_search, 'Unknown'),
        "district": districts_lookup_reverse.get(district_search, 'Unknown'),
        "province": provinces_lookup_reverse.get(province_search, 'Unknown')
    }

    end_time = __import__('time').time()
    execution_time = round(end_time - start_time, 4)

    return address, execution_time