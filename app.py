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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

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

    .main {
        padding-top: 1rem;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* ========================================================
       HEADER
       ======================================================== */

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
        font-size: 17px;
        margin-bottom: 35px;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background: #0b1120;
        border-right: 1px solid rgba(255,255,255,0.08);
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


    /* ========================================================
       QUESTION BOX
       ======================================================== */

    .question-title {
        color: white;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    textarea {
        background-color: #111827 !important;
        color: white !important;
        border: 1px solid rgba(56,189,248,0.35) !important;
        border-radius: 12px !important;
    }

    textarea::placeholder {
        color: #94a3b8 !important;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid rgba(56,189,248,0.4);
        background: linear-gradient(
            90deg,
            #0284c7,
            #7c3aed
        );
        color: white;
        font-weight: 700;
        min-height: 44px;
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        border-color: #38bdf8;
        transform: translateY(-1px);
    }


    /* ========================================================
       ANSWER CARD
       ======================================================== */

    .answer-card {
        background: #ffffff;
        color: #111827;
        border-radius: 16px;
        padding: 28px;
        margin-top: 25px;
        margin-bottom: 20px;
        box-shadow:
            0 10px 30px rgba(0,0,0,0.25);
        line-height: 1.7;
        font-size: 16px;
        overflow-wrap: anywhere;
    }

    .answer-heading {
        color: white;
        font-size: 22px;
        font-weight: 700;
        margin-top: 30px;
        margin-bottom: 10px;
    }


    /* ========================================================
       SOURCES
       ======================================================== */

    .sources-heading {
        color: white;
        font-size: 22px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .source-card {
        background: #111827;
        border: 1px solid rgba(56,189,248,0.25);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }

    .source-name {
        color: white !important;
        font-size: 15px;
        font-weight: 600;
        word-break: break-word;
    }


    /* ========================================================
       INFO BOX
       ======================================================== */

    .info-card {
        background: rgba(15,23,42,0.75);
        border: 1px solid rgba(148,163,184,0.15);
        border-radius: 12px;
        padding: 15px;
        color: #cbd5e1;
        font-size: 14px;
        line-height: 1.6;
        margin-top: 20px;
    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
        text-align: center;
        color: #64748b;
        font-size: 13px;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.08);
    }


    /* ========================================================
       MOBILE
       ======================================================== */

    @media (max-width: 768px) {

        .block-container {
            padding-left: 15px;
            padding-right: 15px;
        }

        .main-title {
            font-size: 34px;
        }

        .subtitle {
            font-size: 14px;
        }

        .answer-card {
            padding: 18px;
            font-size: 15px;
        }

        .source-card {
            padding: 11px 13px;
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
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">⚖️ INSAFBOT</div>',
        unsafe_allow_html=True
    )

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

    answer_language = st.selectbox(
        "Answer Language",
        [
            "English",
            "Urdu",
            "Roman Urdu"
        ]
    )

    st.markdown("---")

    st.markdown("### Example Questions")

    example_questions = [
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

    for example in example_questions:

        if st.button(
            example,
            key=f"example_{example}"
        ):
            st.session_state.question = example
            st.rerun()

    st.markdown(
        """
        <div class="info-card">
            INSAFBOT provides general legal information
            based only on the legal documents available
            in its knowledge base.
            <br><br>
            It does not replace advice from a qualified lawyer.
        </div>
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
    """
    <div class="subtitle">
        AI-Powered Legal Information Assistant for Pakistan
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# QUESTION
# ============================================================

st.markdown(
    '<div class="question-title">Ask your legal question</div>',
    unsafe_allow_html=True
)

question = st.text_area(
    "",
    value=st.session_state.question,
    height=130,
    placeholder=(
        "Example: What legal action can be taken "
        "if a tenant is illegally evicted?"
    ),
    label_visibility="collapsed"
)


# Keep latest typed question
st.session_state.question = question


# ============================================================
# ACTION BUTTONS
# ============================================================

col1, col2 = st.columns(2)

with col1:

    ask_button = st.button(
        "⚖️ Ask INSAFBOT",
        use_container_width=True
    )

with col2:

    if st.button(
        "📚 Legal Resources",
        use_container_width=True
    ):
        st.session_state.show_sources = (
            not st.session_state.show_sources
        )


# ============================================================
# LOAD KNOWLEDGE BASE
# ============================================================

@st.cache_resource
def load_knowledge_base():

    return build_database()


# ============================================================
# ASK QUESTION
# ============================================================

if ask_button:

    question = st.session_state.question.strip()

    if not question:

        st.warning(
            "Please enter a legal question first."
        )

        st.stop()


    # --------------------------------------------------------
    # LOAD DATABASE
    # --------------------------------------------------------

    with st.spinner(
        "Loading legal knowledge base..."
    ):

        try:

            collection = load_knowledge_base()

        except Exception as error:

            st.error(
                "Knowledge base load nahi ho saki."
            )

            st.code(str(error))

            st.stop()


    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    with st.spinner(
        "Searching relevant legal information..."
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


    # ========================================================
    # SAFE RESULT PARSING
    # ========================================================

    documents = []
    metadatas = []

    if isinstance(results, dict):

        raw_documents = results.get(
            "documents",
            []
        )

        raw_metadatas = results.get(
            "metadatas",
            []
        )


        # ----------------------------------------------------
        # DOCUMENTS
        # ----------------------------------------------------

        if raw_documents:

            if (
                isinstance(raw_documents, list)
                and len(raw_documents) > 0
                and isinstance(
                    raw_documents[0],
                    list
                )
            ):

                documents = raw_documents[0]

            elif isinstance(
                raw_documents,
                list
            ):

                documents = raw_documents


        # ----------------------------------------------------
        # METADATA
        # ----------------------------------------------------

        if raw_metadatas:

            if (
                isinstance(raw_metadatas, list)
                and len(raw_metadatas) > 0
                and isinstance(
                    raw_metadatas[0],
                    list
                )
            ):

                metadatas = raw_metadatas[0]

            elif isinstance(
                raw_metadatas,
                list
            ):

                metadatas = raw_metadatas


    # ========================================================
    # NO RESULTS
    # ========================================================

    if not documents:

        st.session_state.answer = (
            "The available legal knowledge base "
            "does not contain enough information "
            "to answer this question accurately."
        )

        st.session_state.sources = []

        st.session_state.show_sources = False

        st.warning(
            "Relevant information knowledge base mein nahi mili."
        )

        st.stop()


    # ========================================================
    # EXTRACT UNIQUE SOURCE FILENAMES ONLY
    # ========================================================

    unique_sources = []

    for metadata in metadatas:

        if not isinstance(metadata, dict):
            continue

        source = metadata.get(
            "source",
            ""
        )

        if not source:
            continue

        # Convert Windows paths to normal paths
        source = str(source).replace(
            "\\",
            "/"
        ).strip()

        # Get ONLY the filename
        source_filename = os.path.basename(
            source
        )

        # Remove query parameters if present
        source_filename = (
            source_filename
            .split("?")[0]
            .strip()
        )

        # Add only unique filenames
        if (
            source_filename
            and source_filename not in unique_sources
        ):

            unique_sources.append(
                source_filename
            )


    # Save only filenames
    st.session_state.sources = unique_sources

    # Hide sources after a new question
    st.session_state.show_sources = False


    # ========================================================
    # BUILD LEGAL CONTEXT
    # ========================================================

    context_parts = []

    for index, document in enumerate(
        documents
    ):

        if index < len(metadatas):

            metadata = metadatas[index]

            if not isinstance(
                metadata,
                dict
            ):

                metadata = {}

        else:

            metadata = {}


        source = str(
            metadata.get(
                "source",
                "Unknown"
            )
        ).strip()


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

    if answer_language == "English":

        language_instruction = """
Answer in clear and simple English.
"""

    elif answer_language == "Urdu":

        language_instruction = """
Answer in Urdu script.
Use clear and understandable Pakistani Urdu.
"""

    else:

        language_instruction = """
Answer in easy Roman Urdu.
Do not use Urdu script.
"""


    # ========================================================
    # EXPLANATION LEVEL
    # ========================================================

    if explanation_level == "Beginner":

        level_instruction = """
Use simple language.
Keep the answer easy to understand.
Use short paragraphs and bullets where useful.
Avoid unnecessary legal terminology.
"""

    elif explanation_level == "Intermediate":

        level_instruction = """
Give a moderately detailed explanation.
Use brief legal terminology when necessary.
Use headings or bullets where useful.
"""

    else:

        level_instruction = """
Give a detailed explanation.
Use appropriate legal terminology.
Clearly distinguish legal rules,
rights, procedures and practical steps.
"""


    # ========================================================
    # SYSTEM PROMPT
    # ========================================================

    system_prompt = f"""
You are INSAFBOT, a Pakistani legal information assistant.

Your job is to provide general legal information
using ONLY the legal information provided in the
retrieved knowledge base.

IMPORTANT RULES:

1. Answer ONLY from the provided legal knowledge base.

2. Do NOT use outside legal knowledge.

3. Do NOT invent:
   - laws
   - sections
   - penalties
   - deadlines
   - fees
   - procedures
   - case citations
   - legal authorities

4. If the retrieved information is insufficient,
   clearly say:

"The available legal knowledge base does not contain
enough information to answer this question accurately."

5. Never pretend to be a lawyer.

6. Provide general legal information only.

7. Where appropriate, advise the user to consult
   a qualified lawyer or relevant government authority.

8. Answer the user's actual question directly.

9. Do not mention irrelevant documents.

10. Do not create a Sources section inside the answer.

11. Do not mention source filenames inside the answer.

12. Do not expose internal retrieval details.

13. Avoid repetition.

14. If the retrieved legal material is conflicting,
   incomplete or insufficient, say so instead of guessing.

15. Do not use Markdown bold formatting.
   Do not use ** anywhere.

16. Do not use unnecessary Markdown heading symbols.

17. Keep the final answer clean and readable.

18. Use short paragraphs and bullet points where helpful.

JURISDICTION:
{jurisdiction}

EXPLANATION LEVEL:
{explanation_level}

{language_instruction}

{level_instruction}
"""


    # ========================================================
    # USER PROMPT
    # ========================================================

    user_prompt = f"""
Answer the following legal question.

QUESTION:
{question}

RETRIEVED LEGAL INFORMATION:
{context}

Remember:

- Use ONLY the retrieved legal information.
- Do not add outside legal information.
- Do not invent sections, penalties, deadlines,
  fees or procedures.
- Do not mention source filenames.
- Do not create a Sources section.
- Keep the answer clean and direct.
- Do not use ** formatting.

Provide the answer in the requested language.
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
            "GROQ_API_KEY Streamlit Secrets mein nahi mili."
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
        base_url="https://api.groq.com/openai/v1"
    )


    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    with st.spinner(
        "Preparing legal answer..."
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
                "AI response generate nahi ho saka."
            )

            st.code(str(error))

            st.stop()


    # ========================================================
    # CLEAN ANSWER
    # ========================================================

    answer = str(answer)

    # Remove bold Markdown
    answer = answer.replace(
        "**",
        ""
    )

    # Remove Markdown headings
    answer = re.sub(
        r"^\s*#{1,6}\s*",
        "",
        answer,
        flags=re.MULTILINE
    )

    # Remove HTML bold tags
    answer = re.sub(
        r"</?(strong|b)>",
        "",
        answer,
        flags=re.IGNORECASE
    )

    # Remove excessive blank lines
    answer = re.sub(
        r"\n{3,}",
        "\n\n",
        answer
    )

    answer = answer.strip()


    # ========================================================
    # SAVE ANSWER
    # ========================================================

    st.session_state.answer = answer


# ============================================================
# DISPLAY ANSWER
# ============================================================

if st.session_state.answer:

    st.markdown(
        '<div class="answer-heading">Legal Answer</div>',
        unsafe_allow_html=True
    )

    safe_answer = html.escape(
        st.session_state.answer
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


# ============================================================
# DISPLAY LEGAL RESOURCES
# ============================================================

if (
    st.session_state.show_sources
    and st.session_state.sources
):

    st.markdown(
        '<div class="sources-heading">Sources</div>',
        unsafe_allow_html=True
    )

    for source in st.session_state.sources:

        safe_source = html.escape(
            str(source)
        )

        st.markdown(
            f"""
            <div class="source-card">
                <div class="source-name">
                    {safe_source}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


elif (
    st.session_state.show_sources
    and not st.session_state.sources
):

    st.info(
        "No legal resources are available for this answer."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        INSAFBOT • AI-Powered Legal Information Assistant
        <br>
        General legal information only — not legal advice.
    </div>
    """,
    unsafe_allow_html=True
)
