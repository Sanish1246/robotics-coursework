import streamlit as st
from PIL import Image
import cv2 as cv
from ultralytics import YOLO
from datetime import datetime
import os
import time
from Arm_Lib import Arm_Device


if "force_refresh" in st.session_state and st.session_state.force_refresh:
    st.session_state.force_refresh = False
    st.rerun()

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

    st.session_state.force_refresh = True
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



def prepare_smoothie(ingredients):
    camera = get_camera()
    picked = [False]*6
    missing = False

    for ingredient in ingredients:
        if st.session_state.emergency_stop:
            st.session_state.status = "Emergency stop activated!"
            arm_move(p_mould, 1000)
            return True
        st.session_state.status ="Searched for:",ingredient
        print("Looking for:", ingredient)
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

                if ingredient in labels:
                    picked[i] = True
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
            break

    arm_move(p_mould, 1000)
    return missing


if "msg" not in st.session_state:
    st.session_state.msg = ""


def make_smoothie(preset):
    st.session_state.emergency_stop = False
    if preset == 1:
        ingredients = ['Lemon','carrot','strawberry']
        msg = "Kiwi Berry Splash ready!"
    elif preset == 2:
        ingredients = ['carrot','Tomato']
        msg = "Garden Duo Juice ready!"
    else:
        ingredients = ['Lemon','carrot','strawberry']
        msg = "Carrot Citrus Mix ready!"

    missing = prepare_smoothie(ingredients)
    st.session_state.status = "Waiting for next selection"
    if not missing and not st.session_state.emergency_stop:
        st.session_state.msg = msg


st.title("Welcome to the Robotic Juice Maker!")
st.header("Choose a juice")

col1, col2, col3 ,col4= st.columns(4)
if col1.button("Kiwi Berry Splash"):
    make_smoothie(1)
if col2.button("Garden Duo Juice"):
    make_smoothie(2)
if col3.button("Carrot Citrus Mix"):
    make_smoothie(3)

if col4.button("EMERGENCY STOP"):
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
