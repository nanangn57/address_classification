
def find_words_start_with(search_list, search_word: str):
    return [word for word in search_list if (search_word + " ") == word[:len(search_word)+1]]

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


def suggest_close_word(search_list, short_list_start, short_list_end, limit):
    close_word = ''
    target_used = ""

    min_edit = limit

    for target in search_list:
        for source in short_list_start:
            edit = min_edit_distance(source, target, ins_cost=1, del_cost=1, rep_cost=2)
            if edit <= min_edit:
                min_edit = edit
                close_word = source
                target_used = target

    # prioritize if matching first half, adding 1 to cost in edit 2nd half
    for target in search_list:
        for source in short_list_end:
            edit = min_edit_distance(source, target, ins_cost=1, del_cost=1, rep_cost=2)
            if edit + 1 < min_edit:
                min_edit = edit
                close_word = source
                target_used = target

    return close_word, target_used