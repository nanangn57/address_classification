
def find_words_start_with(search_list, search_word: str):
    return [word for word in search_list if (search_word+" ") == word[:len(search_word)+1]]

def find_words_end_with(search_list, search_word: str):
    return [word for word in search_list if search_word == word[-len(search_word):]]

def min_edit_distance(source, target, ins_cost=1, del_cost=1, rep_cost=2):

    med = 0
    m = len(source)
    n = len(target)
    D = [[0] * (n + 1) for _ in range(m + 1)]

    for row in range(1, m + 1):
        D[row][0] = D[row - 1][0] + del_cost

    for col in range(1, n + 1):
        D[0][col] = D[0][col - 1] + ins_cost

    for row in range(1, m + 1):
        for col in range(1, n + 1):
            r_cost = rep_cost

            if source[row - 1] == target[col - 1]:
                r_cost = 0

            D[row][col] = min(D[row - 1][col] + del_cost, D[row][col - 1] + ins_cost, D[row - 1][col - 1] + r_cost)

        med = D[m][n]

    return med


def suggest_close_word(search_list, search_list_ngram, ref_source, limit):
    close_word = ""
    target_used = ""
    short_list_start = []
    short_list_end = []

    for w in search_list:
        short_list_start += find_words_start_with(ref_source, w)
        short_list_end += find_words_end_with(ref_source, w)

    min_edit = 1000

    for target in search_list_ngram:
        for source in short_list_start:
            edit = min_edit_distance(source, target, ins_cost=1, del_cost=1, rep_cost=2)
            if edit <= min_edit:
                min_edit = edit
                close_word = source
                target_used = target

    # prioritize if matching first half, adding 1 to cost in edit 2nd half
    for target in search_list_ngram:
        for source in short_list_end:
            edit = min_edit_distance(source, target, ins_cost=1, del_cost=1, rep_cost=2)
            if edit + 1 < min_edit:
                min_edit = edit
                close_word = source
                target_used = target

    if min_edit > limit:
        target_used = ""
        close_word = ""

    return close_word, target_used