from tensorflow.keras.models import load_model

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

def run(FITNESS_MODE, pose_landmarks):
    if FITNESS_MODE == "PUSH_UP":  # 푸쉬업 모델
        left_pushup_model = load_model('classification/model/left_pushup_model.h5')
        left_sel_keypoints = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, RIGHT_ELBOW,
                              RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE]

        right_pushup_model = load_model('classification/model/right_pushup_model.h5')
        right_sel_keypoints = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW,
                               LEFT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE, LEFT_ANKLE]
    else:  # 스쿼트 모델
        model = load_model('classification/model/squat_model.h5')
        sel_keypoints = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW,
                         LEFT_WRIST, RIGHT_WRIST, LEFT_HIP, RIGHT_HIP, LEFT_KNEE, RIGHT_KNEE,
                         LEFT_ANKLE, RIGHT_ANKLE]

    if pose_landmarks != None:
        keypoints_x = []
        keypoints_y = []
        classifier_keypoints = []
        classifier_left_keypoints = []
        classifier_right_keypoints = []
        for i, landmark in enumerate(pose_landmarks.landmark):
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

    return 0