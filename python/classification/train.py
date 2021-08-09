import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf


def train(FITNESS_MODE):
    # csv 파일 불러오기(데이터셋)
    if FITNESS_MODE == "LEFT_PUSH_UP":       # LEFT 푸쉬업
        up_data_path = "dataset/up/up_left_pushup_pose.csv"
        down_data_path = "dataset/down/down_left_pushup_pose.csv"
        nothing_data_path = "dataset/nothing/nothing_left_pushup_pose.csv"
    elif FITNESS_MODE == "RIGHT_PUSH_UP":    # RIGHT 푸쉬업
        up_data_path = "dataset/up/up_right_pushup_pose.csv"
        down_data_path = "dataset/down/down_right_pushup_pose.csv"
        nothing_data_path = "dataset/nothing/nothing_right_pushup_pose.csv"
    else:   # 스쿼트
        up_data_path = "dataset/up/up_squat_pose.csv"
        down_data_path = "dataset/down/down_squat_pose.csv"
        nothing_data_path = "dataset/nothing/nothing_squat_pose.csv"

    # 데이터 전처리 --> 1행 삭제, (26, ?) -> (?, 26)으로 변경
    up_pose_data = np.loadtxt(up_data_path, unpack=True, delimiter=',', skiprows=1, dtype=np.float64).transpose()
    down_pose_data = np.loadtxt(down_data_path, unpack=True, delimiter=',', skiprows=1, dtype=np.float64).transpose()

    nothing_pose_data = np.loadtxt(nothing_data_path, unpack=True, delimiter=',', skiprows=1, dtype=np.float64).transpose()

    print(up_pose_data.shape)
    print(down_pose_data.shape)
    print(nothing_pose_data.shape)

    # 0: up, 1: down, 2: nothing
    up_label = [0 for _ in range(len(up_pose_data))]
    down_label = [1 for _ in range(len(down_pose_data))]
    nothing_label = [2 for _ in range(len(nothing_pose_data))]

    data = np.concatenate((up_pose_data, down_pose_data, nothing_pose_data), axis=0)
    label = np.array(up_label + down_label + nothing_label)

    # train데이터, test데이터 9:1 비유로 분할(레이블도 알아서 분할됨)
    train_x, test_x, train_y, test_y = train_test_split(data, label, test_size=0.1, random_state=121)
    print(train_x.shape)
    print(train_y.shape)
    print(train_y)

    # 모델 생성
    if FITNESS_MODE == "LEFT_PUSH_UP":
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, input_shape=(18,), activation='relu'),   # 9개의 관절 좌표(18개의 입력)
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(3, activation='softmax')                      # 운동상태 3개(출력 3개),
        ])                                                                      # sigmoid보다 softmax가 정확도가 더 좋았음
    elif FITNESS_MODE == "RIGHT_PUSH_UP":
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, input_shape=(18,), activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(3, activation='softmax')
        ])
    else:
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, input_shape=(26,), activation='relu'),   # 13개의 관절 좌표(26개의 입력)
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(3, activation='softmax')                      # 운동상태 3개(출력 3개),
        ])                                                                      # sigmoid보다 softmax가 정확도가 더 좋았음

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    model.summary()     # 모델 요약
    
    # 학습
    model.fit(train_x, train_y, batch_size=50, epochs=100, verbose=1)

    # 가중치 저장
    if FITNESS_MODE == "LEFT_PUSH_UP":
        model.save('model/left_pushup_model.h5')
        print(f"{FITNESS_MODE} 가중치 저장 완료!")
    elif FITNESS_MODE == "RIGHT_PUSH_UP":
        model.save('model/right_pushup_model.h5')
        print(f"{FITNESS_MODE} 가중치 저장 완료!")
    else:
        model.save('model/squat_model.h5')
        print(f"{FITNESS_MODE} 가중치 저장 완료!")

    # 정확도 출력
    results = model.evaluate(test_x, test_y)
    print(f"accuracy : {results[1]}")


if __name__ == '__main__':
    # 학습할 운동 선택
    # FITNESS_MODE = "LEFT_PUSH_UP"
    # FITNESS_MODE = "RIGHT_PUSH_UP"
    FITNESS_MODE = "SQUAT"

    train(FITNESS_MODE)