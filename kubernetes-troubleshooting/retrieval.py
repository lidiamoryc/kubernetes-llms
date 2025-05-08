import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import os
from Issues import config_map_query, database_issues

with open("config.json", "r") as config_file:
    config = json.load(config_file)

INDEX_PATH = config.get("faiss_index_path", "default_index_path/kubernetes_docs_chunks.txt.faiss")
METADATA_PATH = config.get("metadata_path", "kubernetes_docs_chunks.txt.txt")


# Wczytanie indeksu FAISS
# index = faiss.read_index(
#     r"C:\Users\Lidia\PycharmProjects\kubernetes-llms\kubernetes-troubleshooting\configmaps_faiss.index")

index = faiss.read_index(INDEX_PATH)


# Wczytanie metadanych
def load_metadata(path):
    metadata = {}
    current_id = None
    current_text = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().isdigit():
                if current_id is not None:
                    metadata[current_id] = "\n".join(current_text).strip()
                current_id = int(line.strip())
                current_text = []
            else:
                current_text.append(line.strip())

        if current_id is not None:
            metadata[current_id] = "\n".join(current_text).strip()

    return metadata


metadata = load_metadata(METADATA_PATH)

# Wczytanie modelu SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve(query: str, k: int = 10):
    query_embedding = model.encode([query])
    query_vector = np.array(query_embedding).astype("float32")
    distances, indices = index.search(query_vector, k)
    results = []
    for i in indices[0]:
        i = int(i)
        if i in metadata:
            results.append(f"Chunk ID {i}: " + metadata[i])
        else:
            results.append(f"⚠️ Chunk ID {i} not found in metadata.")
    return results


def enhance_query_with_hyde(query: str) -> str:
    from openai import OpenAI
    from dotenv import load_dotenv

    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    # openai_api_key = config.get("openai_api_key")
    if not openai_api_key:
        raise ValueError("OpenAI API key is missing in the config file.")

    client = OpenAI(api_key=openai_api_key)

    prompt = (
        f"Write a very detailed description of the problem related to: {query}\n\n"
        "Include possible causes, effects, context, and potential solutions."
    )

    response = client.chat.completions.create(model="gpt-4o-mini",
    messages=[
        {"role": "system",
         "content": "You are a very helpful assistant specializing in technical problems."},
        {"role": "user", "content": prompt},
    ])

    hypothetical_answer = response.choices[0].message.content.strip()
    return hypothetical_answer


def retrieve_hyde(query: str, k: int = 5):
    hyde_query = enhance_query_with_hyde(query)
    results = retrieve(hyde_query, k)
    return {"hyde_query": hyde_query, "results": results}


def retrieve_zero_shot(query: str, k: int = 5):
    zero_shot_query = f"[Zero-shot] {query}"
    return retrieve(zero_shot_query, k)


def retrieve_few_shot(query: str, k: int = 5):
    few_shot_query = f"[Few-shot] Przykład: Konfiguracja nie została załadowana poprawnie. Kontekst: {query}"
    return retrieve(few_shot_query, k)


def retrieval_methods(case_name: str, query: str, output_dir="results", k: int = 5):
    hyde_result = retrieve_hyde(query, k)

    results = {
        "baseline": retrieve(query, k),
        "hyde": hyde_result["results"],
        "hyde_query": hyde_result["hyde_query"],
        # "few_shot": retrieve_few_shot(query, k),
    }

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{case_name}_results.json")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"✅ Wyniki dla case {case_name} zapisane w {filename}")
    return results


if __name__ == "__main__":
    # Test 1 - ConfigMap problem
    retrieval_methods("ConfigMap_problem", config_map_query)

    for issue_name, issue_data in database_issues.items():
        query = issue_data["query"]
        retrieval_methods(issue_name, query)
    # # Test 2 - Inny problem
    # query2 = "Błąd startupu serwisu w klastrze Kubernetes."
    # test_retrieval_methods("Kubernetes_startup_error", query2)
    #
    # # Test 3 - Jeszcze inny problem
    # query3 = "Problem z rozdzieleniem zasobów przez scheduler."
    # test_retrieval_methods("Scheduler_issue", query3)