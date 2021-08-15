# 자세교정 기준값 추출
import cv2
import mediapipe as mp
import imutils
import math

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


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
            print(keypoints)

        # 좌우 반전 상시
        if FITNESS_MODE == "SQUAT":
            # frame = cv2.flip(frame, 1)
            pass

        elif FITNESS_MODE == "PUSH_UP":
            pass

        # Imshow
        cv2.imshow('Keypoints DataSet Generate', frame)
        k = cv2.waitKey(1)
        if k == 27:
            break
        elif k == ord('s') or k == ord('S'):
            if save_state:
                save_state = False
            else:
                save_state = True

    cap.release()


if __name__ == '__main__':
    # 트레이너 비디오
    path = "../../static/trainer video/1.mp4"

    # 운동 선택
    FITNESS_MODE = "SQUAT"
    # FITNESS_MODE = "PUSH_UP"

    pose_correction(path, FITNESS_MODE=FITNESS_MODE)
