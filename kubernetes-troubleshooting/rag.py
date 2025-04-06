# import faiss
# import numpy as np
# from sentence_transformers import SentenceTransformer

# # Load FAISS index
# index = faiss.read_index("configmaps_faiss.index")

# # Load metadata
# with open("configmaps_chunks.txt", "r", encoding="utf-8") as f:
#     metadata = {int(line.split("\t")[0]): line.split("\t", 1)[1].strip() for line in f}

# # Load embedding model
# model = SentenceTransformer("all-MiniLM-L6-v2")

# # Your actual problem -> convert to query
# query = "why is my pod failing to start due to a missing configmap?"

# # Embed the query
# query_embedding = model.encode([query])
# query_vector = np.array(query_embedding).astype("float32")

# # Search
# D, I = index.search(query_vector, k=5)

# # Print top docs
# print("\n🔍 Top retrieved documentation chunks:\n")
# top_chunks = []
# for i in I[0]:
#     print(f"--- Chunk {i} ---\n{metadata[i]}\n")
#     top_chunks.append(metadata[i])
