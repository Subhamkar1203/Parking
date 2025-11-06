import streamlit as st
import cv2
import pickle
import cvzone
import numpy as np
import time
import os

st.set_page_config(page_title="Smart Parking Dashboard", layout="wide")

# ---------- Constants ----------
WIDTH, HEIGHT = 105, 40
OCCUPANCY_THRESHOLD = 900

# ---------- Load parking coordinates ----------
pos_file_path = "dr.parking/CarParkPos.pkl"

if not os.path.exists(pos_file_path):
    st.sidebar.error("CarParkPos.pkl not found — Run parking_space_picker.py first!")
    st.stop()

try:
    with open(pos_file_path, "rb") as f:
        posList = pickle.load(f)
        NUM_SPOTS = len(posList)
        SPOT_NAMES = [f"Spot {i+1}" for i in range(NUM_SPOTS)]
except Exception as e:
    st.sidebar.error(f"Error loading pos file: {e}")
    st.stop()

# ---------- Session state ----------
if "monitored_spots" not in st.session_state:
    st.session_state.monitored_spots = []
if "prev_status" not in st.session_state:
    st.session_state.prev_status = {}

# ---------- Core parking detection ----------
def checkParkingSpace(img, imgPro, posList):
    spaceCounter = 0
    occupancy_status = []

    for i, pos in enumerate(posList):
        x, y = pos
        spot_id = SPOT_NAMES[i]
        imgCrop = imgPro[y:y+HEIGHT, x:x+WIDTH]
        count = cv2.countNonZero(imgCrop)

        if count < OCCUPANCY_THRESHOLD:
            color = (0,255,0)
            thickness = 2
            status = "Free"
            spaceCounter += 1
        else:
            color = (255,0,0)
            thickness = 2
            status = "Occupied"
        
        occupancy_status.append(status)

        if spot_id in st.session_state.monitored_spots:
            prev = st.session_state.prev_status.get(spot_id)
            if prev != status:
                st.toast(f"{spot_id} → {status}")
            st.session_state.prev_status[spot_id] = status

        cv2.rectangle(img, pos, (pos[0] + WIDTH, pos[1] + HEIGHT), color, thickness)
        cvzone.putTextRect(img, spot_id, (x + 20, y + 25), scale=0.8, thickness=1)

    return img, spaceCounter, occupancy_status


# ---------- Sidebar ----------
with st.sidebar:
    st.title("Controls")

    source_mode = st.selectbox("Video Source", ["Demo Video", "RTSP/IP Stream"])
    if source_mode == "RTSP/IP Stream":
        stream_url = st.text_input("Stream URL", "http://192.168.1.100:8080/video")
    else:
        stream_url = "dr.parking/carPark.mp4"

    selected = st.multiselect("Monitor Spots:", SPOT_NAMES)
    if st.button("Apply"):
        st.session_state.monitored_spots = selected
        st.success("✅ Spot monitoring updated")


# ---------- Main UI ----------
left, right = st.columns([3,1])
video_feed = left.empty()
right.title("Parking Info")
free_display = right.empty()
occ_display = right.empty()

# ---------- Video Capture ----------
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    st.error("❌ Failed to load video")
    st.stop()

try:
    while True:
        success, img = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3,3), 1)
        imgTh = cv2.adaptiveThreshold(imgBlur, 255,
                                      cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY_INV, 25, 16)
        imgMedian = cv2.medianBlur(imgTh, 5)
        imgDilate = cv2.dilate(imgMedian, np.ones((3,3), np.uint8), iterations=1)

        imgResult, free_spaces, status = checkParkingSpace(img.copy(), imgDilate, posList)
        occupied = NUM_SPOTS - free_spaces

        free_display.metric("Free Spots", free_spaces)
        occ_display.metric("Occupied Spots", occupied)

        video_feed.image(cv2.cvtColor(imgResult, cv2.COLOR_BGR2RGB), channels="RGB")

        time.sleep(0.03)

except Exception as e:
    st.error(f"Error: {e}")
finally:
    cap.release()

this is code A rember
