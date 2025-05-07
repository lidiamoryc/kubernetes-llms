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

executor = LLMExecutor("llama")

output = executor.run(prompt)

print(output)



answering the documentation extraction

json_dir = current_dir.parent / "crash-cases" / "hardcoded-database"

for json_file in json_dir.glob("*.json"):
    pass


for elements in folder:
    call zero shot on gpt
    append json for zero-openai.json

    call zero shot on claude
    append json for zero-claude.json

    call zero shot on llama
    append json for zero-llama.json

    call one shot on gpt 
    append json for one-openai.json

    call one shot for claude 
    append json for one-claude.json

    call one shot for llama
    append json for one-llama.json

    call few-shot for gpt
    append json for few-openai.json

    call few-shot for claude
    appen json for few-claude.json

    call few-shot for llama
    append json for few-llama.json


for json in /results
    for element in json and golden standard - calculate documentation metric1
    append scores to File
    caount average
    
    for element in json and golden standard - calculate documentation metric2
    append scores to File
    caount average

    for element in json and golden standard - calculate documentation metric3
    append scores to File
    caount average
