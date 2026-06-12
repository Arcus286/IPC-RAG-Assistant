# LexQuery — IPC RAG Assistant

AI-powered Indian Penal Code research assistant. Ask about specific sections or whether something is legal. Answers are grounded in actual IPC text with section citations.

## Stack
- **Frontend:** React + Vite
- **Backend:** FastAPI (Python)
- **Vector DB:** FAISS (local, persistent)
- **Embeddings:** sentence-transformers (`all-MiniLM-L6-v2`)
- **LLM:** Groq (`llama-3.3-70b-versatile`)

---

## Setup

### 1. Get the IPC PDF
Download the official IPC document from [India Code](https://www.indiacode.nic.in) or the Ministry of Law website.

### 2. Backend

> **Note:** `faiss_index.bin` and `faiss_metadata.json` are not included in the repo, they are generated locally by running `ingest.py` against your PDF.

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set your Groq API key
cp .env.example .env
# Edit .env and add your key from https://console.groq.com

# Ingest the IPC PDF (run once — generates faiss_index.bin + faiss_metadata.json)
python ingest.py --pdf path/to/ipc.pdf

# Start the API server
python main.py
# → Running at http://localhost:8000
# → Docs at http://localhost:8000/docs
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# → Running at http://localhost:5173
```

---

## How It Works

```
User Question
    ↓
Embed with sentence-transformers
    ↓
FAISS cosine similarity search → top-5 IPC sections
    ↓
Groq LLM (Llama) reasons over sections
    ↓
Answer + section citations returned to React UI
```

## Project Structure

```
ipc-rag/
├── backend/
│   ├── ingest.py           # PDF → chunks → embeddings → FAISS (run once)
│   ├── retriever.py        # FAISS query logic
│   ├── llm.py              # Groq API call + prompt
│   ├── main.py             # FastAPI app (/ask endpoint)
│   ├── .env.example        # API key template
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.jsx
        └── components/
            ├── ChatWindow.jsx
            ├── MessageBubble.jsx   # Shows answer + § source chips
            └── InputBar.jsx        # Textarea + suggestion chips
```

## API

### `POST /ask`
```json
{
  "question": "What is the punishment for theft?",
  "top_k": 5
}
```
Response:
```json
{
  "answer": "Under Section 379, theft is punishable...",
  "sources": [
    { "section_num": "379", "title": "Punishment of theft", "score": 0.91 }
  ],
  "question": "What is the punishment for theft?"
}
```

### `GET /health`
```json
{ "status": "ok", "service": "IPC RAG API" }
```