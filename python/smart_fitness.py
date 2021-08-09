from solutions import drawing_utils as mp_drawing
from solutions import pose as mp_pose
from solutions.pose import PoseLandmark as PL
from tensorflow.keras.models import load_model
from playsound import playsound
import threading
import cv2
import numpy as np
import imutils
import math

# 관절 TO 관절의 COLOR를 위한 변수
RIGHT_SHOULDER_TO_LEFT_SHOULDER = 0
RIGHT_SHOULDER_TO_RIGHT_ELBOW = 1
RIGHT_ELBOW_TO_RIGHT_WRIST = 2
RIGHT_WRIST_TO_RIGHT_PINKY = 3
RIGHT_WRIST_TO_RIGHT_INDEX = 4
RIGHT_WRIST_TO_RIGHT_THUMB = 5
RIGHT_PINKY_TO_RIGHT_INDEX = 6
LEFT_SHOULDER_TO_LEFT_ELBOW = 7
LEFT_ELBOW_TO_LEFT_WRIST = 8
LEFT_WRIST_TO_LEFT_PINKY = 9
LEFT_WRIST_TO_LEFT_INDEX = 10
LEFT_WRIST_TO_LEFT_THUMB = 11
LEFT_PINKY_TO_LEFT_INDEX = 12
RIGHT_SHOULDER_TO_RIGHT_HIP = 13
LEFT_SHOULDER_TO_LEFT_HIP = 14
RIGHT_HIP_TO_LEFT_HIP = 15
RIGHT_HIP_TO_RIGHT_KNEE = 16
LEFT_HIP_TO_LEFT_KNEE = 17
RIGHT_KNEE_TO_RIGHT_ANKLE = 18
LEFT_KNEE_TO_LEFT_ANKLE = 19
RIGHT_ANKLE_TO_RIGHT_HEEL = 20
LEFT_ANKLE_TO_LEFT_HEEL = 21
RIGHT_HEEL_TO_RIGHT_FOOT_INDEX = 22
LEFT_HEEL_TO_LEFT_FOOT_INDEX = 23
RIGHT_ANKLE_TO_RIGHT_FOOT_INDEX = 24
LEFT_ANKLE_TO_LEFT_FOOT_INDEX = 25

DOT_COLOR = (0, 255, 0)

LINE_COLOR = [[255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255],
              [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255],
              [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255],
              [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255],
              [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255]]


# 전체LINE 색상 변경
def setAllLineColor(b, g, r, except_parts=False):
    if except_parts:
        for i in range(len(LINE_COLOR)):
            if i not in [7, 8, 1, 2, 14, 13]:
                LINE_COLOR[i] = [b, g, r]
    else:
        for i in range(len(LINE_COLOR)):
            LINE_COLOR[i] = [b, g, r]


# 영상을 붙이는 함수
def showMultiImage(dst, src, h, w, d, col, row):
    # 3 color
    if d == 3:
        dst[(col * h):(col * h) + h, (row * w):(row * w) + w] = src[0:h, 0:w]
    # # 1 color
    # elif d == 1:
    #     dst[(col*h):(col*h)+h, (row*w):(row*w)+w, 0] = src[0:h, 0:w]
    #     dst[(col*h):(col*h)+h, (row*w):(row*w)+w, 1] = src[0:h, 0:w]
    #     dst[(col*h):(col*h)+h, (row*w):(row*w)+w, 2] = src[0:h, 0:w]


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


def run(path, FITNESS_MODE):
    print(f"선택한 운동 : {FITNESS_MODE}")

    # 기본 변수
    keypoints = []
    sel_keypoints = []
    delay = 1

    # 푸쉬업 변수
    pushup_arm_angle = 100
    pushup_count = 0
    pushup_check = False
    # correct_left_elbow = False
    # correct_right_elbow = False
    # correct_left_wrist = False
    # correct_right_wrist = False
    # correct_hip = False
    # pushup_correct_pose = False

    # 스쿼트 변수
    squat_down_angle = 130
    good_foot_angle = [25, 85]
    squat_count = 0
    squat_check = False
    # squat_state = 0
    # correct_right_knee = False
    # correct_left_knee = False
    # correct_right_ankle = False
    # correct_left_ankle = False
    squat_correct_pose = False

    # 사운드 변수
    sound_once = True

    # Pose 객체 생성
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    # 자세 분류기 모델 불러오기
    if FITNESS_MODE == "PUSH_UP":  # 푸쉬업 모델
        left_pushup_model = load_model('classification/model/left_pushup_model.h5')
        left_sel_keypoints = [PL.NOSE, PL.LEFT_SHOULDER, PL.RIGHT_SHOULDER, PL.RIGHT_ELBOW,
                              PL.RIGHT_WRIST, PL.LEFT_HIP, PL.RIGHT_HIP, PL.RIGHT_KNEE, PL.RIGHT_ANKLE]

        right_pushup_model = load_model('classification/model/right_pushup_model.h5')
        right_sel_keypoints = [PL.NOSE, PL.LEFT_SHOULDER, PL.RIGHT_SHOULDER, PL.LEFT_ELBOW,
                               PL.LEFT_WRIST, PL.LEFT_HIP, PL.RIGHT_HIP, PL.LEFT_KNEE, PL.LEFT_ANKLE]
    else:  # 스쿼트 모델
        model = load_model('classification/model/squat_model.h5')
        sel_keypoints = [PL.NOSE, PL.LEFT_SHOULDER, PL.RIGHT_SHOULDER, PL.LEFT_ELBOW, PL.RIGHT_ELBOW,
                         PL.LEFT_WRIST, PL.RIGHT_WRIST, PL.LEFT_HIP, PL.RIGHT_HIP, PL.LEFT_KNEE, PL.RIGHT_KNEE,
                         PL.LEFT_ANKLE, PL.RIGHT_ANKLE]

#######################################################################################################################
    cap = cv2.VideoCapture(path)
    success = True
    while success:
        success, frame = cap.read()

        frame = cv2.flip(frame, 1)  # 좌우반전
        frame = imutils.resize(frame, width=750)  # frame 크기 조절
        height, width, dim = frame.shape  # 높이, 너비, 차원
        origin_frame = frame.copy()  # 원본 프레임 복사

        dark_background = np.zeros(frame.shape, dtype=np.uint8)  # 검은색 배경화면 생성(3채널)

        # 점 세부스펙(color=(색상), thickness=굵기 , circle_radius=반지름)
        # 선 세부스펙(line_color=(색상[?]), thickness=굵기)
        dot_spec = mp_drawing.DrawingSpec(color=DOT_COLOR, thickness=4, circle_radius=2)
        line_spec = mp_drawing.DrawingSpec(line_color=LINE_COLOR, thickness=4)

        # frame 처리과정
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # frame을 BGR에서 RGB로 변경(정확성 증가)
        results = pose.process(frame)  # pose.process는 RGB영상을 처리할때 가장 정확도가 높음
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # frame 원본 색상으로 복구

        # 사람의 관절 점과 선 Draw
        # (frame, 관절 점, 관절 선, 점 스펙, 선 스펙)
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.FTNESS_POSE_CONNECTIONS, dot_spec, line_spec)
        mp_drawing.draw_landmarks(dark_background, results.pose_landmarks, mp_pose.FTNESS_POSE_CONNECTIONS, dot_spec,
                                  line_spec)  # 검은색 배경에도 Draw

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

            # 얼굴 가림막(임시)
            # face_x = int(keypoints[PL.NOSE][0] * width)
            # face_y = int(keypoints[PL.NOSE][1] * height)
            # cv2.circle(frame, (face_x, face_y), 50, [255, 0, 0], 50)

#######################################################################################################################
            # 푸쉬업 카운터 및 자세교정
            if FITNESS_MODE == "PUSH_UP":
                left_keypoints_array = np.array([classifier_left_keypoints])
                right_keypoints_array = np.array([classifier_right_keypoints])
                left_predict = left_pushup_model.predict(left_keypoints_array)
                right_predict = right_pushup_model.predict(right_keypoints_array)

                # up_left_percentage, down_left_percentage, nothing_left_percentage = left_predict[0]
                # up_right_percentage, down_right_percentage, nothing_right_percentage = right_predict[0]

                # 카운트 변수
                left_arm_angle = getAngle3P(keypoints[PL.RIGHT_SHOULDER], keypoints[PL.RIGHT_ELBOW],
                                            keypoints[PL.RIGHT_WRIST])  # 왼팔 각도
                right_arm_angle = getAngle3P(keypoints[PL.LEFT_SHOULDER], keypoints[PL.LEFT_ELBOW],
                                             keypoints[PL.LEFT_WRIST])  # 오른팔 각도

                # 자세교정 변수
                good_left_hip_range = [keypoints[PL.RIGHT_SHOULDER][1] - 30 / height,
                                       keypoints[PL.RIGHT_SHOULDER][1] + 50 / height]

                good_right_hip_range = [keypoints[PL.LEFT_SHOULDER][1] - 30 / height,
                                       keypoints[PL.LEFT_SHOULDER][1] + 50 / height]

                # hip 좌표
                left_hip_px = int(keypoints[PL.RIGHT_HIP][0] * width)
                left_hip_py = int(keypoints[PL.RIGHT_HIP][1] * height)
                right_hip_px = int(keypoints[PL.LEFT_HIP][0] * width)
                right_hip_py = int(keypoints[PL.LEFT_HIP][1] * height)
                
                # 푸쉬업 현재 개수 출력
                pushup_str = "PUSH_UP COUNT : " + str(pushup_count)
                cv2.putText(frame, pushup_str, (20, 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                # 푸쉬업 상태
                if keypoints[PL.LEFT_SHOULDER][0] < keypoints[PL.NOSE][0] or \
                        keypoints[PL.RIGHT_SHOULDER][0] < keypoints[PL.NOSE][0]:  # 캠에 내 왼쪽이 보인다면
                    if np.argmax(left_predict[0]) == 0:  # UP 상태
                        setAllLineColor(255, 255, 255)

                        # 푸쉬업 자세교정
                        if keypoints[PL.RIGHT_SHOULDER][1] < keypoints[PL.RIGHT_ELBOW][1]:  # 팔꿈치
                            LINE_COLOR[RIGHT_SHOULDER_TO_RIGHT_ELBOW] = [255, 255, 255]
                            correct_left_elbow = True
                        else:
                            LINE_COLOR[RIGHT_SHOULDER_TO_RIGHT_ELBOW] = [0, 0, 255]
                            correct_left_elbow = False

                        if keypoints[PL.LEFT_SHOULDER][1] < keypoints[PL.LEFT_ELBOW][1]:
                            LINE_COLOR[LEFT_SHOULDER_TO_LEFT_ELBOW] = [255, 255, 255]
                            correct_right_elbow = True
                        else:
                            LINE_COLOR[LEFT_SHOULDER_TO_LEFT_ELBOW] = [0, 0, 255]
                            correct_right_elbow = False

                        if keypoints[PL.RIGHT_SHOULDER][1] < keypoints[PL.RIGHT_WRIST][1]:  # 손목
                            LINE_COLOR[RIGHT_ELBOW_TO_RIGHT_WRIST] = [255, 255, 255]
                            correct_left_wrist = True
                        else:
                            LINE_COLOR[RIGHT_ELBOW_TO_RIGHT_WRIST] = [0, 0, 255]
                            correct_left_wrist = False

                        if keypoints[PL.LEFT_SHOULDER][1] < keypoints[PL.LEFT_WRIST][1]:
                            LINE_COLOR[LEFT_ELBOW_TO_LEFT_WRIST] = [255, 255, 255]
                            correct_right_wrist = True
                        else:
                            LINE_COLOR[LEFT_ELBOW_TO_LEFT_WRIST] = [0, 0, 255]
                            correct_right_wrist = False

                        if good_left_hip_range[0] < keypoints[PL.RIGHT_HIP][1] < good_left_hip_range[1] or \
                            good_right_hip_range[0] < keypoints[PL.LEFT_HIP][1] < good_right_hip_range[1]:  # 엉덩이
                            LINE_COLOR[RIGHT_HIP_TO_LEFT_HIP] = [255, 255, 255]

                            # hip dot
                            cv2.circle(frame, (left_hip_px, left_hip_py), 2, [0, 255, 0], 4)
                            cv2.circle(frame, (right_hip_px, right_hip_py), 2, [0, 255, 0], 4)
                            cv2.circle(dark_background, (left_hip_px, left_hip_py), 2, [0, 255, 0], 4)
                            cv2.circle(dark_background, (right_hip_px, right_hip_py), 2, [0, 255, 0], 4)
                            correct_hip = True
                        else:
                            LINE_COLOR[RIGHT_HIP_TO_LEFT_HIP] = [0, 0, 255]

                            cv2.circle(frame, (left_hip_px, left_hip_py), 2, [0, 0, 255], 5)
                            cv2.circle(frame, (right_hip_px, right_hip_py), 2, [0, 0, 255], 5)
                            cv2.circle(dark_background, (left_hip_px, left_hip_py), 2, [0, 0, 255], 5)
                            cv2.circle(dark_background, (right_hip_px, right_hip_py), 2, [0, 0, 255], 5)
                            correct_hip = False

                        # 자세 판단
                        if correct_left_elbow and correct_right_elbow and correct_left_wrist and correct_right_wrist and correct_hip:
                            pushup_correct_pose = True
                        else:
                            pushup_correct_pose = False
                            pushup_check = False

                        # 푸쉬업 카운트 조건
                        if pushup_check and pushup_correct_pose:
                            pushup_count += 1
                            pushup_check = False
                            sound_once = True

                        print("LEFT_UP")
                    elif np.argmax(left_predict[0]) == 1:  # DOWN 상태
                        setAllLineColor(255, 255, 255)
                        # squat_angle 만큼 내려가야 카운트 준비
                        if left_arm_angle < pushup_arm_angle:
                            pushup_check = True
                            if sound_once:
                                try:
                                    playsound("sound/check_sound.wav", block=False)
                                    sound_once = False
                                except:
                                    print('\033[31m' + '스피커 연결을 확인해주세요' + '\033[0m')
                                    sound_once = False
                        print("LEFT_DOWN")
                    else:  # NOTHING 상태
                        setAllLineColor(0, 0, 255)
                        cv2.circle(frame, (left_hip_px, left_hip_py), 2, [0, 255, 0], 4)
                        cv2.circle(frame, (right_hip_px, right_hip_py), 2, [0, 255, 0], 4)
                        cv2.circle(dark_background, (left_hip_px, left_hip_py), 2, [0, 255, 0], 4)
                        cv2.circle(dark_background, (right_hip_px, right_hip_py), 2, [0, 255, 0], 4)

                        pushup_check = False
                        print("LEFT_NOTHING")
                # 캠에 내 오른쪽이 보인다면
                else:
                    if np.argmax(right_predict[0]) == 0:  # UP 상태
                        setAllLineColor(255, 255, 255)

                        # 푸쉬업 자세교정
                        if keypoints[PL.RIGHT_SHOULDER][1] < keypoints[PL.RIGHT_ELBOW][1]:  # 팔꿈치
                            LINE_COLOR[RIGHT_SHOULDER_TO_RIGHT_ELBOW] = [255, 255, 255]
                            correct_left_elbow = True
                        else:
                            LINE_COLOR[RIGHT_SHOULDER_TO_RIGHT_ELBOW] = [0, 0, 255]
                            correct_left_elbow = False

                        if keypoints[PL.LEFT_SHOULDER][1] < keypoints[PL.LEFT_ELBOW][1]:
                            LINE_COLOR[LEFT_SHOULDER_TO_LEFT_ELBOW] = [255, 255, 255]
                            correct_right_elbow = True
                        else:
                            LINE_COLOR[LEFT_SHOULDER_TO_LEFT_ELBOW] = [0, 0, 255]
                            correct_right_elbow = False

                        if keypoints[PL.RIGHT_SHOULDER][1] < keypoints[PL.RIGHT_WRIST][1]:  # 손목
                            LINE_COLOR[RIGHT_ELBOW_TO_RIGHT_WRIST] = [255, 255, 255]
                            correct_left_wrist = True
                        else:
                            LINE_COLOR[RIGHT_ELBOW_TO_RIGHT_WRIST] = [0, 0, 255]
                            correct_left_wrist = False

                        if keypoints[PL.LEFT_SHOULDER][1] < keypoints[PL.LEFT_WRIST][1]:
                            LINE_COLOR[LEFT_ELBOW_TO_LEFT_WRIST] = [255, 255, 255]
                            correct_right_wrist = True
                        else:
                            LINE_COLOR[LEFT_ELBOW_TO_LEFT_WRIST] = [0, 0, 255]
                            correct_right_wrist = False

                        if good_left_hip_range[0] < keypoints[PL.RIGHT_HIP][1] < good_left_hip_range[1] or \
                            good_right_hip_range[0] < keypoints[PL.LEFT_HIP][1] < good_right_hip_range[1]:  # 엉덩이
                            LINE_COLOR[RIGHT_HIP_TO_LEFT_HIP] = [255, 255, 255]

                            # hip dot
                            cv2.circle(frame, (left_hip_px, left_hip_py), 2, [0, 255, 0], 4)
                            cv2.circle(frame, (right_hip_px, right_hip_py), 2, [0, 255, 0], 4)
                            cv2.circle(dark_background, (left_hip_px, left_hip_py), 2, [0, 255, 0], 4)
                            cv2.circle(dark_background, (right_hip_px, right_hip_py), 2, [0, 255, 0], 4)
                            correct_hip = True
                        else:
                            LINE_COLOR[RIGHT_HIP_TO_LEFT_HIP] = [0, 0, 255]
                            cv2.circle(frame, (left_hip_px, left_hip_py), 2, [0, 0, 255], 5)
                            cv2.circle(frame, (right_hip_px, right_hip_py), 2, [0, 0, 255], 5)
                            cv2.circle(dark_background, (left_hip_px, left_hip_py), 2, [0, 0, 255], 5)
                            cv2.circle(dark_background, (right_hip_px, right_hip_py), 2, [0, 0, 255], 5)
                            correct_hip = False

                        # 자세 판단
                        if correct_left_elbow and correct_right_elbow and correct_left_wrist and correct_right_wrist and correct_hip:
                            pushup_correct_pose = True
                        else:
                            pushup_correct_pose = False
                            pushup_check = False

                        # 푸쉬업 카운트 조건
                        if pushup_check and pushup_correct_pose:
                            pushup_count += 1
                            pushup_check = False
                            sound_once = True
                            # print(F"푸쉬업 갯수: {pushup_count}")
                        print("RIGHT_UP")
                    elif np.argmax(right_predict[0]) == 1:  # DOWN 상태
                        setAllLineColor(255, 255, 255)
                        # squat_angle 만큼 내려가야 카운트 준비
                        if right_arm_angle < pushup_arm_angle:
                            pushup_check = True
                            if sound_once:
                                try:
                                    playsound("sound/check_sound.wav", block=False)
                                    sound_once = False
                                except:
                                    print('\033[31m' + '스피커 연결을 확인해주세요' + '\033[0m')
                                    sound_once = False
                        print("RIGHT_DOWN")
                    else:  # NOTHING 상태
                        setAllLineColor(0, 0, 255)
                        cv2.circle(frame, (left_hip_px, left_hip_py), 2, [0, 255, 0], 4)
                        cv2.circle(frame, (right_hip_px, right_hip_py), 2, [0, 255, 0], 4)
                        cv2.circle(dark_background, (left_hip_px, left_hip_py), 2, [0, 255, 0], 4)
                        cv2.circle(dark_background, (right_hip_px, right_hip_py), 2, [0, 255, 0], 4)

                        pushup_check = False
                        print("RIGHT_NOTHING")

#######################################################################################################################
            # 스쿼트 카운터 및 자세교정
            else:
                keypoints_array = np.array([classifier_keypoints])
                predict = model.predict(keypoints_array)
                # up_percentage, down_percentage, nothing_percentage = predict[0]
                # print(f"{round(up_percentage, 4)} / {round(down_percentage, 4)}")

                left_leg_angle = getAngle3P(keypoints[PL.RIGHT_HIP], keypoints[PL.RIGHT_KNEE],
                                            keypoints[PL.RIGHT_ANKLE])
                right_leg_angle = getAngle3P(keypoints[PL.LEFT_HIP], keypoints[PL.LEFT_KNEE], keypoints[PL.LEFT_ANKLE])
                
                # 자세 교정 변수
                good_right_knee_ragne = [keypoints[PL.LEFT_SHOULDER][0] - 60 / width,
                                         keypoints[PL.LEFT_SHOULDER][0] + 60 / width]
                good_left_knee_ragne = [keypoints[PL.RIGHT_SHOULDER][0] - 60 / width,
                                        keypoints[PL.RIGHT_SHOULDER][0] + 60 / width]

                good_right_ankle_ragne = [keypoints[PL.LEFT_SHOULDER][0] - 40 / width,
                                          keypoints[PL.LEFT_SHOULDER][0] + 40 / width]
                good_left_ankle_ragne = [keypoints[PL.RIGHT_SHOULDER][0] - 40 / width,
                                         keypoints[PL.RIGHT_SHOULDER][0] + 40 / width]

                left_foot_angle = getAngle3P(keypoints[PL.RIGHT_FOOT_INDEX], keypoints[PL.RIGHT_HEEL],
                                             [keypoints[PL.RIGHT_HEEL][0], keypoints[PL.RIGHT_FOOT_INDEX][1]])

                right_foot_angle = getAngle3P(keypoints[PL.LEFT_FOOT_INDEX], keypoints[PL.LEFT_HEEL],
                                             [keypoints[PL.LEFT_HEEL][0], keypoints[PL.LEFT_FOOT_INDEX][1]])

                # 스쿼트 현재 갯수 출력
                squat_str = "SQUAT COUNT : " + str(squat_count)
                cv2.putText(frame, squat_str, (20, 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

                # Nothing 자세 정확도
                if predict[0][2] > 0.8:
                    squat_state = np.argmax(predict[0])
                else:
                    squat_state = np.argmax(predict[0][0:2])

                # 스쿼트 자세
                if squat_state == 0:    # UP 상태
                    setAllLineColor(255, 255, 255)

                    # 오른쪽 무릎 자세 교정
                    if good_right_knee_ragne[0] < keypoints[PL.LEFT_KNEE][0] < good_right_knee_ragne[1]:
                        # 바른 자세
                        correct_right_knee = True
                        LINE_COLOR[LEFT_HIP_TO_LEFT_KNEE] = [255, 255, 255]
                    else:
                        # 틀린 자세
                        correct_right_knee = False
                        LINE_COLOR[LEFT_HIP_TO_LEFT_KNEE] = [0, 0, 255]

                    # 왼쪽 무릎 자세 교정
                    if good_left_knee_ragne[0] < keypoints[PL.RIGHT_KNEE][0] < good_left_knee_ragne[1]:
                        correct_left_knee = True
                        LINE_COLOR[RIGHT_HIP_TO_RIGHT_KNEE] = [255, 255, 255]
                    else:
                        correct_left_knee = False
                        LINE_COLOR[RIGHT_HIP_TO_RIGHT_KNEE] = [0, 0, 255]

                    # 오른쪽 발목 자세 교정
                    if good_right_ankle_ragne[0] < keypoints[PL.LEFT_ANKLE][0] < good_right_ankle_ragne[1]:
                        correct_right_ankle = True
                        LINE_COLOR[LEFT_KNEE_TO_LEFT_ANKLE] = [255, 255, 255]
                    else:
                        correct_right_ankle = False
                        LINE_COLOR[LEFT_KNEE_TO_LEFT_ANKLE] = [0, 0, 255]

                    # 왼쪽 발목 자세 교정
                    if good_left_ankle_ragne[0] < keypoints[PL.RIGHT_ANKLE][0] < good_left_ankle_ragne[1]:
                        correct_left_ankle = True
                        LINE_COLOR[RIGHT_KNEE_TO_RIGHT_ANKLE] = [255, 255, 255]
                    else:
                        correct_left_ankle = False
                        LINE_COLOR[RIGHT_KNEE_TO_RIGHT_ANKLE] = [0, 0, 255]

                    # 왼쪽 발 각도
                    if good_foot_angle[0] < left_foot_angle < good_foot_angle[1] and keypoints[PL.RIGHT_FOOT_INDEX][0] < \
                            keypoints[PL.RIGHT_HEEL][0]:
                        correct_left_foot = True
                        LINE_COLOR[RIGHT_HEEL_TO_RIGHT_FOOT_INDEX] = [255, 255, 255]
                        LINE_COLOR[RIGHT_ANKLE_TO_RIGHT_HEEL] = [255, 255, 255]
                        LINE_COLOR[RIGHT_ANKLE_TO_RIGHT_FOOT_INDEX] = [255, 255, 255]
                    else:
                        correct_left_foot = False
                        LINE_COLOR[RIGHT_HEEL_TO_RIGHT_FOOT_INDEX] = [0, 0, 255]
                        LINE_COLOR[RIGHT_ANKLE_TO_RIGHT_HEEL] = [0, 0, 255]
                        LINE_COLOR[RIGHT_ANKLE_TO_RIGHT_FOOT_INDEX] = [0, 0, 255]

                    # 오른쪽 발 각도
                    if good_foot_angle[0] < right_foot_angle < good_foot_angle[1] and keypoints[PL.LEFT_FOOT_INDEX][0] > \
                            keypoints[PL.LEFT_HEEL][0]:
                        correct_right_foot = True
                        LINE_COLOR[LEFT_HEEL_TO_LEFT_FOOT_INDEX] = [255, 255, 255]
                        LINE_COLOR[LEFT_ANKLE_TO_LEFT_HEEL] = [255, 255, 255]
                        LINE_COLOR[LEFT_ANKLE_TO_LEFT_FOOT_INDEX] = [255, 255, 255]
                    else:
                        correct_right_foot = False
                        LINE_COLOR[LEFT_HEEL_TO_LEFT_FOOT_INDEX] = [0, 0, 255]
                        LINE_COLOR[LEFT_ANKLE_TO_LEFT_HEEL] = [0, 0, 255]
                        LINE_COLOR[LEFT_ANKLE_TO_LEFT_FOOT_INDEX] = [0, 0, 255]

                    # 최종 스쿼트 자세 판단
                    if correct_right_knee and correct_left_knee and correct_right_ankle and correct_left_ankle and correct_left_foot and correct_right_foot:
                        squat_correct_pose = True
                    else:
                        squat_correct_pose = False

                    if squat_check and squat_correct_pose and left_leg_angle > 170 and right_leg_angle > 170:
                        squat_count += 1
                        squat_check = False
                        sound_once = True
                        # print(F"스쿼트 갯수: {squat_count}")
                    print("UP")

                elif squat_state == 1:      # DOWN 상태
                    setAllLineColor(255, 255, 255)
                    
                    # squat_angle 만큼 내려가야 카운트 준비
                    if right_leg_angle < squat_down_angle and left_leg_angle < squat_down_angle and squat_correct_pose:
                        squat_check = True
                        if sound_once:
                            try:
                                playsound("sound/check_sound.wav", block=False)
                                sound_once = False
                            except:
                                print('\033[31m' + '스피커 연결을 확인해주세요' + '\033[0m')
                                sound_once = False
                    print("DOWN")
                else:       # NOTHING 상태
                    setAllLineColor(0, 0, 255)
                    print("NOTHING")
#######################################################################################################################
        # 각각 가중치를 원본프레임 0.6, 선이있는 frame 0.4 만큼 주어서 자연스럽게 영상 조정
        frame = cv2.addWeighted(origin_frame, 0.6, frame, 0.4, 0)

        # 두 영상을 이어붙일 프레임 생성
        dstframe = np.zeros((height, width * 2, dim), np.uint8)

        # 두 영상 붙이기
        showMultiImage(dstframe, frame, height, width, dim, 0, 0)
        showMultiImage(dstframe, dark_background, height, width, dim, 0, 1)
        cv2.imshow("Smart Fitness", dstframe)

        # 입력 대기
        k = cv2.waitKey(delay)
        if k == 27:  # ESC 클릭 시(종료)
            exit()
        elif k == ord('p') or k == ord('P'):  # P 클릭 시(멈춤)
            if delay == 1:
                delay = 0
            else:
                delay = 1

    cap.release()

#######################################################################################################################
if __name__ == '__main__':
    # 경로 설정
    path = 0  # 캠
    # path = "video_data/video2.mp4"                   # 동영상
    # path = "classification/video/push_up/3.mp4"  # 동영상

    # 운동 선택
    # FITNESS_MODE = "PUSH_UP"
    FITNESS_MODE = "SQUAT"

    run(path, FITNESS_MODE)
