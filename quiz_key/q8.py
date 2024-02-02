from quiz import load_input


def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


def main_test(n):
    sum_of_primes = 0
    for i in range(2, n + 1):
        if is_prime(i):
            sum_of_primes += i
    return sum_of_primes


df, param_cnt = load_input(8)


# 程序主题
for i in df.index:
    output = main_test(df.at[i, "input1"])
    df.at[i, "output"] = output
df.to_excel("result.xlsx")

