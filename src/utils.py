import re
import time

def resolve_abbreviations(text: str) -> str:
    text = text.lower()  # Convert input to lowercase first

    # Remove numbers appearing inside words (e.g., "Đị8nh" -> "Định", "N5am" -> "Nam")
    text = re.sub(r'(?<=[\wÀ-Ỹà-ỹ])\d+(?=[\wÀ-Ỹà-ỹ])', '', text, flags=re.UNICODE)

    MAPPING = {
        r'\bxã\b': ' xã ',
        r'\bhuyện\b': ' huyện ',
        r'\btỉnh\b': ' tỉnh ',
        r'\bphố\b': ' phố ',
        r'(\d)(?!\d)': r'\1 ',  # Ensure standalone digits are kept
        r'\bphường\b': ' ',
        r'\bthị trấn\b': ' ',
        r'\bquận\b': ' ',
        r'\bthị xã\b': ' ',
        r'\bthành phố\b': ' ',
        r'\bkhu phố\b': ' ',
        r'\btp\.\b': ' ',
        r'\bt\.p\b': ' ',
        r'\btp\b': ' ',
        r'0(?=[\dA-Za-z])': '',

        # Expand abbreviations to full province names
        r'\bt[.\s]*p[.\s]*h[.\s]*nội\b': ' Hà Nội ',
        r'\bhn\b': ' hà nội ',
        r'\bh.nội\b': ' hà nội ',
        r'\bt\.p h.nội\b': ' hà nội ',
        r'\bhnội\b': ' Hà Nội ',
        r'\bhcm\b': ' hồ chí minh ',
        r'\bsài gòn\b': ' hồ chí minh ',
        r'\btphcm\b': ' hồ chí minh ',
        r'\bt\.p hcm\b': ' hồ chí minh ',
        r'\bh\.c\.minh\b': ' Hồ Chí Minh ',
        r'\bt[.\s]?t[.\s]?h\b': ' thừa thiên huế ',
        r'\bthừa\.t\.huế\b': ' Thừa Thiên Huế ',
        r'\bthừa t huế\b': ' Thừa Thiên Huế ',
        r'\btth\b': ' thừa thiên huế ',

        r'\bt\.giang\b': ' tiền giang ',
        r'\bt\.ninh\b': ' tây ninh ',
        r'\bb\.liêu\b': ' bạc liêu ',
        r'\bh\.giang\b': ' hà giang ',
        r'\bh\.yên\b': ' hưng yên ',
        r'\bn\.an\b': ' nghệ an ',
        r'\bq\.nam\b': ' quảng nam ',
        r'\bq\.ninh\b': ' quảng ninh ',
        r'\bqninh\b': ' quảng ninh '
    }

    # Replace abbreviations
    for pattern, replacement in MAPPING.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\s,', ',', text)

    return text.lower()

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


def extend_trie_list(lookup_dict, lookup_dict_reverse, trie_list, prefix_list):

    for loc in lookup_dict.keys():
        for pre in prefix_list:
            loc_extend = remove_vietnamese_accents(pre + loc.lower().replace(" ", ""))
            loc_extend_en = remove_vietnamese_accents(pre+loc.lower().replace(" ",""))
            lookup_dict_reverse[loc_extend] = loc
            lookup_dict_reverse[loc_extend_en] = loc
            trie_list.append(loc_extend)
            trie_list.append(loc_extend_en)

    return lookup_dict_reverse, trie_list

def process_ref(file_path):
    locations = read_txt_file(file_path)
    location_lower_no_space = [w.replace(" ", "").lower() for w in locations]
    location_lower_no_space_en = [remove_vietnamese_accents(w) for w in location_lower_no_space]
    locations_lower_clean = [clean_location(w.lower()) for w in locations]
    locations_lower_clean_en = [remove_vietnamese_accents(w) for w in locations_lower_clean]
    location_clean_no_space = [location.replace(" ", "") for location in locations_lower_clean]
    location_clean_no_space_en = [remove_vietnamese_accents(w) for w in location_clean_no_space]

    reverse_location_lookup = {}
    location_lookup = {}

    for i in range(len(locations)):
        reverse_location_lookup[locations_lower_clean[i]] = locations[i]
        reverse_location_lookup[locations_lower_clean_en[i]] = locations[i]
        reverse_location_lookup[location_clean_no_space[i]] = locations[i]
        reverse_location_lookup[location_clean_no_space_en[i]] = locations[i]

        location_lookup[locations[i]] = []
        location_lookup[locations[i]].append(locations_lower_clean[i])
        location_lookup[locations[i]].append(locations_lower_clean_en[i])
        location_lookup[locations[i]].append(location_clean_no_space[i])
        location_lookup[locations[i]].append(location_clean_no_space_en[i])

    reverse_location_lookup[''] = ''

    trie_list = list(
        set(location_lower_no_space + location_lower_no_space_en + location_clean_no_space + location_clean_no_space_en))

    return location_lookup, reverse_location_lookup, trie_list, locations_lower_clean_en

def process_input_string(input_string, total_execution_time):
    start_time = time.time()
    cleaned_location = resolve_abbreviations(input_string)
    cleaned_location = re.sub(r"[.,\-!$?&@(){}|\\\[\]~]", " ", cleaned_location.lower())

    # List of prefixes to remove
    prefixes = ["phường", "xã", "thị xã", "thị trấn", "huyện", "thành phố", "tỉnh", "quận"]

    # Remove all occurrences of prefixes
    for word in prefixes:
        cleaned_location = cleaned_location.replace(word, "").strip()

    list_words_clean = [w for w in cleaned_location.split(" ") if w]
    # list_words_clean_en = [remove_vietnamese_accents(w) for w in list_words_clean]

    total_execution_time += time.time() - start_time

    return list_words_clean, total_execution_time


def find_ngrams(input_list, n):
    return [' '.join(gram) for gram in zip(*[input_list[i:] for i in range(n)])]