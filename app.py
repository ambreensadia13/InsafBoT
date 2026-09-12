import streamlit as st
from openai import OpenAI

from rag import build_database, search_laws


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="INSAFBOT - AI Legal Assistant",
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

    /* ========================================================
       MAIN APP
       ======================================================== */

    .stApp {
        background:
            linear-gradient(
                135deg,
                #061a40 0%,
                #0b3d91 45%,
                #1565c0 75%,
                #1e88e5 100%
            );

        color: white;
    }


    /* ========================================================
       GENERAL TEXT
       ======================================================== */

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
        color: #ffffff !important;
    }


    p,
    li,
    label,
    span {
        color: #ffffff;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #04152f 0%,
                #082b63 50%,
                #0b3d91 100%
            );

        border-right:
            1px solid rgba(255,255,255,0.15);
    }


    section[data-testid="stSidebar"] * {
        color: white !important;
    }


    /* ========================================================
       TITLE
       ======================================================== */

    .main-title {
        text-align: center;

        font-size: 48px;

        font-weight: 800;

        color: white;

        margin-top: 10px;

        margin-bottom: 5px;

        letter-spacing: 1px;
    }


    .subtitle {
        text-align: center;

        font-size: 20px;

        color: #e3f2fd;

        margin-bottom: 30px;
    }


    /* ========================================================
       INTRO CARD
       ======================================================== */

    .intro-card {
        background:
            rgba(255,255,255,0.12);

        border:
            1px solid rgba(255,255,255,0.20);

        border-radius:
            18px;

        padding:
            25px;

        margin-bottom:
            25px;

        backdrop-filter:
            blur(10px);

        box-shadow:
            0 8px 30px rgba(0,0,0,0.18);
    }


    /* ========================================================
       TEXT INPUT
       ======================================================== */

    textarea {
        background-color:
            white !important;

        color:
            #000000 !important;

        border-radius:
            12px !important;

        border:
            2px solid #64b5f6 !important;

        font-size:
            16px !important;
    }


    textarea::placeholder {
        color:
            #555555 !important;
    }


    /* ========================================================
       SELECT BOX
       ======================================================== */

    div[data-baseweb="select"] > div {
        background-color:
            white !important;

        color:
            #111827 !important;

        border-radius:
            10px !important;
    }


    div[data-baseweb="select"] * {
        color:
            #111827 !important;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        width: 100%;

        border-radius:
            12px;

        border:
            1px solid rgba(255,255,255,0.45);

        background:
            rgba(255,255,255,0.12);

        color:
            white;

        font-weight:
            600;

        padding:
            10px 15px;

        transition:
            0.25s;
    }


    .stButton > button:hover {
        background:
            white;

        color:
            #0b3d91;

        border-color:
            white;
    }


    /* ========================================================
       ASK BUTTON
       ======================================================== */

    .ask-button .stButton > button {
        background:
            white;

        color:
            #0b3d91;

        font-size:
            18px;

        font-weight:
            800;

        border:
            none;

        padding:
            14px;

        box-shadow:
            0 6px 20px rgba(0,0,0,0.20);
    }


    .ask-button .stButton > button:hover {
        background:
            #e3f2fd;

        color:
            #061a40;
    }


    /* ========================================================
       WHITE ANSWER BOX
       ======================================================== */

    .answer-card {
        background:
            #ffffff !important;

        color:
            #000000 !important;

        border-radius:
            16px;

        padding:
            28px;

        margin-top:
            20px;

        margin-bottom:
            18px;

        box-shadow:
            0 8px 28px rgba(0,0,0,0.25);

        border:
            1px solid #dbeafe;
    }


    /* ALL ANSWER TEXT BLACK */

    .answer-card,
    .answer-card p,
    .answer-card span,
    .answer-card div,
    .answer-card li,
    .answer-card ul,
    .answer-card ol,
    .answer-card strong,
    .answer-card em {
        color:
            #000000 !important;
    }


    .answer-card h1,
    .answer-card h2,
    .answer-card h3,
    .answer-card h4,
    .answer-card h5,
    .answer-card h6 {
        color:
            #000000 !important;
    }


    .answer-card code {
        color:
            #000000 !important;

        background:
            #f1f5f9 !important;
    }


    .answer-card pre {
        background:
            #f1f5f9 !important;

        color:
            #000000 !important;
    }


    /* ========================================================
       SMALL DISCLAIMER
       ======================================================== */

    .disclaimer {
        background:
            rgba(255,255,255,0.10);

        border:
            1px solid rgba(255,255,255,0.25);

        border-radius:
            10px;

        padding:
            10px 14px;

        margin-top:
            10px;

        margin-bottom:
            15px;

        color:
            white !important;

        font-size:
            13px;
    }


    .disclaimer b {
        color:
            white !important;
    }


    /* ========================================================
       SOURCE CARD
       ======================================================== */

    .source-card {
        background:
            rgba(255,255,255,0.12);

        border:
            1px solid rgba(255,255,255,0.22);

        border-radius:
            12px;

        padding:
            14px;

        margin-bottom:
            10px;

        color:
            white !important;
    }


    .source-card b {
        color:
            white !important;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        text-align:
            center;

        color:
            #dbeafe;

        margin-top:
            45px;

        padding:
            20px;

        font-size:
            14px;
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

if "answer" not in st.session_state:
    st.session_state.answer = None

if "sources" not in st.session_state:
    st.session_state.sources = []

if "error_type" not in st.session_state:
    st.session_state.error_type = None

if "show_sources" not in st.session_state:
    st.session_state.show_sources = False


# ============================================================
# GROK API
# ============================================================

try:

    xai_api_key = st.secrets["XAI_API_KEY"]

except Exception:

    st.error(
        "XAI_API_KEY is missing. "
        "Please add your Grok API key to Streamlit Secrets."
    )

    st.stop()


client = OpenAI(
    api_key=xai_api_key,
    base_url="https://api.x.ai/v1"
)


# ============================================================
# RAG DATABASE
# ============================================================

@st.cache_resource(show_spinner=False)
def initialize_rag():

    return build_database()


with st.spinner("Loading legal knowledge base..."):

    try:

        collection = initialize_rag()

    except Exception as e:

        st.error(
            "The legal knowledge base could not be loaded."
        )

        st.exception(e)

        st.stop()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">⚖️ INSAFBOT</div>',
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
# INTRODUCTION
# ============================================================

st.markdown(
    """
    <div class="intro-card">

    <h3>🇵🇰 Understand Pakistani Law</h3>

    <p>
    INSAFBOT helps users understand Pakistani legal information
    using a local legal knowledge base and AI-powered retrieval.
    </p>

    <p>
    Ask questions in
    <b>English, Urdu, or Roman Urdu</b>.
    </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ⚖️ INSAFBOT")

    st.markdown("### Settings")


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


    st.markdown("---")


    st.markdown("### 💡 Example Questions")


    examples = [

        "Police meri FIR darj nahi kar rahi, main kya kar sakta hoon?",

        "Agar koi shakhs dhoka de kar paisay le le to Pakistan mein konsa jurm banta hai?",

        "Qatl-e-amd ki Pakistan Penal Code mein kya saza hai?",

        "Makan malik bina legal notice ke mujhe ghar se nikal sakta hai?",

        "Kya makan malik har saal rent increase kar sakta hai?",

        "Mera employer meri salary time par nahi de raha, main complaint kahan karun?",

        "Mera CNIC gum ho gaya hai, duplicate CNIC kaise banwa sakta hoon?",

        "Bache ka B-Form ya CRC banwane ke liye kya documents chahiye?",

        "Facebook par mujhe blackmail kiya ja raha hai, cybercrime ki complaint kahan karun?",

        "Khula lene ke liye aurat ko kya legal process follow karna hota hai?",

        "Agar ghar mein domestic violence ho rahi ho to protection order kaise mil sakta hai?",

        "Cheque bounce ho gaya hai, mere paas kya legal options hain?",

        "Zameen ki fake registry ban gayi hai, main kya legal action le sakta hoon?",

        "Kharab product dene par dukandaar ke khilaf consumer complaint kaise kar sakta hoon?",

        "Office mein harassment ho rahi hai, complaint kahan file karni chahiye?",

        "Agar mujhe kisi criminal case mein arrest ka khatra ho to bail kaise mil sakti hai?",

        "Muslim wasiyat mein apni property ka kitna hissa de sakta hoon?",

        "Passport gum ho jaye to naya passport banwane ka kya process hai?",

        "Sarkari daftar se information lene ke liye RTI application kaise submit karun?",

        "Contract ya agreement ki shart doosra person poori na kare to main kya legal action le sakta hoon?"

    ]


    for i, example in enumerate(
        examples,
        start=1
    ):

        if st.button(
            f"{i}. {example}",
            key=f"example_{i}"
        ):

            st.session_state.question = example

            st.session_state.answer = None

            st.session_state.sources = []

            st.session_state.error_type = None

            st.session_state.show_sources = False

            st.rerun()


# ============================================================
# QUESTION INPUT
# ============================================================

st.markdown(
    "## 📝 Ask Your Legal Question"
)

st.markdown(
    "Write your question in English, Urdu, or Roman Urdu."
)


question = st.text_area(
    "Your question",

    value=st.session_state.question,

    height=130,

    placeholder=(
        "Example: Mere husband mujhe maintenance "
        "nahi de rahe, main kya kar sakti hoon?"
    ),

    label_visibility="collapsed"
)


st.session_state.question = question


# ============================================================
# GENERATE ANSWER
# ============================================================

def generate_answer(user_question):

    # --------------------------------------------------------
    # SEARCH RAG
    # --------------------------------------------------------

    results = search_laws(
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


    if not documents:

        return (
            "Available legal documents mein is sawal ka "
            "complete jawab nahi mila.",
            [],
            None
        )


    # --------------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------------

    context_parts = []

    sources = []


    for document, metadata in zip(
        documents,
        metadatas
    ):

        source = metadata.get(
            "source",
            "Unknown"
        )

        page = metadata.get(
            "page",
            "N/A"
        )


        context_parts.append(
            f"""
SOURCE: {source}

PAGE: {page}

LEGAL TEXT:

{document}
"""
        )


        sources.append(
            {
                "source": source,
                "page": page
            }
        )


    context = "\n\n".join(
        context_parts
    )


    # --------------------------------------------------------
    # EXPLANATION LEVEL
    # --------------------------------------------------------

    if explanation_level == "Beginner":

        level_instruction = """
Explain the law in very simple language.

Avoid difficult legal terminology.

Use short paragraphs.

Make the answer easy for an ordinary person
to understand.
"""


    elif explanation_level == "Intermediate":

        level_instruction = """
Give a moderately detailed explanation.

Explain important legal terminology when necessary.

Keep the answer understandable while providing
useful legal detail.
"""


    else:

        level_instruction = """
Provide a detailed legal explanation.

Use legal terminology where appropriate.

Mention sections or legal provisions ONLY when
they are clearly present in the retrieved context.
"""


    # --------------------------------------------------------
    # GROK PROMPT
    # --------------------------------------------------------

    prompt = f"""

You are INSAFBOT, an AI legal information assistant
for Pakistan.

Your job is to explain Pakistani legal information
using ONLY the retrieved documents supplied below.

============================================================
STRICT KNOWLEDGE BASE RULES
============================================================

1. Use ONLY the retrieved legal context.

2. Do NOT use outside legal knowledge.

3. Do NOT invent laws.

4. Do NOT invent sections.

5. Do NOT invent penalties.

6. Do NOT invent deadlines.

7. Do NOT invent government fees.

8. Do NOT assume missing information.

9. If the retrieved documents do not contain
   enough information, clearly say:

"Available legal documents mein is sawal ka
complete jawab nahi mila."

10. Do not fill missing information from
general knowledge.

============================================================
LANGUAGE
============================================================

Respond in the same language/style as the user.

Roman Urdu question = Roman Urdu answer.

English question = English answer.

Urdu question = Urdu answer when possible.

============================================================
JURISDICTION
============================================================

{jurisdiction}

============================================================
EXPLANATION LEVEL
============================================================

{explanation_level}

============================================================
EXPLANATION INSTRUCTIONS
============================================================

{level_instruction}

============================================================
USER QUESTION
============================================================

{user_question}

============================================================
RETRIEVED LEGAL CONTEXT
============================================================

{context}

============================================================
ANSWER FORMAT
============================================================

### Masla

Briefly explain the user's legal issue.

### Qanoon Kya Kehta Hai

Explain what the retrieved legal documents say.

### Relevant Section / Article

Mention a section or legal provision ONLY if it
appears in the retrieved context.

### Agla Step

Give general next steps based ONLY on the
retrieved documents.

### Legal Source

Mention the relevant source document.

============================================================
FINAL RULE
============================================================

Do not claim to be a lawyer.

Do not guarantee any legal outcome.

Do not provide information outside the
retrieved legal context.

This is general legal information only.
"""


    # --------------------------------------------------------
    # GROK API REQUEST
    # --------------------------------------------------------

    try:

        response = client.responses.create(
            model="grok-4.6",
            input=prompt
        )


        answer = response.output_text


        if not answer or not answer.strip():

            return (
                "Grok ne empty response return kiya. "
                "Please dobara try karein.",
                sources,
                "empty_response"
            )


        return (
            answer,
            sources,
            None
        )


    # --------------------------------------------------------
    # API ERROR
    # --------------------------------------------------------

    except Exception as e:

        error_message = str(e)


        return (
            f"""
### Grok API Error

Answer generate nahi ho saka.

Please kuch seconds baad dobara try karein.

Technical error:

`{error_message}`
""",
            sources,
            "api_error"
        )


# ============================================================
# ASK BUTTON
# ============================================================

st.markdown(
    '<div class="ask-button">',
    unsafe_allow_html=True
)


ask_clicked = st.button(
    "⚖️ Ask INSAFBOT",
    type="primary"
)


st.markdown(
    "</div>",
    unsafe_allow_html=True
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if ask_clicked:

    if not question.strip():

        st.warning(
            "Please enter a legal question first."
        )

    else:

        st.session_state.answer = None

        st.session_state.sources = []

        st.session_state.error_type = None

        st.session_state.show_sources = False


        with st.spinner(
            "Searching legal knowledge base and asking Grok..."
        ):

            answer, sources, error_type = generate_answer(
                question.strip()
            )


            st.session_state.answer = answer

            st.session_state.sources = sources

            st.session_state.error_type = error_type


# ============================================================
# DISPLAY ANSWER
# ============================================================

if st.session_state.answer:

    st.markdown(
        "## 🤖 INSAFBOT Answer"
    )


    # ========================================================
    # API ERROR
    # ========================================================

    if st.session_state.error_type == "api_error":

        st.error(
            "Grok API temporarily failed. Please try again."
        )

        st.markdown(
            st.session_state.answer
        )


    # ========================================================
    # EMPTY RESPONSE
    # ========================================================

    elif st.session_state.error_type == "empty_response":

        st.warning(
            "Grok returned an empty response."
        )

        st.markdown(
            st.session_state.answer
        )


    # ========================================================
    # NORMAL ANSWER
    # ========================================================

    else:

        st.markdown(
            '<div class="answer-card">',
            unsafe_allow_html=True
        )


        st.markdown(
            st.session_state.answer
        )


        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ========================================================
    # SHORT DISCLAIMER
    # ========================================================

    st.markdown(
        """
        <div class="disclaimer">

        ⚠️ <b>Disclaimer:</b>
        INSAFBOT provides general legal information
        and is not a substitute for professional legal advice.

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # LEGAL RESOURCES BUTTON
    # ========================================================

    if st.session_state.sources:

        if st.button(
            "📚 Legal Resources",
            key="legal_resources_button"
        ):

            st.session_state.show_sources = (
                not st.session_state.show_sources
            )


        # ----------------------------------------------------
        # SHOW SOURCES
        # ----------------------------------------------------

        if st.session_state.show_sources:

            st.markdown(
                "### 📚 Retrieved Legal Resources"
            )


            displayed_sources = set()


            for source in st.session_state.sources:

                source_name = source.get(
                    "source",
                    "Unknown"
                )

                page = source.get(
                    "page",
                    "N/A"
                )


                source_key = (
                    source_name,
                    page
                )


                if source_key in displayed_sources:

                    continue


                displayed_sources.add(
                    source_key
                )


                st.markdown(
                    f"""
                    <div class="source-card">

                    📄 <b>{source_name}</b>

                    <br>

                    📖 Page: {page}

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

    ⚖️ <b>INSAFBOT</b> —
    AI Legal Information Assistant for Pakistan

    <br><br>

    Built with Python • Streamlit • Grok •
    RAG • ChromaDB • Sentence Transformers

    </div>
    """,
    unsafe_allow_html=True
)
