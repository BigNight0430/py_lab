from quiz import load_input


def main_test(n):
    # Calculate the sum of the first n Fibonacci numbers
    if n <= 0:
        return 0
    elif n == 1:
        return 1

    a, b = 0, 1
    sum = 1  # Initialize sum with the first Fibonacci number
    for _ in range(2, n):
        a, b = b, a + b
        sum += b
    return sum


df, param_cnt = load_input(4)


# 程序主题
for i in df.index:
    output = main_test(df.at[i, "input1"])
    df.at[i, "output"] = output
df.to_excel("result.xlsx")

