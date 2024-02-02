from quiz import load_input


def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)


def main_test(n):
    if n < 0:
        return "Input should be a non-negative integer"
    sum = 0
    for i in range(1, n + 1):
        sum += factorial(i)
    return sum


df, param_cnt = load_input(6)


# 程序主题
for i in df.index:
    output = main_test(df.at[i, "input1"])
    df.at[i, "output"] = output
df.to_excel("result.xlsx")

