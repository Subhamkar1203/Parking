import streamlit as st
import cv2
import pickle
import cvzone
import numpy as np
import time

st.set_page_config(page_title="Smart Parking Dashboard", layout="wide", initial_sidebar_state="expanded")

# ---------- Custom CSS (dark + gradients) ----------
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
    .block-container { padding-top: 1rem; padding-left: 1rem; padding-right: 1rem; }
    .card {
        background: var(--card);
        border-radius: 12px;
        padding: 14px;
        border: 1px solid rgba(255,255,255,0.04);
    }
    .metric {
        background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        padding: 12px;
        border-radius: 10px;
        text-align: center;
    }
    .badge {
        display: inline-block;
        padding: 6px 10px;
        margin: 4px 6px 4px 0;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        color: #0b0f14;
    }
    .badge-free { background: linear-gradient(90deg, rgba(22,163,74,0.95), rgba(22,163,74,0.85)); }
    .badge-occ { background: linear-gradient(90deg, rgba(239,68,68,0.95), rgba(239,68,68,0.85)); }
    .badge-muted { background: rgba(255,255,255,0.03); color: var(--muted); }
    .muted { color: var(--muted); font-size: 13px; }

    /* Custom buttons */
    .stButton>button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease;
        width: 100%;
        color: white;
        border: none;
    }
    .monitor-all>button {
        background: linear-gradient(90deg, #16a34a, #22c55e);
    }
    .monitor-all>button:hover {
        background: linear-gradient(90deg, #22c55e, #16a34a);
        box-shadow: 0 0 10px rgba(34,197,94,0.5);
    }
    .monitor-none>button {
        background: linear-gradient(90deg, #475569, #334155);
    }
    .monitor-none>button:hover {
        background: linear-gradient(90deg, #334155, #475569);
        box-shadow: 0 0 10px rgba(71,85,105,0.4);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Constants ----------
WIDTH, HEIGHT = 105, 40
OCCUPANCY_THRESHOLD = 900

# ---------- Load parking coordinates ----------
try:
    with open("dr.parking/CarParkPos.pkl", "rb") as f:
        posList = pickle.load(f)

    NUM_SPOTS = len(posList)
    SPOT_NAMES = [f"Spot {i+1}" for i in range(NUM_SPOTS)]
except FileNotFoundError:
    st.sidebar.error("CarParkPos.pkl not found — run the picker first.")
    st.stop()
except Exception as e:
    st.sidebar.error(f"Error loading CarParkPos.pkl: {e}")
    st.stop()

# ---------- Session state ----------
if "monitored_spots" not in st.session_state:
    st.session_state.monitored_spots = []
if "prev_status" not in st.session_state:
    st.session_state.prev_status = {}

# ---------- Core parking-space function ----------
def checkParkingSpace(img, imgPro, posList):
    spaceCounter = 0
    occupancy_status = []

    for i, pos in enumerate(posList):
        x, y = pos
        spot_id = SPOT_NAMES[i]
        imgCrop = imgPro[y : y + HEIGHT, x : x + WIDTH]
        count = cv2.countNonZero(imgCrop)

        # green = free, red = occupied
        if count < OCCUPANCY_THRESHOLD:
            color = (0, 255, 0)
            thickness = 2
            status = "Free"
            spaceCounter += 1
        else:
            color = (255, 0, 0)
            thickness = 2
            status = "Occupied"

        occupancy_status.append(status)

        # notification logic
        if spot_id in st.session_state.monitored_spots:
            prev = st.session_state.prev_status.get(spot_id)
            if prev != status:
                if status == "Free":
                    st.toast(f"{spot_id} is now FREE ")
                else:
                    st.toast(f"{spot_id} is now OCCUPIED ")
            st.session_state.prev_status[spot_id] = status

        cv2.rectangle(img, pos, (pos[0] + WIDTH, pos[1] + HEIGHT), color, thickness)
        cvzone.putTextRect(
            img,
            spot_id,
            (x + WIDTH // 4, y + HEIGHT // 2 + 6),
            scale=0.8,
            thickness=1,
            offset=0,
            colorT=(255, 255, 255),
            colorR=color,
        )

    return img, spaceCounter, occupancy_status

# ---------- Sidebar controls ----------
with st.sidebar:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Controls")

    source_mode = st.selectbox("Video Source", ["Demo video", "Live stream (IP/RTSP)"])
    if source_mode == "Live stream (IP/RTSP)":
        stream_url = st.text_input("Stream URL", "http://192.168.1.100:8080/video")
    else:
        stream_url = "carPark.mp4"

    st.markdown("---")

    selected = st.multiselect(
        "Monitor specific spots:",
        SPOT_NAMES,
        default=st.session_state.monitored_spots,
        help="Select one or multiple spots to receive notifications",
    )

    if st.button("Apply Selection"):
        st.session_state.monitored_spots = selected
        st.success(f"Monitoring {len(selected)} spot(s)")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        with st.container():
            st.markdown("<div class='monitor-all'>", unsafe_allow_html=True)
            if st.button("Monitor All"):
                st.session_state.monitored_spots = SPOT_NAMES.copy()
                st.success("Monitoring all spots")
            st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        with st.container():
            st.markdown("<div class='monitor-none'>", unsafe_allow_html=True)
            if st.button("Monitor None"):
                st.session_state.monitored_spots = []
                st.session_state.prev_status = {}
                st.info("Monitoring disabled")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='muted'>Tip: You can use a mobile IP camera app for live monitoring.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Main dashboard ----------
left, right = st.columns([3, 1], gap="large")

with left:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Live Parking Feed")
    video_placeholder = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Overview")
    col1, col2 = st.columns(2)
    free_metric = col1.empty()
    total_metric = col2.empty()
    st.markdown("**Free Spots**")
    free_box = st.empty()
    st.markdown("**Occupied Spots**")
    occ_box = st.empty()
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Video processing ----------
cap = cv2.VideoCapture(stream_url)
if not cap.isOpened():
    st.error("Could not open video source.")
    st.stop()

try:
    while cap.isOpened():
        success, img = cap.read()
        if not success:
            if source_mode == "Demo video":
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                st.error("Stream ended or unavailable.")
                break

        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
        imgThreshold = cv2.adaptiveThreshold(
            imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16
        )
        imgMedian = cv2.medianBlur(imgThreshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

        img_result, free_spaces, status_list = checkParkingSpace(img.copy(), imgDilate, posList)

        free_metric.markdown(
            f"<div class='metric'><div style='color:#a7f3d0'>Free</div><div style='font-size:26px;font-weight:700'>{free_spaces}</div></div>",
            unsafe_allow_html=True,
        )
        total_metric.markdown(
            f"<div class='metric'><div style='color:#94a3b8'>Total</div><div style='font-size:26px;font-weight:700'>{len(posList)}</div></div>",
            unsafe_allow_html=True,
        )

        free_spots = [SPOT_NAMES[i] for i, s in enumerate(status_list) if s == "Free"]
        occ_spots = [SPOT_NAMES[i] for i, s in enumerate(status_list) if s == "Occupied"]

        def make_badges(lst, cls):
            if not lst:
                return "<div class='badge badge-muted'>None</div>"
            return " ".join([f"<span class='badge {cls}'>{x}</span>" for x in lst])

        free_box.markdown(f"<div>{make_badges(free_spots, 'badge-free')}</div>", unsafe_allow_html=True)
        occ_box.markdown(f"<div>{make_badges(occ_spots, 'badge-occ')}</div>", unsafe_allow_html=True)

        video_placeholder.image(cv2.cvtColor(img_result, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)
        time.sleep(0.03)
finally:
    cap.release()
