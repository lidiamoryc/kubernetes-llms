## 🔁 Overview of Steps:
1. Collect Runtime Context from the app -> **for now we take example contexts, later we will automatically collect them**
  The context object:
  ```json
   {
  "logs": "...",
  "traceback": "...",
  "events": "...",
  "env": { "DISCORD_TOKEN": "..." },
  "probe_config": "...",
  "pod_status": "...",
  "summary": "500 errors due to missing secret token"
    }
  ```

2. Preprocess & Normalize that context
  - Strip timestamps (or keep only recent)
  - Remove Kubernetes noise (e.g. scheduling info, unless relevant)
  - Parse traceback into exception type + location
  - Use key-value format for things like env vars and probe config

3. Embed and Index Documentation sources
  Documentation text on github: https://github.com/kubernetes/website/tree/main/content/en/docs

  - Convert docs to text chunks
  - Embed chunks with a model (OpenAI Embeddings, HuggingFace, etc.)
  - Store in a vector DB (like FAISS, Weaviate, Pinecone)
  - **proposed models:** text-embedding-ada-002 (OpenAI), sentence-transformers/all-MiniLM-L6-v2 (HuggingFace, local), InstructorXL, Cohere, or others

  Then we store in a Vector Database. Proposed vector databases: FAISS (local), Pinecone (cloud), Weaviate / Qdrant / Chroma.

4. Generate a Query from the context

5. Retrieve Relevant Docs

6. Feed Context + Docs to LLM for actionable suggestions

