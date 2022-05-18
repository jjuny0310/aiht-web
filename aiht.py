from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from python import main

app = Flask(__name__)
app.config['SECRET_KEY'] = 'keyasdqwmmvfknmttit12314230'

# 데이터 베이스 연동(MySQL)
db = pymysql.connect(
    user='aiht',
    passwd='0310',
    host='localhost',
    db='aihtdb',
    charset='utf8'
)
cursor = db.cursor()

exercise_type = ""
goal_number = 0


# 세션 변수 초기화
def init_session_value():
    # 스쿼트 변수
    session['squat_count'] = 0
    session['squat_count_check'] = False
    session['squat_pose'] = False

    # 푸쉬업 변수
    session['pushup_count'] = 0
    session['pushup_count_check'] = False
    session['pushup_pose'] = False


# 메인 화면 요청
@app.route('/', methods=['GET', 'POST'])
def home():
    init_session_value()
    global exercise_type, goal_number

    if request.method == 'GET':
        return render_template('index.html')

    # 메인 화면에서 운동 선택 시
    if request.method == 'POST':
        exercise_type = request.form['select_exercise']
        goal_number = int(request.form['select_num'])
        return redirect(url_for('run'))


# 운동 수행
@app.route('/run')
def run():
    init_session_value()
    try:
        if session['login']:
            return render_template('run.html', exercise_type=exercise_type, goal_number=goal_number)

        if not session['login']:
            return redirect(url_for('login'))

    except:
        return redirect(url_for('login'))


# 운동 종료 후 결과
@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'GET':
        return render_template('result.html')

    # 운동 결과 저장 시 처리
    if request.method == 'POST':
        sql = f'''INSERT INTO results(date, exercise, result_num, exercise_time, fk_username)
        values("{request.form['result_date']}", "{request.form['result_exercise']}", "{request.form['result_num']}"
        , "{request.form['result_exercise_time']}", "{session['username']}");'''

        cursor.execute(sql)
        db.commit()
        return redirect(url_for('home'))


# 운동 결과 조회(목록)
@app.route('/result_list', methods=['GET'])
def result_list():
    # 사용자의 모든 운동 결과 목록 불러오기
    if session['login']:
        sql = f'''SELECT * FROM results WHERE fk_username="{session['username']}";'''
        cursor.execute(sql)
        results = cursor.fetchall()

        return render_template('result_list.html', results=results)

    if not session['login']:
        return redirect(url_for('login'))


# 운동 결과 삭제
@app.route('/result_delete')
def result_delete():
    # database.js에서 받은 result_id 조회 후 삭제
    result_id = request.args['result_id']
    sql = f'''DELETE FROM results WHERE id={result_id};'''
    cursor.execute(sql)
    db.commit()
    return redirect(url_for('result_list'))


# 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        name = request.form['username']
        passwd = request.form['password']
        try:
            sql = f'''SELECT * FROM users WHERE username="{name}";'''
            cursor.execute(sql)
            old_user = cursor.fetchone()

            # 사용자 계정 검증(id, passwd(복호화))
            if old_user is not None and check_password_hash(old_user[2], passwd):
                # 로그인 성공
                session['login'] = True
                session['username'] = old_user[1]
                session['nickname'] = old_user[3]
                return redirect(url_for('home'))
            else:
                # 로그인 실패
                return render_template('login.html', login_fail=True)
        except:
            return render_template('login.html', login_fail=True)


# 회원 가입
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        try:
            # 사용자 아이디 규칙(영문과 숫자만 가능)
            username_rule = True
            for i in request.form['username']:
                if not i.encode().isalpha() and not i.isnumeric():
                    username_rule = False
                    break

            # 사용자 아이디 길이 확인
            if len(request.form['username']) < 4:
                return render_template('signup.html', username_len_fail=True)
            # 사용자 아이디 규칙 확인
            elif not username_rule:
                return render_template('signup.html', username_rule_fail=True)
            # 비밀번호 길이 확인
            elif len(request.form['password']) < 6:
                return render_template('signup.html', password_len_fail=True)
            else:
                # 사용자 계정 생성(비밀번호 암호화)
                sql = f'''INSERT INTO users(username, password, nickname)
                values("{request.form['username']}", "{generate_password_hash(request.form['password'])}", 
                "{request.form['nickname']}");'''
                cursor.execute(sql)
                db.commit()
                return redirect(url_for('login'))
        except:
            return render_template('signup.html', signup_fail=True)


# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# 운동 자세 분석(딥러닝 처리)
@app.route('/exercise_analysis', methods=['POST'])
def exercise_analysis():
    try:
        # human_pose.js에서 ajax 통신으로 전달된 데이터
        data = request.get_json()
        pose_landmarks = data['pose_landmarks']
        ready_flag = data['ready_flag']

        if not ready_flag:
            return jsonify(success=False)

        # 스쿼트 처리
        if exercise_type == "SQUAT":
            print(session['squat_count'])
            state, squat_result, visibility_check = main.run(exercise_type, pose_landmarks)
            return jsonify(exercise_type=exercise_type, state=state, count=session['squat_count'], result=squat_result,
                           correct_pose=session['squat_pose'], visibility=visibility_check, count_check=session['squat_count_check'],
                           goal_number=goal_number)

        # 푸쉬업 처리
        elif exercise_type == "PUSH_UP":
            print(session['pushup_count'])
            state, pushup_result, visibility_check = main.run(exercise_type, pose_landmarks)
            return jsonify(exercise_type=exercise_type, state=state, count=session['pushup_count'], result=pushup_result,
                           correct_pose=session['pushup_pose'], visibility=visibility_check, count_check=session['pushup_count_check'],
                           goal_number=goal_number)

    except:
        return jsonify(success=False, goal_number=goal_number)


if __name__ == '__main__':
    app.run()
