import cvzone
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import google.generativeai as genai
from PIL import Image
import streamlit as st

# For system control functionality
import mediapipe as mp
import pyautogui
import math
import screen_brightness_control as sbcontrol
from enum import IntEnum
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# ----------------------------
# Streamlit App Configuration
# ----------------------------
st.set_page_config(layout="wide")

# Choose mode: Math Problem Solver or System Control
mode = st.radio("Select Mode", ("Math Problem Solver", "System Control"))

col1, col2 = st.columns([3, 2])
with col1:
    run = st.checkbox('Run', value=True)
    FRAME_WINDOW = st.image([])

with col2:
    st.title("Output")
    output_text_area = st.empty()

# ----------------------------
# Initialize Shared Components
# ----------------------------
# Initialize generative AI (for math solving)
genai.configure(api_key="AIzaSyDS9BPA5ZVkoCvTg1mOCZPQ0FqGm7nTnjU")
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# ----------------------------
# Math Problem Solver Setup
# ----------------------------
detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1,
                        detectionCon=0.7, minTrackCon=0.5)


def getHandInfo_math(img):
    hands, img = detector.findHands(img, draw=False, flipType=True)
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        fingers = detector.fingersUp(hand)
        return fingers, lmList
    return None


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


def sendToAI_math(model, canvas, fingers):
    if fingers == [1, 1, 1, 0, 0]:
        pil_image = Image.fromarray(canvas)
        response = model.generate_content(["Solve this math problem", pil_image])
        return response.text
    return None


# ----------------------------
# System Control Setup
# ----------------------------
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands_mediapipe = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5,
                                 min_tracking_confidence=0.5)

# Volume Control Setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


# Gesture Enum
class Gest(IntEnum):
    FIST = 0
    PALM = 31
    V_GEST = 33
    PINCH_MAJOR = 35
    PINCH_MINOR = 36


# ----------------------------
# System Control Logic
# ----------------------------
def get_finger_distance(lmList, idx1, idx2):
    x1, y1 = lmList[idx1][0], lmList[idx1][1]
    x2, y2 = lmList[idx2][0], lmList[idx2][1]
    return math.hypot(x2 - x1, y2 - y1)


def process_system_control(image, results):
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        hand = results.multi_hand_landmarks[0]
        lmList = [[lm.x, lm.y] for lm in hand.landmark]

        screen_w, screen_h = pyautogui.size()
        x_index = int(lmList[8][0] * screen_w)
        y_index = int(lmList[8][1] * screen_h)

        distance_thumb_index = get_finger_distance(lmList, 4, 8)
        distance_index_middle = get_finger_distance(lmList, 8, 12)

        # -------------------
        # Mouse Control
        # -------------------
        if distance_index_middle > 0.1:
            pyautogui.moveTo(x_index, y_index, duration=0.1)
        if distance_thumb_index < 0.05:
            pyautogui.click()

        # -------------------
        # Volume Control
        # -------------------
        if distance_index_middle < 0.05 and distance_thumb_index > 0.1:
            volume_value = np.interp(distance_thumb_index, [0.05, 0.2], [-65, 0])
            volume.SetMasterVolumeLevel(volume_value, None)

        # -------------------
        # Brightness Control
        # -------------------
        if distance_thumb_index > 0.05 and distance_thumb_index < 0.2:
            brightness_value = np.interp(distance_thumb_index, [0.05, 0.2], [10, 100])
            sbcontrol.set_brightness(int(brightness_value))

        return image, "System Control: Active"

    return image, "No hands detected."


# ----------------------------
# Main Loop
# ----------------------------
prev_pos = None
canvas = None
output_text = ""

while run:
    success, img = cap.read()
    if not success:
        st.error("Failed to grab frame from webcam.")
        break
    img = cv2.flip(img, 1)

    if mode == "Math Problem Solver":
        if canvas is None:
            canvas = np.zeros_like(img)
        info = getHandInfo_math(img)
        if info:
            fingers, lmList = info
            prev_pos, canvas = draw_math(info, prev_pos, canvas, img)
            result_text = sendToAI_math(model, canvas, fingers)
            if result_text:
                output_text = result_text
        image_combined = cv2.addWeighted(img, 0.7, canvas, 0.3, 0)
        FRAME_WINDOW.image(image_combined.astype(np.uint8), channels="BGR")
        output_text_area.text(output_text)
    else:
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        results = hands_mediapipe.process(image_rgb)
        image_rgb.flags.writeable = True
        img_processed = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        processed_img, sys_output = process_system_control(img_processed, results)
        FRAME_WINDOW.image(processed_img.astype(np.uint8), channels="BGR")
        output_text_area.text(sys_output)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
hands_mediapipe.close()
