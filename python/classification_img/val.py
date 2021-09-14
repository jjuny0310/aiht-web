# 이미지 분류 모델 검증
from tensorflow.keras.models import load_model
import cv2
import imutils
import numpy as np


def run(path, model):
    cap = cv2.VideoCapture(path)
    success = True
    while success:
        success, frame = cap.read()
        predict_img = frame.copy()
        frame = imutils.resize(frame, width=1000)

        predict_img = cv2.resize(predict_img, (150, 150))
        # predict_img = imutils.resize(predict_img, width=150)


        height, width, _ = frame.shape

        predict_img = (np.expand_dims(predict_img, 0))

        predict = model.predict(predict_img)
        if(np.argmax(predict) == 0):
            print("down")
        elif(np.argmax(predict) == 1):
            print("nothing")
        else:
            print("up")

        # Imshow
        frame = cv2.flip(frame, 1)
        cv2.imshow('Image Generate', frame)
        k = cv2.waitKey(1)
        if k == 27:
            break

    cap.release()


if __name__ == '__main__':
    path = 0

    # 모델 불러오기
    test_model = load_model('model/squat.h5')
    run(path, test_model)
