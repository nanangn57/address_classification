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


