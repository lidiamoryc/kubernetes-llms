from pathlib import Path

from data_preprocessing import KubernetesPromptBuilder 
from LLM_executor import LLMExecutor

import re 
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metrics.documentation_metrics import DocumentationMetrics


# iterating and building prompts for every example

current_dir = Path(__file__).resolve().parent

json_dir = current_dir.parent / "crash-cases" / "hardcoded-database"

results_dir = current_dir / "results"
results_dir.mkdir(exist_ok=True)

# Helper to append to a JSON list
def append_to_json(file_path, new_data):
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(new_data)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

for json_file in json_dir.glob("*.json"):

    prompt_builder = KubernetesPromptBuilder(json_file)

    zero_shot_prompt = prompt_builder.build_prompt_for_documentation( mode="zero-shot")
    
    one_shot_prompt = prompt_builder.build_prompt_for_documentation( mode="one-shot")

    few_shot_prompt = prompt_builder.build_prompt_for_documentation( mode="few-shot")

    openai_executor = LLMExecutor("gpt-3.5-turbo")
    output_z = openai_executor.run(zero_shot_prompt)
    append_to_json(results_dir / "zero_openai.json", output_z)

    output_o = openai_executor.run(one_shot_prompt)
    append_to_json(results_dir / "one_openai.json", output_o)

    output_f = openai_executor.run(few_shot_prompt)
    append_to_json(results_dir / "few_openai.json", output_f)


#     claude_executor = LLMExecutor("claude-3")
#     output_z = claude_executor.run(zero_shot_prompt)
#     append_to_json(results_dir / "zero_claude.json", output_z)

#     output_o = claude_executor.run(one_shot_prompt)
#     append_to_json(results_dir / "one_claude.json", output_o)


#     output_f = claude_executor.run(few_shot_prompt)
#     append_to_json(results_dir / "few_claude.json", output_f)


#     llama_executor = LLMExecutor("llama")
#     output_z = llama_executor.run(zero_shot_prompt)
#     append_to_json(results_dir / "zero_llama.json", output_z)
#     print(output_z)

#     output_o = llama_executor.run(one_shot_prompt)
#     append_to_json(results_dir / "one_llama.json", output_o)

#     output_f = llama_executor.run(few_shot_prompt)
#     append_to_json(results_dir / "few_llama.json", output_f)
  


def split_documentation_blocks(text: str) -> list:
    """
    Splits a string containing numbered documentation excerpts into individual entries.
    Assumes format like '1. Title\n"Excerpt"' repeated.
    """
    # Normalize numbering (e.g. "1.", "2." etc.)
    blocks = re.split(r'\n?\s*\d+\.\s+', text.strip())
    return [b.strip() for b in blocks if b.strip()]



answers_dir = current_dir.parent / "crash-cases" / "ground-truth-answers"



llama_outputs_path = current_dir / "results" / "zero_llama.json"
metrics = DocumentationMetrics()

with open(llama_outputs_path, "r", encoding="utf-8") as f:
    llama_outputs = json.load(f)

bert_scores_for_zero_shot_llama = []
pk_for_zero_shot_llama = []
mrr_for_zero_shot_llama = []

# Iterate through folders in parallel
for idx, answer_file in enumerate(answers_dir.glob("*.json")):
    with open(answer_file, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    gt_docs = ground_truth["documentation"]         
    llm_output = llama_outputs[idx]                 

    pred = split_documentation_blocks(llm_output)

    bert_score = metrics.compute_bertscore(pred, gt_docs)
    precision = metrics.precision_at_k(gt_docs, pred)
    mrr = metrics.mean_reciprocal_rank(gt_docs, pred)

    print(bert_score, precision, mrr)

    bert_scores_for_zero_shot_llama.append(bert_score)
    pk_for_zero_shot_llama.append(precision)
    mrr_for_zero_shot_llama.append(mrr)

   
def average(values):
    return sum(values) / len(values) if values else 0.0

avg_bert = average(bert_scores_for_zero_shot_llama)
avg_pk = average(pk_for_zero_shot_llama)
avg_mrr = average(mrr_for_zero_shot_llama)

print(avg_bert, avg_pk, avg_mrr)


# Execute the error explanation stage using the best-performing model output
def run_error_explanation_stage():
    """
    Execute the error explanation stage using the documentation from the best model
    and generate comprehensive explanations and solutions.
    """
    print("\n=== Running Error Explanation Stage ===\n")
    
    # Based on benchmark results, we'll use the OpenAI GPT-3.5-turbo model outputs
    # which showed the best performance in the documentation retrieval stage
    best_model_outputs_path = results_dir / "one_openai.json"  # Assuming one-shot is best
    
    if not best_model_outputs_path.exists():
        print(f"Error: Best model output file {best_model_outputs_path} not found!")
        return
    
    with open(best_model_outputs_path, "r", encoding="utf-8") as f:
        best_model_outputs = json.load(f)
    
    error_explanation_results = []
    
    # Process each case
    for idx, json_file in enumerate(json_dir.glob("*.json")):
        print(f"Processing error explanation for {json_file.name}...")
        
        # Get the documentation output from the best model
        if idx < len(best_model_outputs):
            documentation_output = best_model_outputs[idx]
        else:
            print(f"Warning: No documentation output found for {json_file.name}")
            continue
        
        # Create prompt builder for this case
        prompt_builder = KubernetesPromptBuilder(json_file)
        
        # Build the error explanation prompt
        error_explanation_prompt = prompt_builder.build_prompt_for_error_explanation(documentation_output)
        
        # Execute the prompt with the best model (GPT-3.5-turbo)
        openai_executor = LLMExecutor("gpt-3.5-turbo")
        explanation_output = openai_executor.run(error_explanation_prompt)
        
        # Store the result
        result_entry = {
            "case": json_file.stem,
            "documentation": documentation_output,
            "explanation": explanation_output
        }
        
        error_explanation_results.append(result_entry)
        
        # Save individual result
        append_to_json(results_dir / "error_explanation_results.json", result_entry)
        
        print(f"✅ Error explanation completed for {json_file.name}")
    
    print(f"\nCompleted error explanation stage for {len(error_explanation_results)} cases")
    
    return error_explanation_results

# Uncomment to run the error explanation stage
# run_error_explanation_stage()

