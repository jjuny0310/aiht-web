import cv2
import imutils
import threading
import os

dir_num = 0
initial_state = True

def set_initial_state():
    global initial_state
    initial_state = False

def createFolder():
    global dir_num

    while(1):
        directory = f'images/{dir_num}'
        try:
            if not os.path.isdir(directory):
                os.mkdir(directory)
                break
            else:
                dir_num += 1
        except OSError:
            print('Error: Creating directory. ' + directory)


# 관절 좌표 데이터셋 생성
def image_generate(path, ready, save_frequency, reverse):
    save_count = 0
    save_state = False

    # 폴더 생성
    createFolder()

    # 자세 준비 대기(ready 초 뒤에 시작)
    threading.Timer(ready, set_initial_state).start()

    cap = cv2.VideoCapture(path)
    success = True
    while success:
        success, frame = cap.read()
        frame = imutils.resize(frame, width=1000)
        height, width, _ = frame.shape

        # 좌우 반전
        if reverse:
            frame = cv2.flip(frame, 1)

        # 저장
        if save_count != save_frequency and initial_state==False:
            cv2.imwrite(f"images/{dir_num}/{save_count}.jpg", frame)
            save_count += 1
            print(f"저장횟수 : {save_count}/{save_frequency}")
        elif save_count == save_frequency:
            cv2.putText(frame, f"Stop.", (20, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 255), 2, cv2.LINE_AA)

        # Imshow
        cv2.imshow('Image Generate', frame)
        k = cv2.waitKey(1)
        if k == 27:
            break

    cap.release()


if __name__ == '__main__':
    # 초기 옵션
    save_frequency = 1000    # 전체 저장 횟수
    ready = 20               # 준비 시간

    path = 0

    # 푸쉬업만 선택(좌우반전 여부, EX) LEFT_PUSH_UP 이면 영상에서 왼팔이 캠앞에 있어야함(오른팔이 뒤로) )
    reverse = True
    # reverse = False

    image_generate(path, ready, save_frequency, reverse=reverse)
