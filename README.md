**Gesture-Based AI System: Math Solver & System Control**

## **Introduction**

This project is a **Streamlit-based application** that integrates **hand gesture recognition** for two modes:

1. **Math Problem Solver** – Allows users to write math equations using hand gestures and solve them using AI.
2. **System Control** – Enables control of volume, brightness, and mouse using hand gestures.

The application uses **Google Gemini AI, OpenCV, Mediapipe, Pycaw, and PyAutoGUI** to achieve this functionality.

---

## **1. Streamlit App Configuration**

### **Purpose:**

- Creates the user interface.
- Allows selection between Math Solver and System Control modes.

```python
import streamlit as st

st.set_page_config(layout="wide")

mode = st.radio("Select Mode", ("Math Problem Solver", "System Control"))

col1, col2 = st.columns([3, 2])
with col1:
    run = st.checkbox('Run', value=True)
    FRAME_WINDOW = st.image([])

with col2:
    st.title("Output")
    output_text_area = st.empty()
```

### **Explanation:**

- `st.radio()` → Provides a selection between **Math Solver** and **System Control**.
- `st.checkbox('Run', value=True)` → Controls whether the app runs.
- `st.image([])` → Placeholder for the webcam feed.

---

## **2. AI Configuration (Google Gemini API)**

```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')
```

### **Explanation:**

- `genai.configure(api_key=...)` → Initializes Google Gemini API for AI-powered math-solving.
- `GenerativeModel('gemini-1.5-flash')` → Loads a fast, lightweight AI model.

---

## **3. Webcam Initialization**

```python
import cv2

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
```

### **Explanation:**

- `cv2.VideoCapture(0)` → Opens the **default webcam**.
- `cap.set(3, 1280)` → Sets **width**.
- `cap.set(4, 720)` → Sets **height**.

---

## **4. Hand Tracking for Math Solver**

```python
from cvzone.HandTrackingModule import HandDetector

detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.7, minTrackCon=0.5)
```

### **Explanation:**

- Uses **HandDetector** from Cvzone to track hand landmarks.
- `maxHands=1` → Tracks only one hand.

---

## **5. Math Solver: Drawing and AI Processing**

```python
def draw_math(info, prev_pos, canvas, img):
    fingers, lmList = info
    current_pos = None
    if fingers == [0, 1, 0, 0, 0]:
        current_pos = lmList[8][0:2]
        if prev_pos is None:
            prev_pos = current_pos
        cv2.line(canvas, current_pos, prev_pos, (255, 0, 255), 10)
    elif fingers == [1, 0, 0, 0, 0]:
        canvas = np.zeros_like(img)
    return current_pos, canvas
```

### **Explanation:**

- Detects **index finger up** → Draws on the screen.
- Detects **thumb up** → Clears the drawing.

```python
def sendToAI_math(model, canvas, fingers):
    if fingers == [1, 1, 1, 0, 0]:
        pil_image = Image.fromarray(canvas)
        response = model.generate_content(["Solve this math problem", pil_image])
        return response.text
    return None
```

### **Explanation:**

- Sends **handwritten equation** to AI when three fingers are up.
- AI processes and returns the **solution**.

---

## **6. System Control (Mouse, Volume, Brightness)**

### **Volume Control Initialization**

```python
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
```

### **Explanation:**

- Accesses system **audio settings**.
- Allows **volume control** using hand gestures.

### **Processing Hand Gestures for System Control**

```python
def process_system_control(image, results):
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        return image, "System Control: Active"
    return image, "No hands detected."
```

### **Explanation:**

- Detects **hand landmarks**.
- Displays real-time feedback.

---

## **7. Main Loop (Processing Webcam Input)**

```python
while run:
    success, img = cap.read()
    if not success:
        st.error("Failed to grab frame from webcam.")
        break
    img = cv2.flip(img, 1)
```

### **Explanation:**

- Captures **webcam frames**.
- Flips image for a **mirrored effect**.

---

## **Conclusion**

This project successfully integrates **gesture recognition** with AI to provide a unique interaction experience.

- **Math Solver Mode** allows users to **write and solve** math problems.
- **System Control Mode** enables **touch-free** control of the computer.

The combination of **AI, OpenCV, and system automation** makes it a powerful and innovative tool!
# kagitha-b00115813-spring-2025
