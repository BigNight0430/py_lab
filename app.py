import xlrd
from flask import Flask, request, render_template, redirect, url_for, session, flash

from db import validate_credentials, set_password, calculate_score, write_score_to_sql, get_question_by_id
from db import get_history_score, set_user, delete_all_users, get_class_data


app = Flask(__name__)
app.secret_key = 'qufu20240116ldy'


@app.route('/')
def login_form():
    # 这里将返回登录表单的HTML
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form['username']
        password = request.form['password']
        # 假设您有一个函数来验证用户名和密码
        if not validate_credentials(username, password, action):
            error = '用户名或密码输入错误，请重新输入！'
        else:
            session['username'] = username  # 存储用户名到会话
            if action == '学生登录':
                return redirect(url_for('show_questions'))
            else:
                # 教师登录
                return redirect(url_for('admin'))
    return render_template('login.html', error=error)


@app.route('/questions')
def show_questions():
    username = session.get('username', 'Guest')  # 如果会话中没有用户名，则使用默认值'Guest'
    questions = []
    # 读取已经完成的题目的分数。
    scores = get_history_score(username)
    # 打开Excel文件
    workbook = xlrd.open_workbook('quiz/quiz.xls')
    sheet = workbook.sheet_by_index(0)
    # 读取除标题行外的所有行
    for rowx in range(1, sheet.nrows):
        cols = sheet.row_values(rowx)
        q_id = int(cols[0])
        question = {"id": q_id, 'title': cols[1], 'score': 0, 'time_used': " "}
        if q_id in scores:
            question["score"] = scores[q_id]["score"]
            question["time_used"] = scores[q_id]["time_used"]
            question["timestamp"] = scores[q_id]["timestamp"]
        questions.append(question)
    return render_template('questions.html', username=username, questions=questions)


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/question/<int:question_id>')
def show_question(question_id):
    # 从数据库获取题目信息，假设有一个函数 get_question_by_id 来实现这一点
    question_info = get_question_by_id(question_id)
    # 确保找到了题目
    if question_info:
        return render_template('question.html', question=question_info)
    else:
        return "题目未找到", 404


@app.route('/submit_answer/<int:question_id>', methods=['POST'])
def submit_answer(question_id):
    student_answer = request.form['answer']
    score, total_time = calculate_score(student_answer, question_id)
    username = session.get('username')  # 从会话中获取用户名
    write_score_to_sql(username, question_id, score, total_time)
    return redirect(url_for('show_questions'))


@app.route('/user_page')
def user_page():
    # 函数实现...
    return render_template('user_page.html')


@app.route('/reset_password', methods=['POST'], )
def reset_password():
    # 确保用户已登录
    if 'username' not in session:
        flash('请先登录。')
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password != confirm_password:
            # 如果密码不匹配，显示错误消息
            flash('两次输入的密码不匹配，请重试。')
            return redirect(url_for('user_page'))
        username = session['username']
        set_password(username, new_password)
        flash('密码已成功重置。')
    return redirect(url_for('user_page'))


@app.route('/upload_file', methods=['POST'])
def upload_file():
    # 检查是否有文件在请求中
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    # 如果用户未选择文件，浏览器也会提交一个空的文件名
    if file.filename == '':
        return redirect(request.url)

    if file:
        # 这里可以添加保存文件的逻辑
        # file.save(os.path.join('上传文件保存路径', file.filename))

        # 假设是CSV文件并且要导入到MySQL数据库中
        # with open(os.path.join('上传文件保存路径', file.filename), 'r') as f:
        #     csv_file = csv.reader(f)
        #     for row in csv_file:
        #         # 将row插入到MySQL数据库的users表中
        #         # ...
        set_user(file)

        return redirect(url_for('admin'))


@app.route('/delete_users', methods=['POST'])
def delete_users():
    # 连接到数据库并删除users表的内容
    # connection = pymysql.connect(数据库连接信息)
    # with connection.cursor() as cursor:
    #     cursor.execute("DELETE FROM users")
    # connection.commit()
    # connection.close()、
    delete_all_users()

    return redirect(url_for('admin'))


@app.route('/class_page')
def class_page():
    username = session.get('username', 'Guest')  # 如果会话中没有用户名，则使用默认值'Guest'
    data = get_class_data()
    return render_template('class_page.html', data=data, username=username)


if __name__ == '__main__':
    app.run(debug=True)

