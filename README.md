# 🧠 Kubernetes LLM Troubleshooting Assistant

This project aims to build an intelligent system for diagnosing and troubleshooting errors in Kubernetes clusters using **Large Language Models (LLMs)**. The solution integrates real-time logs, error snapshots, and Kubernetes documentation to deliver actionable root-cause analysis and recommended fixes.

---

## 📌 Project Goals

- Automate the analysis of Kubernetes crashes (e.g., `CrashLoopBackOff`, `ImagePullBackOff`, etc.)
- Generate clear, structured responses based on Kubernetes best practices
- Explore and benchmark several LLM-based techniques: prompting, retrieval-augmented generation (RAG), hypothetical document embeddings (HyDE), and fine-tuning

---

## 📦 Architecture Overview

## ⬇️ Snapshot + Logs Collection
- Filtered logs
- Events
- Probes, env config
- Saved or streamed

## ⬇️ Dual Analysis Pipeline

### 1️⃣ LLM-Based Flow

- Consumes structured input (logs, events, env)
- Uses:
  - Prompt engineering (zero-shot, one-shot, few-shot)
  - Optional fine-tuning
  - RAG (doc retrieval)
  - HyDE for hypothetical embedding generation
- Compares current vs past trends
- Outputs structured diagnosis

- ### 2️⃣ Rule-Based Flow

- Static thresholds (e.g. CPU > 90%)
- Pattern matching on log lines
- Rolling window event stats
- Can be augmented by LLM suggestions

## 🔁 Hybrid Decision Logic

- If either path detects a fault:
  - LLM is invoked for explanation
  - Documentation retrieved (RAG)
  - Fix recommendation is generated
  - Final output sent to user (CLI, Slack, API, etc.)
 
---

## 🧪 Benchmark Design

| Technique                         | Description  | Model   | Metrics        |
|-----------------------------------|--------------|---------|----------------|
| Prompting (different strategies)  |              |         |                |
| RAG                               |              |         |                |
| HyDE                              |              |         |                |
| Fine-tuning                       |              |         |                |

## 🧰 Features

- 🔍 **Prompt builder**: Parses logs, events, env data into structured prompts
- 🧠 **LLM Executor**: Choose and query GPT, Claude, or Mistral
- 🗂️ **RAG pipeline**: Index and retrieve Kubernetes documentation
- 🔄 **Prompt modes**: Zero-shot, one-shot, few-shot
- 🧪 **Benchmark support**: Output comparison and evaluation interface

---

## 🔧 Requirements

- Python 3.9+
- `openai`, `anthropic`, `faiss-cpu`, `sentence-transformers`, `python-dotenv`

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔑 API Keys
Create a .env file in the project root with:
```
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
# other models
```

---

## ▶️ Running
