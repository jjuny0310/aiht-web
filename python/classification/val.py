from tensorflow.keras.models import load_model
from sklearn.model_selection import train_test_split
import numpy as np


def validation(FITNESS_MODE):
    # csv 파일 불러오기(데이터셋)
    if FITNESS_MODE == "LEFT_PUSH_UP":       # LEFT 푸쉬업
        up_data_path = "dataset/up/up_left_pushup_pose.csv"
        down_data_path = "dataset/down/down_left_pushup_pose.csv"
        nothing_data_path = "dataset/nothing/nothing_left_pushup_pose.csv"
    elif FITNESS_MODE == "RIGHT_PUSH_UP":    # RIGHT 푸쉬업
        up_data_path = "dataset/up/up_right_pushup_pose.csv"
        down_data_path = "dataset/down/down_right_pushup_pose.csv"
        nothing_data_path = "dataset/nothing/nothing_right_pushup_pose.csv"
    else:                                   # 스쿼트
        up_data_path = "dataset/up/up_squat_pose.csv"
        down_data_path = "dataset/down/down_squat_pose.csv"
        nothing_data_path = "dataset/nothing/nothing_squat_pose.csv"

    up_pose_data = np.loadtxt(up_data_path, unpack=True, delimiter=',', skiprows=1, dtype=np.float64).transpose()
    down_pose_data = np.loadtxt(down_data_path, unpack=True, delimiter=',', skiprows=1, dtype=np.float64).transpose()
    nothing_pose_data = np.loadtxt(nothing_data_path, unpack=True, delimiter=',', skiprows=1, dtype=np.float64).transpose()

    # 0: up, 1: down, 2: Nothing
    up_label = [0 for _ in range(len(up_pose_data))]
    down_label = [1 for _ in range(len(down_pose_data))]
    nothing_label = [2 for _ in range(len(nothing_pose_data))]

    data = np.concatenate((up_pose_data, down_pose_data, nothing_pose_data), axis=0)
    label = np.array(up_label + down_label + nothing_label)


    train_x, test_x, train_y, test_y = train_test_split(data, label, test_size=0.1, random_state=121)

    # 모델 불러오기
    if FITNESS_MODE == "LEFT_PUSH_UP":
        model = load_model('model/left_pushup_model.h5')
    elif FITNESS_MODE == "RIGHT_PUSH_UP":
        model = load_model('model/right_pushup_model.h5')
    else:
        model = load_model('model/squat_model.h5')

    # 검증
    np.set_printoptions(precision=6, suppress=True)

    predict = model.predict(test_x)

    count = 0
    # 0: up, 1: down, 2:nothing
    for i, res in enumerate(predict):
        if np.argmax(res) == 0:
            if test_y[i] == 0:
                print(f"UP / True")     # 정답
                count += 1
            else:
                print(f"UP / False")    # 오답
        elif np.argmax(res) == 1:
            if test_y[i] == 1:
                count += 1
                print(f"DOWN / True")
            else:
                print(f"DOWN / False")
        else:
            if test_y[i] == 2:
                count += 1
                print(f"NOTHING / True")
            else:
                print(f"NOTHING / False")
    accuracy = count / len(predict)
    print(f"정답/전체 : {count}/{len(predict)} = {accuracy}")

    # 정확도 출력
    results = model.evaluate(test_x, test_y)
    print(f"accuracy : {results[1]}")


if __name__ == '__main__':
    # 검증할 운동 선택
    # FITNESS_MODE = "LEFT_PUSH_UP"
    # FITNESS_MODE = "RIGHT_PUSH_UP"
    FITNESS_MODE = "SQUAT"
    
    validation(FITNESS_MODE)