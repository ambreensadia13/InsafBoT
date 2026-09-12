import streamlit as st
from google import genai
from google.genai import errors

from rag import build_database, search_laws


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="INSAFBOT - AI Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS - ROYAL BLUE / CRYSTAL UI
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       MAIN BACKGROUND
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
        font-weight: 700;
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
       MAIN TITLE
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


    /* ========================================================
       SUBTITLE
       ======================================================== */

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

        border-radius: 18px;

        padding: 25px;

        margin-bottom: 25px;

        backdrop-filter: blur(10px);

        box-shadow:
            0 8px 30px rgba(0,0,0,0.18);
    }


    /* ========================================================
       TEXT AREA
       ======================================================== */

    textarea {

        background-color:
            white !important;

        color:
            #111827 !important;

        border-radius:
            12px !important;

        border:
            2px solid #64b5f6 !important;

        font-size:
            16px !important;
    }


    /* ========================================================
       SELECT BOXES
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
       ALL BUTTONS
       ======================================================== */

    .stButton > button {

        width: 100%;

        border-radius: 12px;

        border:
            1px solid rgba(255,255,255,0.5);

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
       PRIMARY ASK BUTTON
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
       ANSWER CARD
       ======================================================== */

    .answer-card {

        background:
            rgba(255,255,255,0.96);

        color:
            #111827;

        border-radius:
            18px;

        padding:
            28px;

        margin-top:
            25px;

        margin-bottom:
            20px;

        box-shadow:
            0 10px 35px rgba(0,0,0,0.25);
    }


    .answer-card h1,
    .answer-card h2,
    .answer-card h3,
    .answer-card h4 {

        color:
            #0b3d91 !important;
    }


    .answer-card p,
    .answer-card li,
    .answer-card strong {

        color:
            #111827 !important;
    }


    /* ========================================================
       DISCLAIMER
       ======================================================== */

    .disclaimer {

        background:
            rgba(255,193,7,0.15);

        border:
            1px solid rgba(255,193,7,0.55);

        border-radius:
            15px;

        padding:
            18px;

        margin-top:
            20px;

        color:
            white;
    }


    .disclaimer-title {

        font-size:
            18px;

        font-weight:
            800;

        margin-bottom:
            8px;
    }


    /* ========================================================
       SOURCE CARD
       ======================================================== */

    .source-card {

        background:
            rgba(255,255,255,0.10);

        border:
            1px solid rgba(255,255,255,0.20);

        border-radius:
            12px;

        padding:
            14px;

        margin-bottom:
            10px;
    }


    /* ========================================================
       QUOTA ERROR CARD
       ======================================================== */

    .quota-card {

        background:
            rgba(255,193,7,0.15);

        border:
            1px solid rgba(255,193,7,0.55);

        border-radius:
            15px;

        padding:
            20px;

        margin-top:
            20px;

        margin-bottom:
            20px;
    }


    .quota-title {

        font-size:
            20px;

        font-weight:
            800;

        margin-bottom:
            10px;

        color:
            #ffffff;
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
            50px;

        padding:
            20px;

        font-size:
            14px;
    }


    /* ========================================================
       DIVIDER
       ======================================================== */

    hr {

        border-color:
            rgba(255,255,255,0.20) !important;
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


# ============================================================
# GEMINI API CONFIGURATION
# ============================================================

try:

    api_key = st.secrets["GEMINI_API_KEY"]

except Exception:

    st.error(
        "GEMINI_API_KEY is missing. "
        "Please add it to Streamlit Secrets."
    )

    st.stop()


client = genai.Client(
    api_key=api_key
)


# ============================================================
# RAG INITIALIZATION
# ============================================================

@st.cache_resource(show_spinner=False)
def initialize_rag():

    return build_database()


with st.spinner(
    "Loading legal knowledge base..."
):

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
    '<div class="subtitle">'
    'AI-Powered Legal Information Assistant for Pakistan'
    '</div>',
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
    You can ask your question in
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

    st.markdown(
        "## ⚖️ INSAFBOT"
    )

    st.markdown(
        "### Settings"
    )


    # --------------------------------------------------------
    # JURISDICTION
    # --------------------------------------------------------

    jurisdiction = st.selectbox(
        "Jurisdiction",
        [
            "Pakistan / Federal",
            "Punjab"
        ]
    )


    # --------------------------------------------------------
    # EXPLANATION LEVEL
    # --------------------------------------------------------

    explanation_level = st.selectbox(
        "Explanation Level",
        [
            "Beginner",
            "Intermediate",
            "Expert"
        ]
    )


    st.markdown("---")


    # --------------------------------------------------------
    # EXAMPLE QUESTIONS
    # --------------------------------------------------------

    st.markdown(
        "### 💡 Example Questions"
    )


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

            # ------------------------------------------------
            # IMPORTANT:
            # Do NOT automatically call Gemini here.
            # This only places the example into the text box.
            # ------------------------------------------------

            st.session_state.question = example

            st.session_state.answer = None

            st.session_state.sources = []

            st.session_state.error_type = None

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
# GENERATE ANSWER FUNCTION
# ============================================================

def generate_answer(user_question):

    # --------------------------------------------------------
    # SEARCH KNOWLEDGE BASE
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


    # --------------------------------------------------------
    # NO RESULTS
    # --------------------------------------------------------

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


    # ========================================================
    # EXPLANATION LEVEL
    # ========================================================

    if explanation_level == "Beginner":

        level_instruction = """
Explain the law in very simple language.

Avoid difficult legal terminology.

Use short paragraphs.

If necessary, give a simple example.

The answer should be easy for an ordinary person
to understand.
"""


    elif explanation_level == "Intermediate":

        level_instruction = """
Give a moderately detailed legal explanation.

Explain important legal terminology when necessary.

Keep the answer understandable but provide
useful legal detail.
"""


    else:

        level_instruction = """
Provide a detailed legal explanation.

Use legal terminology where appropriate.

Mention relevant sections or legal provisions
only when they are clearly present in the
retrieved legal context.
"""


    # ========================================================
    # GEMINI PROMPT
    # ========================================================

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

5. Do NOT invent articles.

6. Do NOT invent penalties.

7. Do NOT invent deadlines.

8. Do NOT invent court procedures.

9. Do NOT invent government fees.

10. Do NOT assume information that is not present
    in the retrieved documents.

11. If the retrieved documents do not contain
    enough information, clearly say:

"Available legal documents mein is sawal ka
complete jawab nahi mila."

12. Do not fill missing information from your
general knowledge.

============================================================
LANGUAGE RULE
============================================================

Respond in the same language/style used by the user.

If the user asks in Roman Urdu,
answer in Roman Urdu.

If the user asks in English,
answer in English.

If the user asks in Urdu,
answer in Urdu when possible.

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

Explain what the retrieved legal documents
specifically say.

### Relevant Section / Article

Mention a section, article, or legal provision
ONLY if it is clearly present in the retrieved
context.

If none is available, say:

"Retrieved documents mein specific section/article
mention nahi hai."

### Agla Step

Give general informational next steps based
ONLY on the retrieved legal documents.

### Legal Source

Mention the relevant TXT document name.

============================================================
FINAL SAFETY RULE
============================================================

Do not claim to be a lawyer.

Do not guarantee any legal outcome.

Do not provide information that is not contained
in the retrieved legal context.

This is general legal information only.

"""


    # ========================================================
    # GEMINI RESPONSE
    # ========================================================

    try:

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )


        # ----------------------------------------------------
        # EMPTY RESPONSE
        # ----------------------------------------------------

        if not response:

            return (
                "Gemini API ne koi response return nahi kiya. "
                "Please dobara try karein.",
                sources,
                "empty_response"
            )


        answer = response.text


        if not answer or not answer.strip():

            return (
                "Gemini API ne empty response return kiya. "
                "Please dobara try karein.",
                sources,
                "empty_response"
            )


        return (
            answer,
            sources,
            None
        )


    # ========================================================
    # GEMINI CLIENT ERROR
    # ========================================================

    except errors.ClientError as e:

        error_message = str(e)


        # ----------------------------------------------------
        # 429 QUOTA EXCEEDED
        # ----------------------------------------------------

        if (
            "429" in error_message
            or "RESOURCE_EXHAUSTED" in error_message
            or "quota" in error_message.lower()
        ):

            quota_message = """
### Gemini API Quota Exceeded

INSAFBOT ka legal knowledge base successfully search ho gaya hai,
lekin Gemini API ki current request quota exceed ho gayi hai.

Aap ke Gemini API project ka free-tier request quota currently
exhaust ho chuka hai.

Please:

- Quota reset hone ke baad dobara try karein.
- Gemini API usage/quota check karein.
- Agar app regularly use karni hai to Gemini project mein
  appropriate billing/paid API access enable karein.

**Important:** Ye RAG, ChromaDB, ya legal TXT files ka error nahi hai.
Legal knowledge base successfully retrieve ho raha hai.
"""

            return (
                quota_message,
                sources,
                "quota"
            )


        # ----------------------------------------------------
        # OTHER GEMINI API ERROR
        # ----------------------------------------------------

        return (
            f"""
### Gemini API Error

Gemini API se answer generate nahi ho saka.

Please apni Gemini API configuration aur model
availability check karein.

Technical error:

`{error_message}`
""",
            sources,
            "gemini_error"
        )


    # ========================================================
    # UNEXPECTED ERROR
    # ========================================================

    except Exception as e:

        return (
            f"""
### Unexpected Error

Answer generate karte waqt unexpected error aa gaya.

Please dobara try karein.

Technical error:

`{str(e)}`
""",
            sources,
            "unexpected_error"
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
# QUESTION PROCESSING
# ============================================================

if ask_clicked:

    if not question.strip():

        st.warning(
            "Please enter a legal question first."
        )

    else:

        # ----------------------------------------------------
        # CLEAR PREVIOUS RESULT
        # ----------------------------------------------------

        st.session_state.answer = None

        st.session_state.sources = []

        st.session_state.error_type = None


        # ----------------------------------------------------
        # GENERATE ANSWER
        # ----------------------------------------------------

        with st.spinner(
            "Searching the legal knowledge base and generating answer..."
        ):

            answer, sources, error_type = generate_answer(
                question.strip()
            )


        # ----------------------------------------------------
        # SAVE RESULT
        # ----------------------------------------------------

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
    # QUOTA ERROR
    # ========================================================

    if st.session_state.error_type == "quota":

        st.markdown(
            f"""
            <div class="quota-card">

            <div class="quota-title">
            ⚠️ Gemini API Quota Limit
            </div>

            {st.session_state.answer}

            </div>
            """,
            unsafe_allow_html=True
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
    # LEGAL DISCLAIMER
    # ========================================================

    st.markdown(
        """
        <div class="disclaimer">

        <div class="disclaimer-title">
        ⚠️ Legal Disclaimer
        </div>

        INSAFBOT provides general legal information
        based on the legal documents available in
        its knowledge base.

        <br><br>

        INSAFBOT is an AI system and is
        <b>not a lawyer</b>.

        It does not provide legal representation
        and does not establish a lawyer-client
        relationship.

        <br><br>

        Laws may change, and the outcome of a legal
        matter depends on the specific facts and
        circumstances.

        <br><br>

        For important, urgent, or high-risk legal
        matters, consult a qualified lawyer or the
        relevant legal authority.

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # RETRIEVED SOURCES
    # ========================================================

    if st.session_state.sources:

        st.markdown(
            "## 📚 Retrieved Legal Sources"
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

    Built with Python • Streamlit • Google Gemini •
    RAG • ChromaDB • Sentence Transformers

    </div>
    """,
    unsafe_allow_html=True
)
