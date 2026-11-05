import streamlit as st
from frontend.components.chat_interface import render_chat_interface

def render_chat_view():
    st.title("💬 Customer Chat")
    render_chat_interface()