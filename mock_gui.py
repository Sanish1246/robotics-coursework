import streamlit as st
from PIL import Image
import cv2 as cv
from ultralytics import YOLO
from datetime import datetime
import os
import time
from Arm_Lib import Arm_Device

# -----------------------------
# Global CSS + 16:9 + 3x3 grid + emergency button styling
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

/* Title (poster-like) */
.robobazaar-title {
    font-size: 42px !important;
    font-weight: 900 !important;
    color: var(--cream) !important;
    text-align: center;
    padding: 18px 0;
    letter-spacing: 1px;
}

/* Subheading */
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

/* Secondary card (darker) */
.card-dark {
    background: rgba(20,21,27,0.45);
    border-radius: 12px;
    padding: 12px;
    border: 1px solid rgba(255,255,255,0.04);
}

/* Buttons style (Streamlit default buttons) */
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

/* Grid layout for 3x3 buttons */
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

# Camera, arm, detection code stays unchanged...
# [Keep all functions: find_camera, arm_clamp_block, arm_move, vegetable, detect, capture_frame, search_ingredient, prepare_search, etc.]

# -----------------------------
# Styled UI: 3x3 grid for buttons
# -----------------------------
st.markdown('<div class="robobazaar-title">ROBOBAZAAR</div>', unsafe_allow_html=True)
st.markdown('<div style="max-width:1100px;margin:0 auto">', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">Choose a Fruit / Vegetable</div>', unsafe_allow_html=True)

st.markdown('<div class="grid-3x3">', unsafe_allow_html=True)

# 1st row
if st.button("Green apple"):
    prepare_search("green apple")
if st.button("Kiwi"):
    prepare_search("kiwi")
if st.button("Tomato"):
    prepare_search("Tomato")

# 2nd row
if st.button("Lemon"):
    prepare_search("Lemon")
if st.button("Strawberry"):
    prepare_search("strawberry")
if st.button("Carrot"):
    prepare_search("carrot")

# 3rd row
st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
if st.button("EMERGENCY STOP"):
    emergency_stop()
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div></div><div></div>', unsafe_allow_html=True)  # blank cells

st.markdown('</div>', unsafe_allow_html=True)  # end grid
st.markdown('</div>', unsafe_allow_html=True)  # end card

if st.session_state.msg:
    st.success(st.session_state.msg)

# Live Detection Card with 16:9 ratio
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

st.markdown('</div>', unsafe_allow_html=True)  # end capture-box
st.markdown('</div>', unsafe_allow_html=True)  # end card

st.markdown('<div class="footer">Designed with ♥ — Palette: Pink / Mint / Deep Dark / Cream</div>', unsafe_allow_html=True)

# Clean up Arm object
try:
    del Arm
except:
    pass
