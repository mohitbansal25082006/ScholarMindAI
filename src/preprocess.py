import os, json, fitz, re
from pathlib import Path

UPLOAD_DIR   = Path("data/uploads")
PROCESSED_DIR= Path("data/processed")
CHUNK_SIZE   = 500          # ~tokens
OVERLAP      = 50

UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
PROCESSED_DIR.mkdir(exist_ok=True, parents=True)

def clean_text(text:str)->str:
    """Remove extra spaces, line breaks, weird chars."""
    text = re.sub(r'\s+', ' ', text)
    text = text.encode('utf-8','ignore').decode()
    return text.strip()

def extract_pdf(pdf_path:Path)->dict:
    """Return dict {page_num: text}"""
    doc = fitz.open(pdf_path)
    pages = {}
    for i, page in enumerate(doc, start=1):
        pages[i] = clean_text(page.get_text())
    doc.close()
    return pages

def chunk_pages(pages:dict)->list:
    """Split pages into overlapping chunks."""
    chunks=[]
    buffer=""
    for page_num, text in pages.items():
        buffer += " " + text
        while len(buffer) >= CHUNK_SIZE:
            chunk_text = buffer[:CHUNK_SIZE]
            chunks.append({
                "doc_id": None,          # filled later
                "page": page_num,
                "text": chunk_text
            })
            buffer = buffer[CHUNK_SIZE-OVERLAP:]
    if buffer.strip():
        chunks.append({
            "doc_id": None,
            "page": list(pages.keys())[-1],
            "text": buffer.strip()
        })
    return chunks

def process_file(file_path:Path, doc_id:str)->list:
    """Full pipeline for one file."""
    if file_path.suffix.lower()==".pdf":
        pages = extract_pdf(file_path)
    else:
        # plain txt
        raw = file_path.read_text(encoding='utf-8', errors='ignore')
        pages = {1: clean_text(raw)}
    
    chunks = chunk_pages(pages)
    for c in chunks:
        c["doc_id"] = doc_id
    
    (PROCESSED_DIR / f"{doc_id}.json").write_text(
    json.dumps(pages, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (PROCESSED_DIR / f"{doc_id}_chunks.json").write_text(
    json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return chunks