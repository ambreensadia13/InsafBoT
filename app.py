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

    /* -------------------------------------------------------
       GLOBAL
    ------------------------------------------------------- */

    .stApp {
        background: #07111f;
        color: #ffffff;
    }

    html, body, [class*="css"] {
        font-family: Arial, sans-serif;
    }

    /* -------------------------------------------------------
       HEADER
    ------------------------------------------------------- */

    .main-title {
        text-align: center;
        color: #ffffff;
        font-size: 42px;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #ffffff;
        font-size: 16px;
        margin-bottom: 25px;
    }

    /* -------------------------------------------------------
       SIDEBAR
    ------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background: #0b1b31;
        border-right: 1px solid #ffffff;
    }

    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* -------------------------------------------------------
       TEXT INPUT
    ------------------------------------------------------- */

    textarea {
        background: #0b1b31 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        border-radius: 10px !important;
    }

    textarea::placeholder {
        color: #ffffff !important;
        opacity: 0.7;
    }

    /* -------------------------------------------------------
       BUTTONS
    ------------------------------------------------------- */

    .stButton > button {
        width: 100%;
        background: #0b1b31 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
        border-radius: 9px !important;
        font-weight: 600;
    }

    .stButton > button:hover {
        background: #142b48 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }

    /* -------------------------------------------------------
       SELECTBOX
    ------------------------------------------------------- */

    div[data-baseweb="select"] > div {
        background: #0b1b31 !important;
        color: #ffffff !important;
        border: 1px solid #ffffff !important;
    }

    div[data-baseweb="select"] * {
        color: #ffffff !important;
    }

    /* -------------------------------------------------------
       SOURCE BOXES
       Native Streamlit containers are used.
       No HTML source cards are generated.
    ------------------------------------------------------- */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #0b1b31 !important;
        border: 1px solid #ffffff !important;
        border-radius: 10px !important;
        margin-bottom: 10px;
    }

    /* -------------------------------------------------------
       GENERAL TEXT
    ------------------------------------------------------- */

    .stMarkdown,
    .stMarkdown p,
    .stMarkdown li,
    label {
        color: #ffffff !important;
    }

    /* -------------------------------------------------------
       RESPONSE BOX
    ------------------------------------------------------- */

    .answer-box {
        background: #0b1b31;
        border: 1px solid #ffffff;
        border-radius: 10px;
        padding: 18px;
        color: #ffffff;
        line-height: 1.7;
        margin-top: 10px;
    }

    /* -------------------------------------------------------
       MOBILE
    ------------------------------------------------------- */

    @media (max-width: 768px) {

        .main-title {
            font-size: 30px;
        }

        .subtitle {
            font-size: 14px;
        }

        .answer-box {
            padding: 14px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
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
# SESSION STATE
# ============================================================

if "database" not in st.session_state:
    st.session_state.database = None

if "answer" not in st.session_state:
    st.session_state.answer = ""

if "sources" not in st.session_state:
    st.session_state.sources = []

if "show_resources" not in st.session_state:
    st.session_state.show_resources = False


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ⚙️ Settings")

    jurisdiction = st.selectbox(
        "Jurisdiction",
        [
            "Pakistan"
        ]
    )

    explanation_level = st.selectbox(
        "Explanation Level",
        [
            "Simple",
            "Detailed"
        ]
    )

    language = st.selectbox(
        "Answer Language",
        [
            "English",
            "Roman Urdu",
            "Urdu"
        ]
    )

    st.markdown("---")

    st.markdown("## ⚖️ Legal Resources")

    if st.button(
        "Show Legal Resources",
        use_container_width=True
    ):
        st.session_state.show_resources = (
            not st.session_state.show_resources
        )


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

st.markdown("### 💡 Example Questions")

example_questions = [
    "What is an FIR and under which law is it registered?",
    "What is the punishment for theft in Pakistan?",
    "What are the legal grounds for divorce or khula?",
    "What are the rights of a tenant in Pakistan?",
    "What is cybercrime under Pakistani law?",
    "What are the legal rights of women regarding inheritance?",
    "What does Pakistani law say about domestic violence?",
    "What are the legal requirements for a valid Nikah?",
    "What are the legal rules regarding maintenance after divorce?",
    "What does Pakistani law say about wills and inheritance?"
]


cols = st.columns(2)

for index, question in enumerate(example_questions):

    with cols[index % 2]:

        if st.button(
            question,
            key=f"example_{index}",
            use_container_width=True
        ):
            st.session_state.selected_question = question


# ============================================================
# QUESTION
# ============================================================

selected_question = st.session_state.get(
    "selected_question",
    ""
)

question = st.text_area(
    "Ask your legal question",
    value=selected_question,
    height=120,
    placeholder=(
        "Example: What are the legal requirements "
        "for a valid Nikah in Pakistan?"
    )
)


# ============================================================
# ASK BUTTON
# ============================================================

ask = st.button(
    "⚖️ Ask INSAFBOT",
    use_container_width=True
)


# ============================================================
# DATABASE
# ============================================================

if st.session_state.database is None:

    with st.spinner(
        "Loading legal knowledge base..."
    ):

        try:

            st.session_state.database = build_database()

        except Exception as e:

            st.error(
                f"Could not load the legal knowledge base: {e}"
            )

            st.stop()


# ============================================================
# GROQ CLIENT
# ============================================================

def get_groq_client():

    try:

        api_key = st.secrets["GROQ_API_KEY"]

    except Exception:

        st.error(
            "GROQ_API_KEY is missing from Streamlit Secrets."
        )

        st.stop()

    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )


# ============================================================
# CLEAN AI ANSWER
# ============================================================

def clean_answer(answer):

    if not answer:
        return ""

    answer = answer.strip()

    # Remove markdown bold
    answer = answer.replace("**", "")

    # Remove markdown italic
    answer = answer.replace("__", "")

    # Remove accidental code fences
    answer = answer.replace("```text", "")
    answer = answer.replace("```", "")

    # Remove HTML tags if model accidentally produces them
    answer = re.sub(
        r"<[^>]+>",
        "",
        answer
    )

    # Clean excessive blank lines
    answer = re.sub(
        r"\n{3,}",
        "\n\n",
        answer
    )

    return answer.strip()


# ============================================================
# ASK QUESTION
# ============================================================

if ask:

    if not question.strip():

        st.warning(
            "Please enter a legal question first."
        )

        st.stop()

    # --------------------------------------------------------
    # Search knowledge base
    # --------------------------------------------------------

    with st.spinner(
        "Searching Pakistani legal documents..."
    ):

        try:

            results = search_laws(
                st.session_state.database,
                question,
                top_k=5
            )

        except Exception as e:

            st.error(
                f"Search failed: {e}"
            )

            st.stop()

    # --------------------------------------------------------
    # No relevant source
    # --------------------------------------------------------

    if not results:

        st.session_state.answer = (
            "I could not find sufficiently relevant "
            "information in the INSAFBOT legal knowledge base "
            "to answer this question."
        )

        st.session_state.sources = []

    else:

        # ----------------------------------------------------
        # Prepare context
        # ----------------------------------------------------

        context_parts = []

        for index, result in enumerate(results, start=1):

            context_parts.append(
                f"""
SOURCE {index}
FILE: {result["source"]}
LAW REFERENCE: {result["law_reference"]}

TEXT:
{result["text"]}
"""
            )

        context = "\n\n".join(
            context_parts
        )

        # ----------------------------------------------------
        # Prompt
        # ----------------------------------------------------

        if language == "Roman Urdu":

            language_instruction = """
Answer in clear Roman Urdu.
Use simple Roman Urdu that a Pakistani user can understand.
Keep official legal names, Act names, Section numbers,
Article numbers and Rule numbers in English.
"""

        elif language == "Urdu":

            language_instruction = """
Answer in Urdu.
Keep official legal names, Act names, Section numbers,
Article numbers and Rule numbers in English where appropriate.
"""

        else:

            language_instruction = """
Answer in clear and simple English.
Keep official legal names, Act names, Section numbers,
Article numbers and Rule numbers accurate.
"""

        if explanation_level == "Simple":

            explanation_instruction = """
Give a simple explanation suitable for a general user.
Avoid unnecessary legal jargon.
"""

        else:

            explanation_instruction = """
Give a detailed explanation while remaining easy to understand.
"""

        system_prompt = f"""
You are INSAFBOT, a Pakistani legal information assistant.

Jurisdiction:
{jurisdiction}

Your answers MUST be based only on the supplied legal
knowledge-base sources.

{language_instruction}

{explanation_instruction}

IMPORTANT RULES:

1. Do not invent laws, sections, articles, rules or cases.

2. Do not use outside legal knowledge when it is not present
   in the supplied sources.

3. If the sources do not contain enough information,
   clearly say that the information was not found in the
   INSAFBOT knowledge base.

4. Give the exact legal reference when it appears in the source.

5. Do not mention source filenames inside the main answer
   unless necessary.

6. Do not create a Sources section yourself.
   The application will display sources separately.

7. Do not use markdown bold formatting.

8. Do not output HTML.

9. Keep the answer clear and structured.
"""

        user_prompt = f"""
LEGAL KNOWLEDGE BASE:

{context}

USER QUESTION:

{question}

Answer the user's question using ONLY the supplied
knowledge-base content.
"""

        # ----------------------------------------------------
        # Groq
        # ----------------------------------------------------

        with st.spinner(
            "Preparing legal answer..."
        ):

            try:

                client = get_groq_client()

                response = client.responses.create(
                    model="openai/gpt-oss-120b",
                    reasoning={
                        "effort": "medium"
                    },
                    input=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ]
                )

                answer = response.output_text

                answer = clean_answer(
                    answer
                )

                st.session_state.answer = answer

                # ------------------------------------------------
                # Save only actual retrieved sources
                # ------------------------------------------------

                source_list = []

                seen_sources = set()

                for result in results:

                    source = str(
                        result.get(
                            "source",
                            ""
                        )
                    ).strip()

                    law = str(
                        result.get(
                            "law_reference",
                            "Not specified in source document"
                        )
                    ).strip()

                    if not source:
                        continue

                    source_key = (
                        source.lower(),
                        law.lower()
                    )

                    if source_key in seen_sources:
                        continue

                    seen_sources.add(
                        source_key
                    )

                    source_list.append({
                        "source": source,
                        "law": law
                    })

                st.session_state.sources = source_list

            except Exception as e:

                st.session_state.answer = ""

                st.error(
                    f"Groq API error: {e}"
                )


# ============================================================
# ANSWER
# ============================================================

if st.session_state.answer:

    st.markdown("### ⚖️ Answer")

    st.markdown(
        f"""
        <div class="answer-box">
        {st.session_state.answer.replace(chr(10), "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# SOURCES
# ============================================================

if st.session_state.sources:

    st.markdown("### 📚 Sources")

    for source_item in st.session_state.sources:

        source_name = source_item["source"]
        law_reference = source_item["law"]

        # ----------------------------------------------------
        # IMPORTANT:
        # Native Streamlit container is intentionally used.
        # No HTML is generated here.
        # ----------------------------------------------------

        with st.container(border=True):

            st.markdown(
                f"**Source:** `{source_name}`"
            )

            st.markdown(
                f"**Exact law:** {law_reference}"
            )


# ============================================================
# LEGAL RESOURCES
# ============================================================

if st.session_state.show_resources:

    st.markdown("### ⚖️ Legal Resources")

    resources = [
        "Pakistan Penal Code",
        "Code of Criminal Procedure",
        "Code of Civil Procedure",
        "Constitution of Pakistan",
        "Family Laws",
        "Cybercrime Laws",
        "Women and Child Protection Laws",
        "Inheritance and Property Laws"
    ]

    for resource in resources:

        with st.container(border=True):

            st.markdown(
                resource
            )


# ============================================================
# DISCLAIMER
# ============================================================

st.markdown("---")

st.caption(
    "INSAFBOT provides general legal information based on "
    "its local knowledge base. It is not a substitute for "
    "professional legal advice."
)
