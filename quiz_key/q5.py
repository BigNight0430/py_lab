from quiz import load_input


def main_test(n):
    if n <= 0:
        return "Input should be a positive integer"
    elif n == 1 or n == 2:
        return 2
    else:
        a, b = 2, 2
        for i in range(3, n + 1):
            a, b = b, a + b
        return b


df, param_cnt = load_input(5)


# 程序主题
for i in df.index:
    output = main_test(df.at[i, "input1"])
    df.at[i, "output"] = output
df.to_excel("result.xlsx")

