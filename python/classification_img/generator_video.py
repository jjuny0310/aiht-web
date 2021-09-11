import cv2
import imutils
import os

dir_num = 0

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
def image_generate(path, reverse):
    save_count = 0
    save_state = False

    # 폴더 생성
    createFolder()

    cap = cv2.VideoCapture(path)
    success = True
    while success:
        success, frame = cap.read()
        frame = imutils.resize(frame, width=1000)
        height, width, _ = frame.shape

        # 좌우 반전
        if reverse:
            frame = cv2.flip(frame, 1)

        # 텍스트 출력
        if save_state:
            # cv2.putText(frame, f"Press 'S' to stop", (20, 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2,
            #             cv2.LINE_AA)
            cv2.imwrite(f"images/{dir_num}/{save_count}.jpg", frame)
            save_count += 1
            print(f"저장횟수 : {save_count}")

        # else:
        #     cv2.putText(frame, f"Press 'S' to save", (20, 60), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2,
        #                 cv2.LINE_AA)

        # Imshow
        cv2.imshow('Image Generate', frame)
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
    path = "../classification/video/squat/4.mp4"
    path = "../classification/video/push_up/1.mp4"

    # 푸쉬업만 선택(좌우반전 여부, EX) LEFT_PUSH_UP 이면 영상에서 왼팔이 캠앞에 있어야함(오른팔이 뒤로) )
    reverse = True
    # reverse = False

    image_generate(path, reverse=reverse)
