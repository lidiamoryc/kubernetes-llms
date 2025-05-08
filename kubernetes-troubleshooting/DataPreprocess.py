import json
import re
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from glob import glob

# Step 1: Load and clean the markdown content
def load_and_clean(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        text = file.read()

    text = re.sub(r"{{<[^>]*>}}", "", text)
    text = re.sub(r"{{%[^%]*%}}", "", text)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"---[\s\S]*?---", "", text, count=1)

    return text.strip()


# Step 2: Chunk the text
def chunk_text(text, source_file, max_length=800, overlap=100):
    sentences = text.split('\n')
    chunks = []
    sources = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_length:
            current_chunk += sentence + '\n'
        else:
            chunks.append(current_chunk.strip())
            sources.append(source_file)
            # Keep overlap (last `overlap` characters) and continue
            current_chunk = current_chunk[-overlap:] + sentence + '\n'

    if current_chunk.strip():
        chunks.append(current_chunk.strip())
        sources.append(source_file)

    return chunks, sources

# Step 3: Embed and save to FAISS
def embed_and_save(chunks, sources, index_file, metadata_file):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)

    dim = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    faiss.write_index(index, index_file)

    with open(metadata_file, "w", encoding="utf-8") as f:
        for i, (chunk, source) in enumerate(zip(chunks, sources)):
            f.write(f"{i}\n[SOURCE: {source}]\n{chunk.strip()}\n\n")

def load_config():
    try:
        with open("config.json", "r") as config_file:
            return json.load(config_file)
    except:
        return {
            "docs_dir": "docs",
            "faiss_index_path": "kubernetes_docs_faiss.index",
            "metadata_path": "kubernetes_docs_chunks.txt"
        }


# --- RUN THE PIPELINE ---
if __name__ == "__main__":
    config = load_config()

    docs_dir = config.get("docs_dir", "docs")

    file_paths = glob(f"{docs_dir}/*.md")

    index_file = config.get("faiss_index_path", "kubernetes_docs_faiss.index")
    metadata_file = config.get("metadata_path", "kubernetes_docs_chunks.txt")

    all_chunks = []
    all_sources = []

    for file_path in file_paths:
        print(f"Processing file: {file_path}")

        # Process MD files
        text = load_and_clean(file_path)
        chunks, sources = chunk_text(text, file_path)
        all_chunks.extend(chunks)
        all_sources.extend(sources)

    embed_and_save(all_chunks, all_sources, index_file, metadata_file)

    print(f"✅ Processed {len(file_paths)} files")
    print(f"✅ Created {len(all_chunks)} chunks")
    print(f"✅ Index saved to {index_file}")
    print(f"✅ Metadata saved to {metadata_file}")