from flask import Flask, render_template, request, jsonify
from python.temp import run
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ajax', methods=['POST'])
def ajax():
    # 자바스크립트 변수 저장
    pose_landmarks = request.get_json()

    # 메인 알고리즘
    # FITNESS_MODE = "PUSH_UP"
    FITNESS_MODE = "SQUAT"
    run(FITNESS_MODE, pose_landmarks)


    return jsonify(success="success", result2=pose_landmarks)

if __name__ == '__main__':
    app.run()
