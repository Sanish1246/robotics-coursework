import streamlit as st
from PIL import Image
import cv2 as cv
from ultralytics import YOLO
from datetime import datetime
import os
import time
from Arm_Lib import Arm_Device

st.markdown("""
<style>
    /* Import font for better aesthetics */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* Color palette */
    :root {
        --teal: #3E6868;
        --red: #C94E44;
        --tan: #C1AB85;
        --black-bg: #1A1A1A;
        --dark-accent: #3D413A;
        --cream: #FBFBFA;
    }
    
    /* Main app background */
    .stApp {
        background-color: #1A1A1A;
        color: #FBFBFA;
        font-family: 'Inter', sans-serif;
    }
    
    /* Center main content */
    .main .block-container {
        max-width: 1200px;
        padding-left: 2rem;
        padding-right: 2rem;
        margin: 0 auto;
    }
    
    /* Header styling */
    h1 {
        color: #FBFBFA !important;
        font-weight: 800 !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        text-align: center;
    }
    
    h2, h3 {
        color: #FBFBFA !important;
        font-weight: 700 !important;
        text-align: center;
    }
    
    /* Button styling - default (teal) */
    .stButton > button {
        background-color: #3E6868 !important;
        color: #FBFBFA !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1.25rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(62, 104, 104, 0.3) !important;
        width: 100% !important;
        height: 80px !important;
    }
    
    .stButton > button:hover {
        background-color: #2d4f4f !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(62, 104, 104, 0.4) !important;
    }
    
    /* Emergency button styling - bigger and redder */
    .emergency-button .stButton > button {
        background: linear-gradient(135deg, #C94E44 0%, #a63d35 100%) !important;
        box-shadow: 0 6px 20px rgba(201, 78, 68, 0.5) !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        height: 100px !important;
        letter-spacing: 1px !important;
        border: 3px solid rgba(251, 251, 250, 0.2) !important;
    }
    
    .emergency-button .stButton > button:hover {
        background: linear-gradient(135deg, #a63d35 0%, #8b2f28 100%) !important;
        box-shadow: 0 8px 24px rgba(201, 78, 68, 0.6) !important;
        transform: translateY(-3px) scale(1.02) !important;
    }
    
    /* Card styling for live detection */
    .poster-frame {
        background: linear-gradient(180deg, rgba(0,0,0,0.35), rgba(0,0,0,0.2));
        border: 4px solid rgba(193, 171, 133, 0.5);
        box-shadow: 0 8px 30px rgba(0,0,0,0.6);
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem auto;
        background-color: #3D413A;
        max-width: 800px;
    }
    
    /* Info boxes */
    .stInfo, .stSuccess, .stWarning {
        background-color: #3D413A !important;
        border-left: 4px solid #3E6868 !important;
        color: #FBFBFA !important;
        border-radius: 6px !important;
    }
    
    .stSuccess {
        border-left-color: #C1AB85 !important;
        background-color: rgba(193, 171, 133, 0.15) !important;
    }
    
    /* Text elements */
    .stMarkdown, p, label {
        color: #FBFBFA !important;
    }
    
    /* Dividers */
    hr {
        border-color: rgba(251, 251, 250, 0.1) !important;
        margin: 2rem 0 !important;
    }
    
    /* Image captions */
    .stImage > div > div {
        background-color: #3D413A;
        border: 3px solid rgba(193, 171, 133, 0.4);
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    
    /* Text styling */
    div[data-testid="stText"] {
        color: #FBFBFA !important;
        font-weight: 500;
        background-color: rgba(62, 104, 104, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 6px;
        border-left: 3px solid #3E6868;
    }
    
    /* Header bar */
    header[data-testid="stHeader"] {
        background-color: #3E6868 !important;
    }
    
    /* Sidebar (if used) */
    section[data-testid="stSidebar"] {
        background-color: #3D413A !important;
    }
    
    /* Column containers */
    div[data-testid="column"] {
        padding: 0.5rem;
    }
    
    /* Detection info */
    .detection-info {
        background-color: rgba(62, 104, 104, 0.2);
        border-left: 4px solid #C1AB85;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    /* Button grid container */
    .button-grid {
        max-width: 900px;
        margin: 2rem auto;
    }
    
    /* Subtitle styling */
    .subtitle {
        font-size: 1.1rem;
        color: #C1AB85;
        font-weight: 500;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Section headers */
    .section-header {
        text-align: center;
        margin: 2rem 0 1rem 0;
        font-size: 1.5rem;
        color: #FBFBFA;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

if "emergency_stop" not in st.session_state:
    st.session_state.emergency_stop = False

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

if "camera" not in st.session_state or st.session_state.camera is None:
    cam = find_camera()
    if cam is not None:
        st.session_state.camera = cam
    else:
        st.session_state.camera = None

if "status" not in st.session_state:
    st.session_state.status = "Waiting for selection"

if "last_capture" not in st.session_state:
    st.session_state.last_capture = None

if "label" not in st.session_state:
    st.session_state.label="None"
if "conf" not in st.session_state:
    st.session_state.conf=0

if "nextIng" not in st.session_state:
    st.session_state.nextIng="None"

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

p_mould = [90, 130, 0, 0, 90]

top_positions=[[180,63,52,0,90],[146,63,52,0,90],[117,63,52,0,90],[82,63,52,0,90],[50,63,52,0,90],[91,106,0,0,90]]
photo_positions=[[180,63,52,0,90],[150,63,52,0,90],[120,63,52,0,90],[86,63,52,0,90],[53,63,52,0,90],[95,106,0,0,90]]
bottom_positions=[[180,43,58,27,90],[146,43,58,27,90],[112,43,58,27,90],[82,43,58,27,90],[50,43,58,27,90],[91,56,40,3,90]]

p_Mixer=[0, 130, 20, 40, 270]

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
        st.session_state.label=label
        
        st.session_state.conf=conf
        if label in ["Tomato","Lemon","carrot","kiwi","green apple","strawberry"]:
            output.append((label, conf, (x1,y1,x2,y2)))
    return output

def detect(frame, draw_boxes=True):
    frame_resized = cv.resize(frame, (640,640))
    detections = vegetable(frame_resized)
    labels = [d[0] for d in detections]

    if draw_boxes:
        for label, conf, (x1,y1,x2,y2) in detections:
            cv.rectangle(frame_resized, (x1,y1),(x2,y2),(62,104,104),3)
            cv.putText(frame_resized, f"{label} {conf:.2f}", (x1,y1-10),
                       cv.FONT_HERSHEY_SIMPLEX, 0.7,(193,171,133),2)

    return labels, frame_resized

def capture_frame(camera, save=True, save_dir="captures"):
    ret, frame = camera.read()
    if not ret or frame is None:
        raise RuntimeError("Camera failed")

    labels, frame_with_boxes = detect(frame, draw_boxes=True)

    with st.session_state.live_container.container():
        st.markdown(f'<div class="detection-info"><strong>Status:</strong> {st.session_state.status}</div>', unsafe_allow_html=True)
        st.image(frame_with_boxes, channels="BGR", caption="Live Detection", use_container_width=True)
        st.markdown(f'<div class="detection-info"><strong>Last Detection:</strong> {st.session_state.label} | <strong>Confidence:</strong> {st.session_state.conf:.2f}</div>', unsafe_allow_html=True)

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

def search_ingredient(ingredient):
    camera = get_camera()

    missing = False

    if st.session_state.emergency_stop:
        st.session_state.status = "Emergency stop activated!"
        arm_move(p_mould, 1000)
        return True
    st.session_state.status ="Searched for:",ingredient
    found = False

    for i in range(len(top_positions)):
        if st.session_state.emergency_stop:
            st.session_state.status = "Emergency stop activated!"
            arm_move(p_mould, 1000)
            return True
        arm_move(top_positions[i], 2000)
        time.sleep(1)

        arm_move(photo_positions[i], 1000)
        time.sleep(0.2)

        flush_camera(camera)
        labels = detect_one_frame(camera)
        frame = capture_frame(camera, save=True)  

        if ingredient in labels:
            arm_move(top_positions[i], 1000)
            arm_move(bottom_positions[i], 1000)
            arm_clamp_block(ingredient)
            arm_move(top_positions[i], 1000)
            arm_move(p_Mixer, 1500)
            arm_clamp_block("Drop")
            found = True
            break

    if not found:
        missing = True

    arm_move(p_mould, 1000)
    return missing

if "msg" not in st.session_state:
    st.session_state.msg = ""

def prepare_search(ingredient):
    st.session_state.emergency_stop = False
    msg = "Item found!"

    missing = search_ingredient(ingredient)
    st.session_state.status = "Waiting for next selection"
    if not missing and not st.session_state.emergency_stop:
        st.session_state.msg = msg

# Header with vintage styling
st.title("Robobazaar")
st.markdown('<p class="subtitle">Automated Fruit & Vegetable Selection System</p>', unsafe_allow_html=True)

st.markdown("---")

st.markdown('<h2 class="section-header">Choose a Fruit or Vegetable</h2>', unsafe_allow_html=True)

# 3x3 Button Grid Layout
st.markdown('<div class="button-grid">', unsafe_allow_html=True)

# Row 1: Green Apple, Kiwi, Tomato
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Green Apple", key="apple"):
        prepare_search("green apple")
with col2:
    if st.button("Kiwi", key="kiwi"):
        prepare_search("kiwi")
with col3:
    if st.button("Tomato", key="tomato"):
        prepare_search("Tomato")

# Row 2: Lemon, Strawberry, Carrot
col4, col5, col6 = st.columns(3)
with col4:
    if st.button("Lemon", key="lemon"):
        prepare_search("Lemon")
with col5:
    if st.button("Strawberry", key="strawberry"):
        prepare_search("strawberry")
with col6:
    if st.button("Carrot", key="carrot"):
        prepare_search("carrot")

# Row 3: Emergency Stop Button (centered and bigger)
st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
col_empty1, col_emergency, col_empty2 = st.columns([1, 2, 1])
with col_emergency:
    st.markdown('<div class="emergency-button">', unsafe_allow_html=True)
    if st.button("EMERGENCY STOP", key="emergency"):
        emergency_stop()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.msg:
    st.success(st.session_state.msg)

st.markdown("---")

# Live Detection Section
st.markdown('<h2 class="section-header">Live Detection Feed</h2>', unsafe_allow_html=True)
if "live_container" not in st.session_state:
    st.session_state.live_container = st.empty()
if "image_placeholder" not in st.session_state:
    st.session_state.image_placeholder = st.empty()

st.markdown("---")

# Latest Capture Section with card styling
st.markdown('<h2 class="section-header">Latest Capture</h2>', unsafe_allow_html=True)
if st.session_state.last_capture and os.path.exists(st.session_state.last_capture):
    st.markdown('<div class="poster-frame">', unsafe_allow_html=True)
    img = Image.open(st.session_state.last_capture)
    st.image(img, caption="Most Recent Detection", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No image captured yet. Select an item to begin detection.")

del Arm