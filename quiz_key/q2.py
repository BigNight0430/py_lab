from quiz import load_input


def main_test(n):
    sum = 0
    for i in range(1, n+1):
        sum += i
    return sum


df, param_cnt = load_input(2)


# 程序主题
for i in df.index:
    output = main_test(df.at[i, "input1"])
    df.at[i, "output"] = output
df.to_excel("result.xlsx")




