# import openai
# import re

# def detect_hallucinations(actual_output: str, documentation_excerpt: str, model="gpt-4") -> float:
#     """
#     Returns a hallucination score between 0 (all claims unsupported) 
#     and 1 (all claims supported by documentation).
#     """
#     prompt = f"""You are a Kubernetes documentation auditor. For each claim in the <ACTUAL OUTPUT>, check if it is fully supported by the <DOCUMENTATION EXCERPT>.
    
#     Rules:
#     1. Consider partial matches as UNSUPPORTED (e.g., "check logs" vs "use 'kubectl logs --previous'")
#     2. Ignore formatting differences (YAML vs CLI commands)
#     3. Technical specifics must match exactly (e.g., "2000m" ≠ "2 cores")
    
#     Format response as: "Supported: X/Y" where X=supported claims, Y=total claims.

#     <DOCUMENTATION EXCERPT>
#     {documentation_excerpt}
    
#     <ACTUAL OUTPUT>
#     {actual_output}
    
#     Analysis:"""
    
#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.0
#     )
#     analysis = response.choices[0].message.content
    
#     # Extract scores using regex
#     match = re.search(r"Supported:\s*(\d+)/(\d+)", analysis)
#     if match:
#         supported, total = map(int, match.groups())
#         return supported / total if total > 0 else 0.0
#     else:
#         raise ValueError("Failed to parse LLM response")

# # Example usage:
# score = detect_hallucinations(
#     actual_output="Check pod logs with 'kubectl logs' and verify service DNS",
#     documentation_excerpt="Use 'kubectl logs --previous' to check crashed pods. Verify DNS with 'nslookup <service>'."
# )
# # score = 0.5 (1/2 claims supported: DNS check matches, but missing '--previous')
