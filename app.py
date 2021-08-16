from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from python.main import run

app = Flask(__name__)

# db연동
app.config['SECRET_KEY'] = 'this is secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 데이터베이스 테이블
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    nickname = db.Column(db.String(80), nullable=False )

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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start')
def start():
    return render_template('start.html')


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
                return redirect(url_for('index'))
            else:
                return "로그인 실패"
        except:
            return '로그인 실패'


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        new_user = User(username=request.form['username'], password=request.form['password'],
                        nickname=request.form['nickname'])
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    return render_template('signup.html')


@app.route('/exercise_analysis', methods=['POST'])
def exercise_analysis():
    try:
        # 관절좌표 저장
        data = request.get_json()
        pose_landmarks = data['pose_landmarks']

        # 해상도
        input_width = data['input_width']
        input_height = data['input_height']
        trainer_width = data['trainer_width']
        trainer_height = data['trainer_height']

        # print(f"캠 사이즈 : {input_width} x {input_height}")
        # print(f"비디오 사이즈 : {trainer_width} x {trainer_height}")

        # 운동 선택
        fitness_mode = "SQUAT"
        # fitness_mode = "PUSH_UP"

        # 메인 알고리즘
        if fitness_mode == "SQUAT":
            state, count, squat_correct_dict = run(fitness_mode, pose_landmarks, input_width, input_height)
            return jsonify(fitness_mode=fitness_mode, state=state, count=count, correct_dict=squat_correct_dict)

        elif fitness_mode == "PUSH_UP":
            state, count = run(fitness_mode, pose_landmarks, input_width, input_height)
            return jsonify(fitness_mode=fitness_mode, state=state, count=count)
    except:
        return jsonify(success=False)


if __name__ == '__main__':
    app.run(debug=True)
