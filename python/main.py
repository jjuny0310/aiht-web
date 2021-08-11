from tensorflow.keras.models import load_model
import numpy as np
import math

# 관절 정의
NOSE = 0
LEFT_EYE_INNER = 1
LEFT_EYE = 2
LEFT_EYE_OUTER = 3
RIGHT_EYE_INNER = 4
RIGHT_EYE = 5
RIGHT_EYE_OUTER = 6
LEFT_EAR = 7
RIGHT_EAR = 8
MOUTH_LEFT = 9
MOUTH_RIGHT = 10
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_ELBOW = 13
RIGHT_ELBOW = 14
LEFT_WRIST = 15
RIGHT_WRIST = 16
LEFT_PINKY = 17
RIGHT_PINKY = 18
LEFT_INDEX = 19
RIGHT_INDEX = 20
LEFT_THUMB = 21
RIGHT_THUMB = 22
LEFT_HIP = 23
RIGHT_HIP = 24
LEFT_KNEE = 25
RIGHT_KNEE = 26
LEFT_ANKLE = 27
RIGHT_ANKLE = 28
LEFT_HEEL = 29
RIGHT_HEEL = 30
LEFT_FOOT_INDEX = 31
RIGHT_FOOT_INDEX = 32

# 모델 로드
pushup_left_parts = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, RIGHT_ELBOW,
                     RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE]
pushup_right_parts = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW,
                      LEFT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE, LEFT_ANKLE]
squat_parts = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW,
               LEFT_WRIST, RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE, RIGHT_KNEE,
               LEFT_ANKLE, RIGHT_ANKLE]

# pushup_left_model = load_model('classification/model/left_pushup_model.h5')
# pushup_right_model = load_model('classification/model/right_pushup_model.h5')
# squat_model = load_model('classification/model/squat_model.h5')

pushup_left_model = load_model('python/classification/model/left_pushup_model.h5')
pushup_right_model = load_model('python/classification/model/right_pushup_model.h5')
squat_model = load_model('python/classification/model/squat_model.h5')

# 스쿼트 변수
squat_count = 0
squat_check = False

# 푸쉬업 변수
pushup_count = 0
pushup_check = False

def run(fitness_mode, pose_landmarks):
    keypoints_x = []
    keypoints_y = []
    keypoints_squat = []
    keypoints_pushup_left = []
    keypoints_pushup_right = []

    for idx, landmark in enumerate(pose_landmarks):
        keypoints_x.append(landmark['x'])
        keypoints_y.append(landmark['y'])
        if fitness_mode == "SQUAT":
            if idx in squat_parts:
                keypoints_squat.append(landmark['x'])
                keypoints_squat.append(landmark['y'])

        elif fitness_mode == "PUSH_UP":
            if idx in pushup_left_parts:
                keypoints_pushup_left.append(landmark['x'])
                keypoints_pushup_left.append(landmark['y'])
            if idx in pushup_right_parts:
                keypoints_pushup_right.append(landmark['x'])
                keypoints_pushup_right.append(landmark['y'])

    keypoints = list(zip(keypoints_x, keypoints_y))
    
    # 스쿼트
    if fitness_mode == "SQUAT":
        global squat_check, squat_count

        keypoints_array = np.array([keypoints_squat])
        predict = squat_model.predict(keypoints_array)

        # 다리 각도
        left_leg_angle = getAngle3P(keypoints[RIGHT_HIP], keypoints[RIGHT_KNEE],
                                    keypoints[RIGHT_ANKLE])
        right_leg_angle = getAngle3P(keypoints[LEFT_HIP], keypoints[LEFT_KNEE], keypoints[LEFT_ANKLE])

        squat_down_angle = 130

        # Nothing 자세 기준치
        if predict[0][2] > 0.8:
            squat_state = np.argmax(predict[0])
        else:
            squat_state = np.argmax(predict[0][0:2])

        # 자세 분류
        if squat_state == 0:
            state = "UP"
            if squat_check and left_leg_angle > 170 and right_leg_angle > 170:
                squat_count += 1
                squat_check = False
                sound_once = True
                # print(F"스쿼트 갯수: {squat_count}")

        elif squat_state == 1:
            state = "DOWN"
            if right_leg_angle < squat_down_angle and left_leg_angle < squat_down_angle:
                squat_check = True

        else:
            state = "NOTHING"

        return state, squat_count
    # 푸쉬업
    elif fitness_mode == "PUSH_UP":
        left_keypoints_array = np.array([keypoints_pushup_left])
        right_keypoints_array = np.array([keypoints_pushup_right])
        left_predict = pushup_left_model.predict(left_keypoints_array)
        right_predict = pushup_right_model.predict(right_keypoints_array)
        if keypoints[LEFT_SHOULDER][0] < keypoints[NOSE][0] or keypoints[RIGHT_SHOULDER][0] < \
                keypoints[NOSE][0]:
            if np.argmax(left_predict[0]) == 0:
                state = "LEFT_UP"
            elif np.argmax(left_predict[0]) == 1:
                state = "LEFT_DOWN"
            else:
                state = "LEFT_NOTHING"
        else:
            if np.argmax(right_predict[0]) == 0:
                state = "RIGHT_UP"
            elif np.argmax(right_predict[0]) == 1:
                state = "RIGHT_DOWN"
            else:
                state = "RIGHT_NOTHING"

        return state

# 두 점 사이의 거리
def getPoint2D(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    dist = (x2 - x1) ** 2 + (y2 - y1) ** 2
    dist = math.sqrt(dist)
    return dist

# 삼각형 세변 길이의 각도(좌표를 받아서 각도 출력)
def getAngle3P(p1, p2, p3):
    dist1 = getPoint2D(p1, p2)
    dist2 = getPoint2D(p2, p3)
    dist3 = getPoint2D(p3, p1)

    radian = math.acos((dist1 ** 2 + dist2 ** 2 - dist3 ** 2) / (2 * dist1 * dist2))
    angle = math.degrees(radian)
    return angle
