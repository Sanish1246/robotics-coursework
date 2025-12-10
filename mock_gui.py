import streamlit as st
from PIL import Image
import cv2 as cv
from ultralytics import YOLO
from datetime import datetime
import os
import time
from Arm_Lib import Arm_Device

# -----------------------------
# Global CSS + 3x3 grid + Emergency + 16:9 styling
# -----------------------------
st.markdown("""
<style>
:root {
    --pink: #FC3E57;
    --mint: #5E918A;
    --deep-dark: #14151B;
    --cream: #FBFBFA;
}

/* Base page */
body, .stApp {
    background: var(--deep-dark) !important;
    color: var(--cream) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial;
}

/* Title */
.robobazaar-title {
    font-size: 42px !important;
    font-weight: 900 !important;
    color: var(--cream) !important;
    text-align: center;
    padding: 18px 0;
    letter-spacing: 1px;
}

/* Section header */
.section-header {
    font-size: 20px !important;
    font-weight: 800 !important;
    color: var(--mint) !important;
    margin-top: 8px;
    margin-bottom: 6px;
}

/* Glass card */
.card {
    background: linear-gradient(180deg, rgba(94,145,138,0.10), rgba(252,62,87,0.04));
    border-radius: 14px;
    padding: 18px;
    border: 1px solid rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 6px 22px rgba(0,0,0,0.45);
}

/* Dark card */
.card-dark {
    background: rgba(20,21,27,0.45);
    border-radius: 12px;
    padding: 12px;
    border: 1px solid rgba(255,255,255,0.04);
}

/* Buttons style */
.stButton>button {
    background: var(--mint) !important;
    color: var(--cream) !important;
    padding: 12px 0 !important;
    width: 100% !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 16px !important;
    box-shadow: 0 6px 14px rgba(94,145,138,0.12);
    transition: transform 0.12s ease, filter 0.12s ease;
}

.stButton>button:hover {
    background: var(--pink) !important;
    color: var(--deep-dark) !important;
    transform: translateY(-2px);
}

/* Emergency button */
.danger-btn .stButton>button {
    background: var(--pink) !important;
    color: var(--deep-dark) !important;
    font-size: 20px !important;
    font-weight: 900 !important;
    padding: 18px 0 !important;
    box-shadow: 0 6px 22px rgba(252,62,87,0.35);
}

.danger-btn .stButton>button:hover {
    filter: brightness(0.9);
}

/* Grid layout 3x3 */
.grid-3x3 {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-gap: 12px;
}

/* Capture box */
.capture-box {
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.06);
    padding: 10px;
    background: rgba(255,255,255,0.01);
}

/* 16:9 image container */
.aspect-16-9 {
    position: relative;
    width: 100%;
    padding-bottom: 56.25%; /* 16:9 ratio */
    overflow: hidden;
    border-radius: 12px;
}

.aspect-16-9 img {
    position: absolute;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* Footer */
.footer {
    margin-top: 28px;
    padding: 18px;
    color: rgba(251,251,250,0.7);
    text-align: center;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Robot logic (unchanged)
# -----------------------------
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

# -----------------------------
# UI: 3x3 button grid + EMERGENCY + 16:9 live preview
# -----------------------------
st.markdown('<div class="robobazaar-title">ROBOBAZAAR</div>', unsafe_allow_html=True)
st.markdown('<div style="max-width:1100px;margin:0 auto">', unsafe_allow_html=True)

# Fruit / Vegetable Card
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">Choose a Fruit / Vegetable</div>', unsafe_allow_html=True)
st.markdown('<div class="grid-3x3">', unsafe_allow_html=True)

# Row 1
if st.button("Green apple"): prepare_search("green apple")
if st.button("Kiwi"): prepare_search("kiwi")
if st.button("Tomato"): prepare_search("Tomato")
# Row 2
if st.button("Lemon"): prepare_search("Lemon")
if st.button("Strawberry"): prepare_search("strawberry")
if st.button("Carrot"): prepare_search("carrot")
# Row 3 (blank, blank, EMERGENCY)
st.markdown('<div></div><div></div>', unsafe_allow_html=True)
st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
if st.button("EMERGENCY STOP"):
    emergency_stop()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # end grid
st.markdown('</div>', unsafe_allow_html=True)  # end card

if st.session_state.msg:
    st.success(st.session_state.msg)

# Live Detection Card
st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">Live Detection</div>', unsafe_allow_html=True)
if "live_container" not in st.session_state:
    st.session_state.live_container = st.empty()
if "image_placeholder" not in st.session_state:
    st.session_state.image_placeholder = st.empty()
st.markdown('<div class="card-dark">', unsafe_allow_html=True)
st.markdown('<div class="faint">Status:</div>', unsafe_allow_html=True)
st.markdown(f"<div style='margin-top:6px;font-weight:700;color:var(--cream)'>{st.session_state.status}</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
st.markdown('<div class="capture-box aspect-16-9">', unsafe_allow_html=True)
if st.session_state.last_capture and os.path.exists(st.session_state.last_capture):
    img = Image.open(st.session_state.last_capture)
    st.image(img, use_column_width=True, caption="Latest Capture")
else:
    st.info("No image detected yet.")
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">Designed with ♥ — Palette: Pink / Mint / Deep Dark / Cream</div>', unsafe_allow_html=True)

# Cleanup
try:
    del Arm
except:
    pass
