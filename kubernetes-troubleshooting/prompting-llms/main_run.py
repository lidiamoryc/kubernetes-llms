from pathlib import Path

from data_preprocessing import KubernetesPromptBuilder 
from LLM_executor import LLMExecutor

import re 
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from metrics.documentation_metrics import DocumentationMetrics


# # iterating and building prompts for every example

# current_dir = Path(__file__).resolve().parent

# json_dir = current_dir.parent / "crash-cases" / "hardcoded-database"

# for json_file in json_dir.glob("*.json"):

#     prompt_builder = KubernetesPromptBuilder(json_file)

#     prompt = prompt_builder.build_prompt_for_documentation()

#     print(prompt)


## test
current_dir = Path(__file__).resolve().parent

json_dir = current_dir.parent / "crash-cases" / "hardcoded-database" / "CrashLoopBackOff.json"

prompt_builder = KubernetesPromptBuilder(json_dir)

prompt = prompt_builder.build_prompt_for_documentation()

print(prompt)

executor = LLMExecutor("llama")

output = executor.run(prompt)

print(output)


answers_dir = current_dir.parent / "crash-cases" / "ground-truth-answers" / "ANS-CrashLoopBackOff.json"

with open(answers_dir, "r", encoding="utf-8") as f:
    ground_truth = json.load(f)


gt = ground_truth["documentation"]      


def split_documentation_blocks(text: str) -> list:
    """
    Splits a string containing numbered documentation excerpts into individual entries.
    Assumes format like '1. Title\n"Excerpt"' repeated.
    """
    # Normalize numbering (e.g. "1.", "2." etc.)
    blocks = re.split(r'\n?\s*\d+\.\s+', text.strip())
    return [b.strip() for b in blocks if b.strip()]

pred = split_documentation_blocks(output)

print(gt)
print(pred)

metrics = DocumentationMetrics()


# BERTScore (semantic match)
bert_score = metrics.compute_bertscore(pred, gt)
precision = metrics.precision_at_k(gt, pred)
mrr = metrics.mean_reciprocal_rank(gt, pred)

print(bert_score, precision, mrr)













# Precision@k and MRR require exact/ID-based matching, so consider simple string overlaps:
# precision = metrics.precision_at_k_semantic(gt, pred)
# mrr = metrics.mrr_semantic(gt, pred)


# ground_truth = """

# 1. Service Discovery & DNS
# "Pods should reference Services by their DNS name (<service>.<namespace>.svc.cluster.local), not static IPs. IPs are ephemeral in Kubernetes clusters."

# 2. CrashLoopBackOff Definition
# "A pod enters CrashLoopBackOff state when its containers repeatedly crash. Check logs with kubectl logs --previous to identify the root cause."

# 3. Readiness Probe Best Practices
# *"For applications with slow startup:

# Set initialDelaySeconds longer than maximum initialization time

# timeoutSeconds should exceed expected request processing time"*

# 4. Endpoint Verification
# *"Validate service-to-pod mapping with:

# kubectl get endpoints <service-name>  
# Empty results indicate no healthy pods match service selectors."*

# 5. DNS Resolution Troubleshooting
# *"Debug DNS issues from within pods using:

# kubectl exec -it <pod> -- nslookup <service>  
# Failure indicates CoreDNS issues or missing service."*


# """


# _d_metrics = DocumentationMetrics()

# print(_d_metrics.compute_bertscore(output, ground_truth))




# answering the documentation extraction

# json_dir = current_dir.parent / "crash-cases" / "hardcoded-database"

# for json_file in json_dir.glob("*.json"):
#     pass


# for elements in folder:
#     call zero shot on gpt
#     append json for zero-openai.json

#     call zero shot on claude
#     append json for zero-claude.json

#     call zero shot on llama
#     append json for zero-llama.json

#     call one shot on gpt 
#     append json for one-openai.json

#     call one shot for claude 
#     append json for one-claude.json

#     call one shot for llama
#     append json for one-llama.json

#     call few-shot for gpt
#     append json for few-openai.json

#     call few-shot for claude
#     appen json for few-claude.json

#     call few-shot for llama
#     append json for few-llama.json


# for json in /results
#     for element in json and golden standard - calculate documentation metric1
#     append scores to File
#     caount average
    
#     for element in json and golden standard - calculate documentation metric2
#     append scores to File
#     caount average

#     for element in json and golden standard - calculate documentation metric3
#     append scores to File
#     caount average
