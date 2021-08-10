from flask import Flask, render_template, request, jsonify
from python.main import run
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/exercise_analysis', methods=['POST'])
def exercise_analysis():
    # 관절좌표 저장
    pose_landmarks = request.get_json()
    
    # 운동 선택
    fitness_mode = "SQUAT"
    # fitness_mode = "PUSH_UP"

    # 메인 알고리즘
    run(fitness_mode, pose_landmarks)

    return jsonify(result=pose_landmarks)


if __name__ == '__main__':
    app.run()
