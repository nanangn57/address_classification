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


def remove_special_characters(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '', text)
