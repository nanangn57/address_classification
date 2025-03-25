import re

convert_vn_en = {
    'e': ['e', 'é', 'è', 'ẽ', 'ẹ', 'ẻ', 'ê', 'ế', 'ề', 'ễ', 'ệ', 'ể'],
    'o': ['o', 'ó', 'ò', 'õ', 'ọ', 'ỏ', 'ô', 'ố', 'ồ', 'ỗ', 'ộ', 'ổ', 'ơ', 'ớ', 'ờ', 'ỡ', 'ợ', 'ở'],
    'i': ['i', 'í', 'ì', 'ĩ', 'ị', 'ỉ'],
    'y': ['y', 'ý', 'ỳ', 'ỹ', 'ỵ', 'ỷ'],
    'a': ['a', 'á', 'à', 'ã', 'ạ', 'ả', 'ă', 'ắ', 'ằ', 'ẵ', 'ặ', 'ẳ', 'â', 'ấ', 'ầ', 'ẫ', 'ậ', 'ẩ'],
    'u': ['u', 'ú', 'ù', 'ũ', 'ụ', 'ủ', 'ư', 'ứ', 'ừ', 'ữ', 'ự', 'ử'],
    'd': ['đ']
}



def clean_input_search(input_string):
    cleaned_input = "".join(char.lower() for char in input_string if char not in ".,-!$?&@(){}|\\[]~")

    # List of prefixes to remove
    prefixes = ["phường", "xã", "thị xã", "thị trấn", "huyện", "thành phố", "tỉnh", "quận", "tp"]

    # Remove all occurrences of prefixes
    for word in prefixes:
        cleaned_input = cleaned_input.replace(word, "").strip()

    return cleaned_input.split()


def remove_vietnamese_accents(location):
    char_map = {v: k for k, values in convert_vn_en.items() for v in values}
    if not isinstance(location, str):  # Ensure it's a string
        return location  # Return unchanged if it's not a string
    else:
        return "".join(char_map.get(c, c) for c in location)
    
def remove_space(location):
    if not isinstance(location, str):  # Ensure it's a string
        return location  # Return unchanged if not a string
    else:
        return location.replace(" ", "")


def clean_location(location):
    if not isinstance(location, str):  # Ensure it's a string
        return location  # Return unchanged if not a string

    # Remove unwanted special characters
    cleaned_location = "".join(char.lower() for char in location if char not in ".,-!$?&@(){}|\\[]~")

    prefixes = ["phường", "xã", "thị xã", "thị trấn", 'huyện', 'thành phố', "tỉnh", "quận"]

    for prefix in prefixes:
        if cleaned_location.startswith(prefix):
            return cleaned_location[len(prefix):].lstrip()  # Remove prefix & keep original case

    return cleaned_location.lower()

def remove_special_characters(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '', text)



def process_ref(locations):
    for word in locations:
        value = locations['value']
        origin_word = locations['name']

        value = remove_vietnamese_accents(value.lower())
        value = remove_special_characters(value)

    trie_list = list(
        set(location_lower_no_space + location_lower_no_space_en + location_clean_no_space + location_clean_no_space_en))

    return trie_list

def process_input_string(input_string):
    cleaned_location = "".join(char.lower() if char not in ".,-!$?&@(){}|\\[]~" else " " for char in input_string)

    # List of prefixes to remove
    prefixes = ["phường", "xã", "thị xã", "thị trấn", "huyện", "thành phố", "tỉnh", "quận", "tp"]

    # Remove all occurrences of prefixes
    for word in prefixes:
        cleaned_location = cleaned_location.replace(word, "").strip()

    list_words_clean = [w for w in cleaned_location.split(" ") if w]
    list_words_clean_en = [remove_vietnamese_accents(w) for w in list_words_clean]

    return list_words_clean_en


def find_ngrams(input_list, n):
    return [' '.join(gram) for gram in zip(*[input_list[i:] for i in range(n)])]