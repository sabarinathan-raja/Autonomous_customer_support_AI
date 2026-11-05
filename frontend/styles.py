
import streamlit as st


def load_custom_styles():

    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        div[data-testid="stMetric"] {
            background-color: rgba(128, 128, 128, 0.08);
            border: 1px solid rgba(128, 128, 128, 0.2);
            padding: 16px;
            border-radius: 12px;
        }

        div[data-testid="stChatMessage"] {
            border-radius: 12px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
