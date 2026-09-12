import streamlit as st
from google import genai

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
# CRYSTAL / ROYAL BLUE UI
# ============================================================

st.markdown(
    """
    <style>

    /* Main application background */
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


    /* Main content */
    .main {
        color: white;
    }


    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700;
    }


    /* Normal text */
    p, li, label, span {
        color: #ffffff;
    }


    /* Sidebar */
    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #04152f 0%,
                #082b63 50%,
                #0b3d91 100%
            );
        border-right: 1px solid rgba(255,255,255,0.15);
    }


    section[data-testid="stSidebar"] * {
        color: white !important;
    }


    /* Main title */
    .main-title {
        text-align: center;
        font-size: 48px;
        font-weight: 800;
        color: white;
        margin-top: 10px;
        margin-bottom: 5px;
        letter-spacing: 1px;
    }


    /* Subtitle */
    .subtitle {
        text-align: center;
        font-size: 20px;
        color: #e3f2fd;
        margin-bottom: 30px;
    }


    /* Intro card */
    .intro-card {
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.20);
        border-radius: 18px;
        padding: 25px;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.18);
    }


    /* Example question card */
    .example-title {
        font-size: 20px;
        font-weight: 700;
        color: white;
        margin-bottom: 12px;
    }


    /* Text area */
    textarea {
        background-color: white !important;
        color: #111827 !important;
        border-radius: 12px !important;
        border: 2px solid #64b5f6 !important;
        font-size: 16px !important;
    }


    /* Select boxes */
    div[data-baseweb="select"] > div {
        background-color: white !important;
        color: #111827 !important;
        border-radius: 10px !important;
    }


    div[data-baseweb="select"] * {
        color: #111827 !important;
    }


    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.5);
        background: rgba(255,255,255,0.12);
        color: white;
        font-weight: 600;
        padding: 10px 15px;
        transition: 0.25s;
    }


    .stButton > button:hover {
        background: white;
        color: #0b3d91;
        border-color: white;
    }


    /* Ask button */
    .ask-button .stButton > button {
        background: white;
        color: #0b3d91;
        font-size: 18px;
        font-weight: 800;
        border: none;
        padding: 14px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    }


    .ask-button .stButton > button:hover {
        background: #e3f2fd;
        color: #061a40;
    }


    /* Answer card */
    .answer-card {
        background: rgba(255,255,255,0.96);
        color: #111827;
        border-radius: 18px;
        padding: 28px;
        margin-top: 25px;
        margin-bottom: 20px;
        box-shadow: 0 10px 35px rgba(0,0,0,0.25);
    }


    .answer-card h3 {
        color: #0b3d91 !important;
    }


    .answer-card p,
    .answer-card li,
    .answer-card strong {
        color: #111827 !important;
    }


    /* Disclaimer */
    .disclaimer {
        background: rgba(255, 193, 7, 0.15);
        border: 1px solid rgba(255, 193, 7, 0.55);
        border-radius: 15px;
        padding: 18px;
        margin-top: 20px;
        color: white;
    }


    .disclaimer-title {
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 8px;
    }


    /* Source card */
    .source-card {
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.20);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
    }


    /* Footer */
    .footer {
        text-align: center;
        color: #dbeafe;
        margin-top: 50px;
        padding: 20px;
        font-size: 14px;
    }


    /* Divider */
    hr {
        border-color: rgba(255,255,255,0.20) !important;
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

if "auto_ask" not in st.session_state:
    st.session_state.auto_ask = False


# ============================================================
# GEMINI API
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
    using a collection of legal documents and AI-powered
    retrieval.
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

    st.markdown(
        "### 💡 Example Questions"
    )

    examples = [

  "Qatl-e-amd ki Pakistan Penal Code mein kya saza hai?",

    "Agar koi shakhs dhoka de kar paisay hasil kare to konsa jurm banta hai?",

    "Criminal breach of trust kya hota hai?",

    "Agar koi mujhe internet par baar baar harass ya stalk kare to PECA ke mutabiq kya offence hai?",

    "Kya kisi minor ko online sexual purpose ke liye groom karna jurm hai?",

    "Malicious code kya hota hai aur PECA mein iski kya punishment hai?",

    "Constitution ke Article 25 mein equality of citizens ke bare mein kya kaha gaya hai?",

    "Kya Pakistan mein sex ki bunyaad par discrimination allowed hai?",

    "Muslim Family Laws Ordinance ke mutabiq nikah ki registration zaroori hai?",

    "Talaq dene ke baad Muslim Family Laws Ordinance ke mutabiq kya procedure follow karna hota hai?"

    ]


    for i, example in enumerate(examples, start=1):

        if st.button(
            f"{i}. {example}",
            key=f"example_{i}"
        ):

            st.session_state.question = example
            st.session_state.auto_ask = True

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
        "Example: Mere husband mujhe maintenance nahi de rahe, "
        "main kya kar sakti hoon?"
    ),
    label_visibility="collapsed"
)


st.session_state.question = question


# ============================================================
# GENERATE ANSWER FUNCTION
# ============================================================

def generate_answer(user_question):

    # Retrieve relevant legal documents
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
            []
        )


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
            "Unknown"
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
Use short paragraphs and simple examples.
"""

    elif explanation_level == "Intermediate":

        level_instruction = """
Give a moderately detailed legal explanation.
Explain important legal terminology when necessary.
"""

    else:

        level_instruction = """
Provide a detailed legal explanation.
Use legal terminology where appropriate.
Mention relevant sections/articles only when
they are clearly present in the retrieved context.
"""


    # ========================================================
    # GEMINI PROMPT
    # ========================================================

    prompt = f"""
You are INSAFBOT, an AI legal information assistant
for Pakistan.

Your task is to provide general legal information based
ONLY on the legal documents retrieved from the INSAFBOT
knowledge base.

IMPORTANT RULES:

1. Do NOT use outside legal knowledge.

2. Do NOT invent laws.

3. Do NOT invent sections.

4. Do NOT invent articles.

5. Do NOT invent penalties.

6. Do NOT invent court procedures.

7. Do NOT invent deadlines.

8. If the retrieved information is insufficient,
   clearly say that the available legal documents
   do not contain enough information.

9. Respond in the same language/style as the user.

10. If the user asks in Roman Urdu, respond in Roman Urdu.

11. Explain the retrieved legal information clearly.

12. Mention the legal source and page when possible.

13. Do not claim to be a lawyer.

14. Do not provide guaranteed legal outcomes.

15. The information is general legal information only.

JURISDICTION:

{jurisdiction}

EXPLANATION LEVEL:

{explanation_level}

EXPLANATION INSTRUCTIONS:

{level_instruction}

USER QUESTION:

{user_question}

RETRIEVED LEGAL CONTEXT:

{context}

Provide the response using this structure:

### Masla

Briefly explain the user's legal issue.

### Qanoon Kya Kehta Hai

Explain what the retrieved legal documents say.

### Relevant Section / Article

Mention the relevant section or article ONLY if it
is clearly available in the retrieved context.

### Agla Step

Give general informational next steps based ONLY
on the retrieved legal information.

### Legal Source

Mention the document name and page number.

Remember:

If the retrieved legal context does not provide
enough information, say:

"Available legal documents mein is sawal ka
complete jawab nahi mila."

Do not make up information.
"""


    # ========================================================
    # GEMINI GENERATION
    # ========================================================

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )


    answer = response.text


    return answer, sources


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
    '</div>',
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

        with st.spinner(
            "Searching the legal knowledge base..."
        ):

            try:

                answer, sources = generate_answer(
                    question.strip()
                )

                st.session_state.answer = answer
                st.session_state.sources = sources

            except Exception as e:

                st.error(
                    "Sorry, an error occurred while "
                    "generating the answer."
                )

                st.exception(e)


# ============================================================
# AUTO ASK EXAMPLE QUESTIONS
# ============================================================

if st.session_state.auto_ask:

    st.session_state.auto_ask = False

    if st.session_state.question.strip():

        with st.spinner(
            "Searching the legal knowledge base..."
        ):

            try:

                answer, sources = generate_answer(
                    st.session_state.question.strip()
                )

                st.session_state.answer = answer
                st.session_state.sources = sources

            except Exception as e:

                st.error(
                    "Sorry, an error occurred while "
                    "generating the answer."
                )

                st.exception(e)


# ============================================================
# DISPLAY ANSWER
# ============================================================

if st.session_state.answer:

    st.markdown(
        "## 🤖 INSAFBOT Answer"
    )


    st.markdown(
        '<div class="answer-card">',
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
    # LEGAL DISCLAIMER
    # ========================================================

    st.markdown(
        """
        <div class="disclaimer">

        <div class="disclaimer-title">
        ⚠️ Legal Disclaimer
        </div>

        INSAFBOT provides general legal information based
        on the legal documents available in its knowledge base.

        <br><br>

        INSAFBOT is an AI system and is <b>not a lawyer</b>
        and does not provide legal representation or establish
        a lawyer-client relationship.

        <br><br>

        Laws may change, and the outcome of a legal matter
        depends on the specific facts and circumstances.

        <br><br>

        For important, urgent, or high-risk legal matters,
        consult a qualified lawyer or the relevant legal
        authority.

        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # SOURCES
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
                "Unknown"
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

    ⚖️ <b>INSAFBOT</b> — AI Legal Information Assistant
    for Pakistan

    <br><br>

    Built with Python • Streamlit • Google Gemini •
    RAG • ChromaDB • Sentence Transformers

    </div>
    """,
    unsafe_allow_html=True
)
