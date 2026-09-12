import streamlit as st
from google import genai

from rag import (
    build_database,
    search_laws
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="INSAFBOT - AI Legal Aid Pakistan",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* =========================
       MAIN BACKGROUND
       ========================= */

    .stApp {
        background: #0b3d91;
        color: white;
    }

    .main {
        background: #0b3d91;
    }

    /* =========================
       ALL TEXT
       ========================= */

    p, span, label, div {
        color: white;
    }

    /* =========================
       HEADINGS
       ========================= */

    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }

    /* =========================
       MAIN TITLE
       ========================= */

    .main-title {
        text-align: center;
        color: white;
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: white;
        font-size: 19px;
        margin-bottom: 30px;
    }

    /* =========================
       CARDS
       ========================= */

    .info-card {
        background: rgba(255, 255, 255, 0.10);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }

    .source-card {
        background: rgba(255, 255, 255, 0.08);
        border-left: 4px solid white;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }

    .disclaimer-card {
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.35);
        border-radius: 12px;
        padding: 16px;
        margin-top: 20px;
    }

    /* =========================
       INPUT
       ========================= */

    textarea {
        background-color: white !important;
        color: #111827 !important;
        border-radius: 10px !important;
    }

    textarea::placeholder {
        color: #6b7280 !important;
    }

    /* =========================
       SELECT BOX
       ========================= */

    div[data-baseweb="select"] > div {
        background-color: white !important;
        color: #111827 !important;
    }

    div[data-baseweb="select"] span {
        color: #111827 !important;
    }

    /* =========================
       BUTTONS
       ========================= */

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.4);
        background-color: rgba(255,255,255,0.12);
        color: white !important;
        font-weight: 600;
        padding: 10px;
    }

    .stButton > button:hover {
        background-color: white;
        color: #0b3d91 !important;
        border-color: white;
    }

    /* =========================
       SIDEBAR
       ========================= */

    section[data-testid="stSidebar"] {
        background: #082f73;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* =========================
       DIVIDER
       ========================= */

    hr {
        border-color: rgba(255,255,255,0.25);
    }

    /* =========================
       ALERTS
       ========================= */

    .stAlert {
        color: white !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# GEMINI API
# ============================================================

try:

    api_key = st.secrets["GEMINI_API_KEY"]

except Exception:

    st.error(
        "GEMINI_API_KEY is not configured. "
        "Please add it to Streamlit Secrets."
    )

    st.stop()


client = genai.Client(
    api_key=api_key
)


# ============================================================
# SESSION STATE
# ============================================================

if "question" not in st.session_state:
    st.session_state.question = ""

if "answer" not in st.session_state:
    st.session_state.answer = None

if "sources" not in st.session_state:
    st.session_state.sources = []


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">⚖️ INSAFBOT</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI Legal Information Assistant for Pakistan'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# INTRODUCTION
# ============================================================

st.markdown(
    """
    <div class="info-card">

    <h3>🛡️ How INSAFBOT Works</h3>

    <p>
    Ask your legal question in <b>Roman Urdu, Urdu, or English</b>.
    INSAFBOT searches its legal knowledge base and uses the
    relevant legal documents to generate an easy-to-understand answer.
    </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ⚙️ Settings")

    province = st.selectbox(
        "Jurisdiction",
        [
            "Punjab",
            "Federal / Pakistan"
        ]
    )

    level = st.selectbox(
        "Explanation Level",
        [
            "Beginner",
            "Intermediate",
            "Expert"
        ]
    )

    st.divider()

    st.markdown("## 💬 Example Questions")

    st.caption(
        "Click any question to ask INSAFBOT."
    )


# ============================================================
# 10 EXAMPLE QUESTIONS
# ============================================================

examples = [
    "Mera landlord bijli aur pani band kar raha hai, main kya karun?",
    "Mera boss meri salary nahi de raha, mere rights kya hain?",
    "Mujhe online blackmail kiya ja raha hai, main kya karun?",
    "Nikah register karwana zaroori hai?",
    "Mere husband mujhe maintenance nahi de rahe, main kya kar sakti hoon?",
    "Mere khilaf FIR ho gayi hai, ab mujhe kya karna chahiye?",
    "Mera landlord mujhe zabardasti ghar se nikal raha hai.",
    "Kisi ne meri private pictures online upload kar di hain.",
    "Mujhe job se bina wajah nikal diya gaya hai, mere legal rights kya hain?",
    "Mujhe ek legal complaint/application likh kar do."
]


# ============================================================
# EXAMPLE QUESTION BUTTONS
# ============================================================

for i, example in enumerate(examples):

    if st.sidebar.button(
        f"{i + 1}. {example}",
        key=f"example_{i}"
    ):

        st.session_state.question = example

        # Clear previous answer
        st.session_state.answer = None
        st.session_state.sources = []

        # Rerun so question appears in input
        st.rerun()


# ============================================================
# BUILD RAG DATABASE
# ============================================================

@st.cache_resource
def initialize_rag():

    return build_database(client)


with st.spinner("Loading INSAFBOT legal knowledge base..."):

    try:

        collection = initialize_rag()

    except Exception as e:

        st.error(
            "The legal knowledge base could not be loaded."
        )

        st.exception(e)

        st.stop()


# ============================================================
# QUESTION INPUT
# ============================================================

st.markdown(
    "### 💬 Ask Your Legal Question"
)


question = st.text_area(
    "Write your question:",
    key="question",
    height=130,
    placeholder=(
        "Example: mera landlord mera bijli "
        "connection kaat raha hai, kya karun?"
    ),
    label_visibility="collapsed"
)


# ============================================================
# ASK BUTTON
# ============================================================

ask_button = st.button(
    "⚖️ Ask INSAFBOT",
    type="primary",
    use_container_width=True
)


# ============================================================
# FUNCTION TO GENERATE ANSWER
# ============================================================

def generate_answer(user_question):

    # --------------------------------------------
    # SEARCH LEGAL DOCUMENTS
    # --------------------------------------------

    with st.spinner(
        "🔎 Searching relevant Pakistani laws..."
    ):

        results = search_laws(
            client,
            collection,
            user_question,
            top_k=5
        )


    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]


    # --------------------------------------------
    # BUILD LEGAL CONTEXT
    # --------------------------------------------

    context_parts = []

    for i, document in enumerate(documents):

        metadata = metadatas[i]

        context_parts.append(
            f"""
SOURCE {i + 1}

Document:
{metadata["source"]}

Page:
{metadata["page"]}

Legal Text:
{document}
"""
        )


    context = "\n\n".join(
        context_parts
    )


    # --------------------------------------------
    # GEMINI PROMPT
    # --------------------------------------------

    prompt = f"""
You are INSAFBOT, an AI legal information
assistant focused on Pakistani law.

JURISDICTION:
{province}

USER KNOWLEDGE LEVEL:
{level}

USER QUESTION:
{user_question}

RETRIEVED LEGAL SOURCES:
{context}


STRICT LEGAL SAFETY RULES:

1. Answer ONLY from the retrieved legal sources.

2. Do NOT invent laws.

3. Do NOT invent sections or articles.

4. Do NOT invent penalties.

5. Do NOT invent legal procedures.

6. Do NOT claim that something is illegal unless
   the retrieved legal material supports that claim.

7. If the retrieved sources do not contain enough
   information, clearly say:
   "The available legal documents do not contain
   enough information to answer this question."

8. Never pretend to be a human lawyer.

9. The user may write in Roman Urdu, Urdu,
   or English.

10. Respond in the same language style as the user.

11. Make the explanation easy to understand.

12. Clearly identify the legal source used.


RESPONSE FORMAT:


### ⚖️ Masla

Briefly explain the user's legal issue.


### 📖 Qanoon Kya Kehta Hai

Explain the relevant legal rule using
ONLY the retrieved sources.


### 📌 Relevant Section / Article

Mention the section or article ONLY if it
is clearly present in the retrieved source.


### ➡️ Agla Step

Give practical next steps based ONLY on
the available legal material.


### 📝 Sample Application

If appropriate, provide a short sample
application or complaint.

If an application is not appropriate,
say so.


### 📚 Legal Source

Give:

Document name
Page number
Relevant section/article if available


Do NOT make up section numbers.


"""


    # --------------------------------------------
    # GENERATE GEMINI RESPONSE
    # --------------------------------------------

    with st.spinner(
        "🤖 INSAFBOT is preparing your answer..."
    ):

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )


    return response.text, metadatas


# ============================================================
# PROCESS QUESTION
# ============================================================

if ask_button:

    if not question.strip():

        st.warning(
            "Please enter a legal question first."
        )

    else:

        try:

            answer, sources = generate_answer(
                question.strip()
            )

            st.session_state.answer = answer
            st.session_state.sources = sources

        except Exception as e:

            st.error(
                "Something went wrong while generating "
                "the answer."
            )

            st.exception(e)


# ============================================================
# DISPLAY ANSWER
# ============================================================

if st.session_state.answer:

    st.markdown("---")

    st.markdown(
        "## ⚖️ INSAFBOT Answer"
    )

    st.markdown(
        '<div class="info-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        st.session_state.answer
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # DISCLAIMER
    # ========================================================

    st.markdown(
        """
        <div class="disclaimer-card">

        <h3>⚠️ Legal Disclaimer</h3>

        <p>
        INSAFBOT provides general legal information based
        on the legal documents available in its knowledge
        base. It is an AI system and is <b>not a lawyer</b>
        and does not provide legal representation.
        </p>

        <p>
        Laws may change, and the outcome of a legal matter
        depends on the specific facts and circumstances.
        For important or urgent legal matters, consult a
        qualified lawyer or the relevant legal authority.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # SOURCES
    # ========================================================

    st.markdown("---")

    st.markdown(
        "## 📚 Retrieved Legal Sources"
    )

    unique_sources = []

    for source in st.session_state.sources:

        source_key = (
            source["source"],
            source["page"]
        )

        if source_key not in unique_sources:

            unique_sources.append(source_key)


    for source_name, page in unique_sources:

        st.markdown(
            f"""
            <div class="source-card">

            📄 <b>{source_name}</b>
            <br>
            📑 Page: {page}

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:white;">

    <p>
    ⚖️ <b>INSAFBOT</b> — AI Legal Information Assistant
    </p>

    <p style="font-size:13px;">
    Built using RAG + Gemini + Streamlit
    </p>

    </div>
    """,
    unsafe_allow_html=True
)
