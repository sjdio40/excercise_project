# 📘 운동 자세 비교 프로그램 함수 설명

이 문서는 운동 자세 비교 프로그램의 주요 함수들을 마크다운으로 문서화한 내용입니다.

---

## 📁 `select_video()`

```python
def select_video():
    global video_path
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi")])
```

- `tkinter`의 `filedialog`를 통해 영상 파일을 선택하는 함수입니다.
- 선택된 파일 경로는 `video_path` 전역 변수에 저장됩니다.

---

## ▶️ `start_program()`

```python
def start_program():
    if video_path:
        threading.Thread(target=run_analysis, args=(video_path,)).start()
```

- 사용자가 영상 선택 후 "start" 버튼을 누르면 `run_analysis()`를 **별도의 스레드**에서 실행합니다.
- 영상이 선택되지 않은 경우 실행되지 않습니다.

---

## 📐 `calculate_angle(a, b, c)`

```python
def calculate_angle(a, b, c):
    ...
    return angle
```

- 세 점 `a, b, c`를 기준으로 두 벡터가 이루는 **각도를 계산**합니다.
- 자세 비교에 사용됩니다.

---

## 🔊 `speak(text)`

```python
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
```

- 텍스트를 음성으로 출력하는 함수입니다.
- pyttsx3 엔진을 사용하여 실시간 자세 피드백을 제공합니다.

---

## 🧠 `run_analysis(video_path)`

```python
def run_analysis(video_path):
    ...
```

- **선택된 영상**과 **웹캠 영상**을 비교하며 운동 자세를 분석하는 핵심 함수입니다.
- Mediapipe 기반의 `poseDetector`를 사용하여 신체 부위 위치를 추출하고, 각도를 비교합니다.
- 피드백은 다음 부위를 기준으로 진행됩니다:
  - 양 팔 (Larm, Rarm)
  - 양 다리 (Lleg, Rleg)
  - 목 (Neck)
- 각 부위의 정확도를 퍼센트로 표기하고, 평균 정확도도 함께 표시합니다.
- 정확도가 80% 미만일 경우 음성 피드백을 제공합니다.

---

## 📌 `class poseDetector`

```python
class poseDetector():
    ...
```

- Mediapipe의 Pose 모듈을 래핑한 클래스입니다.
- 주요 메서드:
  - `findPose(img)`: 이미지에서 포즈를 감지합니다.
  - `getPosition(img)`: 각 관절 위치를 픽셀 좌표로 반환합니다.

---

## 🎬 `main()`

```python
def main():
    ...
```

- 테스트용으로 영상 파일을 불러와 포즈 감지를 확인하는 함수입니다.
- 일반 사용자 실행 시에는 사용되지 않습니다.

---

## 🖥️ GUI 구성 (Tkinter)

- 버튼 구성:
  - `video_upload`: 영상 업로드 버튼
  - `start`: 분석 시작 버튼
- `app.mainloop()`로 GUI 이벤트 루프 실행