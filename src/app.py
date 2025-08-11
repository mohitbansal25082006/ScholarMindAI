# src/app.py
"""
ScholarMindAI – final Streamlit UI
Hybrid local + Gemini research companion
"""

import streamlit as st
import os
import json
import sys
from pathlib import Path
from collections import Counter

# ----------------------------------------------------------
# 0️⃣  Ensure src/ folder is reachable
# ----------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent))

# ----------------------------------------------------------
# 1️⃣  Local modules
# ----------------------------------------------------------
from src.preprocess import process_file
from src.embeddings import embed_and_store
from src.retriever import retriever
from src.compare import load_summaries, compare_docs, find_gaps_only

# ----------------------------------------------------------
# 2️⃣  Gemini setup
# ----------------------------------------------------------
try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    HAS_GEMINI = True
except Exception:
    HAS_GEMINI = False

# ----------------------------------------------------------
# 3️⃣  Paths
# ----------------------------------------------------------
UP_DIR  = Path("data/uploads")
REPORTS = Path("data/processed")
REPORTS.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="ScholarMindAI", layout="wide")

# ----------------------------------------------------------
# 4️⃣  Sidebar
# ----------------------------------------------------------
st.sidebar.title("ScholarMindAI")
st.sidebar.markdown("Free local + Gemini tier")

# Domain-mode toggle
DOMAIN_MODE = st.sidebar.selectbox(
    "Domain Mode",
    ["Scientific", "Business", "Education"],
    help="Changes tone & depth of AI outputs",
)

# ----------------------------------------------------------
# 5️⃣  Tabs
# ----------------------------------------------------------
upload_tab, search_tab, compare_tab, lit_tab, viz_tab = st.tabs(
    ["📤 Upload", "🔍 Search", "⚖️ Compare", "📝 Literature Review", "📊 Visualize"]
)

# ----------------------------------------------------------
# 6️⃣  Helper prompts
# ----------------------------------------------------------
def lit_review_prompt(summaries: dict) -> str:
    SYSTEM = {
        "Scientific": "You are a rigorous scientist. Use technical detail.",
        "Business": "You are a market analyst. Highlight ROI & scalability.",
        "Education": "You are a friendly educator. Explain simply.",
    }
    prompt = f"""
{SYSTEM[DOMAIN_MODE]}

Write a concise literature review (≤ 400 words) in markdown based on:

{json.dumps(summaries, indent=2)}

Structure:
- **Introduction**
- **Methods**
- **Results**
- **Discussion**
"""
    if HAS_GEMINI:
        return genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt).text
    else:
        return "⚠️ Gemini key missing – review unavailable."

# ----------------------------------------------------------
# 📤 UPLOAD
# ----------------------------------------------------------
with upload_tab:
    st.header("Upload Papers")
    files = st.file_uploader(
        "PDF or TXT", type=["pdf", "txt"], accept_multiple_files=True
    )
    if st.button("Process"):
        if not files:
            st.warning("Select at least one file.")
        else:
            progress = st.progress(0)
            for idx, f in enumerate(files, 1):
                path = UP_DIR / f.name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(f.getbuffer())
                chunks = process_file(path, path.stem)
                embed_and_store(chunks)
                progress.progress(idx / len(files))
            st.success("✅ All files processed & embedded!")

# ----------------------------------------------------------
# 🔍 SEARCH
# ----------------------------------------------------------
with search_tab:
    st.header("Semantic Search")
    query = st.text_input("Ask anything...")
    if query:
        docs = retriever().invoke(query)
        st.subheader(f"Top {len(docs)} results")
        for d in docs:
            st.markdown(f"**📄 {d.metadata['citation']}**")
            st.write(d.page_content[:500] + "...")
            st.divider()

# ----------------------------------------------------------
# ⚖️ COMPARE
# ----------------------------------------------------------
with compare_tab:
    st.header("Compare & Find Gaps")
    if st.button("Run comparison"):
        summaries = load_summaries()
        if not summaries:
            st.warning("Upload papers first.")
        else:
            st.markdown("### Comparison Table")
            st.markdown(compare_docs(summaries), unsafe_allow_html=True)
            st.markdown("### Research Gaps")
            st.markdown(find_gaps_only(summaries), unsafe_allow_html=True)

# ----------------------------------------------------------
# 📝 LITERATURE REVIEW
# ----------------------------------------------------------
with lit_tab:
    st.header("AI-Generated Literature Review")
    if st.button("Draft review"):
        summaries = load_summaries()
        if not summaries:
            st.warning("Upload papers first.")
        else:
            with st.spinner("Writing..."):
                review = lit_review_prompt(summaries)
            st.markdown(review)
            st.download_button(
                label="Download .md",
                data=review,
                file_name="literature_review.md",
                mime="text/markdown",
            )

# ----------------------------------------------------------
# 📊 VISUALIZE
# ----------------------------------------------------------
with viz_tab:
    st.header("Quick Visuals")
    summaries = load_summaries()
    if not summaries:
        st.info("Upload papers to see visuals.")
    else:
        # Keyword bar chart
        all_text = " ".join(summaries.values()).lower()
        words = [w for w in all_text.split() if len(w) > 4]
        top = Counter(words).most_common(15)
        if top:
            st.bar_chart({w: c for w, c in top})
        else:
            st.write("No data to plot.")