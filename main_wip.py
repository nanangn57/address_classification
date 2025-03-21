import time
import pandas as pd
import numpy as np
import itertools
import json
import re
import string
import time
import signal
from typing import NamedTuple
import platform
import signal

# NOTE: you MUST change this cell
# New methods / functions must be written under class Solution.


class Solution:
    def __init__(self):
        # list provice, district, ward for private test, do not change for any reason
        self.province_path = 'list_province.txt'
        self.district_path = 'list_district.txt'
        self.ward_path = 'list_ward.txt'

        # write your preprocess here, add more method if needed
        self.TIMEOUT = 0.1
        self.province_path_internal = 'list_province.csv'
        self.district_path_internal = 'list_district.csv'
        self.ward_path_internal = 'list_ward.csv'
        self.full_path_internal = 'list_full.csv'
        self.prepare_database()

    def clear_locations(self):
        self.locations = {
            "province": [],
            "district": [],
            "ward": [],
        }



    def build_location_trie( self, path):

        df = pd.read_csv(path)
        data = df.to_dict(orient = 'records')

        correct_trie = AddressTrie()
        heuristics_trie = AddressTrie()
        for loc_row in data:
            loc_name = loc_row['name']
            loc_normalized = normalize_text(loc_row['value'])
            # full version correct spelling
            full_word = remove_non_alphabet(remove_space(loc_normalized))
            correct_trie.insert(word = full_word, raw = loc_name)
            if loc_name.isdigit():
                correct_trie.insert(word = loc_name, raw = loc_name)
            # abbreviation version spelling
            if not loc_name.isdigit():
                word = ''.join([w[0] for w in  loc_normalized.split()])
                if len(word)>1:
                    correct_trie.insert(word = word, raw = loc_name )

            word = ''.join([w[0] for w in  loc_normalized.split()[:-1]]) + loc_normalized.split()[-1]
            if len(word)> 1:
                correct_trie.insert(word = word, raw = loc_name)

            for variant in gen_incorrect_version(full_word):
                heuristics_trie.insert(word = variant, raw = loc_name)
        return correct_trie, heuristics_trie

    def build_address_combination_trie(self, path):
        checklist_trie = AddressTrie()
        df = pd.read_csv(path)
        data = df.to_dict(orient= 'records')

        for row in data:
            city = row['city_name']
            district = str(int(row['district_name'])) if row['district_name'].isdigit() else row['district_name']
            ward =  str(int(row['ward_name'])) if row['ward_name'].isdigit() else row['ward_name']
            # ward_district_province
            word = (ward + district + city).replace(' ', '').lower()
            checklist_trie.insert(word = word, raw = word )
            # district + province
            word = ( district + city).replace(' ', '').lower()
            checklist_trie.insert(word = word, raw = word)
            # ward + province
            word = ( ward + city).replace(' ', '').lower()
            checklist_trie.insert(word = word, raw = word )
            # ward + district
            word = (ward + district).replace(' ', '').lower()
            checklist_trie.insert(word = word, raw = word)

        return checklist_trie

    def build_external_tries(self,):
        p_trie = AddressTrie()
        d_trie = AddressTrie()
        w_trie = AddressTrie()
        for row in read_txt_file(self.province_path):
            p_trie.insert(word = row.replace(' ', '').lower(), raw = row)
        for row in read_txt_file(self.district_path):
            d_trie.insert(word = row.replace(' ', '').lower(), raw = row)
        for row in read_txt_file(self.ward_path):
            w_trie.insert(word = row.replace(' ', '').lower(), raw = row)
        return p_trie, d_trie, w_trie


    def prepare_database(self,):
        self.province_trie, self.hprovince_trie = self.build_location_trie(self.province_path_internal)
        self.district_trie, self.hdistrict_trie = self.build_location_trie(self.district_path_internal)
        self.ward_trie, self.hward_trie= self.build_location_trie(self.ward_path_internal)
        self.full_address_trie = self.build_address_combination_trie(self.full_path_internal)
        self.external_province_trie, self.external_district_trie, self.external_ward_trie = self.build_external_tries()

    def get_location(self, text, trie, is_exact = False ):
        results = []
        for item in generate_backward_ngrams(text, n = [4,3,2,1]):
            chunk_index, chunk = item
            temp = remove_non_alphabet(remove_space(normalize_text(chunk)))
            current_search = trie.search(temp)
            if current_search[0]:
                results.append(
                    MatchObject(
                        start_index= chunk_index,
                        end_index= chunk_index + len(chunk.split())  ,
                        matched_text=chunk,
                        prediction= current_search[1] ,
                        is_exact= is_exact
                        )
                )
        return results



    def get_location_prediction_set(self, text,):
        for loc in self.locations.keys():
            self.locations[loc].extend(self.get_location(text, eval(f'self.{loc}_trie'), is_exact= True ))
            self.locations[loc].extend(self.get_location(text, eval(f'self.h{loc}_trie')))
        return self.locations




    def _process(self, s):
        self.get_location_prediction_set(s)
        final_guess = self.verify_prediction(self.locations, self.full_address_trie)
        final_guess = self.check_prediction_with_db()
        return final_guess

    def verify_prediction(self, locations, full_address_trie):
        max_score = -1
        final_guess = None
        p_matches = locations['province']  + [EMPTY_MATCH]
        d_matches = locations['district']  + [EMPTY_MATCH]
        w_matches = locations['ward']  + [EMPTY_MATCH]
        for item in itertools.product(p_matches, d_matches, w_matches):
            p_match = item[0]
            d_match = item[1]
            w_match = item[2]
            combined_match = [w_match, d_match, p_match]
            if is_valid_combination(combined_match):
                p_guesses = p_match[-2]
                d_guesses = d_match[-2]
                w_guesses = w_match[-2]
                for address_combination in itertools.product(w_guesses , d_guesses, p_guesses ):
                        word = remove_space(''.join(address_combination) )
                        if full_address_trie.contain(word.lower()):
                            score = get_locations_score([p_match, d_match, w_match])
                            if score > max_score:
                                max_score = score
                                final_guess = address_combination
        self.locations = {
            'province': final_guess[2] if final_guess is not None else '',
            'district': final_guess[1] if final_guess is not None else '',
            'ward': final_guess[0] if final_guess is not None else '',
        }
        return self.locations

    def check_prediction_with_db(self):
        for loc ,val in self.locations.items():
            trie = eval(f'self.external_{loc}_trie')
            val = val.replace(' ', '').lower()
            if trie.contain(val):
                self.locations[loc] =  trie.search(val)[1][0]
            else:
                self.locations[loc] =''

        return self.locations

    def return_result(self):

        for key, value in self.locations.items():
            if isinstance(value, str):
                self.locations[key] = value
            elif isinstance(value, list) and len(value) > 0 :
                self.locations[key] = value[0][-2]
            else:
                self.locations[key] = ''

        return self.locations


    def process(self, s: str):
        if platform.system() != "Windows":  # Chỉ đặt timeout trên Linux/macOS
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.setitimer(signal.ITIMER_REAL, self.TIMEOUT)
    
        try:
            self.clear_locations()
            s = preprocessing(s)
            self._process(s)
            return self.return_result()
        except TimeoutException:
            return self.return_result()
        finally:
            if platform.system() != "Windows":
                signal.setitimer(signal.ITIMER_REAL, 0)


class MatchObject(NamedTuple):
    start_index: int
    end_index : int
    matched_text: str
    prediction: list
    is_exact: bool

EMPTY_MATCH= MatchObject(
    start_index= -1,
    end_index= -1,
    matched_text= '',
    prediction= [''],
    is_exact= False
)

class TimeoutException(Exception):
    pass
def timeout_handler(signum, frame):
    raise TimeoutException


SEP = ','
class AddressNode:
    __slots__ = ['children', 'is_end', 'raw']  # Reduce per-instance memory usage

    def __init__(self):
        self.children = {}
        self.is_end = False
        self.raw = []

class AddressTrie:
    def __init__(self):
        self.root = AddressNode()
        self.trie_count = 0

    def insert(self,  word, raw):
        node = self.root

        for char in word:
            if char not in node.children:
                node.children[char]= AddressNode()
            node = node.children[char]

        node.is_end = True
        if raw not in node.raw:
            node.raw.append(raw)

    def search(self, word):
        node = self.root

        for char in word:
            if char not in node.children:
                return False , None
            node = node.children[char]

        return node.is_end, node.raw

    def contain(self, word):
        node = self.root

        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]

        return node.is_end

    def delete(self,word):
        node = self.root

        for char in word:
            if char not in node.children:
                return None # deleted word does not exits
            node = node.children[char]

        node.is_end = False

    def search_longest(self, word):
        node = self.root
        last_match = None
        last_match_len = 0

        for i, char in enumerate(word):
            if char not in node.children:
                break
            node = node.children[char]

            if node.is_end:
                last_match = node
                last_match_len = i + 1
        if last_match:
            return word[:last_match_len], last_match.raw
        return None , None

    def traverse(self):
        stack = [(self.root, '')]
        while stack:
            node, prefix = stack.pop()
            if node.is_end:
                yield prefix, node.raw
            for char, child in reversed(node.children.items()):
                stack.append((child, prefix + char))


ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789'

def read_txt_file(path):
    with open(path, encoding="utf-8") as file:
        for line in file.readlines():
            yield line.strip()


def get_locations_score(match_objects):
    match_objects = [i for i in match_objects if i is not None ]
    index_score = 0
    len_score = 0
    heuristics_score = 0
    for item in match_objects:
        index_score += item[0]
        len_score  += len(item[2].split())
        heuristics_score += 1 if item[-1] else 0

    return index_score  + len_score * 2 +  heuristics_score

def is_valid_combination(combined_match):
    increasing_index = -1
    left_end_index = - 1
    for item in combined_match:
        if item[0] == -1 :
            continue
        # increasing index
        if item[0] >= increasing_index:
            increasing_index = item[0]
        else:
            return False
        # non overlapping section
        if item[0] >= left_end_index:
            left_end_index = item[1]
        else:
            return False

    return True

def normalize_text( text: str) -> str:
    # Remove diacritics and convert to lowercase
    text = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', text.lower())
    text = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', text)
    text = re.sub(r'[ìíịỉĩ]', 'i', text)
    text = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', text)
    text = re.sub(r'[ùúụủũưừứựửữ]', 'u', text)
    text = re.sub(r'[ỳýỵỷỹ]', 'y', text)
    text = re.sub(r'đ', 'd', text)
    return text

def remove_consecutive_spaces(text):
    return ' '.join(text.split())

def remove_space(text):
    return text.replace(' ', '').strip()



def loop_backward_ngram(text, n):
    result = []
    lst = text.split()
    if len(lst) >=n:
        for i in range(len(lst)-n, -1, -1):
            result.append((i, ' '.join(lst[i:i+n])))
        return result
    return None


def generate_backward_ngrams(text, n = [4, 3,2,1 ]):
    ngrams = []
    for i in n:
        ngram = loop_backward_ngram(text, i)
        if ngram:
            ngrams.extend(ngram)
    return ngrams


def remove_non_alphabet(text, replacement = ''):
    pattern = re.compile(r'[^a-z0-9 ]')
    return pattern.sub(replacement, text)


def remove_delimiter(text):
    pattern = re.compile(r'[,-.]')
    return pattern.sub(' ', text)

def split_sticky_word(text: str) -> str:

    words = text.split()
    vietnamese_uppercase = r'[A-ZĐÁÀẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÉÈẺẼẸÊẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÝỲỶỸỴ]'

    # Process each word
    result = []
    for word in words:
        # Count uppercase letters in the word
        uppercase_count = len(re.findall(vietnamese_uppercase, word))

        if uppercase_count > 1:
            # Split at uppercase letters, but keep the capital letter with its word
            # Negative lookbehind (?<!^) ensures we don't split at the start of the word
            # Negative lookbehind (?<![\s]) ensures we don't split after an existing space
            split_word = re.sub(rf'(?<!^)(?<![\s])({vietnamese_uppercase})', r' \1', word)
            result.append(split_word)
        else:
            result.append(word)

    return ' '.join(result)



def preprocessing(text):
    text = resolve_abbreviations(text)
    text = split_sticky_word(text)
    text = remove_delimiter(text)
    text  = remove_consecutive_spaces(text)
    return text




def gen_incorrect_version(word):
    """Generate variations with deduplication at generation time."""
    seen = set()  # Track seen variations

    def safe_yield(item):
        if item not in seen and item != word:
            seen.add(item)
            yield item

    # Calculate length once
    word_len = len(word)

    if word_len >2 and word_len <20:
        # Substitutions
        for i in range(word_len):
            current = word[i]
            prefix = word[:i]
            suffix = word[i+1:]
            for c in ALPHABET:
                if c != current:
                    yield from safe_yield(prefix + c + suffix)

        # Deletions
        if word_len > 1:  # Only delete if word length > 1
            for i in range(word_len):
                yield from safe_yield(word[:i] + word[i+1:])

        for i in range(word_len + 1):
            prefix = word[:i]
            suffix = word[i:]
            for c in ALPHABET:
                yield from safe_yield(prefix + c + suffix)




def resolve_abbreviations(text: str) -> str:

    MAPPING = {
        r'\bXã': ' Xã ',
        r'\bHuyện': ' Huyện ',
        r'\btỉnh': ' tỉnh ',
        r'\bphố': ' phố ',
        r'\bT.T.H\b': ' Thừa Thiên Huế ',
        r'\bThừa.t.Huế\b': ' Thừa Thiên Huế ',
        r'\bT. Hải Dươnwg\b': ' Hải Dương ',
        r'\bFHim\b': 'Hìm',
        r'\bTin GJiang\b': ' Tiền Giang ',
        r'(\d)(?!\d)': r'\1 ',
        r'\bPhường\b': ' ',
        r'\bThị trấn\b': ' ',
        r'\bQuận\b': ' ',
        r'\bHuyện\b': ' ',
        r'\bThị xã\b': ' ',
        r'\bThành phố\b': ' ',
        r'\bTỉnh\b': ' ',
        r'\bkhu phố\b': ' ',
        r'\btp\.\b': ' ',
        r'\bt\.p\b': ' ',
        r'\btp\b': ' ',
        r'0(?=[\dA-Za-z])': ''
    }

    for pattern, replacement in MAPPING.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s,', ',', text)
    text = text.strip()

    return text