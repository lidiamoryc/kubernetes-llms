# Requires: pip install bert-score
from bert_score import score

class DocumentationMetrics:
    def __init__(self, golden_truth, actual_output):
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


    def compute_bertscore(self, candidates, references):
        """
        Calculate semantic similarity for Kubernetes error explanations.
        
        Args:
            candidates: LLM-generated documentation excerpts
            references: Golden standard documentation
        
        Returns:
            F1 score (0-1) measuring semantic overlap
        """
        _, _, F1 = score(candidates, references, lang='en', verbose=False)
        return F1.mean().item()

    # Kubernetes example:
    bert_score = compute_bertscore(
        candidates=["Check pod logs using kubectl logs --previous"],
        references=["Use 'kubectl logs <pod> --previous' to inspect crashed containers"]
    )
    # Returns ~0.92 (high semantic match)
