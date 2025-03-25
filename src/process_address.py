from src.trie import PrefixTree
import src.utils as u
import src.autocorrect as ac
import pandas as pd
import re

def remove_vietnamese_accents(location):
    char_map = {v: k for k, values in convert_vn_en.items() for v in values}
    if not isinstance(location, str):  # Ensure it's a string
        return location  # Return unchanged if it's not a string
    else:
        return "".join(char_map.get(c, c) for c in location)

def remove_special_characters(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '', text)

def create_abbreviation(name: str) -> str:
    words = name.split()
    abbr_first = ''.join(word[0] for word in words)
    abbr_second = ''.join(word[0] for word in words[:-1]) + words[-1]
    return abbr_first, abbr_second

def create_false_version(word):
    """Generate variations with deduplication at generation time."""
    seen = set()  # Track seen variations

    def safe_yield(item):
        if item not in seen and item != word:
            seen.add(item)
            yield item

    # Calculate length once
    word_len = len(word)

    if 2 < word_len < 20:
        # Substitutions
        for i in range(word_len):
            current = word[i]
            prefix = word[:i]
            suffix = word[i+1:]
            for c in ALPHANUMERIC:
                if c != current:
                    yield from safe_yield(prefix + c + suffix)

        # Deletions
        if word_len > 1:  # Only delete if word length > 1
            for i in range(word_len):
                yield from safe_yield(word[:i] + word[i+1:])

        # Insertions
        for i in range(word_len + 1):
            prefix = word[:i]
            suffix = word[i:]
            for c in ALPHANUMERIC:
                yield from safe_yield(prefix + c + suffix)

def initialize_trie(data_list):
    pd_data = pd.read_csv(data_list)
    data_list = pd_data.to_dict('records')

    correctTrie = PrefixTree()
    falseTrie = PrefixTree()
    """Initialize Trie"""
    for word in data_list:
        value = word['value']
        origin_word = word['name']
        value = remove_vietnamese_accents(value.lower())
        value = remove_special_characters(value)

        correctTrie.insert(value, origin_word)
        if origin_word.isdigit():
            correctTrie.insert(value, origin_word)

        if not origin_word.isdigit():
            first_abbr, second_abbr = create_abbreviation(origin_word)
            if len(origin_word) > 1:
                correctTrie.insert(first_abbr, origin_word)
                correctTrie.insert(second_abbr, origin_word)
        
        for false_value in create_false_version(value):
            falseTrie.insert(false_value, origin_word)

    return correctTrie, falseTrie


def process_address(input_string, ward_path, district_path, province_path, full_address_path):

    # Initialize Trie structures
    wards_trie, f_wards_trie = initialize_trie(ward_path)
    districts_trie, f_districts_trie = initialize_trie(district_path)
    provinces_trie, f_provinces_trie = initialize_trie(province_path)
    full_address_trie, f_full_address_trie = initialize_trie(full_address_path)

    """Process input string to extract address components."""
    start_time = __import__('time').time()


    address = {
        "ward": '',
        "district": '',
        "province": ''
    }

    end_time = __import__('time').time()
    execution_time = round(end_time - start_time, 6)

    return address, execution_time


convert_vn_en = {
    'e': ['e', 'é', 'è', 'ẽ', 'ẹ', 'ẻ', 'ê', 'ế', 'ề', 'ễ', 'ệ', 'ể'],
    'o': ['o', 'ó', 'ò', 'õ', 'ọ', 'ỏ', 'ô', 'ố', 'ồ', 'ỗ', 'ộ', 'ổ', 'ơ', 'ớ', 'ờ', 'ỡ', 'ợ', 'ở'],
    'i': ['i', 'í', 'ì', 'ĩ', 'ị', 'ỉ'],
    'y': ['y', 'ý', 'ỳ', 'ỹ', 'ỵ', 'ỷ'],
    'a': ['a', 'á', 'à', 'ã', 'ạ', 'ả', 'ă', 'ắ', 'ằ', 'ẵ', 'ặ', 'ẳ', 'â', 'ấ', 'ầ', 'ẫ', 'ậ', 'ẩ'],
    'u': ['u', 'ú', 'ù', 'ũ', 'ụ', 'ủ', 'ư', 'ứ', 'ừ', 'ữ', 'ự', 'ử'],
    'd': ['đ']
}

ALPHANUMERIC = "abcdefghijklmnopqrstuvwxyz0123456789"