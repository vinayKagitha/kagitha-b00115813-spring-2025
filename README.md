
---

# **Gesture-Based AI Interaction System – Full Breakdown**

---

## **🎯 Introduction**

This project is a **real-time gesture-controlled AI system** built with **Streamlit**, which offers two primary features:

1. **🧠 Math Problem Solver** – Write math expressions in the air using your hand, and let Google Gemini AI solve it.
2. **🖥️ System Control** – Use your hand to control system functions like **volume**, **brightness**, and **mouse** actions without touching your computer.

---

## **🛠️ Tech Stack**

| Feature           | Library / Tool              |
|------------------|-----------------------------|
| Webcam Access     | `OpenCV`                    |
| Hand Tracking     | `MediaPipe`, `cvzone`       |
| AI Math Solver    | `Google Generative AI (Gemini)` |
| Web Interface     | `Streamlit`                 |
| Mouse Automation  | `pyautogui`                 |
| Volume Control    | `pycaw`                     |
| Brightness Control| `screen_brightness_control` |

---

## **🖼️ Streamlit App UI**

```python
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

### 🔍 Explanation:
- **Mode Switcher**: Select between *Math Solver* or *System Control*.
- **Run Checkbox**: Toggles the webcam and detection loop.
- **Image Window**: Shows webcam stream with overlays.
- **Text Output**: Displays AI response or system status.

---

## **🤖 Google Gemini AI Configuration**

```python
import google.generativeai as genai
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')
```

- **Gemini AI** handles interpretation and solving of hand-drawn equations.

---

## **📷 Webcam Setup & Hand Tracking**

```python
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(staticMode=False, maxHands=1, detectionCon=0.7, minTrackCon=0.5)
```

- Webcam set to **HD resolution**.
- `HandDetector` used for identifying finger states and positions.

---

## **✍️ Math Solver Logic**

### 1. **`getHandInfo_math(img)`**
Returns:
- **`fingers`**: Which fingers are up.
- **`lmList`**: Landmarks of hand for drawing.

---

### 2. **`draw_math(info, prev_pos, canvas, img)`**

```python
if fingers == [0, 1, 0, 0, 0]:
    # Draw with index finger
elif fingers == [1, 0, 0, 0, 0]:
    # Clear canvas
```

- Index finger up ➝ start drawing.
- Thumb up ➝ clear canvas.

---

### 3. **`sendToAI_math(model, canvas, fingers)`**

```python
if fingers == [1, 1, 1, 0, 0]:
    pil_image = Image.fromarray(canvas)
    response = model.generate_content(["Solve this math problem", pil_image])
```

- When 3 fingers are up ➝ take screenshot and send to Gemini AI.
- Gemini interprets handwritten input and replies with solution.

---

## **🕹️ System Control Mode**

### **Mouse, Volume, Brightness using MediaPipe**

#### `get_finger_distance(lmList, idx1, idx2)`
- Calculates distance between two landmarks.
- Used for determining gesture-based control range.

---

#### `process_system_control(image, results)`
```python
# If hand detected:
    - Draw landmarks
    - Interpret gesture
    - Trigger system action
```

- Tracks gesture patterns.
- Controls system volume, brightness, or mouse depending on gesture.

---

## **🔄 Main Loop – Mode Execution**

```python
while run:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    if mode == "Math Problem Solver":
        canvas = np.zeros_like(img) if canvas is None else canvas
        info = getHandInfo_math(img)
        if info:
            fingers, lmList = info
            prev_pos, canvas = draw_math(info, prev_pos, canvas, img)
            result_text = sendToAI_math(model, canvas, fingers)
            if result_text:
                output_text = result_text
        FRAME_WINDOW.image(cv2.addWeighted(img, 0.7, canvas, 0.3, 0).astype(np.uint8), channels="BGR")
        output_text_area.text(output_text)
    
    else:
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands_mediapipe.process(image_rgb)
        img_processed = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        processed_img, sys_output = process_system_control(img_processed, results)
        FRAME_WINDOW.image(processed_img.astype(np.uint8), channels="BGR")
        output_text_area.text(sys_output)

cap.release()
```
---
## **FlowChart**
![92f72000-e362-4baa-b929-a22f64117d26](https://github.com/user-attachments/assets/b355269f-be98-4a1b-bbf8-a86fbd64a2b9)

---

## **💡 Suggestions for Future**

| Feature | Description |
|--------|-------------|
| 🧠 OCR | Improve accuracy for math recognition |
| 🗂️ Custom Gestures | Let users train their own gesture sets |
| 🔊 Voice Assistant | Integrate a voice assistant for hands-free commands |
| 🔁 Gesture Mode Toggle | Switch modes using gesture (no UI interaction needed) |

---

## ✅ Summary

| Mode | Action |
|------|--------|
| **Math Solver** | Write equation with fingers, AI solves |
| **System Control** | Control PC functions via hand gestures |

This app demonstrates a powerful blend of **computer vision**, **gesture recognition**, and **generative AI** — all inside a single Streamlit interface.

---
