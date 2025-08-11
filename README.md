# 📘 ScholarMindAI – README

**A 100 % free, AI-powered research companion that stays inside Google Gemini’s free tier.**  
🚀 **preview:** preview2.png

---

## ✨ Features (v1.0 – Part 6)

| # | Feature | Description |
|--|--|--|
|1|📤 Upload & Auto-Chunk|Drag-and-drop PDF/TXT → clean text → overlap-split → vectors|
|2|🔍 Semantic Search|Ask questions → top-k snippets with **page & citation**|
|3|⚖️ Multi-Document Compare|Side-by-side table + **contradictions & research gaps**|
|4|📝 AI Literature Review|Auto-draft **Intro, Methods, Results, Discussion** (Scientific / Business / Education modes)|
|5|📊 Quick Visuals|Keyword bar-chart & word-cloud|
|6|🎨 Dark/Light Toggle|Sidebar switch|

All Gemini calls ≤ 800 tokens → **free-tier safe**.

---

## 🧰 Tech Stack

| Layer | Tool | Cost |
|---|---|---|
Frontend | Streamlit (Python) | Free  
Embeddings | `all-MiniLM-L6-v2` (CPU) | Free  
Vector DB | ChromaDB (persistent) | Free  
LLM Reasoning | Google Gemini 1.5-Flash | Free Tier  
PDF/TXT Parsing | PyMuPDF + PyPDF2 | Free  
Environment | Conda / Docker | Free  

---

## 🚀 Quick Start (30 seconds)

   ```bash
   git clone https://github.com/<your-username>/ScholarMindAI.git
   cd ScholarMindAI
   conda create -n scholarmind python=3.10 -y
   conda activate scholarmind
   pip install -r requirements.txt
   run streamlit run src/app.py
