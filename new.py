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
    layout="wide",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>


html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"] {
    background-color: #0f172a !important;
}

* {
    box-sizing: border-box;
}

.main .block-container {
    max-width: 1200px !important;
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background-color: #0b1120 !important;
    border-right: 1px solid #1e293b !important;
}

section[data-testid="stSidebar"] > div {
    background-color: #0b1120 !important;
}

.sidebar-title {
    color: #f8fafc !important;
    font-size: 1.55rem !important;
    font-weight: 800 !important;
    margin-bottom: 0.2rem !important;
}

.sidebar-subtitle {
    color: #94a3b8 !important;
    font-size: 0.88rem !important;
    margin-bottom: 1.5rem !important;
}

/* SIDEBAR SELECTBOX */

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    background-color: #111827 !important;
    color: #f8fafc !important;
    border: 1px solid #38bdf8 !important;
    border-radius: 10px !important;
    min-height: 44px !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] * {
    color: #f8fafc !important;
}

section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    color: #38bdf8 !important;
    fill: #38bdf8 !important;
}

div[data-baseweb="popover"] {
    background-color: #111827 !important;
}

div[data-baseweb="popover"] ul {
    background-color: #111827 !important;
    border: 1px solid #38bdf8 !important;
    border-radius: 10px !important;
}

div[data-baseweb="popover"] li {
    background-color: #111827 !important;
    color: #f8fafc !important;
}

div[data-baseweb="popover"] li:hover,
div[data-baseweb="popover"] li[aria-selected="true"] {
    background-color: #075985 !important;
    color: #ffffff !important;
}

/* MAIN TITLE */

.main-title {
    width: 100%;
    text-align: center;
    margin: 0 0 0.8rem 0;
    padding: 0.3rem 0.5rem;
    overflow: visible !important;
}

.main-title span {
    display: inline-block !important;
    width: auto !important;
    max-width: 100% !important;
    padding: 0 0.1em !important;
    white-space: nowrap !important;
    overflow: visible !important;

    font-size: clamp(2.4rem, 7vw, 5.5rem) !important;
    line-height: 1.15 !important;
    font-weight: 900 !important;
    letter-spacing: 0.04em !important;

    background: linear-gradient(
        90deg,
        #38bdf8,
        #8b5cf6
    ) !important;

    -webkit-background-clip: text !important;
    background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    color: transparent !important;
}

.subtitle {
    text-align: center;
    color: #cbd5e1 !important;
    font-size: 1.05rem !important;
    margin-bottom: 1.8rem !important;
}

/* SECTION TITLE */

.section-title {
    color: #f8fafc !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    margin-top: 1rem !important;
    margin-bottom: 0.7rem !important;
}

/* TEXT AREA */

textarea {
    background-color: #111827 !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    font-size: 1rem !important;
    line-height: 1.6 !important;
}

textarea:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 1px #38bdf8 !important;
}

textarea::placeholder {
    color: #64748b !important;
}

/* MAIN BUTTON */

.main .stButton > button {
    width: 100% !important;
    min-height: 48px !important;
    border: none !important;
    border-radius: 12px !important;

    background: linear-gradient(
        90deg,
        #0284c7,
        #7c3aed
    ) !important;

    color: #ffffff !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}

.main .stButton > button:hover {
    opacity: 0.92 !important;
}

.main .stButton > button p {
    color: #ffffff !important;
}

/* SIDEBAR EXAMPLE BUTTONS */

section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    min-height: 42px !important;

    background-color: #111827 !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;

    color: #cbd5e1 !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;

    text-align: left !important;
    padding: 0.4rem 0.7rem !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #075985 !important;
    border-color: #38bdf8 !important;
    color: #ffffff !important;
}

section[data-testid="stSidebar"] .stButton > button p {
    color: inherit !important;
}

/* ANSWER */

.answer-card {
    width: 100% !important;
    background-color: #ffffff !important;
    color: #111827 !important;

    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;

    padding: 1.5rem !important;
    margin-top: 1.2rem !important;
    margin-bottom: 1rem !important;

    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25) !important;

    font-size: 1rem !important;
    line-height: 1.75 !important;

    overflow-wrap: anywhere !important;
}

/* SOURCES */

.source-card {
    background-color: #111827 !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;

    padding: 0.8rem 1rem !important;
    margin-bottom: 0.5rem !important;

    color: #cbd5e1 !important;
    font-size: 0.9rem !important;

    overflow-wrap: anywhere !important;
}

/* INFORMATION */

.info-card {
    background-color: #111827 !important;
    border: 1px solid #334155 !important;
    border-radius: 14px !important;

    padding: 1.2rem !important;
    margin-top: 1.5rem !important;

    color: #cbd5e1 !important;
    line-height: 1.6 !important;
}

.info-card strong {
    color: #38bdf8 !important;
}

/* FOOTER */

.footer {
    text-align: center !important;
    color: #64748b !important;
    font-size: 0.82rem !important;

    margin-top: 2rem !important;
    padding-top: 1rem !important;

    border-top: 1px solid #1e293b !important;
}

/* MOBILE */

@media (max-width: 768px) {

    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 1rem !important;
    }

    .main-title {
        margin-top: 0.3rem !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    .main-title span {
        font-size: clamp(2rem, 14vw, 4rem) !important;
        letter-spacing: 0.02em !important;
    }

    .subtitle {
        font-size: 0.92rem !important;
    }

    .answer-card {
        padding: 1rem !important;
        font-size: 0.95rem !important;
    }
}

@media (max-width: 420px) {

    .main-title span {
        font-size: 2rem !important;
        letter-spacing: 0 !important;
    }

    .subtitle {
        font-size: 0.85rem !important;
    }
}

</style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "question" not in st.session_state:
    st.session_state.question = ""


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

EXAMPLE_QUESTIONS = [
    "How can I file an FIR in Pakistan?",
    "What are the basic rights of a tenant in Pakistan?",
    "Can a landlord evict a tenant without notice?",
    "What can I do if my salary is not paid?",
    "What are my rights if I am terminated from my job?",
    "How can a woman obtain khula in Pakistan?",
    "What is the legal procedure for talaq?",
    "What laws protect women from domestic violence?",
    "What is cybercrime and how can I report it?",
    "What happens if someone issues a dishonoured cheque?",
    "What can I do about property fraud?",
    "What is illegal qabza on property?",
    "How can I correct an error in NADRA records?",
    "What can I do if someone misuses my personal data?",
    "How can I challenge a traffic challan?",
    "What should I do if I am a victim of online fraud?",
    "What are a woman's rights in nikah?",
    "What should be included in a nikahnama?",
    "Can a woman add conditions to her nikahnama?",
    "What are the legal rights of women after marriage?",
]


# ============================================================
# API
# ============================================================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = None

if GROQ_API_KEY:
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )


# ============================================================
# KNOWLEDGE BASE
# ============================================================

@st.cache_resource
def load_knowledge_base():
    return build_database()


# ============================================================
# HELPERS
# ============================================================

def clean_answer(text):
    if not text:
        return ""

    text = str(text).strip()

    text = re.sub(
        r"^```(?:markdown|text|plaintext)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return text.strip()


def extract_documents(results):
    documents = []

    if not results:
        return documents

    for item in results:
        if isinstance(item, dict):
            text = (
                item.get("text")
                or item.get("content")
                or item.get("document")
                or item.get("page_content")
            )

            if text:
                documents.append(str(text))

        elif isinstance(item, str):
            documents.append(item)

        elif hasattr(item, "page_content"):
            text = getattr(item, "page_content", None)

            if text:
                documents.append(str(text))

        elif hasattr(item, "document"):
            text = getattr(item, "document", None)

            if text:
                documents.append(str(text))

    return documents


def extract_source_filenames(results):
    sources = []

    if not results:
        return sources

    for item in results:
        metadata = {}

        if isinstance(item, dict):
            metadata = item.get("metadata", {}) or {}

            if not metadata:
                metadata = item

        elif hasattr(item, "metadata"):
            metadata = getattr(item, "metadata", {}) or {}

        if not isinstance(metadata, dict):
            continue

        source = (
            metadata.get("source")
            or metadata.get("file")
            or metadata.get("filename")
            or metadata.get("file_name")
        )

        if source:
            source = os.path.basename(str(source))

            if source not in sources:
                sources.append(source)

    return sources


def create_system_prompt(
    jurisdiction,
    explanation_level,
    answer_language,
):
    return f"""
You are INSAFBOT, an AI legal information assistant focused on Pakistan.

Jurisdiction: {jurisdiction}

Explanation level: {explanation_level}

Answer language: {answer_language}

Rules:

1. Provide general legal information only.
2. Do not pretend to be a lawyer.
3. Do not invent laws, sections, cases, penalties, or procedures.
4. Use the supplied legal documents as the primary source.
5. If the documents do not contain enough information, say so clearly.
6. Explain the law in a clear and practical manner.
7. Mention legal sections only when supported by the supplied context.
8. Never guess an exact legal provision.
9. For serious or urgent matters, recommend consulting a qualified lawyer.
10. Do not claim to create an attorney-client relationship.
11. Answer in the selected language.
"""


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        '<div class="sidebar-title">⚖️ INSAFBOT</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Pakistan Legal Information Assistant'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-title">Settings</div>',
        unsafe_allow_html=True,
    )

    jurisdiction = st.selectbox(
        "Jurisdiction",
        [
            "Pakistan / Federal",
            "Punjab",
        ],
        index=0,
    )

    explanation_level = st.selectbox(
        "Explanation Level",
        [
            "Beginner",
            "Intermediate",
            "Expert",
        ],
        index=0,
    )

    answer_language = st.selectbox(
        "Answer Language",
        [
            "English",
            "Urdu",
            "Roman Urdu",
        ],
        index=0,
    )

    st.markdown(
        '<div class="section-title">Example Questions</div>',
        unsafe_allow_html=True,
    )

    for index, example in enumerate(EXAMPLE_QUESTIONS):
        if st.button(
            example,
            key=f"example_{index}",
            use_container_width=True,
        ):
            st.session_state.question = example
            st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title"><span>INSAFBOT</span></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'AI-powered legal information assistant for Pakistan'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# QUESTION
# ============================================================

st.markdown(
    '<div class="section-title">Ask a Legal Question</div>',
    unsafe_allow_html=True,
)

question = st.text_area(
    "Question",
    value=st.session_state.question,
    placeholder=(
        "Example: What are a woman's legal rights in nikah in Pakistan?"
    ),
    height=130,
    label_visibility="collapsed",
)

st.session_state.question = question


# ============================================================
# ASK
# ============================================================

ask = st.button(
    "⚖️ Ask INSAFBOT",
    use_container_width=True,
)


# ============================================================
# PROCESS
# ============================================================

if ask:
    question = st.session_state.question.strip()

    if not question:
        st.warning("Please enter a legal question first.")

    elif not GROQ_API_KEY:
        st.error(
            "GROQ_API_KEY is not configured. "
            "Please add GROQ_API_KEY to Streamlit Secrets."
        )

    else:
        try:
            with st.spinner(
                "Searching Pakistani legal information..."
            ):
                collection = load_knowledge_base()

                results = search_laws(
                    collection,
                    question,
                    top_k=5,
                )

                documents = extract_documents(results)
                sources = extract_source_filenames(results)

                if documents:
                    context = "\n\n---\n\n".join(documents)
                else:
                    context = (
                        "No relevant legal document content "
                        "was retrieved."
                    )

                context = context[:30000]

                system_prompt = create_system_prompt(
                    jurisdiction,
                    explanation_level,
                    answer_language,
                )

                user_prompt = f"""
LEGAL DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

Answer the user's question using the supplied legal context.

If the supplied context does not contain enough information,
do not invent an answer. Clearly explain that the available
documents do not provide enough information.
"""

                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": user_prompt,
                        },
                    ],
                    temperature=0.2,
                    max_tokens=1500,
                )

                answer = response.choices[0].message.content
                answer = clean_answer(answer)

            # ====================================================
            # ANSWER DISPLAY
            # ====================================================

            if answer:
                safe_answer = html.escape(answer)
                safe_answer = safe_answer.replace("\n", "<br>")

                st.markdown(
                    f"""
                    <div class="answer-card">
                        {safe_answer}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.warning(
                    "INSAFBOT could not generate an answer."
                )

            # ====================================================
            # SOURCES
            # ====================================================

            if sources:
                with st.expander("📚 Sources used"):
                    for source in sources:
                        safe_source = html.escape(source)

                        st.markdown(
                            f"""
                            <div class="source-card">
                                📄 {safe_source}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

        except Exception as error:
            st.error(
                "An error occurred while processing your question."
            )
            st.exception(error)


# ============================================================
# INFORMATION CARD
# ============================================================

st.markdown(
    """
    <div class="info-card">
        <strong>Important:</strong>
        INSAFBOT provides general legal information for
        educational and informational purposes. It is not
        a substitute for advice from a qualified lawyer.
        For serious or urgent legal matters, consult a
        licensed legal professional or the relevant authority.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        INSAFBOT • Pakistan Legal Information Assistant
    </div>
    """,
    unsafe_allow_html=True,
)
