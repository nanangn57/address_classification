from collections import defaultdict
from src.trie import PrefixTree
import src.utils as u
import src.autocorrect as ac
import pandas as pd
import re
import time

class Solution:
    def __init__(self):
        self.province_path = 'list_province.txt'
        self.district_path = 'list_district.txt'
        self.ward_path = 'list_ward.txt'


        ward_db_path = 'data/list_ward.csv'
        district_db_path = 'data/list_district.csv'
        province_db_path = 'data/list_province.csv'
        full_location_db_path = 'data/list_full.csv'

        # self.ward_trie = self.initialize_trie(ward_db_path)
        # self.district_trie= self.initialize_trie(district_db_path)
        # self.province_trie = self.initialize_trie(province_db_path)
        self.province_trie = self.initialize_trie(self.province_path)
        self.district_trie= self.initialize_trie(self.district_path)
        self.ward_trie = self.initialize_ward_trie(self.ward_path)
        self.full_norm_location, self.full_district_location, self.location_full_dict, self.location_province_ward_dict, self.location_district_ward_dict = self.init_full_address(full_location_db_path)

        self.official_district_lst =open(self.district_path).read().split('\n')
        self.official_province_lst = open(self.province_path).read().split('\n')
        self.official_ward_lst = open(self.ward_path).read().split('\n')

        # self.save_trie_to_file(self.ward_trie, 'ward_trie.txt')
        # self.save_trie_to_file(self.district_trie, 'district_trie.txt')
        # self.save_trie_to_file(self.province_trie, 'province_trie.txt')


    def init_full_address(self, db_path):
        pd_data = pd.read_csv(db_path)
        data_list = pd_data.to_dict('records')

        location_district_dict = defaultdict(lambda: defaultdict(list))
        location_norm_dict = defaultdict(lambda: defaultdict(list))
        location_full_dict = defaultdict(lambda: defaultdict(list))
        location_province_ward_dict = defaultdict(list)
        location_district_ward_dict = defaultdict(list)
        for data in data_list:
            province = data['city_name']
            district = data['district_name']
            ward = data['ward_name']
            district_norm = self.remove_vietnamese_accents(self.lower(data['district_name']))
            district_norm = self.remove_space(district_norm)
            district_norm = self.remove_special_characters(district_norm)
            ward_norm = self.remove_vietnamese_accents(self.lower(data['ward_name']))
            ward_norm = self.remove_space(ward_norm)
            ward_norm = self.remove_special_characters(ward_norm)
            location_district_dict[province][district_norm] = district
            if ward_norm not in location_norm_dict[province][district_norm]:
                location_norm_dict[province][district_norm].append(ward_norm)
            location_full_dict[province][district].append(ward)
            location_province_ward_dict[province].append(ward)
            location_district_ward_dict[district].append(ward)
        
        location_norm_dict = {province: dict(districts) for province, districts in location_norm_dict.items()}
        location_district_dict = {province: dict(districts) for province, districts in location_district_dict.items()}
        location_full_dict = {province: dict(districts) for province, districts in location_full_dict.items()}
        return location_norm_dict, location_district_dict, location_full_dict, location_province_ward_dict, location_district_ward_dict

    def search(self, input_text, trie):
        return trie.search(input_text)

    def remove_vietnamese_accents(self,location):
        char_map = {v: k for k, values in Solution.CONVERT_VN_EN.items() for v in values}
        if not isinstance(location, str):  # Ensure it's a string
            return location  # Return unchanged if it's not a string
        else:
            return "".join(char_map.get(c, c) for c in location)

    def remove_special_characters(self,text: str) -> str:
        return re.sub(r'[^a-z0-9]', '', text)

    def create_abbreviation(self,name: str) -> str:
        words = name.split()
        if not words:  
            return "", ""
        abbr_first = ''.join(word[0] for word in words)
        abbr_second = ''.join(word[0] for word in words[:-1]) + words[-1]
        return abbr_first, abbr_second

    def resolve_abbreviations(self, text: str) -> str:
        for pattern, replacement in Solution.MAPPING.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s,', ',', text)
        text = text.strip()

        return text
    
    def split_word(self, input_string):
        step1 = re.sub(r'(?<!^)(?=[A-Z])', ' ', input_string)
        step2 = re.sub(r'(?<=\D)(?=\d)', ' ', step1)
        step3 = re.sub(r'(?<=\d)(?=\D)', ' ', step2)

        return ' '.join(step3.split())

    def create_variations(self, word):
        variations = set()
        alphabet = Solution.ALPHANUMERIC  # Use the predefined alphanumeric set

        # Deletion: Remove one character at a time
        for i in range(len(word)):
            variations.add(word[:i] + word[i+1:])

        # Substitution: Replace each character with every letter in the alphabet
        for i in range(len(word)):
            for char in alphabet:
                if char != word[i]:  # Avoid replacing with the same character
                    variations.add(word[:i] + char + word[i+1:])

        # Insertion: Insert every letter of the alphabet at every position
        for i in range(len(word) + 1):
            for char in alphabet:
                variations.add(word[:i] + char + word[i:])

        return variations
    
    def initialize_ward_trie(self,data_path):
        # pd_data = pd.read_csv(data_path)
        # data_list = pd_data.to_dict('records')

        data_list = open(data_path).read().split('\n')
        data_list = [{"value": province, "name": province} for province in data_list]

        correctTrie = PrefixTree()
        """Initialize Trie"""
        for word in data_list:
            value = word['value']
            origin_word = word['name']
            value = self.pre_process(value)
            correctTrie.insert(value, origin_word)

            if not word['value'].isdigit():
                for false_value in self.create_variations(value):
                    correctTrie.insert(false_value, origin_word) 
        return correctTrie

    def initialize_trie(self,data_path):
        # pd_data = pd.read_csv(data_path)
        # data_list = pd_data.to_dict('records')

        data_list = open(data_path).read().split('\n')
        data_list = [{"value": province, "name": province} for province in data_list]

        correctTrie = PrefixTree()
        """Initialize Trie"""
        for word in data_list:
            value = word['value']
            origin_word = word['name']
            value = self.pre_process(value)
            correctTrie.insert(value, origin_word)

            if not word['value'].isdigit():
                abbr1, abbr2 = self.create_abbreviation(word['value'])
                abbr2 = self.pre_process(abbr2)
                correctTrie.insert(abbr2, origin_word)

                abbr1 = self.pre_process(abbr1)
                correctTrie.insert(abbr1, origin_word)

                for false_value in self.create_variations(value):
                    correctTrie.insert(false_value, origin_word) 
        return correctTrie

    def remove_space(self,word):
        return word.replace(" ", "")

    def lower(self,word):
        return word.lower()

    def reverse(self,word):
        return word[::-1]
    
    def pre_process(self,word):
        word = self.lower(word)
        word = u.remove_vietnamese_accents(word)
        word = self.remove_space(word)
        word = self.remove_special_characters(word)
        word = self.reverse(word)
        return word

    def search_province(self,input_str,used_time):
        """Search for a province in the trie."""
        if used_time > 0.09:
            return  "", 0
        max_len = min(len(input_str), 15)

        input_text = self.pre_process(input_str)

        true_word_lst = []
        search_text_lst = []

        city_time = time.time()
        for i in range(2, max_len):
            if (time.time() - city_time + used_time > 0.09):
                return "", 0
            
            search_text = input_text[:i]

            result, true_word = self.search(search_text,self.province_trie)
            if true_word is None:
                true_word = []
            elif len(true_word) == 1:
                true_word = true_word[0]
            else:
                best_true_word = ""
                min_score = 9999
                for t in true_word:
                    lower_true_word = self.remove_space(t.lower())
                    lower_input_str = self.remove_space(input_str.lower())
                    score = ac.min_edit_distance(lower_true_word[-i:], lower_input_str[-i:])
                    if score < min_score:
                        min_score = score
                        best_true_word = t
                true_word = best_true_word
            if result == True:
                true_word_lst.append(true_word)
                search_text_lst.append(search_text)
        if len(true_word_lst) > 0:
            best_true_word = ""
            min_score = 9999
            for candidate in set(true_word_lst):
                score = 0
                for part in search_text_lst:
                    score += ac.min_edit_distance(self.pre_process(candidate), part)
                if score < min_score:
                    min_score = score
                    best_true_word = candidate
                    len_true_word = len(part)
        else:
            best_true_word = ""
            len_true_word = 0

        if "-" in best_true_word:
            len_true_word += 3

        # print("best_true_word", best_true_word)
        # print("len_true_word", len_true_word)

        return best_true_word, len(best_true_word)
    
    def search_district(self,input_str,province,used_time):
        """Search for a district in the trie."""
        if used_time > 0.09:
            return  "", 0
        min_threshold = 0.29
        input_text = input_str.replace('Tnh', '').replace('Tinh', '').replace('tỉn', '').replace('Tỉn', '')
        input_text = self.resolve_abbreviations(input_text)
        input_text = self.lower(input_text)
        input_text = u.remove_vietnamese_accents(input_text)
        input_text = self.remove_space(input_text)
        input_text = self.remove_special_characters(input_text)
        
        max_len = min(len(input_text) + 1, 15 )

        district_time = time.time()
        if (province != ""):
            for i in range(1, max_len):
                if (time.time() - district_time + used_time > 0.5):
                    return False, "", 0

                search_text = input_text[-i:]
                if search_text == "":
                    continue

                for candidate in self.full_norm_location[province].keys():
                    if candidate in search_text and candidate.isdigit() == True:
                        if i + 1 <= len(input_text) and input_text[-i - 1].isdigit():
                            continue
                        return candidate, len(search_text)
                    score = ac.min_edit_distance(candidate, search_text)
                    if score < min_threshold*len(search_text):
                        if self.full_district_location[province][candidate] not in self.official_district_lst:
                            return "", 0
                        return self.full_district_location[province][candidate], len(self.full_district_location[province][candidate])
        else:
            input_text = self.pre_process(input_str)

            true_word_lst = []
            search_text_lst = []

            district_time = time.time()
            for i in range(1, max_len):
                if (time.time() - district_time + used_time > 0.09):
                    return "", 0
                
                search_text = input_text[:i]

                result, true_word = self.search(search_text,self.district_trie)
                if true_word is None:
                    true_word = []
                elif len(true_word) == 1:
                    true_word = true_word[0]
                else:
                    best_true_word = ""
                    min_score = 9999
                    for t in true_word:
                        lower_true_word = self.remove_space(t.lower())
                        lower_input_str = self.remove_space(input_str.lower())
                        score = ac.min_edit_distance(lower_true_word[-i:], lower_input_str[-i:])
                        if score < min_score:
                            min_score = score
                            best_true_word = t
                    true_word = best_true_word
                if result == True:
                    true_word_lst.append(true_word)
                    search_text_lst.append(search_text)
            if len(true_word_lst) > 0:
                best_true_word = ""
                min_score = 9999
                for candidate in set(true_word_lst):
                    score = 0
                    for part in search_text_lst:
                        score += ac.min_edit_distance(candidate, part)
                    if score < min_score:
                        min_score = score
                        best_true_word = candidate
                        len_true_word = len(part)
            else:
                best_true_word = ""
                len_true_word = 0

            # print("best_true_word", best_true_word)
            # print("len_true_word", len_true_word)

            return best_true_word, len_true_word

        return "", 0  
    
    def search_ward(self,input_str,province,district,used_time,min_threshold = 0.29):
        results = list(dict())
        input_text = self.split_word(input_str)
        ward_time = time.time()
        best_len = 0
        for item in self.generate_backward_ngrams(input_text, n = [4,3,2,1]):
            if (time.time() - ward_time + used_time > 0.09):
                    return "", 0

            chunk_index, chunk = item
            temp = self.pre_process(chunk)
            result, origin_word = self.search(temp, self.ward_trie)
            if result:
                results.append(
                    {
                        "start_index": chunk_index,
                        "end_index": chunk_index + len(chunk.split()),
                        "matched_text": chunk,
                        "prediction": origin_word,
                        "is_exact": True
                    }
                )
        
        if (province != "" and district != ""):
            min_score = 9999
            best_ward = ""
            for ward in results:
                if (time.time() - ward_time + used_time > 0.09):
                    return "", 0
                for _ward in ward["prediction"]:
                    if (time.time() - ward_time + used_time > 0.09):
                        return "", 0
                    if _ward not in self.location_full_dict[province][district]:
                        continue
                    score = ac.min_edit_distance(ward["matched_text"], _ward)
                    if score < min_score:
                        min_score = score
                        best_ward = _ward
            return best_ward, len(best_ward)
            
        elif (province != ""):
            min_score = 9999
            best_ward = ""
            for ward in results:
                if (time.time() - ward_time + used_time > 0.09):
                    return "", 0
                for _ward in ward["prediction"]:
                    if (time.time() - ward_time + used_time > 0.09):
                        return "", 0
                    if _ward not in self.location_province_ward_dict[province]:
                        continue
                    score = ac.min_edit_distance(ward["matched_text"], _ward)
                    if score < min_score:
                        min_score = score
                        best_ward = _ward
            return best_ward, len(best_ward)
        elif (district != ""):
            min_score = 9999
            best_ward = ""
            for ward in results:
                # if (time.time() - ward_time + used_time > 0.09):
                #     return "", 0
                for _ward in ward["prediction"]:
                    # if (time.time() - ward_time + used_time > 0.09):
                    #     return "", 0
                    if _ward not in self.location_district_ward_dict[district]:
                        continue
                    score = ac.min_edit_distance(ward["matched_text"], _ward)
                    if score < min_score:
                        min_score = score
                        best_ward = _ward
            return best_ward, len(best_ward)
        else:
            min_score = 9999
            best_ward = ""
            for _ward in ward["prediction"]:
                if (time.time() - ward_time + used_time > 0.09):
                    return "", 0
                score = ac.min_edit_distance(ward["matched_text"], ward["prediction"])
                if score < len(ward["matched_text"].lower())*min_threshold:
                    min_score = score
                    best_ward = _ward
            return best_ward, len(best_ward)



    def loop_backward_ngram(self, text, n):
        result = []
        lst = text.split()
        if len(lst) >=n:
            for i in range(len(lst)-n, -1, -1):
                result.append((i, ' '.join(lst[i:i+n])))
            return result
        return None

    def generate_backward_ngrams(self, text, n = [4, 3,2,1 ]):
        ngrams = []
        for i in n:
            ngram = self.loop_backward_ngram(text, i)
            if ngram:
                ngrams.extend(ngram)
        return ngrams
    
    
    def process(self,input_string):

        """Process input string to extract address components."""
        start_time = time.time()

        # input_string = unicodedata.normalize("NFC", input_string)
        input_string = self.resolve_abbreviations(input_string)

        final_candidate, len_remove_province = self.search_province(input_string,used_time=time.time() - start_time)
        province = final_candidate

        new_input_string = input_string[:-len_remove_province] if len_remove_province > 0 else input_string
        final_candidate, len_remove_district = self.search_district(new_input_string, province, used_time=time.time() - start_time)
        district = final_candidate

        new_input_string = new_input_string[:-len_remove_district] if len_remove_district > 0 else new_input_string
        final_candidate, len_remove = self.search_ward(new_input_string, province, district, used_time=time.time() - start_time)
        ward = final_candidate

        if province not in self.official_province_lst:
            province = ""
        if district not in self.official_district_lst:
            district = ""
        if ward not in self.official_ward_lst:
            ward = ""

        address = {
            "ward": ward,
            "district": district,
            "province": province
        }

        end_time = time.time()
        execution_time = round(end_time - start_time, 6)

        return address, execution_time
    

    CONVERT_VN_EN = {
        'e': ['e', 'é', 'è', 'ẽ', 'ẹ', 'ẻ', 'ê', 'ế', 'ề', 'ễ', 'ệ', 'ể'],
        'o': ['o', 'ó', 'ò', 'õ', 'ọ', 'ỏ', 'ô', 'ố', 'ồ', 'ỗ', 'ộ', 'ổ', 'ơ', 'ớ', 'ờ', 'ỡ', 'ợ', 'ở'],
        'i': ['i', 'í', 'ì', 'ĩ', 'ị', 'ỉ'],
        'y': ['y', 'ý', 'ỳ', 'ỹ', 'ỵ', 'ỷ'],
        'a': ['a', 'á', 'à', 'ã', 'ạ', 'ả', 'ă', 'ắ', 'ằ', 'ẵ', 'ặ', 'ẳ', 'â', 'ấ', 'ầ', 'ẫ', 'ậ', 'ẩ'],
        'u': ['u', 'ú', 'ù', 'ũ', 'ụ', 'ủ', 'ư', 'ứ', 'ừ', 'ữ', 'ự', 'ử'],
        'd': ['đ']
    }

    ALPHANUMERIC = "abcdefghijklmnopqrstuvwxyz0123456789"

    MAPPING = {
        r'\bXã': ' ',
        r'\bHuyện': ' ',
        r'\btỉnh': ' ',
        r'Tỉnwh\b': ' ',
        r'\bTỉnwh\b': ' ',
        r'\bTỉnwh': ' ',
        r'\bTP.HCM\b': ' Hồ Chí Minh ',
        r'\bTPHCM\b': ' Hồ Chí Minh ',
        r'\bT.P H.C.Minh\b': ' Hồ Chí Minh ',
        r'\bTP. HCM\b': ' Hồ Chí Minh ',
        r'\bT.T.H\b': ' Thừa Thiên Huế ',
        r'\bThừa.t.Huế\b': ' Thừa Thiên Huế ',
        r'\bT Quảyg Nm\b': ' Quảng Nam ',
        r'\bTQdung trị\b': ' Quảng Trị ',
        r'\bFHim\b': 'Hìm',
        r'\bTin GJiang\b': ' Tiền Giang ',
        r'\bT.Giang\b': ' Tiền Giang ',
        r'\bTGiang\b': ' Tiền Giang ',
        r'\bThành phố': ' ',
        r'\bthành phố': ' ',
        r'\bthành phô': ' ',
        r'\bThành phô': ' ',
        r'\bThành Phố': ' ',
        r'\bThành Phô': ' ',
        r'\bThành phố\b': ' ',
        r'\bPhường\b': ' ',
        r'\bThị trấn\b': ' ',
        r'\bQuận\b': ' ',
        r'\bHuyện\b': ' ',
        r'\bThị xã\b': ' ',
        r'\bTỉnh\b': ' ',
        r'\btỉnh\b': ' ',
        r'\bquận\b': ' ',
        r'\bhuyện\b': ' ',
        r'\bthị xã\b': ' ',
        r'\bphường\b': ' ',
        r'\bthị trấn\b': ' ',
        r'\btỉ,nh': ' ',
        r'\bt,ỉnh': ' ',
        r'\bxã\b': ' ',
        r'\bx,ã\b': ' ',
        r'\bx.ã\b': ' ',
        r'\bkhu phố\b': ' ',
        r'\bk.hu phố\b': ' ',
        r'\btp\.\b': ' ',
        r'\bt\.p\b': ' ',
        r'\btp\b': ' ',
    }

    

    def save_trie_to_file(self, trie, file_path):
        """Save all words in the trie to a text file."""
        def traverse(node, prefix, file):
            if node.end:  # Check if the current node marks the end of a word
                file.write(prefix + '\n')  # Write the word to the file
            for char, child_node in node.children.items():
                traverse(child_node, prefix + char, file)

        with open(file_path, 'w') as file:  # Open the file in write mode
            traverse(trie.root, "", file)

    # Example usage
    # Assuming `correctTrie` is an instance of PrefixTree
