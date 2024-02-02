import pandas as pd


def load_input(q_id):
    df = pd.read_excel("../quiz/" + str(q_id) + "/test.xlsx")
    input_cnt = len(df.columns) - 1
    return df, input_cnt


