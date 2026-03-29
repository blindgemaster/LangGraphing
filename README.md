# 🧠 LangGraph Lab

> *Building intelligence, one graph at a time.*

---

## Graphs

### 1 — Tool Agent

An agent that decides whether to use a tool or answer directly.

```
You: "what is 2+3?"
        │
        ▼
   ┌─────────┐        "I need to call add(2,3)"
   │  Agent  │ ──────────────────────────────────► ┌──────────┐
   └─────────┘                                      │   Tool   │ → runs add() → returns 5
        ▲                                           └────┬─────┘
        │                 "2 + 3 = 5"                    │
        └───────────────────────────────────────────────┘
        │
        ▼
      Answer
```

> No tool needed? Agent skips straight to the answer.

**→** [`tool_agent.ipynb`](tool_agent.ipynb)

---

### 2 — Drafting Agent with Human Input

A human-in-the-loop agent that keeps revising a document until you're happy.
Can also edit files on disk directly via the `fix_txt_file` tool.

```
You: "Draft a project proposal"
        │
        ▼
   ┌─────────┐    needs fix_txt_file?
   │  Agent  │ ──────────────────────► ┌──────────────┐
   └─────────┘                         │ fix_txt_file │ → reads file → edits → saves
        │                              └──────┬───────┘
        │  "Here's your draft..."             │
        ▼ ◄──────────────────────────────────┘
   ┌─────────┐
   │  Human  │ → "Make it more formal" → loops back to Agent
   └─────────┘
        │
      exit → done
```

> The loop only breaks when you type `exit`. Every iteration the agent sees the full conversation history.

**→** [`drafting_agent_with_human_input.py`](drafting_agent_with_human_input.py) — run via CLI

---

### 3 — RAG Agent

> *"Don't hallucinate. Go read."*

A Retrieval-Augmented Generation agent that grounds every answer in a real PDF document.
Instead of relying on the LLM's training data, it retrieves the most relevant chunks from a
vector database before forming a response.

```
You: "Do they stock ibuprofen?"
        │
        ▼
   ┌───────────┐   "I need to search the PDF"
   │   Agent   │ ──────────────────────────────► ┌──────────────────────┐
   └───────────┘                                  │  retrieve_pdf_info   │
        ▲                                         │  ┌────────────────┐  │
        │                                         │  │  ChromaDB      │  │
        │   Top 5 matching chunks returned        │  │  (vector store)│  │
        │ ◄───────────────────────────────────    │  └────────────────┘  │
        │                                         └──────────────────────┘
        ▼
   "Ibuprofen is a major interaction with warfarin — avoid, use paracetamol."
```

**How it works under the hood:**

| Step | What happens |
|------|-------------|
| 1. **Ingest** | PDF is loaded, split into 1000-char chunks with 200-char overlap |
| 2. **Embed** | Each chunk is embedded via `text-embedding-3-small` and stored in ChromaDB |
| 3. **Cache** | If the vector DB already exists on disk, embedding is skipped entirely |
| 4. **Query** | User question → similarity search → top 5 chunks retrieved |
| 5. **Answer** | LLM reads the chunks and answers grounded in the actual document |

**Why RAG?**
The LLM has no knowledge of your specific PDF. RAG bridges that gap — the agent only answers
from what's actually in the document, making it accurate, auditable, and hallucination-resistant.

**→** [`Rag_Agent.py`](Rag_Agent.py) — run via CLI, place your PDF as `example.pdf`

---

## What's This?

An active workspace for experimenting with **LangGraph** — stateful, multi-agent workflows built as graphs.

Each node is a step. Each edge is a decision. Every run is a new path through the graph.

---

## Stack

![LangGraph](https://img.shields.io/badge/LangGraph-0.1+-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-yellow?style=flat-square)
![Jupyter](https://img.shields.io/badge/Jupyter-notebook-orange?style=flat-square)

---

## Setup

```bash
pip install langgraph langchain
cp .env.example .env   # add your API keys
```

---

*Graphs are just thoughts with structure.*
