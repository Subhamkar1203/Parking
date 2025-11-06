import streamlit as st
import cv2
import pickle
import cvzone
import numpy as np
import time
import os

st.set_page_config(page_title="Smart Parking Dashboard", layout="wide", initial_sidebar_state="expanded")

# ---------- CSS ----------
st.markdown(
    """
    <style>
    :root {
        --bg: #0b0f14;
        --card: #0f1720;
        --muted: #94a3b8;
        --accent: #16a34a;
        --danger: #ef4444;
    }
    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg);
        color: #e6eef6;
    }
    .block-container { padding-top: 1rem !important; }
    .card {
        background: var(--card);
        border-radius: 12px;
        padding: 14px;
        border: 1px solid rgba(255,255,255,0.04);
    }
    .metric {
        background: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    .badge {
        display: inline-block;
        padding: 6px 10px;
        margin: 4px 6px 4px 0;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        color: #fff;
    }
    .badge-free { background: var(--accent); }
    .badge-occ { background: var(--danger); }
    .badge-muted { background: rgba(255,255,255,0.1); color: var(--muted); }

    .monitor-all>button {
        background: var(--accent);
        width: 100%;
        border-radius: 8px;
        color: white;
        font-weight: 600;
    }
    .monitor-none>button {
        background: #4b5563;
        width: 100%;
        border-radius: 8px;
        color: white;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Constants ----------
WIDTH, HEIGHT = 105, 40
OCCUPANCY_THRESHOLD = 900

# ---------- Load Parking Coordinates ----------
try:
    with open("dr.parking/CarParkPos.pkl", "rb") as f:
        posList = pickle.load(f)
except FileNotFoundError:
    st.sidebar.error("❌ CarParkPos.pkl not found — Run parking_space_picker first")
    st.stop()
except Exception as e:
    st.sidebar.error(f"Error loading CarParkPos.pkl: {e}")
    st.stop()

NUM_SPOTS = len(posList)
SPOT_NAMES = [f"Spot {i+1}" for i in range(NUM_SPOTS)]

# ---------- Session State ----------
if "monitored_spots" not in st.session_state:
    st.session_state.monitored_spots = []

if "prev_status" not in st.session_state:
    st.session_state.prev_status = {}

# ---------- Parking Space Check Function ----------
def checkParkingSpace(img, imgPro, posList):
    spaceCounter = 0
    occupancy_status = []

    for i, pos in enumerate(posList):
        x, y = pos
        spot_id = SPOT_NAMES[i]
        imgCrop = imgPro[y:y+HEIGHT, x:x+WIDTH]
        count = cv2.countNonZero(imgCrop)

        if count < OCCUPANCY_THRESHOLD:
            color = (0, 255, 0)
            status = "Free"
            spaceCounter += 1
        else:
            color = (255, 0, 0)
            status = "Occupied"

        occupancy_status.append(status)

        # Toast notification
        if spot_id in st.session_state.monitored_spots:
            prev = st.session_state.prev_status.get(spot_id)
            if prev != status:
                st.toast(f"{spot_id} ➜ {status.upper()}", icon="✅" if status == "Free" else "🚫")
            st.session_state.prev_status[spot_id] = status

        cv2.rectangle(img, pos, (x+WIDTH, y+HEIGHT), color, 2)
        cvzone.putTextRect(img, spot_id, (x + 10, y + 30), scale=0.7, thickness=1, colorR=color)

    return img, spaceCounter, occupancy_status

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 🎛 Controls")

    source_mode = st.selectbox("Video Source", ["Demo video", "Live stream (IP/RTSP)"])
    stream_url = (
        "dr.parking/carPark.mp4" if source_mode == "Demo video"
        else st.text_input("Stream URL", "http://192.168.1.100:8080/video")
    )

    selected = st.multiselect("Monitor spots:", SPOT_NAMES, default=st.session_state.monitored_spots)
    if st.button("Apply"):
        st.session_state.monitored_spots = selected
        st.success("✅ Selection Updated")

    colA, colB = st.columns(2)
    with colA:
        st.markdown("<div class='monitor-all'>", unsafe_allow_html=True)
        if st.button("Monitor All"):
            st.session_state.monitored_spots = SPOT_NAMES.copy()
        st.markdown("</div>", unsafe_allow_html=True)

    with colB:
        st.markdown("<div class='monitor-none'>", unsafe_allow_html=True)
        if st.button("Monitor None"):
            st.session_state.monitored_spots = []
            st.session_state.prev_status = {}
        st.markdown("</div>", unsafe_allow_html=True)

# ---------- Main Layout ----------
left, right = st.columns([3, 1])
video_placeholder = left.empty()

right.markdown("### Parking Status")
free_metric = right.empty()
occup_metric = right.empty()
free_box = right.empty()
occ_box = right.empty()

# ---------- Video Stream ----------
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    st.error("❌ Could not open video source")
    st.stop()

while True:
    success, img = cap.read()
    if not success:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3,3), 1)
    imgThres = cv2.adaptiveThreshold(imgBlur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV,25,16)
    imgMedian = cv2.medianBlur(imgThres,5)
    imgDilate = cv2.dilate(imgMedian, np.ones((3,3),np.uint8),iterations=1)

    img_result, free_spaces, status_list = checkParkingSpace(img.copy(), imgDilate, posList)

    free_metric.metric("Free Spots", free_spaces)
    occup_metric.metric("Occupied Spots", NUM_SPOTS-free_spaces)

    free_badges = [SPOT_NAMES[i] for i,s in enumerate(status_list) if s=="Free"]
    occ_badges = [SPOT_NAMES[i] for i,s in enumerate(status_list) if s=="Occupied"]

    free_box.markdown(" ".join([f"<span class='badge badge-free'>{x}</span>" for x in free_badges]),
                      unsafe_allow_html=True)
    occ_box.markdown(" ".join([f"<span class='badge badge-occ'>{x}</span>" for x in occ_badges]),
                     unsafe_allow_html=True)

    video_placeholder.image(cv2.cvtColor(img_result, cv2.COLOR_BGR2RGB),
                            channels="RGB", use_container_width=True)

    time.sleep(0.03)

cap.release()
