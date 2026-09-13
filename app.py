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
            #0f172a;

        color: white;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    section[data-testid="stSidebar"] {
        background: #0b1120 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    section[data-testid="stSidebar"] > div {
        background: #0b1120 !important;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    .sidebar-title {
        font-size: 26px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 20px;

        background: linear-gradient(
            90deg,
            #38bdf8,
            #8b5cf6
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }


    /* =====================================================
       SIDEBAR LABELS
       ===================================================== */

    section[data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
        font-weight: 400 !important;
    }


    /* =====================================================
       BLUE SETTINGS DROPDOWN BOXES
       ===================================================== */

    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background: linear-gradient(
            90deg,
            #0284c7 0%,
            #2563eb 50%,
            #7c3aed 100%
        ) !important;

        border: 1px solid #38bdf8 !important;
        border-radius: 10px !important;

        min-height: 46px !important;

        box-shadow:
            0 0 10px rgba(
                56,
                189,
                248,
                0.25
            ) !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: linear-gradient(
            90deg,
            #0284c7 0%,
            #2563eb 50%,
            #7c3aed 100%
        ) !important;

        border: none !important;
        border-radius: 10px !important;

        color: white !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [role="combobox"] {
        background: transparent !important;
        color: white !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [role="combobox"] span {
        color: white !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] * {
        color: white !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] svg {
        color: white !important;
        fill: white !important;
    }


    /* =====================================================
       DROPDOWN MENU
       ===================================================== */

    div[data-baseweb="popover"] {
        background: #0f172a !important;
    }

    div[data-baseweb="popover"] > div {
        background: #0f172a !important;
    }

    ul[role="listbox"] {
        background: #0f172a !important;

        border: 1px solid #38bdf8 !important;

        border-radius: 10px !important;

        box-shadow:
            0 8px 25px rgba(
                0,
                0,
                0,
                0.45
            ) !important;
    }

    li[role="option"] {
        background: #0f172a !important;
        color: white !important;
    }

    li[role="option"]:hover {
        background: #075985 !important;
        color: white !important;
    }

    li[role="option"][aria-selected="true"] {
        background: #0369a1 !important;
        color: white !important;
    }


    /* =====================================================
       MAIN TITLE
       ===================================================== */

    .main-title {
        text-align: center;

        font-size: 48px;

        font-weight: 800;

        margin-bottom: 5px;

        background: linear-gradient(
            90deg,
            #38bdf8,
            #8b5cf6
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        text-align: center;

        color: #cbd5e1;

        font-size: 16px;

        margin-bottom: 35px;
    }


    /* =====================================================
       QUESTION TITLE
       ===================================================== */

    .question-title {
        color: white;

        font-size: 20px;

        font-weight: 400;

        margin-bottom: 10px;
    }


    /* =====================================================
       TEXT AREA
       ===================================================== */

    textarea {
        background-color: #111827 !important;

        color: white !important;

        border: 1px solid rgba(
            56,
            189,
            248,
            0.35
        ) !important;

        border-radius: 12px !important;
    }

    textarea::placeholder {
        color: #94a3b8 !important;
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
        width: 100%;

        border-radius: 10px;

        border: 1px solid rgba(
            56,
            189,
            248,
            0.4
        );

        background: linear-gradient(
            90deg,
            #0284c7,
            #7c3aed
        );

        color: white !important;

        font-weight: 400;

        min-height: 44px;

        transition: 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);

        border-color: rgba(
            56,
            189,
            248,
            0.8
        );
    }

    .stButton > button p {
        color: white !important;

        font-weight: 400 !important;
    }


    /* =====================================================
       SIDEBAR EXAMPLE QUESTIONS
       ===================================================== */

    section[data-testid="stSidebar"] .stButton > button {
        background: #111827 !important;

        border: 1px solid rgba(
            56,
            189,
            248,
            0.25
        ) !important;

        color: #e2e8f0 !important;

        text-align: left !important;

        font-weight: 400 !important;

        min-height: 42px !important;

        margin-bottom: 5px !important;

        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #075985 !important;

        border-color: rgba(
            56,
            189,
            248,
            0.65
        ) !important;
    }

    section[data-testid="stSidebar"] .stButton > button p {
        color: #e2e8f0 !important;

        text-align: left !important;

        white-space: normal !important;

        font-weight: 400 !important;
    }


    /* =====================================================
       ANSWER
       ===================================================== */

    .answer-heading {
        color: white;

        font-size: 22px;

        font-weight: 400;

        margin-top: 30px;

        margin-bottom: 10px;
    }

    .answer-card {
        background: #ffffff;

        color: #111827;

        border-radius: 16px;

        padding: 28px;

        margin-top: 25px;

        margin-bottom: 20px;

        box-shadow:
            0 10px 30px rgba(
                0,
                0,
                0,
                0.25
            );

        line-height: 1.7;

        font-size: 16px;

        overflow-wrap: anywhere;

        word-break: break-word;
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

        margin-top: 20px;
    }

    div[data-testid="stExpander"] summary {
        color: white !important;

        font-weight: 400 !important;
    }

    div[data-testid="stExpander"] summary p {
        color: white !important;

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
        background: #0f172a !important;

        border: 1px solid rgba(
            56,
            189,
            248,
            0.25
        );

        border-radius: 8px;

        padding: 10px 14px;

        margin-bottom: 8px;
    }

    .source-name {
        color: white !important;

        font-size: 15px;

        font-weight: 400;

        word-break: break-word;
    }


    /* =====================================================
       INFO CARD
       ===================================================== */

    .info-card {
        background: rgba(
            15,
            23,
            42,
            0.75
        );

        border: 1px solid rgba(
            148,
            163,
            184,
            0.15
        );

        border-radius: 12px;

        padding: 15px;

        color: #cbd5e1;

        font-size: 14px;

        line-height: 1.6;

        margin-top: 25px;
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;

        color: #64748b;

        font-size: 13px;

        margin-top: 50px;

        padding-top: 20px;

        border-top: 1px solid rgba(
            255,
            255,
            255,
            0.08
        );
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    @media (max-width: 768px) {

        .block-container {
            padding-left: 12px;
            padding-right: 12px;
            padding-top: 1.2rem;
        }

        .main-title {
            font-size: 34px;
        }

        .subtitle {
            font-size: 14px;

            margin-bottom: 25px;
        }

        .question-title {
            font-size: 19px;
        }

        .answer-card {
            padding: 18px;

            font-size: 15px;

            border-radius: 13px;
        }

        .answer-heading {
            font-size: 20px;
        }

        .source-card {
            padding: 10px 12px;
        }

        .source-name {
            font-size: 14px;
        }


        /* =============================================
           MOBILE BLUE SETTINGS
           ============================================= */

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            background: linear-gradient(
                90deg,
                #0284c7 0%,
                #2563eb 50%,
                #7c3aed 100%
            ) !important;

            border: 1px solid #38bdf8 !important;

            min-height: 48px !important;

            border-radius: 10px !important;

            box-shadow:
                0 0 10px rgba(
                    56,
                    189,
                    248,
                    0.30
                ) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background: linear-gradient(
                90deg,
                #0284c7 0%,
                #2563eb 50%,
                #7c3aed 100%
            ) !important;

            border-radius: 10px !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [role="combobox"] {
            background: transparent !important;

            color: white !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] * {
            color: white !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stSelectbox"] svg {
            color: white !important;

            fill: white !important;
        }


        /* =============================================
           MOBILE EXAMPLE QUESTIONS
           ============================================= */

        section[data-testid="stSidebar"] .stButton > button {
            min-height: 46px !important;

            font-size: 13px !important;

            padding: 8px 10px !important;

            border-radius: 9px !important;
        }

        textarea {
            font-size: 15px !important;
        }


        /* =============================================
           MOBILE SOURCES
           ============================================= */

        div[data-testid="stExpander"] {
            border-radius: 10px !important;
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
# GROQ API KEY
# ============================================================

try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    groq_api_key = os.getenv("GROQ_API_KEY")


# ============================================================
# GROQ CLIENT
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

    answer = answer.replace(
        "**",
        ""
    )

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

    metadatas = results.get(
        "metadatas",
        []
    )

    if not metadatas:
        return source_files

    if (
        isinstance(metadatas, list)
        and len(metadatas) > 0
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

        source = source.replace(
            "\\",
            "/"
        ).strip()

        source = source.split("?")[0].strip()

        source_filename = os.path.basename(
            source
        ).strip()

        if not source_filename:
            continue

        if not source_filename.lower().endswith(
            ".txt"
        ):
            continue

        if source_filename not in source_files:
            source_files.append(
                source_filename
            )

    return source_files


# ============================================================
# EXTRACT DOCUMENTS
# ============================================================

def extract_documents(results):

    if not results:
        return []

    if not isinstance(results, dict):
        return []

    documents = results.get(
        "documents",
        []
    )

    if not documents:
        return []

    if (
        isinstance(documents, list)
        and len(documents) > 0
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
            "Provide a detailed legal explanation "
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
    """
    <div class="main-title">
        INSAFBOT
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
        AI-Powered Legal Information Assistant for Pakistan
    </div>
    """,
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
    """
    <div class="question-title">
        Ask a legal question
    </div>
    """,
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
    # CHECK API KEY
    # ========================================================

    if not groq_api_key:

        st.error(
            "GROQ_API_KEY is not configured. "
            "Please add GROQ_API_KEY to Streamlit Secrets."
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

    documents = extract_documents(
        results
    )


    # ========================================================
    # EXTRACT SOURCES
    # ========================================================

    source_files = extract_source_filenames(
        results
    )

    st.session_state.sources = source_files


    # ========================================================
    # CHECK RESULTS
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

    context = "\n".join(
        context_parts
    )


    # ========================================================
    # LIMIT CONTEXT
    # ========================================================

    max_context_length = 30000

    if len(context) > max_context_length:

        context = context[
            :max_context_length
        ]


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

            answer = response.choices[
                0
            ].message.content

    except Exception as error:

        st.error(
            "The AI service could not generate an answer."
        )

        st.exception(error)

        st.stop()


    # ========================================================
    # CLEAN ANSWER
    # ========================================================

    answer = clean_answer(
        answer
    )


    # ========================================================
    # ANSWER DISPLAY
    # ========================================================

    st.markdown(
        '<div class="answer-heading">Answer</div>',
        unsafe_allow_html=True
    )

    safe_answer = html.escape(
        answer
    )

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
        INSAFBOT provides general legal information based
        on its available Pakistani legal documents.
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
