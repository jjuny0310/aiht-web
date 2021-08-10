import numpy as np
from python import main


def squat(model, keypoints):
    keypoints_array = np.array([keypoints])
    predict = model.predict(keypoints_array)

    # Nothing 자세 정확도
    if predict[0][2] > 0.8:
        squat_state = np.argmax(predict[0])
    else:
        squat_state = np.argmax(predict[0][0:2])

    # 자세 분류
    if squat_state == 0:
        print("UP")
    elif squat_state == 1:
        print("DOWN")
    else:
        print("NOTHING")

def pushup(left_model, right_model, keypoints_left, keypoints_right, keypoints):
    left_keypoints_array = np.array([keypoints_left])
    right_keypoints_array = np.array([keypoints_right])
    left_predict = left_model.predict(left_keypoints_array)
    right_predict = right_model.predict(right_keypoints_array)
    if keypoints[main.LEFT_SHOULDER][0] < keypoints[main.NOSE][0] or keypoints[main.RIGHT_SHOULDER][0] < keypoints[main.NOSE][0]:
        if np.argmax(left_predict[0]) == 0:
            print("LEFT_UP")
        elif np.argmax(left_predict[0]) == 1:
            print("LEFT_DOWN")
        else:
            print("LEFT_NOTHING")
    else:
        if np.argmax(right_predict[0]) == 0:
            print("RIGHT_UP")
        elif np.argmax(right_predict[0]) == 1:
            print("RIGHT_DOWN")
        else:
            print("RIGHT_NOTHING")
