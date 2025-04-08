import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from Issues import config_map_query


# Load FAISS index
index = faiss.read_index(r"C:\Users\Lidia\PycharmProjects\kubernetes-llms\kubernetes-troubleshooting\configmaps_faiss.index")


# Load metadata
def load_metadata(path):
    metadata = {}
    current_id = None
    current_text = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().isdigit():
                # New chunk ID found — save the previous one
                if current_id is not None:
                    metadata[current_id] = "\n".join(current_text).strip()
                current_id = int(line.strip())
                current_text = []
            else:
                current_text.append(line.strip())

        if current_id is not None:
            metadata[current_id] = "\n".join(current_text).strip()

    return metadata

metadata = load_metadata("configmaps_chunks.txt")

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Your actual problem -> convert to query
query = config_map_query

# Embed the query
query_embedding = model.encode([query])
query_vector = np.array(query_embedding).astype("float32")

# Search
D, I = index.search(query_vector, k=5)

# Print top docs
print("\n🔍 Top retrieved documentation chunks:\n")
top_chunks = []
for i in I[0]:
    i = int(i)  # <- this is the key fix
    if i in metadata:
        print(f"--- Chunk {i} ---\n{metadata[i]}\n")
        top_chunks.append(metadata[i])
    else:
        print(f"⚠️ Chunk ID {i} not found in metadata.\n")
