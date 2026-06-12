"""
llm.py
Calls Groq LLM (Llama) with the retrieved IPC context and returns an answer.
"""

import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an expert Indian legal assistant specializing in the Indian Penal Code (IPC).

Your job:
- Answer questions strictly based on the IPC sections provided in the context.
- For situational questions ("Is X legal?", "Can I do Y?"), reason through the relevant sections and give a clear verdict.
- Always cite the specific IPC section number(s) that back your answer (e.g., "Under Section 302...").
- If the provided sections don't cover the question, say: "The provided IPC sections don't directly address this. You should consult a legal professional."
- Keep answers clear, structured, and accessible to non-lawyers.
- Never fabricate section numbers or legal content not present in the context.

Disclaimer: Your answers are informational only and do not constitute legal advice."""


def build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a readable context block."""
    parts = []
    for chunk in chunks:
        parts.append(
            f"--- Section {chunk['section_num']}: {chunk['title']} ---\n{chunk['content']}"
        )
    return "\n\n".join(parts)


def ask_groq(question: str, chunks: list[dict]) -> str:
    """
    Send question + IPC context to Groq and return the answer string.
    """
    context = build_context(chunks)

    user_message = f"""Context (relevant IPC sections):
{context}

Question: {question}

Please answer based strictly on the sections above."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,   # low temp = consistent, factual answers
        max_tokens=1024,
    )

    return response.choices[0].message.content
