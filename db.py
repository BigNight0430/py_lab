import copy
import pymysql
import xlrd
import time
import pandas as pd

from exec_py import run_case


# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'CU202056',
    'db': 'py_lab',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


# 数据库连接函数
def get_db_connection():
    return pymysql.connect(**db_config)


def validate_credentials(username, password, action):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if action == "学生登录":
                sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            else:
                sql = "SELECT * FROM admin_users WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            result = cursor.fetchone()
    finally:
        connection.close()
    return result


def calculate_score(student_answer, question_id):
    df = pd.read_excel("./quiz/" + str(question_id) + "/test.xlsx")
    rst_lst = []
    param_cnt = len(df.columns) - 1
    start_time = time.time()
    for i in df.index:
        input = []
        output = None
        for c in df.columns:
            if c == "output":
                output = df.at[i, c]
            else:
                input.append(df.at[i, c])
        rst = run_case(input, output, student_answer, param_cnt)
        rst_lst.append(rst)
    # 记录结束时间
    end_time = time.time()
    # 计算所需的总时间，并将秒转换为毫秒
    total_time = (end_time - start_time) * 1000  # 转换为毫秒
    score = sum(rst_lst) / len(rst_lst) * 100
    # 将分数存入数据库。
    return score, total_time


def get_question_by_id(q_id):
    desc = ("你需要编写一个名为main_test函数，该函数必须按照[提示1]来确定输入参数的个数，并在计算结果后，以函数返回值方式传回答案。\n"
            "举例，如果你想实现一个加法计算器，可以在文本框内输入下面的代码：\n\n"
            "def main_test(x1, x2):\n"
            "\treturn x1+x2\n")
    # 打开Excel文件
    workbook = xlrd.open_workbook('quiz/quiz.xls')
    sheet = workbook.sheet_by_index(0)
    # 题目号范围检查
    if q_id > sheet.nrows:
        assert False
    else:
        cols = sheet.row_values(q_id)
        info = {"title": cols[1], "description1": cols[2], "description2": desc, "id": q_id}
        return info


def write_score_to_sql(username, question_id, score, time_used):
    # 连接到数据库
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            # SQL 插入语句
            sql = """
            INSERT INTO user_scores (username, question_id, score, time_used)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE score = %s, time_used = %s;
            """
            # 执行SQL语句
            cursor.execute(sql, (username, question_id, score, time_used, score, time_used))

        # 提交到数据库执行
        connection.commit()

    finally:
        # 关闭数据库连接
        connection.close()


def get_history_score(username):
    # 连接到数据库
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            # SQL 查询语句
            sql = "SELECT * FROM user_scores WHERE username = %s"
            cursor.execute(sql, (username,))

            # 获取查询结果
            results = cursor.fetchall()
            score_dict = {}
            for score in results:
                score_dict[score['question_id']] = {"score": score["score"], "timestamp": score["timestamp"],
                                                    "time_used": score["time_used"], }
    finally:
        # 关闭数据库连接
        connection.close()

    return score_dict


def set_password(username, password):
    # 连接到数据库
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            # 安全地更新密码，使用哈希处理新密码
            # 以下是使用bcrypt库的示例，您可能需要根据实际情况进行调整
            # import bcrypt
            # hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            # sql = "UPDATE admin_users SET password = %s WHERE username = %s"
            # cursor.execute(sql, (hashed_password, username))

            # 如果您未使用bcrypt，只是简单的示例（不推荐用于生产环境）
            sql = "UPDATE users SET password = %s WHERE username = %s"
            cursor.execute(sql, (password, username))

        # 提交更改
        connection.commit()
    finally:
        # 关闭数据库连接
        connection.close()


# 用excel批量加入新用户。
def set_user(file):
    df = pd.read_excel(file)
    for i in df.index:
        username = df.at[i, "姓名"]
        stu_id = df.at[i, "学号"]
        if not isinstance(stu_id, str):
            stu_id_str = str(stu_id)
        else:
            stu_id_str = stu_id
        password = stu_id_str[-4:]
        # 连接到数据库
        connection = get_db_connection()

        try:
            with connection.cursor() as cursor:
                # SQL 插入语句
                sql = """
                    INSERT INTO users (username, id, password)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE username = %s, password = %s;
                    """
                # 执行SQL语句
                cursor.execute(sql, (username, stu_id, password, username, password))

            # 提交到数据库执行
            connection.commit()

        finally:
            # 关闭数据库连接
            connection.close()


def delete_all_users():
    # 连接到数据库
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            sql = """SET SQL_SAFE_UPDATES = 0;"""
            cursor.execute(sql)
            sql = """DELETE FROM users;"""
            cursor.execute(sql)

        # 提交到数据库执行
        connection.commit()

    finally:
        # 关闭数据库连接
        connection.close()


def get_class_data():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # SQL查询语句
            sql = "SELECT username, question_id, score, timestamp, time_used FROM user_scores"
            cursor.execute(sql)
            rows = cursor.fetchall()
    finally:
        connection.close()
    # 转换为DataFrame
    df = pd.DataFrame(rows, columns=['username', 'question_id', 'score', 'timestamp', 'time_used'])
    df = copy.deepcopy(df[df["score"] > 0])
    df.dropna(inplace=True)
    # 补充两个检查：（1）不显示姓名，只显示学号。（2）用户名不在users表中的不显示。
    user_lst = get_all_users()
    user_df = pd.DataFrame(user_lst)
    user_df.set_index(user_df["username"], inplace=True)
    # 剔除姓名不在数据库里的所有记录。
    for i in df.index:
        if df.at[i, "username"] in user_df["username"]:
            df.at[i, "del"] = "*"
    df = copy.deepcopy(df[df["del"] == "*"])
    df_grp = df.groupby("question_id")
    df_lst = []
    for q_id, i_df in df_grp:
        i_df.sort_values("score")
        i_df.sort_values(by=['score', 'time_used'], ascending=[False, True], inplace=True)
        df_lst.append(i_df.iloc[0:1, :])
    rst_df = pd.concat(df_lst, ignore_index=True)
    # 把根据姓名增加学号字段
    for i in rst_df.index:
        username = rst_df.at[i, "username"]
        rst_df.at[i, "stu_id"] = user_df.at[username, "id"]
    rst_df["stu_id"] = rst_df["stu_id"].astype(int)
    data = rst_df.to_dict("records")
    return data


def get_all_users():
    # 连接到数据库
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # SQL 查询语句
            sql = "SELECT * FROM users"
            cursor.execute(sql)

            # 获取所有记录列表
            results = cursor.fetchall()
    finally:
        # 关闭数据库连接
        connection.close()
    return results


