from collections import Counter
import re



class SolutionMetrics:
    def __init__(self):
        pass

    # --------------
# 1. Command Exactness
# --------------

    def extract_kubectl_commands(text):
        """Extracts kubectl commands with all flags/parameters"""
        pattern = r"kubectl\s+[\w\-]+\s+[^\n]+(?=\n|$)"
        return [cmd.strip() for cmd in re.findall(pattern, text, re.IGNORECASE)]

    def command_exactness(golden_text, generated_text):
        """Measures exact match of Kubernetes CLI commands"""
        golden_cmds = extract_kubectl_commands(golden_text)
        generated_cmds = extract_kubectl_commands(generated_text)
        
        if not golden_cmds:
            return 1.0 if not generated_cmds else 0.0
        if not generated_cmds:
            return 0.0

        # Strict match including parameters and order
        matches = sum(1 for cmd in golden_cmds if cmd in generated_cmds)
        return matches / len(golden_cmds)

    # Kubernetes Example:
    golden = """
    kubectl get endpoints database-service -n default
    kubectl exec web-pod -- nslookup database-service.default.svc.cluster.local
    """
    generated = """
    kubectl get endpoints database-service -n default
    kubectl exec web-pod -- nslookup database-service
    """
    print(command_exactness(golden, generated))  # 0.5 (second command missing FQDN)

    # --------------
    # 2. F1 Over Words (Technical Adaptation)
    # --------------


    def f1_over_words_technical(actual, golden):
        """F1 score focusing on technical terms, ignoring commands"""
        # Remove kubectl commands before comparison
        cleaned_actual = re.sub(r"kubectl\s+[\w\-]+\s+[^\n]+", "", actual)
        cleaned_golden = re.sub(r"kubectl\s+[\w\-]+\s+[^\n]+", "", golden)
        
        actual_words = re.findall(r'\w+', cleaned_actual.lower())
        golden_words = re.findall(r'\w+', cleaned_golden.lower())

        actual_counts = Counter(actual_words)
        golden_counts = Counter(golden_words)

        common = sum((actual_counts & golden_counts).values())
        if common == 0:
            return 0.0

        precision = common / sum(actual_counts.values())
        recall = common / sum(golden_counts.values())

        return 2 * (precision * recall) / (precision + recall) if (precision + recall) else 0.0

    # Kubernetes Example:
    golden_explanation = "Verify service endpoints and DNS resolution using nslookup"
    generated_explanation = "Check service endpoints and domain name resolution"
    print(f1_over_words_technical(generated_explanation, golden_explanation))  # ~0.71

    # --------------
    # 3. Hallucination Detection (Kubernetes-aware)
    # --------------
    def kubernetes_hallucination_detection(actual_steps, allowed_steps, threshold=0.6):
        """Detects non-standard troubleshooting steps"""
        penalties = 0
        for step in actual_steps:
            if not any(_step_similarity(step, allowed, threshold) for allowed in allowed_steps):
                penalties += 1
        return max(0, 1 - (penalties / len(actual_steps))) if actual_steps else 1.0

    def _step_similarity(a, b, threshold):
        """Fuzzy match using Jaccard similarity"""
        a_tokens = set(a.lower().split())
        b_tokens = set(b.lower().split())
        intersection = len(a_tokens & b_tokens)
        union = len(a_tokens | b_tokens)
        return (intersection / union) >= threshold

    # Kubernetes Example:
    allowed_steps = [
        "check service endpoints",
        "verify DNS resolution",
        "inspect pod logs with --previous flag"
    ]

    generated_steps = [
        "kubectl get endpoints",  # Valid
        "restart the node",       # Hallucination
        "check DNS with nslookup" # Valid (similar to "verify DNS resolution")
    ]

    print(kubernetes_hallucination_detection(generated_steps, allowed_steps))  # 0.666...
