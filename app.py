from __future__ import annotations

from pathlib import Path
from html import escape

import streamlit as st
from dotenv import load_dotenv

from src.ai import generate_grounded_reflection
from src.retrieval import detect_crisis, load_content, retrieve_content


ROOT = Path(__file__).parent
CONTENT_PATH = ROOT / "data" / "content_seed.json"
FEELING_CHIPS = [
    "anxious",
    "exhausted",
    "grateful",
    "lonely",
    "hope",
    "guilt",
    "fear",
    "sad",
    "angry",
]


st.set_page_config(
    page_title="Quran & Sunnah Reflection",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_dotenv()


@st.cache_data
def get_content() -> list[dict]:
    return load_content(CONTENT_PATH)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 12% 8%, rgba(47,111,94,.13), transparent 28%),
                linear-gradient(135deg, #f7f5ef 0%, #eef4f0 45%, #f8f2e9 100%);
        }
        .block-container {
            padding-top: 2rem;
            max-width: 1180px;
        }
        .hero {
            padding: 1.2rem 0 1rem;
        }
        .hero h1 {
            font-size: 2.55rem;
            line-height: 1.08;
            margin-bottom: .5rem;
            color: #17231f;
            letter-spacing: 0;
        }
        .hero p {
            max-width: 760px;
            color: #47564f;
            font-size: 1.05rem;
        }
        .notice {
            border-left: 4px solid #b7791f;
            background: #fff8ea;
            padding: .85rem 1rem;
            border-radius: 8px;
            color: #4f3b16;
            margin: .8rem 0 1.2rem;
        }
        .result-card {
            background: rgba(255,255,255,.92);
            border: 1px solid rgba(39,79,67,.16);
            border-radius: 8px;
            padding: 1.05rem 1.05rem .9rem;
            margin-bottom: .85rem;
            box-shadow: 0 8px 22px rgba(34,49,43,.07);
        }
        .badge {
            display: inline-block;
            font-size: .75rem;
            font-weight: 700;
            color: #214e42;
            background: #e4f1ec;
            border: 1px solid #c7ded5;
            border-radius: 999px;
            padding: .18rem .55rem;
            margin-right: .35rem;
            margin-bottom: .45rem;
        }
        .arabic {
            direction: rtl;
            text-align: right;
            font-size: 1.55rem;
            line-height: 2.2;
            color: #152d26;
            margin: .25rem 0 .65rem;
        }
        .english {
            font-size: 1rem;
            color: #27332f;
            line-height: 1.65;
        }
        .reflection {
            color: #526159;
            border-top: 1px solid #edf1ee;
            margin-top: .8rem;
            padding-top: .7rem;
        }
        .source-link a {
            color: #2f6f5e;
            text-decoration: none;
            font-weight: 700;
        }
        div[data-testid="stTextArea"] textarea {
            border-radius: 8px;
            min-height: 165px;
        }
        .stButton button {
            border-radius: 8px;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_card(item: dict) -> None:
    type_label = item["type"].title()
    parts = [
        '<div class="result-card">',
        f'<span class="badge">{escape(type_label)}</span>',
        f'<span class="badge">{escape(item["reference"])}</span>',
        f'<span class="badge">{escape(item["authenticity"])}</span>',
    ]
    if item.get("arabic_text"):
        parts.append(f'<div class="arabic">{escape(item["arabic_text"])}</div>')
    parts.extend(
        [
            f'<div class="english">{escape(item["english_text"])}</div>',
            f'<div class="reflection">{escape(item["reflection_note"])}</div>',
            (
                '<div class="source-link" style="margin-top:.6rem;">'
                f'<a href="{escape(item["source_url"], quote=True)}" target="_blank">Open source reference</a>'
                "</div>"
            ),
            "</div>",
        ]
    )
    st.markdown("".join(parts), unsafe_allow_html=True)


def copy_text(items: list[dict], reflection: str) -> str:
    lines = [reflection, ""]
    for item in items:
        lines.extend(
            [
                f"{item['type'].title()} - {item['reference']} ({item['authenticity']})",
                item.get("arabic_text", ""),
                item["english_text"],
                item["source_url"],
                "",
            ]
        )
    return "\n".join(line for line in lines if line is not None)


inject_css()
content = get_content()

st.markdown(
    """
    <div class="hero">
        <h1>Quran & Sunnah Reflection</h1>
        <p>Share what you are feeling and receive grounded reminders from the Quran, authentic hadith, and selected Seerah lessons with clear references.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Grounding")
    st.write("The app uses local reviewed citations first. API keys are optional for later enrichment.")
    st.caption("This is spiritual support, not medical care, therapy, or a fatwa service.")
    per_type = st.slider("Results per source", min_value=1, max_value=3, value=2)

left, right = st.columns([1.04, 0.96], gap="large")

with left:
    user_text = st.text_area(
        "What are you feeling today?",
        placeholder="Example: I feel anxious about the future and emotionally exhausted...",
        label_visibility="visible",
    )
    selected = st.multiselect("Feeling chips", FEELING_CHIPS, placeholder="Add quick feelings")
    reflect = st.button("Reflect", type="primary", use_container_width=True)

    st.markdown(
        """
        <div class="notice">
        If you might hurt yourself or someone else, please contact local emergency services now and reach out to a trusted person nearby. You still deserve care and help in this moment.
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.subheader("How it works")
    st.write(
        "The prototype detects themes, retrieves matching citations, and writes a short grounded reflection from those citations only."
    )
    st.write("It will still work offline with the curated seed library.")

if reflect:
    if not user_text.strip() and not selected:
        st.warning("Write a few words or choose a feeling chip to begin.")
        st.stop()

    themes, results = retrieve_content(user_text, content, selected, per_type=per_type)
    crisis = detect_crisis(user_text)
    reflection = generate_grounded_reflection(user_text, themes, results, crisis=crisis)

    st.divider()
    st.subheader("Reflection")
    if crisis:
        st.error(
            "Your words may point to immediate danger or severe distress. Please contact local emergency services now if you may act on these thoughts, and reach a trusted person, imam, family member, or friend who can stay with you."
        )
    st.info(reflection)
    st.caption("Detected themes: " + ", ".join(themes))

    grouped = {
        "Quran": [item for item in results if item["type"] == "quran"],
        "Hadith": [item for item in results if item["type"] == "hadith"],
        "Seerah": [item for item in results if item["type"] == "seerah"],
    }

    tabs = st.tabs(list(grouped.keys()))
    for tab, (group_name, items) in zip(tabs, grouped.items()):
        with tab:
            if not items:
                st.write(f"No {group_name.lower()} result matched this input yet.")
            for item in items:
                render_card(item)

    st.download_button(
        "Download reflection",
        data=copy_text(results, reflection),
        file_name="quran_sunnah_reflection.txt",
        mime="text/plain",
    )
else:
    st.divider()
    st.subheader("Try one")
    sample_cols = st.columns(3)
    examples = [
        ("Anxious", "I feel anxious about the future and cannot calm my heart."),
        ("Grateful", "I feel happy and grateful for what Allah has given me."),
        ("Lonely", "I feel lonely and forgotten, like nobody understands me."),
    ]
    for col, (label, text) in zip(sample_cols, examples):
        with col:
            st.code(text, language=None)
