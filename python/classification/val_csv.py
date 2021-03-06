import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import load_model

def train(FITNESS_MODE):
    # csv 파일 불러오기(데이터셋)
    if FITNESS_MODE == "LEFT_PUSH_UP":  # LEFT 푸쉬업
        up_data_path = "test_data/left_pushup_up.csv"
        down_data_path = "test_data/left_pushup_down.csv"
        nothing_data_path = "dataset/nothing/nothing_left_pushup_pose.csv"
        model = load_model('model/left_pushup_model.h5')
    elif FITNESS_MODE == "RIGHT_PUSH_UP":  # RIGHT 푸쉬업
        up_data_path = "test_data/right_pushup_up.csv"
        down_data_path = "test_data/right_pushup_down.csv"
        nothing_data_path = "dataset/nothing/nothing_right_pushup_pose.csv"
        model = load_model('model/right_pushup_model.h5')
    else:  # 스쿼트
        up_data_path = "test_data/squat_up.csv"
        down_data_path = "test_data/squat_down.csv"
        nothing_data_path = "dataset/nothing/nothing_squat_pose.csv"
        model = load_model('model/squat_model.h5')

    # 데이터 전처리 --> 1행 삭제, (26, ?) -> (?, 26)으로 변경
    up_pose_data = np.loadtxt(up_data_path, unpack=True, delimiter=',', skiprows=1, dtype=np.float64).transpose()
    down_pose_data = np.loadtxt(down_data_path, unpack=True, delimiter=',', skiprows=1, dtype=np.float64).transpose()
    nothing_pose_data = np.loadtxt(nothing_data_path, unpack=True, delimiter=',', skiprows=1,
                                   dtype=np.float64).transpose()

    print(f"UP 데이터 : {up_pose_data.shape}")
    print(f"DOWN 데이터 : {down_pose_data.shape}")
    print(f"NOTHING 데이터 : {nothing_pose_data.shape}")

    # 0: up, 1: down, 2: nothing
    up_label = [0 for _ in range(len(up_pose_data))]
    down_label = [1 for _ in range(len(down_pose_data))]
    nothing_label = [2 for _ in range(len(nothing_pose_data))]

    data = np.concatenate((up_pose_data, down_pose_data, nothing_pose_data), axis=0)
    label = np.array(up_label + down_label + nothing_label)

    # train데이터, test데이터 9:1 비유로 분할(레이블도 알아서 분할됨)
    train_x, test_x, train_y, test_y = train_test_split(data, label, test_size=0.1, random_state=121)

    print(f"Train 데이터 : {train_x.shape}")
    print(f"Test 데이터 : {test_x.shape}")

    # 검증
    np.set_printoptions(precision=6, suppress=True)

    train_predict = model.predict(train_x)
    test_predict = model.predict(test_x)

    count = 0
    nothing_count = 0
    # 0: up, 1: down, 2:nothing
    for i, res in enumerate(train_predict):
        if np.argmax(res) == 0:
            if train_y[i] == 0:
                print(f"UP / True")  # 정답
                count += 1
            else:
                print(f"UP / False")  # 오답
        elif np.argmax(res) == 1:
            if train_y[i] == 1:
                count += 1
                print(f"DOWN / True")
            else:
                print(f"DOWN / False")
        else:
            if train_y[i] == 2:
                nothing_count += 1
                print(f"NOTHING / True")
            else:
                print(f"NOTHING / False")


    for i, res in enumerate(test_predict):
        if np.argmax(res) == 0:
            if test_y[i] == 0:
                print(f"UP / True")  # 정답
                count += 1
            else:
                print(f"UP / False")  # 오답
        elif np.argmax(res) == 1:
            if test_y[i] == 1:
                count += 1
                print(f"DOWN / True")
            else:
                print(f"DOWN / False")
        else:
            if test_y[i] == 2:
                nothing_count += 1
                print(f"NOTHING / True")
            else:
                print(f"NOTHING / False")

    accuracy = count / (len(train_predict) + len(test_predict) - nothing_count)
    print(f"정답(NOHTING제외)/전체 : {count}/{len(train_predict) + len(test_predict) - nothing_count} = {accuracy}")

if __name__ == '__main__':
    # 운동 선택
    # FITNESS_MODE = "LEFT_PUSH_UP"
    # FITNESS_MODE = "RIGHT_PUSH_UP"
    FITNESS_MODE = "SQUAT"

    train(FITNESS_MODE)