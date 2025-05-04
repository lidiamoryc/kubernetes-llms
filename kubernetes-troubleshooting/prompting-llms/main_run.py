from pathlib import Path

from data_preprocessing import KubernetesPromptBuilder 
from LLM_executor import LLMExecutor

current_dir = Path(__file__).resolve().parent


### ITERATION
# json_dir = current_dir.parent / "crash-cases" / "hardcoded-database"

# # Iterate through all JSON files in the folder
# for json_file in json_dir.glob("*.json"):
#     try:
#         prompt = build_prompt_from_json(json_file)
#         print(f"\nPrompt for: {json_file.name}\n")
#         print(prompt)
#         print("\n" + "="*80 + "\n")
#     except Exception as e:
#         print(f"Failed to process {json_file.name}: {e}")



json_path = current_dir.parent / "crash-cases" / "hardcoded-database" / "CrashLoopBackOff.json"

prompt_builder = KubernetesPromptBuilder(json_path)

prompt = prompt_builder.build_prompt()

print(prompt)

executor = LLMExecutor("claude-3")

output = executor.run(prompt)

print(output)
