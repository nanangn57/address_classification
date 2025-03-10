convert_vn_en = {
    'e': ['e', 'é', 'è', 'ẽ', 'ẹ', 'ẻ', 'ê', 'ế', 'ề', 'ễ', 'ệ', 'ể'],
    'o': ['o', 'ó', 'ò', 'õ', 'ọ', 'ỏ', 'ô', 'ố', 'ồ', 'ỗ', 'ộ', 'ổ', 'ơ', 'ớ', 'ờ', 'ỡ', 'ợ', 'ở'],
    'i': ['i', 'í', 'ì', 'ĩ', 'ị', 'ỉ'],
    'y': ['y', 'ý', 'ỳ', 'ỹ', 'ỵ', 'ỷ'],
    'a': ['a', 'á', 'à', 'ã', 'ạ', 'ả', 'ă', 'ắ', 'ằ', 'ẵ', 'ặ', 'ẳ', 'â', 'ấ', 'ầ', 'ẫ', 'ậ', 'ẩ'],
    'u': ['u', 'ú', 'ù', 'ũ', 'ụ', 'ủ', 'ư', 'ứ', 'ừ', 'ữ', 'ự', 'ử'],
    'd': ['đ']
}

def read_txt_file(filename):
    result = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            result.append(line.strip())  # Remove newline characters
    return result


def clean_location(location):
    if not isinstance(location, str):  # Ensure it's a string
        return location  # Return unchanged if not a string

    # Remove unwanted special characters
    cleaned_location = "".join(char.lower() for char in location if char not in ".,-!$?&@(){}|\\[]~")

    prefixes = ["phường", "xã", "thị xã", "thị trấn", 'huyện', 'thành phố', "tỉnh", "quận", "tp", "x"]

    for prefix in prefixes:
        if cleaned_location.startswith(prefix):
            return cleaned_location[len(prefix):].lstrip()  # Remove prefix & keep original case

    return cleaned_location.lower()



def remove_vietnamese_accents(location):
    char_map = {v: k for k, values in convert_vn_en.items() for v in values}
    if not isinstance(location, str):  # Ensure it's a string
        return location  # Return unchanged if it's not a string
    else:
        return "".join(char_map.get(c, c) for c in location)


def process_ref(file_path):
    locations =  read_txt_file(file_path)
    locations_lower_clean = [clean_location(w.lower()) for w in locations]
    locations_lower_clean_en = [remove_vietnamese_accents(w) for w in locations_lower_clean]
    return locations, locations_lower_clean, locations_lower_clean_en


def process_input_string(input_string):
    cleaned_location = "".join(char.lower() for char in input_string if char not in ".,-!$?&@(){}|\\[]~")

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


def remove_up_to(words, phrase):
    phrase_list = phrase.split()  # Convert phrase into a list of words

    for i in range(len(words) - len(phrase_list) + 1):
        if words[i:i+len(phrase_list)] == phrase_list:  # Match the full sequence
            return words[i+len(phrase_list):] # Keep only the part after the phrase

    return words  # Return original list if phrase not found


def search_loc(input_trie, input_list):
    output = ""
    n_gram = 1

    while n_gram < 3:
        list_search = find_ngrams(input_list, n_gram)
        for w in list_search:
            if input_trie.search(w):
                output = w
                break
        n_gram += 1

    return output


def remap_en_vn(word_input, list_en, list_vn):
    if len(word_input) > 0:
        return list_vn[list_en.index(word_input)]
    else:
        return word_input