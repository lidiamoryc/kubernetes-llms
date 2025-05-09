from bert_score import score
from sentence_transformers import SentenceTransformer, util

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class DocumentationMetrics:
    def __init__(self, similarity_threshold=0.50, model_name="all-MiniLM-L6-v2"):
        self.similarity_threshold = similarity_threshold
        self.model = SentenceTransformer(model_name)

    def _embed(self, texts):
        return self.model.encode(texts, convert_to_tensor=False)  # Critical fix

    def _is_similar(self, candidate, references):
        cand_emb = self._embed([candidate])
        ref_embs = self._embed(references)
        scores = cosine_similarity(cand_emb, ref_embs)[0]
        return np.max(scores) >= self.similarity_threshold

    def precision_at_k(self, ground_truth, output, k=3):
        """
        Semantic Precision@k for technical docs - compares content meaning
        instead of exact matches.
        """
        top_k = output[:k]
        
        matches = sum(
            1 for retrieved_doc in top_k 
            if self._is_similar(retrieved_doc, ground_truth)
        )
        
        return matches / k

    def mean_reciprocal_rank(self, ground_truth, output):
        """
        Semantic MRR - finds first position of semantically relevant doc
        """
        for rank, retrieved_doc in enumerate(output, start=1):
            if self._is_similar(retrieved_doc, ground_truth):
                return 1.0 / rank
        return 0.0
    

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