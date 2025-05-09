from pathlib import Path
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_preprocessing import KubernetesPromptBuilder
from LLM_executor import LLMExecutor
from metrics.documentation_metrics import DocumentationMetrics
import re

# Import the HyDE functionality from the retrieval module
from retrieval import retrieve_hyde, retrieve


# Directory setup
current_dir = Path(__file__).resolve().parent
json_dir = current_dir.parent / "crash-cases" / "hardcoded-database"
results_dir = current_dir / "results"
results_dir.mkdir(exist_ok=True)


def append_to_json(file_path, new_data):
    """Helper to append to a JSON list"""
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(new_data)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def split_documentation_blocks(text: str) -> list:
    """
    Splits a string containing numbered documentation excerpts into individual entries.
    Assumes format like '1. Title\n"Excerpt"' repeated.
    """
    # Normalize numbering (e.g. "1.", "2." etc.)
    blocks = re.split(r'\n?\s*\d+\.\s+', text.strip())
    return [b.strip() for b in blocks if b.strip()]


def run_hyde_retrieval():
    """
    Process each example file with HyDE-enhanced retrieval
    """
    hyde_results = []
    
    for json_file in json_dir.glob("*.json"):
        print(f"Processing {json_file.name} with HyDE...")
        # Load and preprocess the data
        prompt_builder = KubernetesPromptBuilder(json_file)
        
        # Build the query from the preprocessed data
        query = f"Error: {' '.join(prompt_builder.filtered_logs[:3])}"
        if prompt_builder.critical_events:
            query += f" Events: {' '.join(prompt_builder.critical_events[:2])}"
        if prompt_builder.probe_note:
            query += f" Note: {prompt_builder.probe_note}"
            
        # Use HyDE to enhance and retrieve
        hyde_result = retrieve_hyde(query, k=5)
        
        # Format the results for saving
        result_entry = {
            "file": json_file.name,
            "query": query,
            "hyde_query": hyde_result["hyde_query"],
            "results": hyde_result["results"]
        }
        
        hyde_results.append(result_entry)
        
        # Save individual result
        output_file = results_dir / f"hyde_{json_file.stem}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result_entry, f, indent=2)
        
        print(f"✅ HyDE results for {json_file.name} saved to {output_file}")
    
    # Save all results together
    with open(results_dir / "hyde_all_results.json", "w", encoding="utf-8") as f:
        json.dump(hyde_results, f, indent=2)
    
    return hyde_results


def evaluate_hyde_results():
    """
    Evaluate HyDE results against ground truth
    """
    answers_dir = current_dir.parent / "crash-cases" / "ground-truth-answers"
    hyde_results_path = results_dir / "hyde_all_results.json"
    
    if not hyde_results_path.exists():
        print("❌ HyDE results not found. Run run_hyde_retrieval() first.")
        return
    
    with open(hyde_results_path, "r", encoding="utf-8") as f:
        hyde_outputs = json.load(f)
    
    metrics = DocumentationMetrics()
    
    bert_scores = []
    precision_scores = []
    mrr_scores = []
    
    # Match each result with its ground truth file
    for hyde_output in hyde_outputs:
        file_stem = hyde_output["file"].split(".")[0]
        answer_file = answers_dir / f"{file_stem}.json"
        
        if not answer_file.exists():
            print(f"⚠️ Ground truth not found for {file_stem}")
            continue
        
        with open(answer_file, "r", encoding="utf-8") as f:
            ground_truth = json.load(f)
        
        gt_docs = ground_truth["documentation"]
        
        # Process HyDE results into the expected format
        pred_docs = []
        for idx, result in enumerate(hyde_output["results"], 1):
            # Extract just the content part after the Chunk ID
            content = result.split(": ", 1)[1] if ": " in result else result
            pred_docs.append(content)
        
        # Calculate metrics
        bert_score = metrics.compute_bertscore(pred_docs, gt_docs)
        precision = metrics.precision_at_k(gt_docs, pred_docs)
        mrr = metrics.mean_reciprocal_rank(gt_docs, pred_docs)
        
        print(f"Metrics for {file_stem}:")
        print(f"  BERT Score: {bert_score:.4f}")
        print(f"  Precision@k: {precision:.4f}")
        print(f"  MRR: {mrr:.4f}")
        
        bert_scores.append(bert_score)
        precision_scores.append(precision)
        mrr_scores.append(mrr)
    
    # Calculate averages
    avg_bert = sum(bert_scores) / len(bert_scores) if bert_scores else 0
    avg_precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0
    avg_mrr = sum(mrr_scores) / len(mrr_scores) if mrr_scores else 0
    
    # Save metrics
    metrics_results = {
        "individual_results": [
            {"file": hyde_outputs[i]["file"], 
             "bert_score": bert_scores[i],
             "precision": precision_scores[i],
             "mrr": mrr_scores[i]}
            for i in range(len(bert_scores))
        ],
        "average_metrics": {
            "bert_score": avg_bert,
            "precision": avg_precision,
            "mrr": avg_mrr
        }
    }
    
    with open(results_dir / "hyde_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_results, f, indent=2)
    
    print("\nAverage Metrics:")
    print(f"  BERT Score: {avg_bert:.4f}")
    print(f"  Precision@k: {avg_precision:.4f}")
    print(f"  MRR: {avg_mrr:.4f}")
    
    return metrics_results


if __name__ == "__main__":
    # Run HyDE retrieval
    hyde_results = run_hyde_retrieval()
    
    # Evaluate results
    metrics = evaluate_hyde_results()