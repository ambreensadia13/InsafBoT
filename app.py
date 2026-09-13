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
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > section {
        background-color: #0f172a !important;
    }

    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(56, 189, 248, 0.12),
                transparent 35%
            ),
            radial-gradient(
                circle at top right,
                rgba(139, 92, 246, 0.12),
                transparent 35%
            ),
            #0f172a !important;

        color: #ffffff !important;
    }

    .block-container {
        width: 100% !important;
        max-width: 100% !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    html,
    body,
    [class*="css"] {
        font-family: Arial, Helvetica, sans-serif !important;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background: #0b1120 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    section[data-testid="stSidebar"] > div {
        background: #0b1120 !important;
    }


    /* =====================================================
       SIDEBAR TITLE
       ===================================================== */

    .sidebar-title {
        width: 100% !important;
        display: block !important;

        text-align: center !important;

        font-size: 26px !important;
        line-height: 1.2 !important;

        font-weight: 800 !important;

        margin-top: 4px !important;
        margin-bottom: 20px !important;

        white-space: nowrap !important;
        overflow: visible !important;

        color: #38bdf8 !important;

        background: linear-gradient(
            90deg,
            #38bdf8 0%,
            #8b5cf6 100%
        ) !important;

        -webkit-background-clip: text !important;
        background-clip: text !important;

        -webkit-text-fill-color: transparent !important;
    }


    /* =====================================================
       SIDEBAR LABELS
       ===================================================== */

    section[data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
        font-weight: 400 !important;
    }


    /* =====================================================
       SETTINGS DROPDOWN
       FIXED DARK COLOUR
       ===================================================== */

    section[data-testid="stSidebar"]
    div[data-baseweb="select"] {
        width: 100% !important;

        background-color: #111827 !important;

        border: 1px solid rgba(
            56,
            189,
            248,
            0.25
        ) !important;

        border-radius: 9px !important;

        min-height: 42px !important;

        box-shadow: none !important;
    }

    section[data-testid="stSidebar"]
    div[data-baseweb="select"] > div {
        background-color: #111827 !important;

        border: 0 !important;

        border-radius: 9px !important;

        min-height: 42px !important;

        box-shadow: none !important;
    }

    section[data-testid="stSidebar"]
    div[data-baseweb="select"]
    [role="combobox"] {
        background-color: #111827 !important;

        color: #e2e8f0 !important;

        border: 0 !important;

        border-radius: 9px !important;

        min-height: 42px !important;

        box-shadow: none !important;

        outline: none !important;
    }

    section[data-testid="stSidebar"]
    div[data-baseweb="select"]
    [role="combobox"]:focus,
    section[data-testid="stSidebar"]
    div[data-baseweb="select"]
    [role="combobox"]:active {
        background-color: #111827 !important;
        color: #e2e8f0 !important;
        outline: none !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"]
    div[data-baseweb="select"] span {
        color: #e2e8f0 !important;
        font-weight: 400 !important;
    }

    section[data-testid="stSidebar"]
    div[data-baseweb="select"] svg {
        color: #38bdf8 !important;
        fill: #38bdf8 !important;
        stroke: #38bdf8 !important;
    }

    section[data-testid="stSidebar"]
    div[data-baseweb="select"]:hover {
        background-color: #111827 !important;

        border-color: rgba(
            56,
            189,
            248,
            0.45
        ) !important;
    }

    section[data-testid="stSidebar"]
    div[data-baseweb="select"]:focus-within {
        background-color: #111827 !important;

        border-color: rgba(
            56,
            189,
            248,
            0.45
        ) !important;

        box-shadow: none !important;
    }


    /* =====================================================
       DROPDOWN POPUP
       ===================================================== */

    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] [data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: #111827 !important;

        border-color: rgba(
            56,
            189,
            248,
            0.35
        ) !important;
    }

    ul[role="listbox"] {
        border: 1px solid rgba(
            56,
            189,
            248,
            0.35
        ) !important;

        border-radius: 9px !important;

        padding: 4px !important;
    }

    li[role="option"] {
        background-color: #111827 !important;

        color: #e2e8f0 !important;

        border-radius: 6px !important;

        font-weight: 400 !important;
    }

    li[role="option"] span {
        color: #e2e8f0 !important;
    }

    li[role="option"]:hover {
        background-color: #075985 !important;
        color: #ffffff !important;
    }

    li[role="option"]:hover span {
        color: #ffffff !important;
    }

    li[role="option"][aria-selected="true"] {
        background-color: #075985 !important;
        color: #ffffff !important;
    }

    li[role="option"][aria-selected="true"] span {
        color: #ffffff !important;
    }


    /* =====================================================
       MAIN TITLE
       ===================================================== */

    .main-title {
        width: 100% !important;

        display: block !important;

        text-align: center !important;

        font-size: clamp(
            32px,
            5vw,
            48px
        ) !important;

        line-height: 1.2 !important;

        font-weight: 800 !important;

        margin-top: 0 !important;
        margin-bottom: 5px !important;

        padding-left: 5px !important;
        padding-right: 5px !important;

        white-space: nowrap !important;

        overflow: visible !important;

        color: #38bdf8 !important;

        background: linear-gradient(
            90deg,
            #38bdf8 0%,
            #8b5cf6 100%
        ) !important;

        -webkit-background-clip: text !important;
        background-clip: text !important;

        -webkit-text-fill-color: transparent !important;
    }


    /* =====================================================
       SUBTITLE
       ===================================================== */

    .subtitle {
        width: 100% !important;

        text-align: center !important;

        color: #cbd5e1 !important;

        font-size: 16px !important;

        line-height: 1.5 !important;

        margin-bottom: 35px !important;
    }


    /* =====================================================
       QUESTION TITLE
       ===================================================== */

    .question-title {
        color: #ffffff !important;

        font-size: 20px !important;

        line-height: 1.4 !important;

        font-weight: 400 !important;

        margin-bottom: 10px !important;
    }


    /* =====================================================
       TEXT AREA
       ===================================================== */

    textarea,
    textarea:focus,
    textarea:hover {
        background-color: #111827 !important;

        color: #ffffff !important;

        border: 1px solid rgba(
            56,
            189,
            248,
            0.35
        ) !important;

        border-radius: 12px !important;

        caret-color: #38bdf8 !important;

        outline: none !important;
    }

    textarea::placeholder {
        color: #94a3b8 !important;

        opacity: 1 !important;
    }

    textarea:focus {
        border-color: #38bdf8 !important;

        box-shadow:
            0 0 0 1px #38bdf8 !important;
    }


    /* =====================================================
       MAIN BUTTON
       ===================================================== */

    .stButton > button {
        width: 100% !important;

        min-height: 44px !important;

        border-radius: 10px !important;

        border: 1px solid rgba(
            56,
            189,
            248,
            0.4
        ) !important;

        background: linear-gradient(
            90deg,
            #0284c7 0%,
            #7c3aed 100%
        ) !important;

        color: #ffffff !important;

        font-weight: 400 !important;

        box-shadow: none !important;
    }

    .stButton > button:hover {
        border-color: rgba(
            56,
            189,
            248,
            0.8
        ) !important;

        background: linear-gradient(
            90deg,
            #0284c7 0%,
            #7c3aed 100%
        ) !important;
    }

    .stButton > button:focus,
    .stButton > button:active {
        color: #ffffff !important;

        background: linear-gradient(
            90deg,
            #0284c7 0%,
            #7c3aed 100%
        ) !important;

        outline: none !important;

        box-shadow: none !important;
    }

    .stButton > button p {
        color: #ffffff !important;

        font-weight: 400 !important;
    }


    /* =====================================================
       SIDEBAR EXAMPLE QUESTION BUTTONS
       ===================================================== */

    section[data-testid="stSidebar"]
    .stButton > button {
        width: 100% !important;

        min-height: 42px !important;

        background-color: #111827 !important;

        border: 1px solid rgba(
            56,
            189,
            248,
            0.25
        ) !important;

        color: #e2e8f0 !important;

        text-align: left !important;

        font-weight: 400 !important;

        margin-bottom: 5px !important;

        box-shadow: none !important;

        white-space: normal !important;
    }

    section[data-testid="stSidebar"]
    .stButton > button:hover {
        background-color: #075985 !important;

        border-color: rgba(
            56,
            189,
            248,
            0.65
        ) !important;
    }

    section[data-testid="stSidebar"]
    .stButton > button:focus,
    section[data-testid="stSidebar"]
    .stButton > button:active {
        background-color: #111827 !important;

        color: #e2e8f0 !important;

        outline: none !important;

        box-shadow: none !important;
    }

    section[data-testid="stSidebar"]
    .stButton > button p {
        color: #e2e8f0 !important;

        text-align: left !important;

        white-space: normal !important;

        font-weight: 400 !important;
    }


    /* =====================================================
       ANSWER
       ===================================================== */

    .answer-card {
        width: 100% !important;

        box-sizing: border-box !important;

        background: #ffffff !important;

        color: #111827 !important;

        border-radius: 16px !important;

        padding: 28px !important;

        margin-top: 25px !important;

        margin-bottom: 20px !important;

        box-shadow:
            0 10px 30px rgba(
                0,
                0,
                0,
                0.25
            ) !important;

        line-height: 1.7 !important;

        font-size: 16px !important;

        overflow-wrap: anywhere !important;

        word-break: break-word !important;
    }

    .answer-heading {
        color: #ffffff !important;

        font-size: 22px !important;

        line-height: 1.4 !important;

        font-weight: 400 !important;

        margin-top: 30px !important;

        margin-bottom: 10px !important;
    }


    /* =====================================================
       SOURCES EXPANDER
       ===================================================== */

    div[data-testid="stExpander"] {
        background: #111827 !important;

        border: 1px solid rgba(
            56,
            189,
            248,
            0.35
        ) !important;

        border-radius: 10px !important;

        margin-top: 20px !important;
    }

    div[data-testid="stExpander"] summary {
        color: #ffffff !important;

        font-weight: 400 !important;
    }

    div[data-testid="stExpander"] summary p {
        color: #ffffff !important;

        font-weight: 400 !important;
    }

    div[data-testid="stExpander"] summary svg {
        color: #38bdf8 !important;

        fill: #38bdf8 !important;
    }


    /* =====================================================
       SOURCE CARD
       ===================================================== */

    .source-card {
        width: 100% !important;

        box-sizing: border-box !important;

        background: #0f172a !important;

        border: 1px solid rgba(
            56,
            189,
            248,
            0.25
        ) !important;

        border-radius: 8px !important;

        padding: 10px 14px !important;

        margin-bottom: 8px !important;
    }

    .source-name {
        color: #ffffff !important;

        font-size: 15px !important;

        font-weight: 400 !important;

        word-break: break-word !important;
    }


    /* =====================================================
       INFO CARD
       ===================================================== */

    .info-card {
        width: 100% !important;

        box-sizing: border-box !important;

        background: rgba(
            15,
            23,
            42,
            0.75
        ) !important;

        border: 1px solid rgba(
            148,
            163,
            184,
            0.15
        ) !important;

        border-radius: 12px !important;

        padding: 15px !important;

        color: #cbd5e1 !important;

        font-size: 14px !important;

        line-height: 1.6 !important;

        margin-top: 25px !important;
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        width: 100% !important;

        box-sizing: border-box !important;

        text-align: center !important;

        color: #64748b !important;

        font-size: 13px !important;

        line-height: 1.5 !important;

        margin-top: 50px !important;

        padding-top: 20px !important;

        border-top: 1px solid rgba(
            255,
            255,
            255,
            0.08
        ) !important;
    }


    /* =====================================================
       TABLET
       ===================================================== */

    @media (max-width: 900px) {

        .block-container {
            padding-left: 16px !important;
            padding-right: 16px !important;
        }

        .main-title {
            font-size: clamp(
                34px,
                7vw,
                44px
            ) !important;
        }
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    @media (max-width: 768px) {

        .block-container {
            padding-left: 12px !important;
            padding-right: 12px !important;
            padding-top: 1.2rem !important;
        }

        .main-title {
            font-size: 34px !important;

            line-height: 1.25 !important;

            padding-left: 4px !important;
            padding-right: 4px !important;

            white-space: nowrap !important;

            overflow: visible !important;
        }

        .sidebar-title {
            font-size: 25px !important;

            line-height: 1.25 !important;

            white-space: nowrap !important;

            overflow: visible !important;
        }

        .subtitle {
            font-size: 14px !important;

            line-height: 1.5 !important;

            margin-bottom: 25px !important;
        }

        .question-title {
            font-size: 19px !important;
        }

        .answer-card {
            padding: 18px !important;

            font-size: 15px !important;

            border-radius: 13px !important;
        }

        .answer-heading {
            font-size: 20px !important;
        }

        .source-card {
            padding: 10px 12px !important;
        }

        .source-name {
            font-size: 14px !important;
        }

        textarea {
            font-size: 15px !important;
        }


        /* -------------------------------------------------
           MOBILE SETTINGS
           ------------------------------------------------- */

        section[data-testid="stSidebar"]
        div[data-baseweb="select"],
        section[data-testid="stSidebar"]
        div[data-baseweb="select"] > div,
        section[data-testid="stSidebar"]
        div[data-baseweb="select"]
        [role="combobox"] {

            background-color: #111827 !important;

            color: #e2e8f0 !important;

            border-radius: 9px !important;

            min-height: 46px !important;

            box-shadow: none !important;
        }

        section[data-testid="stSidebar"]
        div[data-baseweb="select"] span {
            color: #e2e8f0 !important;
        }

        section[data-testid="stSidebar"]
        div[data-baseweb="select"] svg {
            color: #38bdf8 !important;

            fill: #38bdf8 !important;

            stroke: #38bdf8 !important;
        }

        section[data-testid="stSidebar"]
        div[data-baseweb="select"]:hover,
        section[data-testid="stSidebar"]
        div[data-baseweb="select"]:active,
        section[data-testid="stSidebar"]
        div[data-baseweb="select"]:focus-within {

            background-color: #111827 !important;

            border-color: rgba(
                56,
                189,
                248,
                0.45
            ) !important;

            box-shadow: none !important;
        }


        /* -------------------------------------------------
           MOBILE EXAMPLE QUESTIONS
           ------------------------------------------------- */

        section[data-testid="stSidebar"]
        .stButton > button {

            min-height: 46px !important;

            font-size: 13px !important;

            line-height: 1.35 !important;

            padding: 8px 10px !important;

            border-radius: 9px !important;
        }


        /* -------------------------------------------------
           MOBILE SOURCE EXPANDER
           ------------------------------------------------- */

        div[data-testid="stExpander"] {
            border-radius: 10px !important;
        }
    }


    /* =====================================================
       VERY SMALL PHONES
       ===================================================== */

    @media (max-width: 380px) {

        .block-container {
            padding-left: 9px !important;
            padding-right: 9px !important;
        }

        .main-title {
            font-size: 30px !important;

            line-height: 1.3 !important;

            letter-spacing: 0 !important;
        }

        .sidebar-title {
            font-size: 23px !important;
        }

        .subtitle {
            font-size: 13px !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "question" not in st.session_state:
    st.session_state.question = ""

if "sources" not in st.session_state:
    st.session_state.sources = []


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

example_questions = [
    "Pakistan mein FIR kaise darj karwai ja sakti hai?",
    "Agar police FIR darj na kare to kya kiya ja sakta hai?",
    "Tenant ko ghar se nikalne ka qanooni tareeqa kya hai?",
    "Agar landlord security deposit wapas na kare to tenant kya kar sakta hai?",
    "Agar employer salary na de to employee kya qanooni karwai kar sakta hai?",
    "Agar employer bina wajah job se nikal de to employee ke kya rights hain?",
    "Pakistan mein khula lene ka qanooni tareeqa kya hai?",
    "Pakistan mein talaq ke baad aurat ke kya qanooni rights hain?",
    "Domestic violence ki surat mein aurat ko qanooni protection kaise mil sakti hai?",
    "Agar husband wife ko physically abuse kare to wife kya qanooni karwai kar sakti hai?",
    "Agar koi online dhamki de raha ho to kya qanooni karwai ki ja sakti hai?",
    "Cybercrime ki complaint Pakistan mein kaise ki ja sakti hai?",
    "Agar cheque bounce ho jaye to kya qanooni karwai ho sakti hai?",
    "Property fraud ki surat mein victim kya qanooni karwai kar sakta hai?",
    "Agar kisi ne meri property par illegal qabza kar liya ho to kya kar sakta hoon?",
    "NADRA record mein naam ki ghalti kaise theek karwai ja sakti hai?",
    "Agar kisi ne meri personal information online misuse ki ho to kya kar sakta hoon?",
    "Pakistan mein traffic challan milne ke baad kya karna chahiye?",
    "Agar kisi ne mujhe online fraud ka shikar banaya ho to kya qanooni karwai kar sakta hoon?",
    "Pakistan mein aurat ke nikah ke qanooni rights kya hain?"
]


# ============================================================
# LOAD GROQ API KEY
# ============================================================

try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    groq_api_key = os.getenv("GROQ_API_KEY")


# ============================================================
# OPENAI-COMPATIBLE GROQ CLIENT
# ============================================================

client = None

if groq_api_key:
    client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

@st.cache_resource
def load_knowledge_base():
    return build_database()


# ============================================================
# CLEAN ANSWER
# ============================================================

def clean_answer(answer):

    answer = str(answer)

    answer = answer.replace("**", "")

    answer = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        answer,
        flags=re.MULTILINE
    )

    answer = re.sub(
        r"</?(strong|b)>",
        "",
        answer,
        flags=re.IGNORECASE
    )

    answer = re.sub(
        r"\n{3,}",
        "\n\n",
        answer
    )

    return answer.strip()


# ============================================================
# EXTRACT SOURCE FILENAMES
# ============================================================

def extract_source_filenames(results):

    source_files = []

    if not results:
        return source_files

    if not isinstance(results, dict):
        return source_files

    metadatas = results.get("metadatas", [])

    if not metadatas:
        return source_files

    if isinstance(metadatas, list):

        if (
            len(metadatas) > 0
            and isinstance(metadatas[0], list)
        ):
            metadatas = metadatas[0]

    if not isinstance(metadatas, list):
        return source_files

    for metadata in metadatas:

        if not isinstance(metadata, dict):
            continue

        source = (
            metadata.get("source")
            or metadata.get("file")
            or metadata.get("filename")
            or metadata.get("file_name")
            or ""
        )

        if not source:
            continue

        source = str(source)
        source = source.replace("\\", "/").strip()

        source = source.split("?")[0].strip()

        source_filename = os.path.basename(source).strip()

        if not source_filename:
            continue

        if not source_filename.lower().endswith(".txt"):
            continue

        if source_filename not in source_files:
            source_files.append(source_filename)

    return source_files


# ============================================================
# EXTRACT DOCUMENTS
# ============================================================

def extract_documents(results):

    if not results:
        return []

    if not isinstance(results, dict):
        return []

    documents = results.get("documents", [])

    if not documents:
        return []

    if isinstance(documents, list):

        if (
            len(documents) > 0
            and isinstance(documents[0], list)
        ):
            documents = documents[0]

    if not isinstance(documents, list):
        return []

    return [
        str(document)
        for document in documents
        if document
    ]


# ============================================================
# SYSTEM PROMPT
# ============================================================

def create_system_prompt(
    jurisdiction,
    explanation_level,
    answer_language
):

    language_instruction = {
        "English": (
            "Answer in clear and simple English."
        ),

        "Urdu": (
            "Answer in Urdu script."
        ),

        "Roman Urdu": (
            "Answer in simple Roman Urdu."
        )
    }.get(
        answer_language,
        "Answer in clear and simple English."
    )

    level_instruction = {
        "Beginner": (
            "Explain the law in simple language "
            "that an ordinary person can understand."
        ),

        "Intermediate": (
            "Give a balanced explanation with "
            "relevant legal terminology."
        ),

        "Expert": (
            "Provide a more detailed legal explanation "
            "using appropriate legal terminology."
        )
    }.get(
        explanation_level,
        "Explain the law clearly."
    )

    return f"""
You are INSAFBOT, an AI-powered legal information
assistant focused on Pakistani law.

Jurisdiction:
{jurisdiction}

Explanation level:
{explanation_level}

{level_instruction}

{language_instruction}

IMPORTANT RULES:

1. Answer only from the legal information contained
   in the supplied context whenever possible.

2. Do not invent laws, sections, cases, penalties,
   procedures, or legal rights.

3. If the supplied context does not contain enough
   information to answer the question, clearly say
   that the available legal documents do not provide
   enough information.

4. Do not pretend to be a lawyer.

5. Give general legal information and not personalized
   legal representation.

6. Keep the answer clear and practical.

7. Do not use Markdown bold formatting.

8. Do not use double asterisks.

9. Do not add a separate Sources section.
   Sources are displayed separately by the application.

10. If the context contains an exact law, section,
    ordinance, act, rule, or legal provision relevant
    to the question, mention it clearly.

11. Do not create citations that are not present
    in the supplied context.

12. If the question is unrelated to Pakistani law,
    politely explain that INSAFBOT is designed for
    Pakistani legal information.
"""


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="main-title">INSAFBOT</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Legal Information Assistant for Pakistan'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">INSAFBOT</div>',
        unsafe_allow_html=True
    )

    st.write("Settings")

    jurisdiction = st.selectbox(
        "Jurisdiction",
        [
            "Pakistan / Federal",
            "Punjab"
        ]
    )

    explanation_level = st.selectbox(
        "Explanation Level",
        [
            "Beginner",
            "Intermediate",
            "Expert"
        ]
    )

    answer_language = st.selectbox(
        "Answer Language",
        [
            "English",
            "Urdu",
            "Roman Urdu"
        ]
    )

    st.write("")

    st.write("Example Questions")

    for index, example in enumerate(
        example_questions,
        start=1
    ):

        if st.button(
            example,
            key=f"example_{index}",
            use_container_width=True
        ):

            st.session_state.question = example


# ============================================================
# QUESTION AREA
# ============================================================

st.markdown(
    '<div class="question-title">Ask a legal question</div>',
    unsafe_allow_html=True
)

question = st.text_area(
    "Legal question",
    value=st.session_state.question,
    placeholder=(
        "Example: Pakistan mein FIR kaise darj "
        "karwai ja sakti hai?"
    ),
    height=130,
    label_visibility="collapsed"
)

st.session_state.question = question


# ============================================================
# ASK BUTTON
# ============================================================

ask_button = st.button(
    "Ask INSAFBOT",
    use_container_width=True
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if ask_button:

    question = st.session_state.question.strip()

    if not question:

        st.warning(
            "Please enter a legal question."
        )

        st.stop()


    # ========================================================
    # API KEY CHECK
    # ========================================================

    if not groq_api_key:

        st.error(
            "GROQ_API_KEY is not configured. "
            "Add GROQ_API_KEY to Streamlit Secrets."
        )

        st.stop()


    if client is None:

        st.error(
            "Unable to initialize the AI client."
        )

        st.stop()


    # ========================================================
    # LOAD KNOWLEDGE BASE
    # ========================================================

    try:

        with st.spinner(
            "Loading legal knowledge base..."
        ):

            collection = load_knowledge_base()

    except Exception as error:

        st.error(
            "Could not load the legal knowledge base."
        )

        st.exception(error)

        st.stop()


    # ========================================================
    # SEARCH LEGAL DOCUMENTS
    # ========================================================

    try:

        with st.spinner(
            "Searching Pakistani legal information..."
        ):

            results = search_laws(
                collection,
                question,
                top_k=5
            )

    except Exception as error:

        st.error(
            "There was a problem searching the legal "
            "knowledge base."
        )

        st.exception(error)

        st.stop()


    # ========================================================
    # EXTRACT DOCUMENTS
    # ========================================================

    documents = extract_documents(results)


    # ========================================================
    # EXTRACT SOURCE FILENAMES
    # ========================================================

    source_files = extract_source_filenames(results)

    st.session_state.sources = source_files


    # ========================================================
    # CHECK CONTEXT
    # ========================================================

    if not documents:

        st.warning(
            "I could not find relevant information "
            "in the available legal documents."
        )

        st.stop()


    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1
    ):

        context_parts.append(
            f"""
LEGAL DOCUMENT {index}

{document}
"""
        )

    context = "\n".join(context_parts)


    # ========================================================
    # LIMIT CONTEXT
    # ========================================================

    max_context_length = 30000

    if len(context) > max_context_length:

        context = context[:max_context_length]


    # ========================================================
    # SYSTEM PROMPT
    # ========================================================

    system_prompt = create_system_prompt(
        jurisdiction,
        explanation_level,
        answer_language
    )


    # ========================================================
    # USER PROMPT
    # ========================================================

    user_prompt = f"""
Use the following retrieved Pakistani legal
documents to answer the user's question.

================ LEGAL CONTEXT ================

{context}

================ USER QUESTION ================

{question}

================ INSTRUCTIONS ================

Give a clear and direct answer.

Use only information supported by the
retrieved legal context.

Do not use Markdown bold.

Do not use double asterisks.

If the exact legal provision is available
in the context, mention its name or section.

If the context is insufficient, say so clearly.

Do not invent missing legal information.
"""


    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    try:

        with st.spinner(
            "Preparing legal information..."
        ):

            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",

                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],

                temperature=0.2,

                max_tokens=1500
            )

            answer = response.choices[0].message.content

    except Exception as error:

        st.error(
            "The AI service could not generate an answer."
        )

        st.exception(error)

        st.stop()


    # ========================================================
    # CLEAN ANSWER
    # ========================================================

    answer = clean_answer(answer)


    # ========================================================
    # ANSWER DISPLAY
    # ========================================================

    st.markdown(
        '<div class="answer-heading">Answer</div>',
        unsafe_allow_html=True
    )

    safe_answer = html.escape(answer)

    safe_answer = safe_answer.replace(
        "\n",
        "<br>"
    )

    st.markdown(
        f"""
        <div class="answer-card">
            {safe_answer}
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # SOURCES
    # ========================================================

    if source_files:

        with st.expander(
            "Sources",
            expanded=False
        ):

            for index, source_file in enumerate(
                source_files,
                start=1
            ):

                safe_source = html.escape(
                    source_file
                )

                st.markdown(
                    f"""
                    <div class="source-card">
                        <div class="source-name">
                            {index}. {safe_source}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ============================================================
# INFORMATION CARD
# ============================================================

st.markdown(
    """
    <div class="info-card">
        INSAFBOT provides general legal information
        based on its available Pakistani legal documents.
        It is not a substitute for advice from a qualified
        lawyer or legal professional.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        INSAFBOT — AI-Powered Legal Information Assistant
        for Pakistan
    </div>
    """,
    unsafe_allow_html=True
)
