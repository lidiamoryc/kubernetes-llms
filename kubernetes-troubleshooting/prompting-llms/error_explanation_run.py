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

def run_error_explanation_stage(use_answers_json=False):
    """
    Execute the error explanation stage using the documentation from the best model
    or from the ANS-*.json answer files.
    
    Args:
        use_answers_json (bool): If True, use documentation from ANS-*.json files
                                instead of model outputs
    """
    print("\n=== Running Error Explanation Stage ===\n")

    answers_dir = current_dir.parent / "crash-cases" / "ground-truth-answers"
    
    error_explanation_results = []
    
    # Process each case
    for json_file in json_dir.glob("*.json"):
        case_name = json_file.stem
        print(f"Processing error explanation for {json_file.name}...")
        
        # Get documentation either from answers JSON or model outputs
        if use_answers_json:
            # Get documentation from answer JSON file
            answer_file = answers_dir / f"ANS-{case_name}.json"
            
            if not answer_file.exists():
                print(f"Warning: Answer file {answer_file} not found for {case_name}")
                continue
            
            try:
                with open(answer_file, "r", encoding="utf-8") as f:
                    answer_data = json.load(f)
                
                # Format documentation for prompt
                if isinstance(answer_data["documentation"], list):
                    documentation_output = "\n\n".join(answer_data["documentation"])
                else:
                    documentation_output = answer_data["documentation"]
                
                print(f"Using documentation from answer file: {answer_file}")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error reading answer file {answer_file}: {e}")
                continue
        else:
            # Use model outputs as before
            best_model_outputs_path = results_dir / "one_openai.json"  # Assuming one-shot is best
            
            if not best_model_outputs_path.exists():
                print(f"Error: Best model output file {best_model_outputs_path} not found!")
                return
            
            try:
                with open(best_model_outputs_path, "r", encoding="utf-8") as f:
                    best_model_outputs = json.load(f)
                
                # Find matching case in model outputs
                case_output = None
                for output in best_model_outputs:
                    if output.get("case") == case_name or output.get("file", "").startswith(case_name):
                        case_output = output
                        break
                
                if not case_output:
                    idx = next((i for i, item in enumerate(best_model_outputs) if json_file.name in item.get("file", "")), None)
                    if idx is not None and idx < len(best_model_outputs):
                        documentation_output = best_model_outputs[idx]
                    else:
                        print(f"Warning: No documentation output found for {case_name}")
                        continue
                else:
                    documentation_output = case_output
            except (json.JSONDecodeError, IndexError) as e:
                print(f"Error reading model outputs: {e}")
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
            "case": case_name,
            "documentation": documentation_output,
            "explanation": explanation_output
        }
        
        error_explanation_results.append(result_entry)
        
        # Save individual result with appropriate filename
        output_filename = "error_explanation_from_answers.json" if use_answers_json else "error_explanation_results.json"
        append_to_json(results_dir / output_filename, result_entry)
        
        print(f"✅ Error explanation completed for {json_file.name}")
    
    print(f"\nCompleted error explanation stage for {len(error_explanation_results)} cases")
    print(f"Results saved to {results_dir / (output_filename if 'output_filename' in locals() else 'error_explanation_results.json')}")
    
    return error_explanation_results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run error explanation using documentation from model outputs or answer files")
    parser.add_argument("--use-answers", action="store_true", 
                        help="Use documentation from ANS-*.json files instead of model outputs")
    
    args = parser.parse_args()
    
    run_error_explanation_stage(use_answers_json=args.use_answers)
