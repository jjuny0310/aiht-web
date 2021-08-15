# 자세교정 기준값 추출
import cv2
import mediapipe as mp
import imutils
import math

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


# 관절 좌표 데이터셋 생성
def pose_correction(path, FITNESS_MODE):
    # Pose 객체 생성
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    # 관절 정보
    keypoints = []
    visibilitys = []

    # 다리 각도 변수
    leg_angle_list = []
    min_leg_angle = 999
    leg_angle_check = False

    # 발 각도 변수
    right_foot_angle_list = []
    left_foot_angle_list = []
    
    # 발목 범위 변수
    right_shoulder_to_ankle_list = []
    left_shoulder_to_ankle_list = []

    

    cap = cv2.VideoCapture(path)
    success = True
    while success:
        success, frame = cap.read()
        frame = imutils.resize(frame, width=1000)
        height, width, _ = frame.shape

        # Frame 처리
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # 관절 좌표 저장
        if results.pose_landmarks != None:
            keypoints_x = []
            keypoints_y = []
            visibilitys = []
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                keypoints_x.append(landmark.x)  # 실제좌표 : x * width
                keypoints_y.append(landmark.y)  # 실제좌표 : y * height
                visibilitys.append(landmark.visibility)

            keypoints = list(zip(keypoints_x, keypoints_y))

        if FITNESS_MODE == "SQUAT":
            # 다리 각도 저장
            leg_angle = getAngle3P(keypoints[LEFT_HIP], keypoints[LEFT_KNEE], keypoints[LEFT_ANKLE])
            if leg_angle <= 150:
                if min_leg_angle > leg_angle:
                    min_leg_angle = leg_angle
                else:
                    if leg_angle_check:
                        leg_angle_list.append(min_leg_angle)
                        min_leg_angle = 999
                        leg_angle_check = False
            else:
                leg_angle_check = True

            # 발 각도 저장
            right_foot_angle = getAngle3P(keypoints[RIGHT_FOOT_INDEX], keypoints[RIGHT_HEEL],
                                         [keypoints[RIGHT_HEEL][0], keypoints[RIGHT_FOOT_INDEX][1]])
            left_foot_angle = getAngle3P(keypoints[LEFT_FOOT_INDEX], keypoints[LEFT_HEEL],
                                          [keypoints[LEFT_HEEL][0], keypoints[LEFT_FOOT_INDEX][1]])
            right_foot_angle_list.append(right_foot_angle)
            left_foot_angle_list.append(left_foot_angle)
            
            # 발목 범위 저장
            right_shoulder_to_ankle = abs(keypoints[RIGHT_SHOULDER][0] - keypoints[RIGHT_ANKLE][0])
            left_shoulder_to_ankle = abs(keypoints[LEFT_SHOULDER][0] - keypoints[LEFT_ANKLE][0])
            right_shoulder_to_ankle_list.append(right_shoulder_to_ankle)
            left_shoulder_to_ankle_list.append(left_shoulder_to_ankle)




        elif FITNESS_MODE == "PUSH_UP":
            pass

        # Imshow
        frame = cv2.flip(frame, 1)
        cv2.imshow('Pose Correction', frame)
        k = cv2.waitKey(1)

        if k == 27:
            if FITNESS_MODE == "SQUAT":
                print(f"<'{FITNESS_MODE}' 트레이너 비디오 종합 결과>")
                print(f"평균 Down 다리 각도 : {round(sum(leg_angle_list) / len(leg_angle_list), 2)}°")
                print(f"왼발 각도 범위(최소~최대) : {round(min(left_foot_angle_list), 2)}° ~ {round(max(left_foot_angle_list), 2)}°")
                print(f"오른발 각도 범위(최소~최대) : {round(min(right_foot_angle_list), 2)}° ~ {round(max(right_foot_angle_list), 2)}°")
                print(f"왼쪽 어깨~발목 사이 거리(0~1) : {round(min(left_shoulder_to_ankle_list), 2)} ~ {round(max(left_shoulder_to_ankle_list), 2)}")
                print(f"오른쪽 어깨~발목 사이 거리(0~1) : {round(min(right_shoulder_to_ankle_list), 2)} ~ {round(max(right_shoulder_to_ankle_list), 2)}")
            elif FITNESS_MODE == "PUSH_UP":
                print(f"'{FITNESS_MODE}' 트레이너 비디오 종합 결과")


            break

    cap.release()


if __name__ == '__main__':
    # 트레이너 비디오
    path = "../../static/trainer video/1.mp4"

    # 운동 선택
    FITNESS_MODE = "SQUAT"
    # FITNESS_MODE = "PUSH_UP"

    pose_correction(path, FITNESS_MODE=FITNESS_MODE)
