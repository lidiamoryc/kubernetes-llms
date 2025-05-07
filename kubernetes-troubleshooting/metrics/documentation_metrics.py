from bert_score import score
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def is_similar(candidate, reference_list, threshold=0.75):
    candidate_embedding = model.encode(candidate, convert_to_tensor=True)
    reference_embeddings = model.encode(reference_list, convert_to_tensor=True)
    cosine_scores = util.cos_sim(candidate_embedding, reference_embeddings)
    return any(score > threshold for score in cosine_scores[0])


class DocumentationMetrics:
    def __init__(self):
        pass
        
    def mean_reciprocal_rank(self, golden_list, retrieved_list):
        """
        Calculate MRR for a single query.
        
        Args:
            golden_list: List of relevant doc IDs (e.g., ["k8s-doc-123", "k8s-doc-456"])
            retrieved_list: Ordered list of retrieved doc IDs
        
        Returns:
            MRR score (0-1)
        """
        for rank, doc in enumerate(retrieved_list, start=1):
            if doc in golden_list:
                return 1.0 / rank
        return 0.0

    def mrr_semantic(golden_list, retrieved_list, threshold=0.75):
        for rank, candidate in enumerate(retrieved_list, start=1):
            if is_similar(candidate, golden_list, threshold):
                return 1.0 / rank
        return 0.0

    def precision_at_k(self, golden_list, retrieved_list, k=3):
        """
        Calculate Precision@k for technical documentation retrieval.
        
        Args:
            golden_list: Relevant doc IDs for a Kubernetes error
            retrieved_list: Retrieved doc IDs ordered by relevance
            k: Top documents to consider
        
        Returns:
            Precision score (0-1)
        """
        top_k = retrieved_list[:k]
        relevant = len(set(top_k) & set(golden_list))
        return relevant / k

    def precision_at_k_semantic(golden_list, retrieved_list, k=3, threshold=0.75):
        top_k = retrieved_list[:k]
        relevant = sum(is_similar(cand, golden_list, threshold) for cand in top_k)
        return relevant / k

    # def compute_bertscore(self, candidates, references):
    #     """
    #     Calculate semantic similarity for Kubernetes error explanations.
        
    #     Args:
    #         candidates: LLM-generated documentation excerpts
    #         references: Golden standard documentation
        
    #     Returns:
    #         F1 score (0-1) measuring semantic overlap
    #     """
    #     _, _, F1 = score(candidates, references, lang='en', verbose=False)
    #     return F1.mean().item()

    def compute_bertscore(self, candidates, references):
            """
            Compute max pairwise BERTScore F1 between each candidate and all references.
            This makes the score order- and count-agnostic.

            Args:
                candidates (list of str): LLM outputs
                references (list of str): Gold standard docs

            Returns:
                float: Mean of max F1s per candidate
            """
            all_scores = []

            for cand in candidates:
                # Compare one candidate against all references
                _, _, F1 = score([cand] * len(references), references, lang='en', verbose=False)
                all_scores.append(F1.max().item())  # keep best-matching reference

            return sum(all_scores) / len(all_scores) if all_scores else 0.0