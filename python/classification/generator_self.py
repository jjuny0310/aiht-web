import cv2
import mediapipe as mp
import csv
import threading
import imutils

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


initial_state = True

def init_variable(FITNESS_MODE):
    global keypoints_name
    global sel_keypoints
    global keypoints_num

    if FITNESS_MODE == "LEFT_PUSH_UP":
        keypoints_name = ['nose_x', 'nose_y',
                          'left_shoulder_x', 'left_shoulder_y',
                          'right_shoulder_x', 'right_shoulder_y',
                          'right_elbow_x', 'right_elbow_y',
                          'right_wrist_x', 'right_wrist_y',
                          'left_hip_x', 'left_hip_y',
                          'right_hip_x', 'right_hip_y',
                          'right_knee_x', 'right_knee_y',
                          'right_ankle_x', 'right_ankle_y']

        # 9개의 관절 좌표만 저장(좌우반전이므로 실제 left는 화면상의 right)
        sel_keypoints = [0, 11, 12, 14, 16, 23, 24, 26, 28]
        keypoints_num = 9
    elif FITNESS_MODE == "RIGHT_PUSH_UP":
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


def set_initial_state():
    global initial_state
    initial_state = False


# 관절 좌표 데이터셋 생성
def csv_generate(path, save_frequency, ready, pose_choice, FITNESS_MODE):
    # Pose 객체 생성
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    # CSV 파일 생성
    if FITNESS_MODE == "LEFT_PUSH_UP":   # LEFT 푸쉬업
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
    elif FITNESS_MODE == "RIGHT_PUSH_UP":   # RIGHT 푸쉬업
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
    else:   # 스쿼트
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
    count = 0
    save_count = 0

    # 자세 준비 대기(ready 초 뒤에 시작)
    threading.Timer(ready, set_initial_state).start()

    cap = cv2.VideoCapture(path)
    success = True
    while success:
        success, frame = cap.read()
        frame = imutils.resize(frame, width=1000)
        height, width, _ = frame.shape

        # Frame 처리
        frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
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
                    keypoints.append(landmark.x)      # 실제좌표 : x * width
                    keypoints.append(landmark.y)      # 실제좌표 : y * height
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

        # 텍스트 출력
        if initial_state:
            cv2.putText(frame, f"Start after {ready} seconds..", (20, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
        elif save_count == save_frequency:
            cv2.putText(frame, f"Stop.", (20, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)
        elif ~initial_state:
            cv2.putText(frame, f"Take a pose!", (20, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)

        # CSV 관절좌표 저장
        if save_count != save_frequency and visibility_check and initial_state == False:
            writer.writerow(keypoints)
            print(f"저장 횟수 -> {save_count + 1}/{save_frequency}")
            save_count += 1

        # Imshow
        cv2.imshow('Keypoints DataSet Generate', frame)
        k = cv2.waitKey(1)
        if k == 27:
            break

    cap.release()


if __name__ == '__main__':
    # 초기 옵션
    save_frequency = 200    # 전체 저장 횟수
    ready = 20               # 준비 시간
    
    # 경로 설정
    path = 0                # 캠

    # 운동 선택
    # FITNESS_MODE = "LEFT_PUSH_UP"
    # FITNESS_MODE = "RIGHT_PUSH_UP"
    FITNESS_MODE = "SQUAT"

    # 수집할 자세 선택
    pose_choice = 'UP'
    # pose_choice = 'DOWN'
    # pose_choice = 'NOTHING'

    init_variable(FITNESS_MODE)
    csv_generate(path, save_frequency, ready, pose_choice=pose_choice, FITNESS_MODE=FITNESS_MODE)
