import sys
import io


def run_case(input, exp_output, source_code, param_cnt):
    # exec(source_code)
    exec(source_code, globals())
    if param_cnt == 1:
        result = main_test(input[0])
    elif param_cnt == 2:
        result = main_test(input[0], input[1])
    if not isinstance(result, int):
        result = int(result)
    if not isinstance(exp_output, int):
        exp_output = int(exp_output)
    if result == exp_output:
        return 1
    else:
        return 0

