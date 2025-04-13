import tkinter as tk
from tkinter import filedialog
import threading  # threading 모듈을 import 해야 함
import cv2
import numpy as np
import pyttsx3
import PoseModule
import time
import mediapipe as mp

def select_video():
    global video_path
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])

def start_program():
    if video_path:  # video_path가 None이 아니어야 함
        print("video_path:", video_path)  # 경로 출력
        threading.Thread(target=run_analysis, args=(video_path,)).start()
    else:
        print("video_path not exist")

# 각도 계산 함수
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle
    return angle

# 음성 피드백 함수
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# 메인 분석 함수
def run_analysis(video_path):
    cap_video = cv2.VideoCapture(video_path)
    cap_cam = cv2.VideoCapture(0)

    detector = poseDetector()
    feedback_timer = 0

    while cap_video.isOpened() and cap_cam.isOpened():
        ret1, frame1 = cap_video.read()
        ret2, frame2 = cap_cam.read()

        if not ret1 or not ret2:
            print("카메라 또는 영상 프레임을 불러오지 못했습니다.")
            break  # 또는 continue

        frame1 = cv2.resize(frame1, (640, 480))
        frame2 = cv2.resize(frame2, (640, 480))

        # 포즈 감지
        frame1 = detector.findPose(frame1)
        frame2 = detector.findPose(frame2, draw=True)
        lmList1 = detector.getPosition(frame1, draw=False)
        lmList2 = detector.getPosition(frame2, draw=False)

        feedback_text = ""
        accuracy_total = 0
        part_count = 0

        if len(lmList1) > 28 and len(lmList2) > 28:
            def compare_part(name, p1, p2, p3):
                angle1 = calculate_angle(lmList1[p1][1:], lmList1[p2][1:], lmList1[p3][1:])
                angle2 = calculate_angle(lmList2[p1][1:], lmList2[p2][1:], lmList2[p3][1:])
                diff = abs(angle1 - angle2)
                accuracy = max(0, 100 - diff)
                return accuracy, diff

            # 부위별 비교
            parts = {
                "Larm": (11, 13, 15),
                "Rarm": (12, 14, 16),
                "Lleg": (23, 25, 27),
                "Rleg": (24, 26, 28),
                "Neck": (11, 0, 12),  # 어깨-코-어깨로 간이 목자세 추정
            }

            for name, (a, b, c) in parts.items():
                acc, diff = compare_part(name, a, b, c)
                accuracy_total += acc
                part_count += 1
                if feedback_timer % 30 == 0:
                    if acc < 80:
                        speak(f"{name} Correct your posture")
                feedback_text += f"{name}: {int(acc)}%  "

            # 평균 정확도 계산
            avg_accuracy = int(accuracy_total / part_count)

            # 퍼센트 표시
            cv2.putText(frame2, f"accuracy: {avg_accuracy}%", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 3)
            cv2.putText(frame2, feedback_text, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 100, 255), 2)

            feedback_timer += 1

        # 화면 결합
        combined = np.hstack((frame1, frame2))
        cv2.imshow("comparison screen", combined)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap_video.release()
    cap_cam.release()
    cv2.destroyAllWindows()

class poseDetector():

    def __init__(self, static_image_mode = False,
                 model_complexity = 1,
                 smooth_landmarks = True,
                 enable_segmentation = False,
                 smooth_segmentation = True,
                 min_detection_confidence = 0.5,
                 min_tracking_confidence = 0.5):

        self.static_image_mode = static_image_mode
        self.model_complexity = model_complexity
        self.smooth_landmarks = smooth_landmarks
        self.enable_segmentation = enable_segmentation
        self.smooth_segmentation = smooth_segmentation
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.static_image_mode, self.model_complexity, self.smooth_landmarks,
                                     self.enable_segmentation, self.smooth_segmentation, self.min_detection_confidence,
                                     self.min_tracking_confidence)

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        return img

    def getPosition(self, img, draw=True):
        lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 3, (255, 0, 255), cv2.FILLED)
        return lmList


def main():
    cap = cv2.VideoCapture("../PoseVideos/2.mp4")
    pTime = 0
    detector = poseDetector()
    while True:
        success, img = cap.read()
        img = cv2.resize(img, (960, 540))
        img = detector.findPose(img)
        lmList = detector.getPosition(img)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (30, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)
        
video_path = None

app = tk.Tk()
app.title("exercise helper program")
app.geometry("400x200")

btn_select = tk.Button(app, text="video_upload", command=select_video, height=2, width=30)
btn_select.pack(pady=20)

btn_start = tk.Button(app, text="start", command=start_program, height=2, width=30)
btn_start.pack(pady=10)

app.mainloop()
