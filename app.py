import html
import os
import re

import streamlit as st
from openai import OpenAI

from rag import build_database, search_laws

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="INSAFBOT",
    page_icon="⚖️",
    layout="wide"
)

# ============================================================
# SESSION STATE INIT
# ============================================================
if "jurisdiction" not in st.session_state:
    st.session_state.jurisdiction = "Pakistan / Federal"
if "language" not in st.session_state:
    st.session_state.language = "Urdu"

# ============================================================
# CSS - THEME FIX
# ============================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(56, 189, 248, 0.12), transparent 35%),
            radial-gradient(circle at bottom right, rgba(14, 165, 233, 0.10), transparent 40%),
            #0B1120;
        color: #E5E7EB;
    }

    /* =====================================================
       SIDEBAR SETTINGS - DARK BLUE THEME
       ===================================================== */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid rgba(56, 189, 248, 0.2);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label {
        color: #E5E7EB !important;
    }

    /* Dropdown / Selectbox styling */
    div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1.5px solid #38BDF8 !important;
        border-radius: 10px !important;
        color: #E5E7EB !important;
    }
    
    div[data-baseweb="select"] > div:hover {
        border-color: #0EA5E9 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.3) !important;
    }

    /* Dropdown options list */
    ul[data-baseweb="menu"] {
        background-color: #1E293B !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 10px !important;
    }
    
    li[data-baseweb="option"] {
        color: #E5E7EB !important;
        background-color: #1E293B !important;
    }
    
    li[data-baseweb="option"]:hover {
        background-color: #334155 !important;
        color: #38BDF8 !important;
    }
    
    /* Selected option in dropdown */
    li[aria-selected="true"] {
        background-color: #0EA5E9 !important;
        color: white !important;
    }

    /* =====================================================
       EXAMPLE QUESTIONS BOX - MATCHING THEME
       ===================================================== */
    .example-box {
        background-color: #1E293B;
        border: 1.5px solid #38BDF8;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        color: #E5E7EB;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .example-box:hover {
        background-color: #334155;
        border-color: #0EA5E9;
        transform: translateX(4px);
    }

    /* Main buttons */
    .stButton>button {
        background-color: #0EA5E9;
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #0284C7;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# SIDEBAR - SETTINGS
# ============================================================
with st.sidebar:
    st.markdown("## Settings")
    
    st.session_state.jurisdiction = st.selectbox(
        "Jurisdiction",
        ["Pakistan / Federal", "Punjab", "Sindh", "KPK", "Balochistan", "AJK", "GB"],
        index=0
    )
    
    st.session_state.language = st.selectbox(
        "Answer Language",
        ["Urdu", "English", "Roman Urdu"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### Example Questions")
    
    examples = [
        "Pakistan mein FIR kaise darj karwai ja sakti hai?",
        "Agar malik makan tenant ko ghar se nikalna chahe to kya qanooni tareeqa hai?"
    ]
    
    for q in examples:
        st.markdown(f'<div class="example-box">{html.escape(q)}</div>', unsafe_allow_html=True)

# ============================================================
# MAIN APP LOGIC
# ============================================================
st.title("⚖️ INSAFBOT")
st.write(f"Jurisdiction: **{st.session_state.jurisdiction}** | Language: **{st.session_state.language}**")

user_query = st.text_input("Apna sawal likhain...")

if st.button("Poochain"):
    if user_query:
        with st.spinner("Jawab dhoond rahe hain..."):
            results = search_laws(user_query, st.session_state.jurisdiction)
            st.success("Jawab tayar hai!")
            st.write(results)
