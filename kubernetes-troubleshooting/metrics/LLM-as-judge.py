import openai
import re

def llm_as_judge(output: str, golden: str, question: str = None, model="gpt-4") -> float:
    """
    Uses an LLM as a judge to score how well 'output' matches the 'golden' answer.
    Optionally include the original question for context.
    Returns a float score (e.g., 0–10).
    """
    # Compose the evaluation prompt
    prompt = f"""
You are an expert evaluator. Your task is to provide a 'total rating' scoring how well the system_answer matches the golden reference answer.
Give your answer as a float on a scale of 0 to 10, where 0 means that the system_answer is not helpful at all, and 10 means that the answer completely and helpfully matches the golden answer.

Provide your feedback as follows:

Feedback:::
Total rating: (your rating, as a float between 0 and 10)

Now here are the answers to evaluate.
Golden answer: {golden}
System answer: {output}
Feedback:::
Total rating:
"""
    # Call the LLM (replace with your LLM API call)
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=32,
        temperature=0.0,
    )
    answer = response['choices'][0]['message']['content']

    # Extract the score using regex
    match = re.search(r"Total rating:\s*([0-9]+(?:\.[0-9]+)?)", answer)
    if match:
        return float(match.group(1))
    else:
        raise ValueError("LLM did not return a valid score.")

# Example usage:
# score = llm_as_judge(output="...", golden="...", question="...")

