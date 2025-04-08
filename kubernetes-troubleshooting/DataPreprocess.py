import re
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


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
def chunk_text(text, max_length=800, overlap=100):
    sentences = text.split('\n')
    chunks, current_chunk = [], []

    for sentence in sentences:
        if sum(len(s) for s in current_chunk) + len(sentence) < max_length:
            current_chunk.append(sentence)
        else:
            chunks.append('\n'.join(current_chunk))
            current_chunk = current_chunk[-overlap:] + [sentence]

    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks


# Step 3: Embed and save to FAISS
def embed_and_save(chunks, index_file, metadata_file):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)

    dim = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    faiss.write_index(index, index_file)

    with open(metadata_file, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"{i}\t{chunk}\n")


# --- RUN THE PIPELINE ---
if __name__ == "__main__":
    file_path = "ConfigMaps.md"
    index_file = "configmaps_faiss.index"
    metadata_file = "configmaps_chunks.txt"

    text = load_and_clean(file_path)
    chunks = chunk_text(text)
    embed_and_save(chunks, index_file, metadata_file)

    print(f"✅ Index saved to {index_file}")
    print(f"✅ Metadata saved to {metadata_file}")
