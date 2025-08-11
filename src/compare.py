import json, os, textwrap
from pathlib import Path
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

CHUNKS_DIR = Path("data/processed")
REPORTS_DIR = Path("data/processed")
REPORTS_DIR.mkdir(exist_ok=True)

# ----------------- local helpers -----------------
def load_summaries() -> Dict[str, str]:
    """Read *_chunks.json and build a short summary for each doc."""
    summaries = {}
    for file in CHUNKS_DIR.glob("*_chunks.json"):
        doc_id = file.stem.replace("_chunks", "")
        chunks = json.loads(file.read_text(encoding="utf-8"))
        full_text = " ".join(c["text"] for c in chunks)
        # crude local summary – first 600 chars + last 200
        summary = full_text[:600] + " ... " + full_text[-200:]
        summaries[doc_id] = summary
    return summaries

# ----------------- Gemini helpers -----------------
gemini = genai.GenerativeModel("gemini-1.5-flash")

def compare_docs(summaries: Dict[str, str]) -> str:
    prompt = f"""
You are an expert research analyst.  Below are short summaries of uploaded papers.

Summaries:
{json.dumps(summaries, indent=2)}

Tasks:
1. Create a markdown table with columns: Document, Methodology, Key Finding, Dataset.
2. Identify any contradictions or conflicting results.
3. List 3-5 **research gaps** not addressed by any paper.

Answer concisely (< 600 tokens).  Use bullet points for gaps.
"""
    response = gemini.generate_content(prompt)
    return response.text

def find_gaps_only(summaries: Dict[str, str]) -> str:
    prompt = f"""
Identify **research gaps** from these summaries:

{json.dumps(summaries, indent=2)}

Return a markdown bullet list of 3-5 high-impact gaps.
"""
    return gemini.generate_content(prompt).text

# ----------------- CLI -----------------
if __name__ == "__main__":
    summaries = load_summaries()
    if not summaries:
        print("❌ No documents found in data/processed/")
        exit()

    print("🔍 Running comparison ...")
    compare_md = compare_docs(summaries)
    (REPORTS_DIR / "compare_report.md").write_text(compare_md, encoding="utf-8")
    print("✅ compare_report.md saved")

    gaps_md = find_gaps_only(summaries)
    (REPORTS_DIR / "gaps_report.md").write_text(gaps_md, encoding="utf-8")
    print("✅ gaps_report.md saved")