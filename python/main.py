from aiht import session
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
squat_parts = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW,
               LEFT_WRIST, RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE, RIGHT_KNEE,
               LEFT_ANKLE, RIGHT_ANKLE]
pushup_left_parts = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW,
                      LEFT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE, LEFT_ANKLE]
pushup_right_parts = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, RIGHT_ELBOW,
                     RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE]

# 모델 경로
squat_model = load_model('python/classification/model/squat_model.h5')
pushup_left_model = load_model('python/classification/model/left_pushup_model.h5')
pushup_right_model = load_model('python/classification/model/right_pushup_model.h5')

# 스쿼트 자세 교정 수치
squat_up_angle = 160
squat_down_angle = 110
foot_angle_range = [20, 70]
ankle_distance_range = [-0.01, 0.04]

# 푸쉬업 자세 교정 수치
pushup_up_angle = 150
pushup_down_angle = 110
hip_distance_range = [0, 0.15]
min_hand_angle = 130

# 안내 음성 최소 신뢰도 값
squat_visibility_rate = 0.3
pushup_visibility_rate = 0.6


def run(exercise_type, pose_landmarks):
    squat_count = session['pushup_count']
    pushup_count = session['pushup_pose']

    # 관절 좌표 저장 변수(x, y)
    keypoints_x = []
    keypoints_y = []

    # 포즈 분류 모델 input 변수
    squat_input = []
    pushup_left_input = []
    pushup_right_input = []
    
    # 신뢰도 값 저장 변수(visibility)
    visibilitys_squat = []
    visibilitys_pushup_left = []
    visibilitys_pushup_right = []

    for idx, landmark in enumerate(pose_landmarks):
        # 관절 좌표 저장
        keypoints_x.append(landmark['x'])
        keypoints_y.append(landmark['y'])

        if exercise_type == "SQUAT":
            # 스쿼트 포즈 분류 모델 input 저장
            if idx in squat_parts:
                squat_input.append(landmark['x'])
                squat_input.append(landmark['y'])

            # 스쿼트 신뢰도 값 저장
            if idx in squat_parts[7:]:
                visibilitys_squat.append(landmark['visibility'])

        if exercise_type == "PUSH_UP":
            # 푸쉬업(L, R) 포즈 분류 모델 input 저장
            if idx in pushup_left_parts:
                pushup_left_input.append(landmark['x'])
                pushup_left_input.append(landmark['y'])
            if idx in pushup_right_parts:
                pushup_right_input.append(landmark['x'])
                pushup_right_input.append(landmark['y'])

            # 푸쉬업(L, R) 신뢰도 값 저장
            if idx in list(set(pushup_left_parts) - {RIGHT_SHOULDER, RIGHT_HIP}):
                visibilitys_pushup_left.append(landmark['visibility'])
            if idx in list(set(pushup_right_parts) - {LEFT_SHOULDER, LEFT_HIP}):
                visibilitys_pushup_right.append(landmark['visibility'])

    # 관절 좌표 최종 저장
    keypoints = list(zip(keypoints_x, keypoints_y))

    # 스쿼트 처리
    if exercise_type == "SQUAT":
        visibility_count = 0
        visibility_check = False

        # 신뢰도 값 체크(모든 관절이 정확히 나오면 자세교정 사운드 출력 가능)
        for v in visibilitys_squat:
            if v > squat_visibility_rate:
                visibility_count += 1
            if visibility_count == len(squat_parts[7:]):
                visibility_check = True

        # 포즈 분류 모델 추론(스쿼트)
        predict = squat_model.predict(np.array([squat_input]))

        # 다리 각도
        right_leg_angle = getAngle3P(keypoints[RIGHT_HIP], keypoints[RIGHT_KNEE],
                                    keypoints[RIGHT_ANKLE])
        left_leg_angle = getAngle3P(keypoints[LEFT_HIP], keypoints[LEFT_KNEE], keypoints[LEFT_ANKLE])

        # 발 각도
        right_foot_angle = getAngle3P(keypoints[RIGHT_FOOT_INDEX], keypoints[RIGHT_HEEL],
                                     [keypoints[RIGHT_HEEL][0], keypoints[RIGHT_FOOT_INDEX][1]])

        left_foot_angle = getAngle3P(keypoints[LEFT_FOOT_INDEX], keypoints[LEFT_HEEL],
                                      [keypoints[LEFT_HEEL][0], keypoints[LEFT_FOOT_INDEX][1]])

        # 어깨 ~ 발목 거리(x 좌표)
        right_shoulder_to_ankle = keypoints[RIGHT_SHOULDER][0] - keypoints[RIGHT_ANKLE][0]
        left_shoulder_to_ankle = keypoints[LEFT_ANKLE][0] - keypoints[LEFT_SHOULDER][0]
        
        # 스쿼트 자세 결과 저장 변수
        squat_result = {}

        # Nothing 자세 기준 정확도
        if predict[0][2] > 0.8:
            squat_state = np.argmax(predict[0])
        else:
            squat_state = np.argmax(predict[0][0:2])

        # 스쿼트 자세 분류
        # UP
        if squat_state == 0:
            state = "UP"

            # 발 각도 체크
            if foot_angle_range[0] <= left_foot_angle <= foot_angle_range[1] and keypoints[LEFT_FOOT_INDEX][0] > keypoints[LEFT_HEEL][0] \
                    and foot_angle_range[0] <= right_foot_angle <= foot_angle_range[1] and keypoints[RIGHT_FOOT_INDEX][0] < keypoints[RIGHT_HEEL][0]:
                foot_state = "pass"

            else:
                if foot_angle_range[0] > left_foot_angle or foot_angle_range[0] > right_foot_angle or keypoints[LEFT_FOOT_INDEX][0] <= keypoints[LEFT_HEEL][0] or \
                        keypoints[RIGHT_FOOT_INDEX][0] >= keypoints[RIGHT_HEEL][0]:
                    foot_state = "narrow"
                else:
                    foot_state = "wide"

            # 어깨 ~ 발목 거리 체크
            ankle_state = "pass"
            if right_shoulder_to_ankle >= ankle_distance_range[0] and left_shoulder_to_ankle >= ankle_distance_range[0]:
                if right_shoulder_to_ankle <= ankle_distance_range[1] and left_shoulder_to_ankle <= \
                        ankle_distance_range[1]:
                    ankle_state = "pass"
                elif right_shoulder_to_ankle > ankle_distance_range[1] and left_shoulder_to_ankle > \
                        ankle_distance_range[1]:
                    ankle_state = "wide"
            elif right_shoulder_to_ankle <= ankle_distance_range[0] and left_shoulder_to_ankle <= \
                    ankle_distance_range[0]:
                ankle_state = "narrow"
            else:
                pass

            # 스쿼트 자세 결과 저장
            squat_result = {"ankle_state": ankle_state, 'foot_state': foot_state}

            # 스쿼트 자세 올바른지 판별 및 카운터
            if foot_state == "pass" and ankle_state == "pass":
                session['squat_pose'] = True
            else:
                session['squat_pose'] = False
                session['squat_count_check'] = False

            if session['squat_pose'] and session['squat_count_check'] and left_leg_angle > squat_up_angle and right_leg_angle > squat_up_angle:
                squat_count += 1
                session['squat_count_check'] = False

        # DOWN
        elif squat_state == 1:
            state = "DOWN"
            if session['squat_pose'] and right_leg_angle < squat_down_angle and left_leg_angle < squat_down_angle:
                session['squat_count_check'] = True

        # NOTHING
        else:
            state = "NOTHING"
            session['squat_pose'] = False
            session['squat_count_check'] = False

        return state, squat_result, visibility_check, squat_count

    # 푸쉬업
    if exercise_type == "PUSH_UP":
        # 푸쉬업 자세 결과 저장 변수
        pushup_result = {}

        # 푸쉬업(L)
        if keypoints[LEFT_SHOULDER][0] > keypoints[NOSE][0] or keypoints[RIGHT_SHOULDER][0] > \
                keypoints[NOSE][0]:
            visibility_count = 0
            visibility_check = False

            # 신뢰도 값 체크(모든 관절이 정확히 나오면 자세 교정 사운드 출력 가능)
            for v in visibilitys_pushup_left:
                if v > pushup_visibility_rate:
                    visibility_count += 1
                if visibility_count == len(list(set(pushup_left_parts) - {RIGHT_SHOULDER, RIGHT_HIP})):
                    visibility_check = True

            # 포즈 분류 모델 추론(푸쉬업 L)
            predict = pushup_left_model.predict(np.array([pushup_left_input]))

            # 팔의 각도
            left_arm_angle = getAngle3P(keypoints[LEFT_SHOULDER], keypoints[LEFT_ELBOW],
                                        keypoints[LEFT_WRIST])

            # 손의 각도
            left_hand_angle = getAngle3P(keypoints[LEFT_ELBOW], keypoints[LEFT_WRIST], keypoints[LEFT_INDEX])

            # 엉덩이 ~ 어깨 거리(y 좌표)
            shoulder_to_hip = abs(keypoints[LEFT_SHOULDER][1] - keypoints[LEFT_HIP][1])

            # UP
            if np.argmax(predict[0]) == 0:
                state = "UP"
                
                # 푸쉬업(L) 자세교정
                # 손 방향 체크
                if keypoints[LEFT_PINKY][0] < keypoints[LEFT_WRIST][0] and \
                   keypoints[LEFT_INDEX][0] < keypoints[LEFT_WRIST][0] and \
                   keypoints[LEFT_THUMB][0] < keypoints[LEFT_WRIST][0] and left_hand_angle < min_hand_angle:
                    hand_state = True
                else:
                    hand_state = False
                
                # 엉덩이 ~ 어깨 거리 체크
                if hip_distance_range[0] <= shoulder_to_hip <= hip_distance_range[1] and keypoints[LEFT_SHOULDER][1] <= keypoints[LEFT_HIP][1]:
                    hip_state = True
                else:
                    hip_state = False
                
                # 푸쉬업(L) 자세 결과 저장
                pushup_result = {'hand_state': hand_state, 'hip_state': hip_state}

                # 푸쉬업(L) 자세 올바른지 판별 및 카운터
                if hand_state and hip_state:
                    session['pushup_pose'] = True
                else:
                    session['pushup_pose'] = False
                    session['pushup_count_check'] = False

                if session['pushup_pose'] and session['pushup_count_check'] and left_arm_angle > pushup_up_angle:
                    pushup_count += 1
                    session['pushup_count_check'] = False

            # DOWN
            elif np.argmax(predict[0]) == 1:
                state = "DOWN"
                if session['pushup_pose'] and left_arm_angle < pushup_down_angle:
                    session['pushup_count_check'] = True

            # NOTHING
            else:
                state = "NOTHING"
                session['pushup_pose'] = False
                session['pushup_count_check'] = False
        
        # 푸쉬업(R)
        else:
            visibility_count = 0
            visibility_check = False

            # 신뢰도 값 체크(모든 관절이 정확히 나오면 자세교정 사운드 출력 가능)
            for v in visibilitys_pushup_right:
                if v > pushup_visibility_rate:
                    visibility_count += 1
                if visibility_count == len(list(set(pushup_right_parts) - {LEFT_SHOULDER, LEFT_HIP})):
                    visibility_check = True

            # 포즈 분류 모델 추론(푸쉬업 R)
            predict = pushup_right_model.predict(np.array([pushup_right_input]))

            # 팔의 각도
            right_arm_angle = getAngle3P(keypoints[RIGHT_SHOULDER], keypoints[RIGHT_ELBOW],
                                        keypoints[RIGHT_WRIST])

            # 손의 각도
            right_hand_angle = getAngle3P(keypoints[RIGHT_ELBOW], keypoints[RIGHT_WRIST], keypoints[RIGHT_INDEX])

            # 엉덩이 범위
            shoulder_to_hip = abs(keypoints[RIGHT_SHOULDER][1] - keypoints[RIGHT_HIP][1])

            # UP
            if np.argmax(predict[0]) == 0:
                state = "UP"

                # 푸쉬업(R) 자세교정
                # 손 방향 체크
                if keypoints[RIGHT_PINKY][0] > keypoints[RIGHT_WRIST][0] and\
                   keypoints[RIGHT_INDEX][0] > keypoints[RIGHT_WRIST][0] and \
                   keypoints[RIGHT_THUMB][0] > keypoints[RIGHT_WRIST][0] and right_hand_angle < min_hand_angle:
                    hand_state = True
                else:
                    hand_state = False

                # 엉덩이 ~ 어깨 거리 체크
                if hip_distance_range[0] <= shoulder_to_hip <= hip_distance_range[1] and keypoints[RIGHT_SHOULDER][1] <= keypoints[RIGHT_HIP][1]:
                    hip_state = True
                else:
                    hip_state = False
                
                # 푸쉬업(R) 자세 결과 저장
                pushup_result = {'hand_state': hand_state, 'hip_state': hip_state}

                # 푸쉬업(R) 자세 판별
                if hand_state and hip_state:
                    session['pushup_pose'] = True
                else:
                    session['pushup_pose'] = False
                    session['pushup_count_check'] = False

                if session['pushup_pose'] and session['pushup_count_check'] and right_arm_angle > pushup_up_angle:
                    session['pushup_count'] += 1
                    session['pushup_count_check'] = False

            # DOWN
            elif np.argmax(predict[0]) == 1:
                state = "DOWN"
                if session['pushup_pose'] and right_arm_angle < pushup_down_angle:
                    session['pushup_count_check'] = True

            # NOTHING
            else:
                state = "NOTHING"
                session['pushup_pose'] = False
                session['pushup_count_check'] = False

        return state, pushup_result, visibility_check, pushup_count


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
