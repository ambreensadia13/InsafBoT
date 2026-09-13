```css
/* ========================================================
   STRICT TWO-COLOUR DESIGN
   DARK BLUE BOXES + WHITE TEXT
   ======================================================== */

:root {
    --dark-blue: #0f172a;
    --white: #ffffff;
}


/* ========================================================
   SIDEBAR
   ======================================================== */

section[data-testid="stSidebar"] {
    background: #0f172a !important;
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}


/* ========================================================
   SETTINGS SELECTBOXES
   ======================================================== */

section[data-testid="stSidebar"]
div[data-baseweb="select"] > div {

    background: #0f172a !important;

    color: #ffffff !important;

    border: 1px solid #ffffff !important;

    border-radius: 8px !important;

    box-shadow: none !important;
}


/* Selectbox text */

section[data-testid="stSidebar"]
div[data-baseweb="select"] span {

    color: #ffffff !important;
}


/* Selectbox arrow */

section[data-testid="stSidebar"]
div[data-baseweb="select"] svg {

    fill: #ffffff !important;

    color: #ffffff !important;
}


/* ========================================================
   DROPDOWN MENU
   ======================================================== */

div[data-baseweb="popover"] {

    background: #0f172a !important;

    color: #ffffff !important;
}

div[data-baseweb="popover"] > div {

    background: #0f172a !important;
}

div[data-baseweb="popover"] ul {

    background: #0f172a !important;
}

div[data-baseweb="popover"] li {

    background: #0f172a !important;

    color: #ffffff !important;
}

div[data-baseweb="popover"] li span {

    color: #ffffff !important;
}

div[data-baseweb="popover"] li:hover {

    background: #0f172a !important;

    color: #ffffff !important;
}


/* ========================================================
   EXAMPLE QUESTIONS
   ======================================================== */

section[data-testid="stSidebar"]
button {

    background: #0f172a !important;

    color: #ffffff !important;

    border: 1px solid #ffffff !important;

    border-radius: 8px !important;

    box-shadow: none !important;
}

section[data-testid="stSidebar"]
button p {

    color: #ffffff !important;
}


/* ========================================================
   LEGAL RESOURCES BUTTON
   ======================================================== */

div[data-testid="stButton"]
button {

    background: #0f172a !important;

    color: #ffffff !important;

    border: 1px solid #ffffff !important;

    border-radius: 8px !important;

    box-shadow: none !important;
}

div[data-testid="stButton"]
button p {

    color: #ffffff !important;
}


/* ========================================================
   SOURCE BOXES
   ======================================================== */

.source-card {

    background: #0f172a !important;

    color: #ffffff !important;

    border: 1px solid #ffffff !important;

    border-left: 4px solid #ffffff !important;

    border-radius: 8px !important;

    padding: 12px 15px !important;

    margin-bottom: 8px !important;

    box-shadow: none !important;
}

.source-card * {

    color: #ffffff !important;
}

.source-card strong {

    color: #ffffff !important;

    font-weight: 600;
}


/* ========================================================
   MOBILE
   EXACT SAME COLOURS
   ======================================================== */

@media (max-width: 768px) {

    section[data-testid="stSidebar"] {
        background: #0f172a !important;
    }

    section[data-testid="stSidebar"]
    div[data-baseweb="select"] > div {

        background: #0f172a !important;

        color: #ffffff !important;

        border: 1px solid #ffffff !important;
    }

    section[data-testid="stSidebar"]
    div[data-baseweb="select"] span {

        color: #ffffff !important;
    }

    section[data-testid="stSidebar"]
    div[data-baseweb="select"] svg {

        fill: #ffffff !important;
    }

    section[data-testid="stSidebar"] button {

        background: #0f172a !important;

        color: #ffffff !important;

        border: 1px solid #ffffff !important;
    }

    section[data-testid="stSidebar"] button p {

        color: #ffffff !important;
    }

    div[data-testid="stButton"] button {

        background: #0f172a !important;

        color: #ffffff !important;

        border: 1px solid #ffffff !important;
    }

    div[data-testid="stButton"] button p {

        color: #ffffff !important;
    }

    .source-card {

        background: #0f172a !important;

        color: #ffffff !important;

        border: 1px solid #ffffff !important;

        border-left: 4px solid #ffffff !important;
    }

    .source-card * {

        color: #ffffff !important;
    }
}
```
