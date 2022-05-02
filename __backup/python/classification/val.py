# 검증
from tensorflow.keras.models import load_model
import mediapipe as mp
import cv2
import numpy as np
import imutils

import math
import time

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

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

ankle_state = True
def run(path, FITNESS_MODE):
    global ankle_state
    print(f"선택한 운동 : {FITNESS_MODE}")

    # 기본 변수
    runtime_list = []

    sel_keypoints = []
    delay = 1

    # Pose 객체 생성
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    # 자세 분류기 모델 불러오기
    if FITNESS_MODE == "PUSH_UP":  # 푸쉬업 모델
        left_pushup_model = load_model('model/left_pushup_model.h5')
        left_sel_keypoints = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW,
                               LEFT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE, LEFT_ANKLE]

        right_pushup_model = load_model('model/right_pushup_model.h5')
        right_sel_keypoints = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, RIGHT_ELBOW,
                              RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE]

    else:  # 스쿼트 모델
        model = load_model('model/squat_model.h5')
        sel_keypoints = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW,
                         LEFT_WRIST, RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE, RIGHT_KNEE,
                         LEFT_ANKLE, RIGHT_ANKLE]

    cap = cv2.VideoCapture(path)
    success = True
    while success:
        success, frame = cap.read()
        frame = imutils.resize(frame, width=750)  # frame 크기 조절

        # frame 처리과정
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # frame을 BGR에서 RGB로 변경(정확성 증가)
        results = pose.process(frame)  # pose.process는 RGB영상을 처리할때 가장 정확도가 높음
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # frame 원본 색상으로 복구

        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # 관절 좌표 저장
        if results.pose_landmarks != None:
            keypoints_x = []
            keypoints_y = []
            classifier_keypoints = []
            classifier_left_keypoints = []
            classifier_right_keypoints = []
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                keypoints_x.append(landmark.x)  # 실제좌표 : x * width
                keypoints_y.append(landmark.y)  # 실제좌표 : y * height

                # 자세 분류용 관절 좌표
                if FITNESS_MODE == "PUSH_UP":
                    if i in left_sel_keypoints:
                        classifier_left_keypoints.append(landmark.x)
                        classifier_left_keypoints.append(landmark.y)
                    if i in right_sel_keypoints:
                        classifier_right_keypoints.append(landmark.x)
                        classifier_right_keypoints.append(landmark.y)
                else:
                    if i in sel_keypoints:
                        classifier_keypoints.append(landmark.x)
                        classifier_keypoints.append(landmark.y)

            keypoints = list(zip(keypoints_x, keypoints_y))

            start = time.time()
            # 푸쉬업 카운터 및 자세교정
            if FITNESS_MODE == "PUSH_UP":
                left_keypoints_array = np.array([classifier_left_keypoints])
                right_keypoints_array = np.array([classifier_right_keypoints])

                # 푸쉬업
                if keypoints[LEFT_SHOULDER][0] > keypoints[NOSE][0] or keypoints[RIGHT_SHOULDER][0] > \
                        keypoints[NOSE][0]:
                    left_predict = left_pushup_model.predict(left_keypoints_array)

                    if np.argmax(left_predict[0]) == 0:  # UP 상태
                       print("LEFT_UP")
                    elif np.argmax(left_predict[0]) == 1:  # DOWN 상태
                       print("LEFT_DOWN")
                    else:  # NOTHING 상태
                       print("LEFT_NOTHING")
                else:
                    right_predict = right_pushup_model.predict(right_keypoints_array)

                    if np.argmax(right_predict[0]) == 0:  # UP 상태
                       print("RIGHT_UP")
                    elif np.argmax(right_predict[0]) == 1:  # DOWN 상태
                       print("RIGHT_DOWN")
                    else:  # NOTHING 상태
                       print("RIGHT_NOTHING")

            # 스쿼트
            else:
                keypoints_array = np.array([classifier_keypoints])
                predict = model.predict(keypoints_array)

                # --수정
                # ankle_distance_range = [-0.01, 0.04]
                #
                # # 발목 범위
                # right_shoulder_to_ankle = keypoints[RIGHT_SHOULDER][0] - keypoints[RIGHT_ANKLE][0]
                # left_shoulder_to_ankle = keypoints[LEFT_ANKLE][0] - keypoints[LEFT_SHOULDER][0]
                #
                # # 발목 자세 교정
                # if right_shoulder_to_ankle >= ankle_distance_range[0] and left_shoulder_to_ankle >= ankle_distance_range[0]:
                #     if right_shoulder_to_ankle <= ankle_distance_range[1] and left_shoulder_to_ankle <= \
                #             ankle_distance_range[1]:
                #         ankle_state = "pass"
                #     elif right_shoulder_to_ankle > ankle_distance_range[1] and left_shoulder_to_ankle > \
                #             ankle_distance_range[1]:
                #         ankle_state = "wide"
                # elif right_shoulder_to_ankle <= ankle_distance_range[0] and left_shoulder_to_ankle <= \
                #         ankle_distance_range[0]:
                #     ankle_state = "narrow"
                # else:

                # print(ankle_state,left_shoulder_to_ankle,right_shoulder_to_ankle )
                #--수정


                # Nothing 자세 정확도
                if predict[0][2] > 0.8:
                    squat_state = np.argmax(predict[0])
                else:
                    squat_state = np.argmax(predict[0][0:2])

                # # 스쿼트 자세
                # if squat_state == 0:    # UP 상태
                #    print("UP")
                # elif squat_state == 1:      # DOWN 상태
                #    print("DOWN")
                # else:       # NOTHING 상태
                #    print("NOTHING")

            end = time.time()
            runtime_list.append(end - start)
            # print(f"{end - start:.5f} sec")
    
        # 좌우 반전
        frame = cv2.flip(frame, 1)
        cv2.imshow("Smart Fitness", frame)

        # 입력 대기
        k = cv2.waitKey(delay)
        if k == 27:  # ESC 클릭 시(종료)
            print(f"평균 수행시간 : {sum(runtime_list)/len(runtime_list)}")
            exit()
        elif k == ord('p') or k == ord('P'):  # P 클릭 시(멈춤)
            if delay == 1:
                delay = 0
            else:
                delay = 1

    cap.release()

if __name__ == '__main__':
    # 경로 설정
    path = 0  # 캠
    # path = "video/squat/4.mp4"  # 동영상
    # path = "video/squat_test/2.mp4"
    # path = "video/push_up_test/5.mp4"

    # 운동 선택
    FITNESS_MODE = "SQUAT"
    # FITNESS_MODE = "PUSH_UP"



    run(path, FITNESS_MODE)
