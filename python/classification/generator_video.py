import cv2
import mediapipe as mp
import csv
import threading
import imutils

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def init_variable(FITNESS_MODE):
    global keypoints_name
    global sel_keypoints
    global keypoints_num

    if FITNESS_MODE == "LEFT_PUSH_UP":
        keypoints_name = ['nose_x', 'nose_y',
                          'left_shoulder_x', 'left_shoulder_y',
                          'right_shoulder_x', 'right_shoulder_y',
                          'left_elbow_x', 'left_elbow_y',
                          'left_wrist_x', 'left_wrist_y',
                          'left_hip_x', 'left_hip_y',
                          'right_hip_x', 'right_hip_y',
                          'left_knee_x', 'left_knee_y',
                          'left_ankle_x', 'left_ankle_y']

        sel_keypoints = [0, 11, 12, 13, 15, 23, 24, 25, 27]
        keypoints_num = 9
    elif FITNESS_MODE == "RIGHT_PUSH_UP":
        keypoints_name = ['nose_x', 'nose_y',
                          'left_shoulder_x', 'left_shoulder_y',
                          'right_shoulder_x', 'right_shoulder_y',
                          'right_elbow_x', 'right_elbow_y',
                          'right_wrist_x', 'right_wrist_y',
                          'left_hip_x', 'left_hip_y',
                          'right_hip_x', 'right_hip_y',
                          'right_knee_x', 'right_knee_y',
                          'right_ankle_x', 'right_ankle_y']

        # 9개의 관절 좌표만 저장
        sel_keypoints = [0, 11, 12, 14, 16, 23, 24, 26, 28]
        keypoints_num = 9
    else:
        keypoints_name = ['nose_x', 'nose_y',
                          'left_shoulder_x', 'left_shoulder_y',
                          'right_shoulder_x', 'right_shoulder_y',
                          'left_elbow_x', 'left_elbow_y',
                          'right_elbow_x', 'right_elbow_y',
                          'left_wrist_x', 'left_wrist_y',
                          'right_wrist_x', 'right_wrist_y',
                          'left_hip_x', 'left_hip_y',
                          'right_hip_x', 'right_hip_y',
                          'left_knee_x', 'left_knee_y',
                          'right_knee_x', 'right_knee_y',
                          'left_ankle_x', 'left_ankle_y',
                          'right_ankle_x', 'right_ankle_y']

        # 13개의 관절 좌표만 저장
        sel_keypoints = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        keypoints_num = 13


# 관절 좌표 데이터셋 생성
def csv_generate(path, pose_choice, FITNESS_MODE, reverse):
    # Pose 객체 생성
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    # CSV 파일 생성
    if FITNESS_MODE == "LEFT_PUSH_UP":  # LEFT 푸쉬업
        if pose_choice == "UP":
            f = open('dataset/up/up_left_pushup_pose.csv', 'w', newline='')
            writer = csv.writer(f)
            writer.writerow(keypoints_name)
        elif pose_choice == "DOWN":
            f = open('dataset/down/down_left_pushup_pose.csv', 'w', newline='')
            writer = csv.writer(f)
            writer.writerow(keypoints_name)
        else:
            f = open('dataset/nothing/nothing_left_pushup_pose.csv', 'w', newline='')
            writer = csv.writer(f)
            writer.writerow(keypoints_name)
    elif FITNESS_MODE == "RIGHT_PUSH_UP":  # RIGHT 푸쉬업
        if pose_choice == "UP":
            f = open('dataset/up/up_right_pushup_pose.csv', 'w', newline='')
            writer = csv.writer(f)
            writer.writerow(keypoints_name)
        elif pose_choice == "DOWN":
            f = open('dataset/down/down_right_pushup_pose.csv', 'w', newline='')
            writer = csv.writer(f)
            writer.writerow(keypoints_name)
        else:
            f = open('dataset/nothing/nothing_right_pushup_pose.csv', 'w', newline='')
            writer = csv.writer(f)
            writer.writerow(keypoints_name)
    else:  # 스쿼트
        if pose_choice == "UP":
            f = open('dataset/up/up_squat_pose.csv', 'w', newline='')
            writer = csv.writer(f)
            writer.writerow(keypoints_name)
        elif pose_choice == "DOWN":
            f = open('dataset/down/down_squat_pose.csv', 'w', newline='')
            writer = csv.writer(f)
            writer.writerow(keypoints_name)
        else:
            f = open('dataset/nothing/nothing_squat_pose.csv', 'w', newline='')
            writer = csv.writer(f)
            writer.writerow(keypoints_name)

    # 관절 정보
    keypoints = []
    visibilitys = []

    # CSV 변수
    save_count = 0
    save_state = False

    cap = cv2.VideoCapture(path)
    success = True
    while success:
        success, frame = cap.read()
        frame = imutils.resize(frame, width=1000)
        height, width, _ = frame.shape

        # Frame 처리
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 좌우 반전(푸쉬업 전용, (ON, OFF)로 설정)
        if reverse and (FITNESS_MODE == "LEFT_PUSH_UP" or FITNESS_MODE == "RIGHT_PUSH_UP"):
            frame = cv2.flip(frame, 1)

        results = pose.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # 관절 좌표 저장
        if results.pose_landmarks != None:
            keypoints = []
            visibilitys = []
            for i, landmark in enumerate(results.pose_landmarks.landmark):
                # 의미있는 좌표만 추출
                if i in sel_keypoints:
                    keypoints.append(landmark.x)  # 실제좌표 : x * width
                    keypoints.append(landmark.y)  # 실제좌표 : y * height
                    visibilitys.append(landmark.visibility)

        # visibility 체크(모든 좌표가 화면에 들어와야 저장)
        visibility_count = 0
        visibility_check = False
        for visibility in visibilitys:
            if visibility > 0.8:
                visibility_count += 1
            # 모든 관절 정확도 80% 이상이면 True
            if visibility_count == keypoints_num:
                visibility_check = True

        # 좌우 반전 상시
        if FITNESS_MODE == "SQUAT":
            frame = cv2.flip(frame, 1)

        # 텍스트 출력
        if save_state:
            cv2.putText(frame, f"Press 'S' to stop", (20, 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2,
                        cv2.LINE_AA)
        else:
            cv2.putText(frame, f"Press 'S' to save", (20, 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2,
                        cv2.LINE_AA)

        # CSV 관절좌표 저장
        if visibility_check and save_state:
            writer.writerow(keypoints)
            save_count += 1
            print(f"저장 횟수 -> {save_count}")

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
    # 사용할 동영상 선택
    # path = "video/push_up/7.mp4"
    # path = "video/squat/4.mp4"

    # 임시
    path = "video/3.mp4"

    # 수집할 운동 선택
    # FITNESS_MODE = "LEFT_PUSH_UP"
    # FITNESS_MODE = "RIGHT_PUSH_UP"
    FITNESS_MODE = "SQUAT"

    # 수집할 자세 선택
    # pose_choice = 'UP'
    pose_choice = 'DOWN'
    # pose_choice = 'NOTHING'

    # 푸쉬업만 사용(좌우반전 여부, EX) LEFT_PUSH_UP 이면 영상에서 왼팔이 캠앞에 있어야함(오른팔이 뒤로) )
    reverse = True
    # reverse = False

    init_variable(FITNESS_MODE)
    csv_generate(path, pose_choice=pose_choice, FITNESS_MODE=FITNESS_MODE, reverse=reverse)
