from tensorflow.keras.models import load_model
from python import exercise

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

pushup_left_model = load_model('python/classification/model/left_pushup_model.h5')
pushup_right_model = load_model('python/classification/model/right_pushup_model.h5')
squat_model = load_model('python/classification/model/squat_model.h5')

def run(FITNESS_MODE, pose_landmarks):
    keypoints_x = []
    keypoints_y = []
    keypoints_squat = []
    keypoints_pushup_left = []
    keypoints_pushup_right = []
    for idx, landmark in enumerate(pose_landmarks):
        keypoints_x.append(landmark['x'])
        keypoints_y.append(landmark['y'])
        if FITNESS_MODE == "SQUAT":
            if idx in squat_parts:
                keypoints_squat.append(landmark['x'])
                keypoints_squat.append(landmark['y'])

        elif FITNESS_MODE == "PUSH_UP":
            if idx in pushup_left_parts:
                keypoints_pushup_left.append(landmark['x'])
                keypoints_pushup_left.append(landmark['y'])
            if idx in pushup_right_parts:
                keypoints_pushup_right.append(landmark['x'])
                keypoints_pushup_right.append(landmark['y'])

    keypoints = list(zip(keypoints_x, keypoints_y))

    if FITNESS_MODE == "SQUAT":
        exercise.squat(squat_model, keypoints_squat)
    elif FITNESS_MODE == "PUSH_UP":
        exercise.pushup(pushup_left_model, pushup_right_model, keypoints_pushup_left, keypoints_pushup_right, keypoints)

    return 0