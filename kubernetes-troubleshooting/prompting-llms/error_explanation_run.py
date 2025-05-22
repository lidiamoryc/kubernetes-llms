from pathlib import Path
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_preprocessing import KubernetesPromptBuilder
from LLM_executor import LLMExecutor

# Directory setup
current_dir = Path(__file__).resolve().parent
json_dir = current_dir.parent / "crash-cases" / "hardcoded-database"
results_dir = current_dir / "results"
results_dir.mkdir(exist_ok=True)

# Helper to append to a JSON list
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

if __name__ == "__main__":
    run_error_explanation_stage()
