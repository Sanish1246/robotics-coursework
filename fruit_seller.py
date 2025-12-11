import streamlit as st
from PIL import Image
import cv2 as cv
from ultralytics import YOLO
from datetime import datetime
import os
import time
from Arm_Lib import Arm_Device



if "emergency_stop" not in st.session_state:
    st.session_state.emergency_stop = False

if "order_items" not in st.session_state:
    st.session_state.order_items = []

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
        "Tomato": 112,
        "Lemon": 95,
        "carrot": 145,
        "green apple": 81,
        "kiwi": 100,
        "strawberry": 124
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



def search_items():
    camera = get_camera()
    picked = [False]*6
    missing = False

    for item in st.session_state.order_items:
        if st.session_state.emergency_stop:
            st.session_state.status = "Emergency stop activated!"
            st.session.state.order_items=[]
            arm_move(p_mould, 1000)
            return True
        st.session_state.status ="Searched for:",item
        print("Looking for:", item)
        found = False

        for i in range(len(top_positions)):
            if st.session_state.emergency_stop:
                st.session_state.status = "Emergency stop activated!"
                st.session.state.order_items=[]
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

    arm_move(p_mould, 1000)
    st.session_state.order_items=[]
    return missing


if "msg" not in st.session_state:
    st.session_state.msg = ""


def prepare_search():
    st.session_state.emergency_stop = False
    msg = "Item found!"
    print(st.session_state.order_items)

    missing = search_items()
    st.session_state.status = "Waiting for next selection"
    if not missing and not st.session_state.emergency_stop:
        st.session_state.msg = msg


st.title("Robobazaar")
st.header("Choose a fruit/vegetable")

col1, col2, col3 ,col4,col5,col6,col7,col8= st.columns(8)
if col1.button("Green apple"):
    st.session_state.order_items.append("green apple")
if col2.button("Kiwi"):
    st.session_state.order_items.append("kiwi")
if col3.button("Tomato"):
    st.session_state.order_items.append("Tomato")
if col4.button("Lemon"):
    st.session_state.order_items.append("Lemon")
if col5.button("Strawberry"):
    st.session_state.order_items.append("strawberry")
if col6.button("Carrot"):
    st.session_state.order_items.append("carrot")

if col7.button("Search"):
    prepare_search()

if col8.button("EMERGENCY STOP"):
    emergency_stop()

if st.session_state.msg:
    st.success(st.session_state.msg)

st.subheader("Live Detection")
if "live_container" not in st.session_state:
    st.session_state.live_container = st.empty()
if "image_placeholder" not in st.session_state:
    st.session_state.image_placeholder = st.empty()
st.text("Last detection")
if st.session_state.last_capture and os.path.exists(st.session_state.last_capture):
    img = Image.open(st.session_state.last_capture)
    st.image(img, width=300, caption="Latest Capture")
else:
    st.info("No image detected yet.")

del Arm