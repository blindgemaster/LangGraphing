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

**→** [`tool_agent.ipynb`](notebooks/agents/tool_agent.ipynb)

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

**→** [`drafting_agent_with_human_input.py`](agents/drafting_agent_with_human_input.py) — run via CLI

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

**→** [`Rag_Agent.py`](agents/Rag_Agent.py) — run via CLI, place your PDF in `data/example.pdf`

---

### 4 — Map-Reduce (Fan-Out / Fan-In)

> *"Split. Score. Pick the winner."*

A graph that fans out a dynamic list of items to parallel workers using LangGraph's `Send` API,
then merges the results back into a single list via an `operator.add` reducer. The classic
map-reduce pattern — one node decides the work, many copies of a worker run side by side, one
node aggregates.

```
            ┌─────────────────┐
            │  generate_items │   "fruits" → [apple, banana, cherry, date, elderberry]
            └────────┬────────┘
                     │  Send(item=...)   Send(item=...)   Send(item=...)
          ┌──────────┼─────────────┬──────────────┬──────────────┐
          ▼          ▼             ▼              ▼              ▼
      ┌───────┐  ┌───────┐     ┌───────┐      ┌───────┐      ┌───────┐
      │ score │  │ score │ ... │ score │      │ score │      │ score │   (parallel)
      └───┬───┘  └───┬───┘     └───┬───┘      └───┬───┘      └───┬───┘
          │          │             │              │              │
          └──────────┴─────────────┴──────┬───────┴──────────────┘
                                          ▼
                                  ┌───────────────┐
                                  │   pick_best   │  → reduces list, returns winner
                                  └───────────────┘
```

> The conditional edge returns a list of `Send` objects instead of a route name — that's what tells LangGraph to spin up N parallel branches at runtime.

**→** [`Map_Reduce.ipynb`](notebooks/graphs/Map_Reduce.ipynb)

---

### 5 — Reflection Loop (Generator + Critic)

> *"Draft. Critique. Refine. Repeat — until it passes."*

A self-correcting loop: a generator drafts an answer, a critic evaluates it against
explicit rules, and the graph either accepts the draft, retries with feedback, or
gives up after a bounded number of attempts. The example refines a password until
it satisfies a length-and-character policy.

```
   "give me a password"
            │
            ▼
      ┌──────────┐
      │ generate │ ◄─────────────────┐
      └────┬─────┘                   │
           │ draft                   │
           ▼                         │
      ┌──────────┐                   │ retry
      │  critic  │ ── feedback ──────┤  (with feedback)
      └────┬─────┘                   │
           │                         │
        decide ──── retry ───────────┘
           │
           ├── done   ──► END  (accepted)
           └── giveup ──► END  (attempts exhausted)
```

> The critic returns a list of missing requirements. The next `generate` reads that
> feedback and widens its character pool / length accordingly — feedback is the
> signal that drives refinement.

**→** [`Reflection_Loop.ipynb`](notebooks/graphs/Reflection_Loop.ipynb)

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
