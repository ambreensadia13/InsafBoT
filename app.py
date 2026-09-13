in my sourse i just want to see from which .txt file the law is taken from  import streamlit as st
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

    /* ======================================================
       MAIN APP
       ====================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at top left,
                #2563eb 0%,
                #1e40af 25%,
                #172554 55%,
                #020617 100%
            );

        color: #ffffff;
    }


    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #0f172a 0%,
                #172554 100%
            ) !important;
    }


    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }


    section[data-testid="stSidebar"] hr {
        border-color: #ffffff !important;
        opacity: 0.2;
    }


    /* ======================================================
       SIDEBAR SELECT BOX
       ====================================================== */

    section[data-testid="stSidebar"]
    [data-testid="stSelectbox"] {
        width: 100% !important;
    }


    section[data-testid="stSidebar"]
    [data-testid="stSelectbox"]
    [data-baseweb="select"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border-radius: 12px !important;
    }


    section[data-testid="stSidebar"]
    [data-testid="stSelectbox"]
    [data-baseweb="select"] > div {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        border-radius: 12px !important;
        min-height: 48px !important;
    }


    section[data-testid="stSidebar"]
    [data-testid="stSelectbox"]
    [data-baseweb="select"] div {
        background-color: #0f172a !important;
        color: #ffffff !important;
    }


    section[data-testid="stSidebar"]
    [data-testid="stSelectbox"]
    input {
        background-color: #0f172a !important;
        color: #ffffff !important;
    }


    section[data-testid="stSidebar"]
    [data-testid="stSelectbox"]
    svg {
        color: #ffffff !important;
        fill: #ffffff !important;
    }


    /* ======================================================
       DROPDOWN
       ====================================================== */

    div[data-baseweb="popover"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        border-radius: 12px !important;
    }


    div[data-baseweb="popover"] > div {
        background-color: #0f172a !important;
        color: #ffffff !important;
    }


    div[role="listbox"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        border-radius: 12px !important;
    }


    div[role="option"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
    }


    div[role="option"] * {
        background-color: #0f172a !important;
        color: #ffffff !important;
    }


    div[role="option"]:hover {
        background-color: #172554 !important;
        color: #ffffff !important;
    }


    div[role="option"][aria-selected="true"] {
        background-color: #172554 !important;
        color: #ffffff !important;
    }


    /* ======================================================
       TITLE
       ====================================================== */

    .main-title {
        text-align: center;
        font-size: 52px;
        font-weight: 800;
        margin-bottom: 0;
        color: #ffffff !important;
    }


    .subtitle {
        text-align: center;
        color: #ffffff !important;
        font-size: 18px;
        margin-bottom: 35px;
    }


    /* ======================================================
       TEXT AREA
       ====================================================== */

    textarea {
        background-color: #ffffff !important;
        color: #111827 !important;
        border-radius: 12px !important;
        border: 1px solid #ffffff !important;
    }


    textarea::placeholder {
        color: #555555 !important;
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

    div[data-testid="stButton"] button {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #315a91 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }


    div[data-testid="stButton"] button p {
        color: #ffffff !important;
    }


    div[data-testid="stButton"] button:hover {
        background-color: #172554 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }


    div[data-testid="stButton"] button:focus {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }


    div[data-testid="stButton"] button:active {
        background-color: #0f172a !important;
        color: #ffffff !important;
    }


    /* ======================================================
       ANSWER BOX
       ====================================================== */

    .answer-box {
        background-color: #ffffff;
        color: #111827;
        padding: 25px;
        border-radius: 16px;
        margin-top: 20px;
        line-height: 1.75;
        font-size: 16px;
        box-shadow:
            0 10px 35px rgba(
                0,
                0,
                0,
                0.25
            );

        overflow-wrap: break-word;
    }


    /* ======================================================
       SOURCES TITLE
       ====================================================== */

    .sources-title {
        color: #ffffff !important;
        font-size: 30px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 15px;
    }


    /* ======================================================
       NATIVE SOURCE BOX
       ====================================================== */

    .source-box {
        background-color: #0f172a !important;
        border: 1px solid #ffffff !important;
        border-left: 4px solid #ffffff !important;
        border-radius: 10px !important;

        padding: 14px 18px !important;

        margin-bottom: 12px !important;

        width: 100% !important;

        box-sizing: border-box !important;
    }


    .source-title {
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: 600 !important;
    }


    .source-page {
        color: #ffffff !important;
        font-size: 13px !important;
        margin-top: 5px !important;
    }


    /* ======================================================
       ALERTS
       ====================================================== */

    [data-testid="stAlert"] {
        background-color: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }


    [data-testid="stAlert"] * {
        color: #ffffff !important;
    }


    /* ======================================================
       DISCLAIMER
       ====================================================== */

    .disclaimer {
        font-size: 12px;
        color: #ffffff !important;
        text-align: center;
        margin-top: 25px;
    }


    /* ======================================================
       FOOTER
       ====================================================== */

    .footer {
        text-align: center;
        color: #ffffff !important;
        font-size: 13px;
        margin-top: 45px;
        margin-bottom: 20px;
    }


    /* ======================================================
       MOBILE
       ====================================================== */

    @media (max-width: 768px) {

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1.5rem;
        }


        .main-title {
            font-size: 38px;
        }


        .subtitle {
            font-size: 16px;
        }


        .answer-box {
            font-size: 15px;
            padding: 18px;
        }


        .source-box {
            padding: 13px 15px !important;
        }


        .source-title {
            font-size: 14px !important;
        }


        .source-page {
            font-size: 12px !important;
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


    st.subheader(
        "Example Questions"
    )


    examples = [
        "How to register an FIR in Pakistan?",

        "What can a tenant do if a landlord tries to evict them illegally?",

        "What can an employee do if their employer does not pay their salary?",

        "How can a person correct an error in their NADRA record?",

        "What should I do if someone threatens me online?",

        "What is the legal procedure for obtaining Khula in Pakistan?",

        "What legal protection is available against domestic violence?",

        "What legal action can be taken if a cheque is dishonoured?",

        "What legal action can be taken in case of property fraud?",

        "What should I do after receiving a traffic challan?"
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
        "its local Pakistani legal knowledge base."
    )


# ============================================================
# BUILD / LOAD RAG DATABASE
# ============================================================

try:

    collection = build_database()

except Exception as error:

    st.error(
        "Knowledge base load nahi ho saki."
    )

    st.code(
        str(error)
    )

    st.stop()


# ============================================================
# QUESTION AREA
# ============================================================

st.subheader(
    "Ask Your Legal Question"
)


question = st.text_area(
    "Enter your question",

    value=st.session_state.question,

    height=140,

    placeholder=(
        "Example: How to register an FIR in Pakistan?"
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
# ASK / RAG PROCESS
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
                "Legal knowledge base search mein "
                "error aa gaya."
            )

            st.code(
                str(error)
            )

            st.stop()


    documents = results.get(
        "documents",
        [[]]
    )[0]


    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]


    # --------------------------------------------------------
    # NO RELEVANT DOCUMENTS
    # --------------------------------------------------------

    if not documents:

        st.session_state.answer = (
            "The available legal knowledge base "
            "does not contain enough information "
            "to answer this question accurately."
        )

        st.session_state.sources = []

        st.session_state.show_sources = False

        st.warning(
            "Relevant information knowledge base "
            "mein nahi mili."
        )

        st.stop()


    # ========================================================
    # CREATE RAG CONTEXT
    # ========================================================

    context_parts = []


    for index, document in enumerate(
        documents
    ):

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


    context = "\n\n".join(
        context_parts
    )


    # ========================================================
    # LANGUAGE INSTRUCTION
    # ========================================================

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


    # ========================================================
    # EXPLANATION LEVEL
    # ========================================================

    if explanation_level == "Beginner":

        level_instruction = """
Use very simple language.

Avoid unnecessary legal terminology.

Use short paragraphs.

Use simple bullet points where useful.

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


    # ========================================================
    # SYSTEM PROMPT
    # ========================================================

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

2. Do NOT use outside legal information.

3. Do NOT invent laws.

4. Do NOT invent section numbers.

5. Do NOT invent penalties.

6. Do NOT invent deadlines.

7. Do NOT invent fees.

8. Do NOT invent government procedures.

9. Do NOT invent case citations.

10. If the knowledge base does not contain
enough information, clearly say:

"The available legal knowledge base does not
contain enough information to answer this
question accurately."

11. Never pretend to be a lawyer.

12. Give general legal information only.

13. Suggest consulting a qualified lawyer
or relevant government authority when appropriate.

14. Keep the answer directly related
to the user's question.

15. Do NOT use Markdown bold formatting.

16. Do NOT use ** symbols.

17. Do NOT create a Sources section.

18. Do NOT list source filenames
inside the answer.

19. Sources are displayed separately
by the application.

20. Keep the final answer clean and simple.

21. Do not mention irrelevant documents.

22. Do not make assumptions outside
the provided legal information.

{language_instruction}

{level_instruction}
"""


    # ========================================================
    # USER PROMPT
    # ========================================================

    user_prompt = f"""
LEGAL KNOWLEDGE BASE:

{context}


USER QUESTION:

{question}


Answer the user's question using ONLY
the legal knowledge base above.

Do not use outside legal information.

Do not make assumptions.

Do not invent information.

Do not use Markdown bold formatting.

Do not use ** symbols.

Do not create a Sources section.

Do not list source filenames.

Keep the answer clean and easy to read.

If the retrieved information is insufficient,
say so clearly.
"""


    # ========================================================
    # GROQ API KEY
    # ========================================================

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


    # ========================================================
    # GROQ CLIENT
    # ========================================================

    client = OpenAI(
        api_key=groq_api_key,

        base_url=(
            "https://api.groq.com/openai/v1"
        )
    )


    # ========================================================
    # GENERATE ANSWER
    # ========================================================

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
                "Groq API se answer generate "
                "nahi ho saka."
            )

            st.code(
                str(error)
            )

            st.stop()


    # ========================================================
    # CLEAN ANSWER
    # ========================================================

    answer = answer.replace(
        "**",
        ""
    )

    answer = answer.replace(
        "### ",
        ""
    )

    answer = answer.replace(
        "## ",
        ""
    )

    answer = answer.replace(
        "# ",
        ""
    )

    answer = answer.strip()


    st.session_state.answer = answer


    # ========================================================
    # COLLECT SOURCES
    # ========================================================

    unique_sources = []


    for metadata in metadatas:

        source = metadata.get(
            "source",
            "Unknown"
        )


        source = str(
            source
        ).strip()


        if (
            source
            and source != "Unknown"
            and source not in unique_sources
        ):

            unique_sources.append(
                source
            )


    st.session_state.sources = (
        unique_sources
    )


    st.session_state.show_sources = False


# ============================================================
# DISPLAY ANSWER
# ============================================================

if st.session_state.answer:

    st.subheader(
        "INSAFBOT Answer"
    )


    answer = st.session_state.answer


    answer = answer.replace(
        "**",
        ""
    )

    answer = answer.replace(
        "### ",
        ""
    )

    answer = answer.replace(
        "## ",
        ""
    )

    answer = answer.replace(
        "# ",
        ""
    )

    answer = answer.strip()


    # --------------------------------------------------------
    # IMPORTANT:
    # Answer is displayed using native Streamlit markdown.
    # No source HTML is involved here.
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="answer-box">
            {answer}
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # LEGAL RESOURCES BUTTON
    # ========================================================

    if st.button(
        "Legal Resources",
        use_container_width=True
    ):

        st.session_state.show_sources = (
            not st.session_state.show_sources
        )


    # ========================================================
    # SOURCE DISPLAY
    # ========================================================

    if st.session_state.show_sources:

        st.markdown(
            '<div class="sources-title">Sources</div>',
            unsafe_allow_html=True
        )


        if not st.session_state.sources:

            st.info(
                "No sources available."
            )


        else:

            for source in (
                st.session_state.sources
            ):

                clean_source = str(
                    source
                ).strip()


                # ==================================================
                # IMPORTANT FIX:
                #
                # We DO NOT create:
                #
                # <div class="source-name">
                #
                # or:
                #
                # <div class="source-page">
                #
                # Therefore those HTML tags can never
                # appear as source text.
                # ==================================================


                st.markdown(
                    f"""
                    <div class="source-box">

                        <div class="source-title">
                            {clean_source}
                        </div>

                        <div class="source-page">
                            Page: N/A
                        </div>

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
