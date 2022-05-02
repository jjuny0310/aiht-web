from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, join_room, emit, leave_room
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from python import main

app = Flask(__name__)

# SocketIO 연동
app.debug = True
app.config['SECRET_KEY'] = 'qwlem12kkasdniovni2r23nkzx12'
socketio = SocketIO()
socketio.init_app(app)

# 데이터 베이스 연동
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aiht.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

exercise_type = ""
goal_number = 0


# 세션 변수 초기화
def reset_session_value():
    # 스쿼트 변수
    session['squat_count'] = 0
    session['squat_check'] = False
    session['squat_correct_pose'] = False
    session['ankle_state'] = "pass"

    # 푸쉬업 변수
    session['pushup_count'] = 0
    session['pushup_check'] = False
    session['pushup_correct_pose'] = False


# 사용자 테이블
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

    # 암호화 된 비밀번호 체크
    def check_password(self, password):
        return check_password_hash(self.password, password)


# 운동 결과 테이블
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


# 메인 화면 요청
@app.route('/', methods=['GET', 'POST'])
def home():
    reset_session_value()
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
    reset_session_value()
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
        new_result = Result(date=request.form['result_date'], exercise=request.form['result_exercise'],
                            result_num=request.form['result_num'], exercise_time=request.form['result_exercise_time'],
                            user_id=session['username'])
        db.session.add(new_result)
        db.session.commit()
        return redirect(url_for('home'))


# 운동 결과 조회(목록)
@app.route('/result_list', methods=['GET'])
def result_list():
    # 사용자의 모든 운동 결과 목록 불러오기
    if session['login']:
        results = Result.query.filter_by(user_id=session['username']).all()
        return render_template('result_list.html', results=results)

    if not session['login']:
        return redirect(url_for('login'))


# 운동 결과 삭제
@app.route('/result_delete')
def result_delete():
    # database.js에서 받은 result_id 조회 후 삭제
    result_id = request.args['result_id']
    item = Result.query.filter_by(id=result_id).first()
    db.session.delete(item)
    db.session.commit()
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
            old_user = User.query.filter_by(username=name).first()

            # 사용자 계정 검증(id, passwd)
            if old_user is not None and check_password_hash(old_user.password, passwd):
                # 로그인 성공
                session['login'] = True
                session['username'] = old_user.username
                session['nickname'] = old_user.nickname
                session['room'] = session.get('username')
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
            username_rule = False
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
                # 사용자 계정 생성
                new_user = User(username=request.form['username'], password=request.form['password'],
                                nickname=request.form['nickname'])
                db.session.add(new_user)
                db.session.commit()
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
            state, squat_correct_dict, visibility_check = main.run(exercise_type, pose_landmarks)
            return jsonify(exercise_type=exercise_type, state=state, count=session['squat_count'], correct_dict=squat_correct_dict,
                           correct_pose=session['squat_correct_pose'], visibility=visibility_check, angle_check=session['squat_check'],
                           goal_number=goal_number)

        # 푸쉬업 처리
        if exercise_type == "PUSH_UP":
            state, pushup_correct_dict, visibility_check = main.run(exercise_type, pose_landmarks)
            return jsonify(exercise_type=exercise_type, state=state, count=session['pushup_count'], correct_dict=pushup_correct_dict,
                           correct_pose=session['pushup_correct_pose'], visibility=visibility_check, angle_check=session['pushup_check'],
                           goal_number=goal_number)
    except:
        return jsonify(success=False, goal_number=goal_number)


@socketio.on('joined', namespace='/run')
def joined(message):
    room = session.get('room')
    join_room(room)


@socketio.on('run', namespace='/run')
def exercise_analysis(data):
    room = session.get('room')

    # pose_landmarks = data['pose_landmarks']
    # ready_flag = data['ready_flag']

    # result = ""
    state = ""

    # 스쿼트 처리
    if exercise_type == "SQUAT":
        state, squat_correct_dict, visibility_check = main.run(exercise_type, data['pose_landmarks'])
        result = jsonify(exercise_type=exercise_type, state=state, count=session['squat_count'],
                       correct_dict=squat_correct_dict,
                       correct_pose=session['squat_correct_pose'], visibility=visibility_check,
                       angle_check=session['squat_check'],
                       goal_number=goal_number)
    #
    # # 푸쉬업 처리
    # if exercise_type == "PUSH_UP":
    #     state, pushup_correct_dict, visibility_check = main.run(exercise_type, pose_landmarks)
    #     result = jsonify(exercise_type=exercise_type, state=state, count=session['pushup_count'],
    #                    correct_dict=pushup_correct_dict,
    #                    correct_pose=session['pushup_correct_pose'], visibility=visibility_check,
    #                    angle_check=session['pushup_check'],
    #                    goal_number=goal_number)


    emit('run', {'data' : state}, room=room)


if __name__ == '__main__':
    # debug는 소스코드 변경시 자동 재시작
    # aiht_app.run(debug=True)

    # 배포 시 debug 해제 해야함
    # app.run()
    socketio.run(app)