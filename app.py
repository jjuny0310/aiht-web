from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from python import main

app = Flask(__name__)

# db연동
app.config['SECRET_KEY'] = 'qwlem12kkasdniovni2r23nkzx12'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aiht.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 운동 선택
fitness_mode = ""
num = 0


# 초기변수 초기화
def init_value():
    # 스쿼트 변수
    session['squat_count'] = 0
    session['squat_check'] = False
    session['squat_correct_pose'] = False
    session['ankle_state'] = "pass"

    # 푸쉬업 변수
    session['pushup_count'] = 0
    session['pushup_check'] = False
    session['pushup_correct_pose'] = False


# 데이터베이스 테이블
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    nickname = db.Column(db.String(80), nullable=False)

    def __init__(self, username, nickname, password, **kwargs):
        self.username = username
        self.set_password(password)
        self.nickname = nickname

    # 문자열 형태로 반환
    def __repr__(self):
        return f"<User('{self.id}', '{self.username}', '{self.nickname}')>"
    
    # 암호화
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # 암호화된 비밀번호 체크
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(80), nullable=False)
    exercise = db.Column(db.String(80), nullable=False)
    result_num = db.Column(db.String(80), nullable=False)
    exercise_time = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('user.username'))

    user = relationship("User", backref=backref('results', order_by=id))

    def __init__(self, date, exercise, result_num, exercise_time, user_id):
        self.date = date
        self.exercise = exercise
        self.result_num = result_num
        self.exercise_time = exercise_time
        self.user_id = user_id

    def __repr__(self):
        return f"<Result('{self.id}', '{self.date}', '{self.exercise}', '{self.result_num}', '{self.exercise_time}', '{self.user_id}')>"



@app.route('/', methods=['GET', 'POST'])
def home():
    init_value()
    global fitness_mode, num

    if request.method == 'GET':
        return render_template('index.html')
    else:
        fitness_mode = request.form['select_exercise']
        num = int(request.form['select_num'])
        return redirect(url_for('run'))


@app.route('/run')
def run():
    init_value()
    try:
        if session['login']:
            return render_template('run.html', fitness_mode=fitness_mode, num=num)
        else:
            return redirect(url_for('login'))
    except:
        return redirect(url_for('login'))

@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == "GET":
        return render_template('result.html')
    else:
        new_result = Result(date=request.form['result_date'], exercise=request.form['result_exercise'],
                            result_num=request.form['result_num'], exercise_time=request.form['result_exercise_time'],
                            user_id=session['username'])
        db.session.add(new_result)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/result_list', methods=['GET'])
def result_list():
    if session['login']:
        results = Result.query.filter_by(user_id=session['username']).all()
        return render_template('result_list.html', results=results)
    else:
        return redirect(url_for('login'))


@app.route('/result_delete')
def result_delete():
    result_id = request.args['result_id']
    item = Result.query.filter_by(id=result_id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('result_list'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form['username']
        passwd = request.form['password']
        try:
            old_user = User.query.filter_by(username=name).first()

            if old_user is not None and check_password_hash(old_user.password, passwd):
                session['login'] = True
                session['username'] = old_user.username
                session['nickname'] = old_user.nickname
                return redirect(url_for('home'))
            else:
                return render_template('login.html', login_fail=True)
        except:
            return render_template('login.html', login_fail=True)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            # 아이디 규칙(영문과 숫자만)
            username_rule = False
            for i in request.form['username']:
                if i.encode().isalpha() or i.isnumeric():
                    username_rule = True
                else:
                    username_rule = False
                    break

            # 아이디 길이 제한
            if len(request.form['username']) < 4:
                return render_template('signup.html', username_len_fail=True)
            # 아이디 규칙
            elif not username_rule:
                return render_template('signup.html', username_rule_fail=True)
            # 비밀번호 길이 제한
            elif len(request.form['password']) < 6:
                return render_template('signup.html', password_len_fail=True)
            else:
                new_user = User(username=request.form['username'], password=request.form['password'],
                                nickname=request.form['nickname'])
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
        except:
            return render_template('signup.html', signup_fail=True)
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    # session['login'] = False
    session.clear()
    return redirect(url_for('home'))


@app.route('/exercise_analysis', methods=['POST'])
def exercise_analysis():
    try:
        # 관절좌표 저장
        data = request.get_json()
        pose_landmarks = data['pose_landmarks']
        ready_flag = data['ready_flag']

        # 메인 알고리즘
        if not ready_flag:
            return jsonify(success=False)

        if fitness_mode == "SQUAT":
            state, squat_correct_dict, visibility_check = main.run(fitness_mode, pose_landmarks)
            return jsonify(fitness_mode=fitness_mode, state=state, count=session['squat_count'], correct_dict=squat_correct_dict,
                           correct_pose=session['squat_correct_pose'], visibility=visibility_check, angle_check=session['squat_check'],
                           num=num)

        elif fitness_mode == "PUSH_UP":
            state, pushup_correct_dict, visibility_check = main.run(fitness_mode, pose_landmarks)
            return jsonify(fitness_mode=fitness_mode, state=state, count=session['pushup_count'], correct_dict=pushup_correct_dict,
                           correct_pose=session['pushup_correct_pose'], visibility=visibility_check, angle_check=session['pushup_check'],
                           num=num)
    except:
        if fitness_mode == "SQUAT":
            return jsonify(success=False, fitness_mode=fitness_mode, num=num, count=session['squat_count'])
        elif fitness_mode == "PUSH_UP":
            return jsonify(success=False, fitness_mode=fitness_mode, num=num, count=session['pushup_count'])

if __name__ == '__main__':
    # debug는 소스코드 변경시 자동 재시작
    # app.run(debug=True)
    
    # 배포 시 debug 해제 해야함
    app.run()
