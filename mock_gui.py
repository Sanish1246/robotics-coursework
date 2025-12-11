import streamlit as st
from PIL import Image
import cv2 as cv
from ultralytics import YOLO
from datetime import datetime
import os
import time
from Arm_Lib import Arm_Device


retro_css = """
<style>
/* ========== CSS VARIABLES ========== */
:root {
    --teal: #3E6868;
    --red: #C94E44;
    --tan: #C1AB85;
    --black-bg: #1A1A1A;
    --dark-accent: #3D413A;
    --cream: #FBFBFA;
    --grain-opacity: 0.03;
}

/* ========== BASE RESETS ========== */
.stApp {
    background: var(--cream) !important;
    background-image: 
        repeating-linear-gradient(
            0deg, 
            transparent, 
            transparent 2px, 
            rgba(0,0,0,0.02) 2px, 
            rgba(0,0,0,0.02) 4px
        );
}

/* ========== TYPOGRAPHY ========== */
h1, h2, h3, h4, h5, h6 {
    color: var(--black-bg) !important;
    font-family: 'Courier New', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    text-shadow: 2px 2px 0px var(--tan) !important;
}

h1 {
    font-size: 3rem !important;
    border-bottom: 4px solid var(--teal) !important;
    padding-bottom: 0.5rem !important;
    margin-bottom: 1.5rem !important;
}

h2 {
    font-size: 2rem !important;
    color: var(--dark-accent) !important;
    border-left: 6px solid var(--red) !important;
    padding-left: 1rem !important;
    margin-top: 2rem !important;
}

p, .stMarkdown, .stText {
    color: var(--dark-accent) !important;
    font-family: 'Courier New', monospace !important;
    font-size: 1rem !important;
    line-height: 1.6 !important;
}

/* ========== BUTTONS ========== */
.stButton button {
    background: linear-gradient(135deg, var(--teal) 0%, var(--dark-accent) 100%) !important;
    color: var(--cream) !important;
    border: 3px solid var(--black-bg) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.5rem !important;
    font-family: 'Courier New', monospace !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    box-shadow: 
        4px 4px 0px var(--black-bg),
        inset 0 -2px 8px rgba(0,0,0,0.2) !important;
    transition: all 0.15s ease !important;
    cursor: pointer !important;
}

.stButton button:hover {
    background: linear-gradient(135deg, var(--red) 0%, var(--tan) 100%) !important;
    transform: translate(2px, 2px) !important;
    box-shadow: 
        2px 2px 0px var(--black-bg),
        inset 0 -2px 8px rgba(0,0,0,0.3) !important;
}

.stButton button:active {
    transform: translate(4px, 4px) !important;
    box-shadow: 
        0px 0px 0px var(--black-bg),
        inset 0 2px 8px rgba(0,0,0,0.4) !important;
}

/* Emergency Stop Button Styling */
.stButton button:last-child {
    background: linear-gradient(135deg, var(--red) 0%, #8B0000 100%) !important;
    border-color: var(--black-bg) !important;
    animation: pulse-emergency 2s infinite !important;
}

@keyframes pulse-emergency {
    0%, 100% { box-shadow: 4px 4px 0px var(--black-bg), 0 0 0 0 rgba(201, 78, 68, 0); }
    50% { box-shadow: 4px 4px 0px var(--black-bg), 0 0 0 10px rgba(201, 78, 68, 0.3); }
}

/* ========== CONTAINERS & BLOCKS ========== */
.block-container {
    padding: 2rem 3rem !important;
    max-width: 1400px !important;
}

div[data-testid="stVerticalBlock"] > div {
    background: rgba(255, 255, 255, 0.6) !important;
    border: 2px solid var(--tan) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    margin: 1rem 0 !important;
    box-shadow: 
        6px 6px 0px var(--dark-accent),
        inset 0 0 20px rgba(62, 104, 104, 0.05) !important;
}

/* ========== IMAGES ========== */
img {
    border: 4px solid var(--black-bg) !important;
    border-radius: 12px !important;
    box-shadow: 8px 8px 0px var(--teal) !important;
    transition: transform 0.2s ease !important;
}

img:hover {
    transform: scale(1.02) !important;
}

/* ========== SUCCESS/INFO MESSAGES ========== */
.stSuccess {
    background: linear-gradient(135deg, var(--teal), var(--dark-accent)) !important;
    color: var(--cream) !important;
    border-left: 6px solid var(--tan) !important;
    border-radius: 10px !important;
    padding: 1rem 1.5rem !important;
    font-family: 'Courier New', monospace !important;
    font-weight: 600 !important;
    box-shadow: 4px 4px 0px var(--black-bg) !important;
}

.stInfo {
    background: var(--tan) !important;
    color: var(--black-bg) !important;
    border-left: 6px solid var(--teal) !important;
    border-radius: 10px !important;
    padding: 1rem 1.5rem !important;
    font-family: 'Courier New', monospace !important;
    box-shadow: 4px 4px 0px var(--dark-accent) !important;
}

/* ========== COLUMNS ========== */
div[data-testid="column"] {
    padding: 0.5rem !important;
}

/* ========== TEXT ELEMENTS ========== */
.stText {
    background: var(--black-bg) !important;
    color: var(--cream) !important;
    padding: 0.75rem 1.25rem !important;
    border-radius: 8px !important;
    border: 2px solid var(--teal) !important;
    font-family: 'Courier New', monospace !important;
    font-weight: 600 !important;
    box-shadow: 3px 3px 0px var(--dark-accent) !important;
    margin: 0.5rem 0 !important;
}

/* ========== CAPTIONS ========== */
.stImage > div > div {
    color: var(--dark-accent) !important;
    font-family: 'Courier New', monospace !important;
    font-style: italic !important;
    margin-top: 0.5rem !important;
}

/* ========== SCROLLBAR ========== */
::-webkit-scrollbar {
    width: 12px;
    background: var(--cream);
}

::-webkit-scrollbar-track {
    background: var(--tan);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: var(--teal);
    border-radius: 10px;
    border: 2px solid var(--cream);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--dark-accent);
}

/* ========== RETRO SCAN LINES ========== */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.05),
        rgba(0, 0, 0, 0.05) 1px,
        transparent 1px,
        transparent 2px
    );
    pointer-events: none;
    z-index: 9999;
}

/* ========== VIGNETTE EFFECT ========== */
.stApp::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    box-shadow: inset 0 0 150px rgba(26, 26, 26, 0.3);
    pointer-events: none;
    z-index: 9998;
}
</style>
"""

st.markdown(retro_css, unsafe_allow_html=True)

if "emergency_stop" not in st.session_state:
    st.session_state.emergency_stop = False

if "items" not in st.session_state:
    st.session_state.items = []

if "camera" not in st.session_state:
    st.session_state.camera = None

if "status" not in st.session_state:
    st.session_state.status = "Waiting for selection"

if "last_capture" not in st.session_state:
    st.session_state.last_capture = None

if "label" not in st.session_state:
    st.session_state.label = "None"

if "conf" not in st.session_state:
    st.session_state.conf = 0

if "nextIng" not in st.session_state:
    st.session_state.nextIng = "None"

if "msg" not in st.session_state:
    st.session_state.msg = ""

if "live_container" not in st.session_state:
    st.session_state.live_container = st.empty()

if "image_placeholder" not in st.session_state:
    st.session_state.image_placeholder = st.empty()

def emergency_stop():
    st.session_state.emergency_stop = True
    try:
        arm_clamp_block("Drop")
        arm_move(p_mould, 1000)
    except:
        pass

def find_camera(max_index=5):
    for i in range(max_index):
        cam = cv.VideoCapture(i)
        if cam.isOpened():
            print(f"Camera found at index {i}")
            return cam
        cam.release()
    return None

if st.session_state.camera is None:
    cam = find_camera()
    if cam is not None:
        st.session_state.camera = cam

Arm = Arm_Device()
time.sleep(.1)

def arm_clamp_block(enable):
    mapping = {
        "Drop": 15,
        "Tomato": 116,
        "Lemon": 90,
        "carrot": 144,
        "green apple": 81,
        "kiwi": 100,
        "strawberry": 122
    }
    if enable in mapping:
        Arm.Arm_serial_servo_write(6, mapping[enable], 400)
    time.sleep(.5)

def arm_move(p, s_time=500):
    for i in range(5):
        sid = i + 1
        t = int(s_time * 1.2) if sid == 5 else s_time
        Arm.Arm_serial_servo_write(sid, p[i], t)
        time.sleep(.01)
    time.sleep(s_time/1000)

# Position arrays
p_mould = [90, 130, 0, 0, 90]
top_positions = [[180,63,52,0,90],[146,63,52,0,90],[117,63,52,0,90],[82,63,52,0,90],[50,63,52,0,90],[91,106,0,0,90]]
photo_positions = [[180,63,52,0,90],[150,63,52,0,90],[120,63,52,0,90],[86,63,52,0,90],[53,63,52,0,90],[95,106,0,0,90]]
bottom_positions = [[180,43,58,27,90],[146,43,58,27,90],[112,43,58,27,90],[82,43,58,27,90],[50,43,58,27,90],[91,56,40,3,90]]
p_Mixer = [0, 130, 20, 40, 270]

arm_clamp_block("Drop")
arm_move(p_mould, 1000)
time.sleep(1)

model = YOLO('best.pt', task='detect')

def vegetable(frame):
    results = model(frame)
    detections = results[0].boxes
    output = []
    if len(detections) == 0:
        st.session_state.label = "None"
        st.session_state.conf = 0
        return []
    for box in detections:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        label = model.names[int(box.cls[0])]
        st.session_state.label = label
        st.session_state.conf = conf
        if label in ["Tomato","Lemon","carrot","kiwi","green apple","strawberry"]:
            output.append((label, conf, (x1,y1,x2,y2)))
    return output

def detect(frame, draw_boxes=True):
    frame_resized = cv.resize(frame, (640,640))
    detections = vegetable(frame_resized)
    labels = [d[0] for d in detections]

    if draw_boxes:
        for label, conf, (x1,y1,x2,y2) in detections:
            cv.rectangle(frame_resized, (x1,y1),(x2,y2),(0,255,0),2)
            cv.putText(frame_resized, f"{label} {conf:.2f}", (x1,y1-10),
                       cv.FONT_HERSHEY_SIMPLEX, 0.6,(0,255,0),2)

    return labels, frame_resized

def capture_frame(camera, save=True, save_dir="captures"):
    ret, frame = camera.read()
    if not ret or frame is None:
        raise RuntimeError("Camera failed")

    labels, frame_with_boxes = detect(frame, draw_boxes=True)

    with st.session_state.live_container.container():
        st.text(st.session_state.status)
        st.image(frame_with_boxes, channels="BGR", caption="Live Detection")
        st.write(f"**Last detection:** {st.session_state.label} - **Confidence:** {st.session_state.conf:.2f}")

    if save:
        os.makedirs(save_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(save_dir, f"capture_{ts}.jpg")
        cv.imwrite(filename, frame_with_boxes)
        st.session_state.last_capture = filename

    return frame_with_boxes

def detect_one_frame(camera):
    ret, frame = camera.read()
    if not ret:
        camera.release()
        st.session_state.camera = find_camera()
        ret, frame = st.session_state.camera.read()
    labels, _ = detect(frame, draw_boxes=True)
    return labels

def flush_camera(camera, frames=5):
    for _ in range(frames):
        camera.read()

def get_camera():
    return st.session_state.camera

def search_items(items):
    camera = get_camera()
    picked = [False]*6
    missing = False

    for item in items:
        if st.session_state.emergency_stop:
            st.session_state.status = "Emergency stop activated!"
            arm_move(p_mould, 1000)
            return True
        st.session_state.status = f"Searched for: {item}"
        print("Looking for:", item)
        found = False

        for i in range(len(top_positions)):
            if st.session_state.emergency_stop:
                st.session_state.status = "Emergency stop activated!"
                arm_move(p_mould, 1000)
                return True
            arm_move(top_positions[i], 2000)
            time.sleep(1)

            if not picked[i]:
                arm_move(photo_positions[i], 1000)
                time.sleep(0.2)

                flush_camera(camera)
                labels = detect_one_frame(camera)
                frame = capture_frame(camera, save=True)

                if item in labels:
                    picked[i] = True
                    arm_move(top_positions[i], 1000)
                    arm_move(bottom_positions[i], 1000)
                    arm_clamp_block(item)
                    arm_move(top_positions[i], 1000)
                    arm_move(p_Mixer, 1500)
                    arm_clamp_block("Drop")
                    found = True
                    break

        if not found:
            missing = True
            arm_move(p_mould, 1000)
            break

    arm_move(p_mould, 1000)
    return missing

def prepare_search(items):
    st.session_state.emergency_stop = False
    msg = "Item added to basket!"
    missing = search_items(st.session_state.items)
    st.session_state.status = "Waiting for next selection"
    if not missing and not st.session_state.emergency_stop:
        st.session_state.msg = msg


st.title("Robobazaar")
st.header("Choose an Item")

col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

if col1.button("Green apple"):
    st.session_state.items.append("green apple")
if col2.button("Kiwi"):
    st.session_state.items.append("kiwi")
if col3.button("Tomato"):
    st.session_state.items.append("Tomato")
if col4.button("Lemon"):
    st.session_state.items.append("Lemon")
if col5.button("Strawberry"):
    st.session_state.items.append("strawberry")
if col6.button("Carrot"):
    st.session_state.items.append("carrot")
if col7.button("Search"):
    prepare_search(st.session_state.items)
if col8.button("EMERGENCY STOP"):
    emergency_stop()

if st.session_state.msg:
    st.success(st.session_state.msg)

st.subheader("Live Detection")
st.session_state.live_container

st.text("Last detection")
if st.session_state.last_capture and os.path.exists(st.session_state.last_capture):
    img = Image.open(st.session_state.last_capture)
    st.image(img, width=300, caption="Latest Capture")
else:
    st.info("No image detected yet.")

del Arm