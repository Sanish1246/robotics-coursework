import streamlit as st
from PIL import Image

if "msg" not in st.session_state:
    st.session_state.msg = ""

if "status" not in st.session_state:
    st.session_state.status = "Waiting for selection"

def make_smoothie(preset):
    st.session_state.status = "Preparing your juice..."
    if preset == 1:
        st.session_state.msg = ""
        st.session_state.status = "Waiting for next selection"
        st.session_state.msg = "Kiwi Berry Splash ready!"
    elif preset == 2:
        st.session_state.msg = ""
        st.session_state.status = "Waiting for next selection"
        st.session_state.msg = "Garden Duo Juice ready!"
    elif preset == 3:
        st.session_state.msg = ""
        st.session_state.status = "Waiting for next selection"
        st.session_state.msg = "Carrot Kiwi Citrus Mix ready!"
    

st.title("Welcome to the Robotic Juice maker!")
st.header("Choose a juice from our selection")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Kiwi Berry Splash"):
        make_smoothie(1)
    st.text("Ingredients: 🥝 + 🍓 + 🍏")

with col2:
    if st.button("Garden Duo Juice"):
        make_smoothie(2)
    st.text("Ingredients: 🍅 + 🥕")

with col3:
    if st.button("Carrot Kiwi Citrus Mix"):
        make_smoothie(3)
    st.text("Ingredients: 🥕 + 🥝 + 🍋")

st.text(st.session_state.status)
if st.session_state.msg!="":
    st.success(st.session_state.msg)


# We could display the last detected image here
st.text("Last detection")
img = Image.open("streamlit.png")  # We could replace this image with the last capture
st.image(img, width=200) 
