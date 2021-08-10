from flask import Flask, render_template, request, jsonify
from python import main
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ajax', methods=['POST'])
def ajax():
    # 관절좌표 저장
    pose_landmarks = request.get_json()
    
    # 운동 선택
    # FITNESS_MODE = "SQUAT"
    FITNESS_MODE = "PUSH_UP"

    # 메인 알고리즘
    main.run(FITNESS_MODE, pose_landmarks)

    return jsonify(result=pose_landmarks)

if __name__ == '__main__':
    app.run()
