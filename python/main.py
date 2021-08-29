import app
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
pushup_right_parts = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, RIGHT_ELBOW,
                     RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE]
pushup_left_parts = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW,
                      LEFT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE, LEFT_ANKLE]
squat_parts = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW,
               LEFT_WRIST, RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE, RIGHT_KNEE,
               LEFT_ANKLE, RIGHT_ANKLE]

# Flask 자체실행 모델 경로
pushup_left_model = load_model('python/classification/model/left_pushup_model.h5')
pushup_right_model = load_model('python/classification/model/right_pushup_model.h5')
squat_model = load_model('python/classification/model/squat_model.h5')

# # Apache로 실행할때 모델 경로
# pushup_left_model = load_model('C:/Users/LeeYongJun/Desktop/AIHT/aiht-web/python/classification/model/left_pushup_model.h5')
# pushup_right_model = load_model('C:/Users/LeeYongJun/Desktop/AIHT/aiht-web/python/classification/model/right_pushup_model.h5')
# squat_model = load_model('C:/Users/LeeYongJun/Desktop/AIHT/aiht-web/python/classification/model/squat_model.h5')


# 스쿼트 자세 교정 변수
squat_up_angle = 150
squat_down_angle = 100
good_foot_angle = [30, 70]
# ankle_distance_range = [0.000002, 0.01]
# knee_distance_range = [0.000003, 0.04]
ankle_distance_range = [0, 0.05]
knee_distance_range = [0, 0.1]

# 푸쉬업 자세 교정 변수
pushup_up_angle = 150
pushup_down_angle = 100
hip_distance_range = [0, 0.15]
elbow_distance_range = [0, 0.1]


def run(fitness_mode, pose_landmarks, input_width, input_height):
    # 관절 좌표 저장(분리해서)
    keypoints_x = []
    keypoints_y = []
    keypoints_squat = []
    keypoints_pushup_left = []
    keypoints_pushup_right = []

    visibilitys_squat = []
    visibilitys_pushup_left = []
    visibilitys_pushup_right = []

    for idx, landmark in enumerate(pose_landmarks):
        keypoints_x.append(landmark['x'])
        keypoints_y.append(landmark['y'])

        if fitness_mode == "SQUAT":
            if idx in squat_parts:
                keypoints_squat.append(landmark['x'])
                keypoints_squat.append(landmark['y'])
            if idx in squat_parts[7:]:
                visibilitys_squat.append(landmark['visibility'])

        elif fitness_mode == "PUSH_UP":
            if idx in pushup_left_parts:
                keypoints_pushup_left.append(landmark['x'])
                keypoints_pushup_left.append(landmark['y'])
                visibilitys_pushup_left.append(landmark['visibility'])
            if idx in pushup_right_parts:
                keypoints_pushup_right.append(landmark['x'])
                keypoints_pushup_right.append(landmark['y'])
                visibilitys_pushup_right.append(landmark['visibility'])


    keypoints = list(zip(keypoints_x, keypoints_y))
    
    # 스쿼트
    if fitness_mode == "SQUAT":
        # visibility 체크(관절이 정확히 나오면 자세교정 사운드 출력)
        visibility_count = 0
        visibility_check = False
        for visibility in visibilitys_squat:
            if visibility > 0.8:
                visibility_count += 1
            # 모든 관절 정확도 60% 이상이면 True
            if visibility_count == len(squat_parts[7:]):
                visibility_check = True

        keypoints_array = np.array([keypoints_squat])
        predict = squat_model.predict(keypoints_array)

        # 다리 각도
        right_leg_angle = getAngle3P(keypoints[RIGHT_HIP], keypoints[RIGHT_KNEE],
                                    keypoints[RIGHT_ANKLE])
        left_leg_angle = getAngle3P(keypoints[LEFT_HIP], keypoints[LEFT_KNEE], keypoints[LEFT_ANKLE])

        # 발 각도
        right_foot_angle = getAngle3P(keypoints[RIGHT_FOOT_INDEX], keypoints[RIGHT_HEEL],
                                     [keypoints[RIGHT_HEEL][0], keypoints[RIGHT_FOOT_INDEX][1]])

        left_foot_angle = getAngle3P(keypoints[LEFT_FOOT_INDEX], keypoints[LEFT_HEEL],
                                      [keypoints[LEFT_HEEL][0], keypoints[LEFT_FOOT_INDEX][1]])

        # 발목 범위
        right_shoulder_to_ankle = abs(keypoints[RIGHT_SHOULDER][0] - keypoints[RIGHT_ANKLE][0])
        left_shoulder_to_ankle = abs(keypoints[LEFT_SHOULDER][0] - keypoints[LEFT_ANKLE][0])


        # 무릎 범위
        right_shoulder_to_knee = abs(keypoints[RIGHT_SHOULDER][0] - keypoints[RIGHT_KNEE][0])
        left_shoulder_to_knee = abs(keypoints[LEFT_SHOULDER][0] - keypoints[LEFT_KNEE][0])

        squat_correct_dict = {}


        # Nothing 자세 기준 정확도
        if predict[0][2] > 0.8:
            squat_state = np.argmax(predict[0])
        else:
            squat_state = np.argmax(predict[0][0:2])

        # 스쿼트 자세 분류
        if squat_state == 0:
            state = "UP"

            # 자세 교정
            # 왼쪽 발 각도
            if good_foot_angle[0] <= left_foot_angle <= good_foot_angle[1] and keypoints[LEFT_FOOT_INDEX][0] > keypoints[LEFT_HEEL][0]:
                correct_left_foot = True
            else:
                correct_left_foot = False

            # 오른쪽 발 각도
            if good_foot_angle[0] <= right_foot_angle <= good_foot_angle[1] and keypoints[RIGHT_FOOT_INDEX][0] < keypoints[RIGHT_HEEL][0]:
                correct_right_foot = True
            else:
                correct_right_foot = False

            # 오른쪽 발목 자세 교정
            if ankle_distance_range[0] <= right_shoulder_to_ankle <= ankle_distance_range[1]:
                correct_right_ankle = True
            else:
                correct_right_ankle = False

            # 왼쪽 발목 자세 교정
            if ankle_distance_range[0] <= left_shoulder_to_ankle <= ankle_distance_range[1]:
                correct_left_ankle = True
            else:
                correct_left_ankle = False

            # 오른쪽 무릎 자세 교정
            if knee_distance_range[0] <= right_shoulder_to_knee <= knee_distance_range[1]:
                correct_right_knee = True
            else:
                correct_right_knee = False

            # 왼쪽 무릎 자세 교정
            if knee_distance_range[0] <= left_shoulder_to_knee <= knee_distance_range[1]:
                correct_left_knee = True
            else:
                correct_left_knee = False

            # 스쿼트 자세 상태 저장
            squat_correct_dict = {'correct_right_knee' : correct_right_knee, 'correct_left_knee' : correct_left_knee,
                               'correct_right_ankle' : correct_right_ankle, 'correct_left_ankle' : correct_left_ankle,
                               'correct_left_foot' : correct_left_foot, 'correct_right_foot' : correct_right_foot}

            # 스쿼트 자세 판별
            if correct_right_knee and correct_left_knee and correct_right_ankle and correct_left_ankle and correct_left_foot and correct_right_foot:
                app.session['squat_correct_pose'] = True
            else:
                app.session['squat_correct_pose'] = False
                app.session['squat_check'] = False

            if app.session['squat_correct_pose'] and app.session['squat_check'] and left_leg_angle > squat_up_angle and right_leg_angle > squat_up_angle:
                app.session['squat_count'] += 1
                app.session['squat_check'] = False

        elif squat_state == 1:
            state = "DOWN"
            if app.session['squat_correct_pose'] and right_leg_angle < squat_down_angle and left_leg_angle < squat_down_angle:
                app.session['squat_check'] = True

        else:
            state = "NOTHING"
            app.session['squat_correct_pose'] = False
            app.session['squat_check'] = False

        return state, squat_correct_dict, visibility_check

    # 푸쉬업
    elif fitness_mode == "PUSH_UP":
        pushup_correct_dict = {}

        # LEFT 푸쉬업
        if keypoints[LEFT_SHOULDER][0] > keypoints[NOSE][0] or keypoints[RIGHT_SHOULDER][0] > \
                keypoints[NOSE][0]:
            left_keypoints_array = np.array([keypoints_pushup_left])
            left_predict = pushup_left_model.predict(left_keypoints_array)

            # 팔의 각도
            left_arm_angle = getAngle3P(keypoints[LEFT_SHOULDER], keypoints[LEFT_ELBOW],
                                        keypoints[LEFT_WRIST])

            # 엉덩이 범위
            shoulder_to_hip = abs(keypoints[LEFT_SHOULDER][1] - keypoints[LEFT_HIP][1])

            # 팔꿈치 범위
            wrist_to_elbow = abs(keypoints[LEFT_WRIST][0] - keypoints[LEFT_ELBOW][0])

            if np.argmax(left_predict[0]) == 0:
                state = "LEFT_UP"
                
                # 푸쉬업 자세교정
                # 손 방향 자세교정
                if keypoints[LEFT_PINKY][0] < keypoints[LEFT_WRIST][0] and\
                   keypoints[LEFT_INDEX][0] < keypoints[LEFT_WRIST] and \
                   keypoints[LEFT_THUMB][0] < keypoints[LEFT_WRIST][0]:
                    correct_hand = True
                else:
                    correct_hand = False
                
                # 엉덩이 자세교정
                if hip_distance_range[0] <= shoulder_to_hip <= hip_distance_range[1] and keypoints[LEFT_SHOULDER][1] <= keypoints[LEFT_HIP][1]:
                    correct_hip = True
                else:
                    correct_hip = False
                
                # 팔꿈치 방향 자세교정
                if keypoints[LEFT_ELBOW][0] > keypoints[LEFT_WRIST][0] and elbow_distance_range[0] <= wrist_to_elbow <= elbow_distance_range[1]:
                    correct_elbow = True
                else:
                    correct_elbow = False

                pushup_correct_dict = {'correct_hand': correct_hand, 'correct_hip': correct_hip, 'correct_elbow': correct_elbow}

                # 푸쉬업 자세 판별
                if correct_hand and correct_hip and correct_elbow:
                    app.session['pushup_correct_pose'] = True
                else:
                    app.session['pushup_correct_pose'] = False
                    app.session['pushup_check'] = False

                if app.session['pushup_correct_pose'] and app.session['pushup_check'] and left_arm_angle > pushup_up_angle:
                    app.session['pushup_count'] += 1
                    app.session['pushup_check'] = False

            elif np.argmax(left_predict[0]) == 1:
                state = "LEFT_DOWN"
                if app.session['pushup_correct_pose'] and left_arm_angle < pushup_down_angle:
                    app.session['pushup_check'] = True

            else:
                state = "NOTHING"
                app.session['pushup_correct_pose'] = False
                app.session['pushup_check'] = False
        
        # RIGHT 푸쉬업
        else:
            right_keypoints_array = np.array([keypoints_pushup_right])
            right_predict = pushup_right_model.predict(right_keypoints_array)

            if np.argmax(right_predict[0]) == 0:
                state = "RIGHT_UP"
            elif np.argmax(right_predict[0]) == 1:
                state = "RIGHT_DOWN"
            else:
                state = "NOTHING"

        return state, pushup_correct_dict


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
