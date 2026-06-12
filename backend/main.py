"""
main.py
FastAPI app — the single backend that serves the React frontend.

Endpoints:
  POST /ask     — takes a question, returns answer + source sections
  GET  /health  — sanity check
"""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from retriever import retrieve
from llm import ask_groq

# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="IPC RAG API",
    description="Ask questions about the Indian Penal Code",
    version="1.0.0",
)

# CORS — allow React dev server (port 5173 for Vite, 3000 for CRA)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas ───────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=10)


class SourceSection(BaseModel):
    section_num: str
    title: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceSection]
    question: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "IPC RAG API"}


@app.post("/ask", response_model=AskResponse)
def ask(body: AskRequest):
    """
    Main RAG endpoint.
    1. Retrieve top-k relevant IPC sections from ChromaDB
    2. Pass question + sections to Groq LLM
    3. Return answer + source citations
    """
    try:
        # Step 1: Retrieve
        chunks = retrieve(body.question, top_k=body.top_k)

        if not chunks:
            raise HTTPException(
                status_code=404,
                detail="No relevant IPC sections found. Try rephrasing your question.",
            )

        # Step 2: Generate
        answer = ask_groq(body.question, chunks)

        # Step 3: Build source list (without full content to keep response lean)
        sources = [
            SourceSection(
                section_num=c["section_num"],
                title=c["title"],
                score=c["score"],
            )
            for c in chunks
        ]

        return AskResponse(answer=answer, sources=sources, question=body.question)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# ── Dev entrypoint ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
