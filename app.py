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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at top left,
                #2563eb 0%,
                #1e40af 25%,
                #172554 55%,
                #020617 100%
            );
        color: white;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #0f172a,
                #172554
            );
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    .main-title {
        text-align: center;
        font-size: 52px;
        font-weight: 800;
        margin-bottom: 0px;

        background:
            linear-gradient(
                90deg,
                #ffffff,
                #bfdbfe,
                #60a5fa
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        text-align: center;
        color: #dbeafe;
        font-size: 18px;
        margin-bottom: 35px;
    }

    textarea {
        background-color: white !important;
        color: black !important;
        border-radius: 12px !important;
    }

    textarea::placeholder {
        color: #555 !important;
    }

    .answer-card {
        background: white;
        color: black !important;
        padding: 25px;
        border-radius: 16px;
        margin-top: 25px;

        box-shadow:
            0 10px 35px rgba(
                0,
                0,
                0,
                0.25
            );

        line-height: 1.7;
    }

    .answer-card * {
        color: black !important;
    }

    .source-card {
        background: #eff6ff;

        border-left:
            4px solid #2563eb;

        padding: 12px 15px;
        margin-bottom: 8px;
        border-radius: 8px;

        color: black !important;
    }

    .source-card * {
        color: black !important;
    }

    .disclaimer {
        font-size: 12px;
        color: #dbeafe;
        text-align: center;
        margin-top: 15px;
    }

    .footer {
        text-align: center;
        color: #bfdbfe;
        font-size: 13px;
        margin-top: 45px;
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
    st.session_state.answer = ""

if "sources" not in st.session_state:
    st.session_state.sources = []

if "show_sources" not in st.session_state:
    st.session_state.show_sources = False


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">INSAFBOT</div>',
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

    st.header("Settings")

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

    language = st.selectbox(
        "Answer Language",
        [
            "English",
            "Urdu",
            "Roman Urdu"
        ]
    )

    st.divider()

    st.subheader("Example Questions")

    examples = [
        "Pakistan mein FIR kaise darj karwai ja sakti hai?",
        "Agar malik makan tenant ko ghar se nikalna chahe to kya qanooni tareeqa hai?",
        "Agar employer meri salary nahi de raha to main kya kar sakti hoon?",
        "NADRA record mein naam ki ghalti kaise theek karwai ja sakti hai?",
        "Agar koi mujhe online dhamki de raha hai to main kya karoon?",
        "Pakistan mein khula lene ka qanooni tareeqa kya hai?",
        "Aurat ko domestic violence se qanooni protection kaise mil sakti hai?",
        "Agar cheque bounce ho jaye to kya qanooni karwai ho sakti hai?",
        "Property fraud ki surat mein main kya qanooni karwai kar sakti hoon?",
        "Traffic challan milne ke baad kya karna chahiye?"
    ]

    for example in examples:

        if st.button(
            example,
            use_container_width=True
        ):
            st.session_state.question = example

    st.divider()

    st.info(
        "INSAFBOT answers questions using "
        "its local legal knowledge base."
    )


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

try:

    collection = build_database()

except Exception as error:

    st.error(
        "Knowledge base load nahi ho saki."
    )

    st.code(str(error))

    st.stop()


# ============================================================
# QUESTION INPUT
# ============================================================

st.subheader(
    "Ask Your Legal Question"
)

question = st.text_area(
    "Enter your question",

    value=st.session_state.question,

    height=140,

    placeholder=(
        "Example: Pakistan mein FIR "
        "kaise darj karwai ja sakti hai?"
    ),

    label_visibility="collapsed"
)

st.session_state.question = question


# ============================================================
# ASK BUTTON
# ============================================================

ask_button = st.button(
    "Ask INSAFBOT",
    type="primary",
    use_container_width=True
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if ask_button:

    question = question.strip()

    if not question:

        st.warning(
            "Please enter a legal question."
        )

        st.stop()

    # --------------------------------------------------------
    # SEARCH KNOWLEDGE BASE
    # --------------------------------------------------------

    with st.spinner(
        "Searching legal knowledge base..."
    ):

        try:

            results = search_laws(
                collection,
                question,
                top_k=5
            )

        except Exception as error:

            st.error(
                "Legal knowledge search mein error aa gaya."
            )

            st.code(str(error))

            st.stop()

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    if not documents:

        st.warning(
            "Is question ke liye relevant "
            "information knowledge base mein nahi mili."
        )

        st.stop()

    # --------------------------------------------------------
    # BUILD CONTEXT
    # --------------------------------------------------------

    context_parts = []

    for index, document in enumerate(documents):

        if index < len(metadatas):

            metadata = metadatas[index]

        else:

            metadata = {}

        source = metadata.get(
            "source",
            "Unknown"
        )

        context_parts.append(
            f"""
SOURCE: {source}

CONTENT:
{document}
"""
        )

    context = "\n\n".join(context_parts)

    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    if language == "English":

        language_instruction = (
            "Answer entirely in clear and simple English."
        )

    elif language == "Urdu":

        language_instruction = (
            "Answer entirely in Urdu script."
        )

    else:

        language_instruction = (
            "Answer entirely in easy Roman Urdu."
        )

    # --------------------------------------------------------
    # EXPLANATION LEVEL
    # --------------------------------------------------------

    if explanation_level == "Beginner":

        level_instruction = """
Use very simple language.
Avoid unnecessary legal terminology.
Use short paragraphs and bullet points.
Explain important terms in simple words.
"""

    elif explanation_level == "Intermediate":

        level_instruction = """
Give a moderately detailed explanation.
Explain important legal terms briefly.
Use headings and bullet points where useful.
"""

    else:

        level_instruction = """
Give a detailed explanation.
Use appropriate legal terminology.
Clearly distinguish between legal rules,
rights, procedures and practical steps.
"""

    # --------------------------------------------------------
    # SYSTEM PROMPT
    # --------------------------------------------------------

    system_prompt = f"""
You are INSAFBOT.

You are an AI legal information assistant
focused on Pakistani law.

Jurisdiction:
{jurisdiction}

Explanation level:
{explanation_level}

Requested language:
{language}

IMPORTANT RULES:

1. Answer ONLY using the provided legal
knowledge base.

2. Do NOT invent laws.

3. Do NOT invent section numbers.

4. Do NOT invent penalties.

5. Do NOT invent deadlines.

6. Do NOT invent fees.

7. Do NOT invent government procedures.

8. Do NOT invent case citations.

9. If the knowledge base does not contain
enough information, clearly say:

"The available legal knowledge base does
not contain enough information to answer
this question accurately."

10. Never pretend to be a lawyer.

11. Give general legal information only.

12. Suggest consulting a qualified lawyer
or relevant government authority when
appropriate.

13. Keep the answer directly related
to the user's question.

{language_instruction}

{level_instruction}
"""

    # --------------------------------------------------------
    # USER PROMPT
    # --------------------------------------------------------

    user_prompt = f"""
LEGAL KNOWLEDGE BASE:

{context}

USER QUESTION:

{question}

Answer the user's question using ONLY
the legal knowledge base above.

Do not use outside legal information.

Do not make assumptions.

If the retrieved information is insufficient,
say so clearly.
"""

    # --------------------------------------------------------
    # GROQ API KEY
    # --------------------------------------------------------

    try:

        groq_api_key = st.secrets[
            "GROQ_API_KEY"
        ]

    except Exception:

        st.error(
            "GROQ_API_KEY Streamlit Secrets "
            "mein nahi mili."
        )

        st.code(
            'GROQ_API_KEY = "your_api_key_here"'
        )

        st.stop()

    # --------------------------------------------------------
    # GROQ CLIENT
    # --------------------------------------------------------

    client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    # --------------------------------------------------------
    # GENERATE ANSWER
    # --------------------------------------------------------

    with st.spinner(
        "INSAFBOT is preparing your answer..."
    ):

        try:

            response = client.responses.create(
                model="openai/gpt-oss-120b",
                instructions=system_prompt,
                input=user_prompt,
                reasoning={
                    "effort": "medium"
                },
                max_output_tokens=1500
            )

            answer = response.output_text

        except Exception as error:

            st.error(
                "Groq API se answer generate nahi ho saka."
            )

            st.code(str(error))

            st.stop()

    # --------------------------------------------------------
    # SAVE ANSWER
    # --------------------------------------------------------

    st.session_state.answer = answer

    # --------------------------------------------------------
    # SAVE SOURCES
    # --------------------------------------------------------

    unique_sources = []

    for metadata in metadatas:

        source = metadata.get(
            "source",
            "Unknown"
        )

        if source not in unique_sources:

            unique_sources.append(source)

    st.session_state.sources = unique_sources

    st.session_state.show_sources = False


# ============================================================
# DISPLAY ANSWER
# ============================================================

if st.session_state.answer:

    st.subheader(
        "INSAFBOT Answer"
    )

    answer_html = (
        st.session_state.answer
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )

    st.markdown(
        f"""
        <div class="answer-card">
            {answer_html}
        </div>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # LEGAL RESOURCES BUTTON
    # --------------------------------------------------------

    if st.button(
        "Legal Resources",
        use_container_width=True
    ):

        st.session_state.show_sources = (
            not st.session_state.show_sources
        )

    # --------------------------------------------------------
    # SOURCES
    # --------------------------------------------------------

    if st.session_state.show_sources:

        st.markdown(
            "### Sources"
        )

        for source in st.session_state.sources:

            st.markdown(
                f"""
                <div class="source-card">

                    <strong>
                        {source}
                    </strong>

                    <br>

                    Page: N/A

                </div>
                """,
                unsafe_allow_html=True
            )


# ============================================================
# DISCLAIMER
# ============================================================

st.markdown(
    """
    <div class="disclaimer">

    INSAFBOT provides general legal information
    and is not a substitute for professional
    legal advice.

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

    © 2026 INSAFBOT • Legal Information Assistant
    for Pakistan

    </div>
    """,
    unsafe_allow_html=True
)
