# 🧠 LangGraph Lab

> *Building intelligence, one graph at a time.*

---

```
              [START]
                 │
                 ▼
           ┌─────────┐
      ┌───►│  Agent  │
      │    └────┬────┘
      │         │
      │   ┌─────▼──────────────┐
      │   │ decider            │
      │   │ tool_calls? ───Yes─┼──► ┌──────────┐
      │   │             No     │    │   Tool   │
      │   └────────────────────┘    └────┬─────┘
      │                │                │
      └────────────────┘◄───────────────┘
                       │
                      END
```

> **Notebook:** [`tool_agent.ipynb`](tool_agent.ipynb)

---

```
              [START]
                 │
                 ▼
           ┌─────────┐
      ┌───►│  Human  │◄──────────────┐
      │    └────┬────┘               │
      │         │                    │
      │   ┌─────▼──────────────┐     │
      │   │ decider            │     │
      │   │ HumanMessage? ─Yes─┼──►┌─┴───────┐
      │   │ tool_calls?  ──Yes─┼──►│  Tool   │
      │   │ else (No)          │   └─────────┘
      │   └────────────────────┘
      │                │
      └────────────────┘  (No → back to Human)
                       │
                     EXIT
```

> **Script:** [`drafting_agent_with_human_input.py`](drafting_agent_with_human_input.py) — run via CLI, type `exit` to quit

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
