from flask import Flask, render_template, request, jsonify
from python.main import run
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    return render_template('start.html')



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
    app.run()
