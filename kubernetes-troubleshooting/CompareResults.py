import json
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from deepeval.evaluate import evaluate  # module-level evaluate function
from tabulate import tabulate


def load_results(file_path):
    """Load JSON results from the specified file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_responses(results, ground_truth, problem_description):
    """
    Compare responses from different methods using DeepEval.
    Use the provided ground truth as the expected output.
    """
    methods = ["baseline", "hyde"]
    comparisons = {}

    # Create a list of metrics.
    relevancy_metric = AnswerRelevancyMetric(model="gpt-3.5-turbo")
    metrics = [relevancy_metric]

    for method in methods:
        method_outputs = results.get(method)
        if not method_outputs or not isinstance(method_outputs, list):
            print(f"Skipping method '{method}': results not found or incorrect format.")
            comparisons[method] = None
            continue

        # Build test cases: use the same ground truth for every test case.
        test_cases = []
        for output in method_outputs:
            test_cases.append(
                LLMTestCase(
                    input=problem_description,  # common input for context
                    actual_output=output,
                    expected_output=ground_truth
                )
            )

        # Evaluate the test case(s)
        eval_result = evaluate(test_cases, metrics=metrics, use_cache=False)

        # Aggregate scores for the method
        scores = [
            metric_data.score
            for test_result in eval_result.test_results
            for metric_data in test_result.metrics_data
            if metric_data.score is not None
        ]
        avg_score = sum(scores) / len(scores) if scores else None
        comparisons[method] = avg_score

    return comparisons



if __name__ == "__main__":
    # Path to the results file (adjust as needed)
    file_path = "/Users/damianotto/PycharmProjects/kubernetes-llms/kubernetes-troubleshooting/results/ConfigMap_problem_results.json"

    # Load retrieval results
    results = load_results(file_path)

    # Define your diagnostic problem description (context for evaluation)
    problem_description = (
        "A Node.js web app deployed via a Deployment in Kubernetes is failing to start because "
        "the app cannot find the config file injected via a ConfigMap mounted at /app/config.json. "
        "The logs show an error 'ENOENT: no such file or directory' and kubectl describe indicates that "
        "the ConfigMap 'web-app-config' is not found. Diagnose the issue and suggest a fix."
    )

    # Set the ground truth answer according to Kubernetes documentation.
    ground_truth = (
        """To resolve the issue, you must first ensure the ConfigMap exists and includes the correct key. For example, if you have a local file config.json, create the ConfigMap with:
kubectl create configmap web-app-config --from-file=config.json=./config.json
Then, in your pod (or Deployment) manifest, mount it as a file using a subPath:

volumeMounts:
  - name: config
    mountPath: /app/config.json
    subPath: config.json
volumes:
  - name: config
    configMap:
      name: web-app-config"""
    )

    comparison_results = compare_responses(results, ground_truth, problem_description)

    table_data = [
        [method, f"{score:.4f}" if score is not None else "N/A"]
        for method, score in comparison_results.items()
    ]

    headers = ["Method", "Avg Answer Relevancy Score vs HyDE"]
    print("\nComparison Results:")
    print(tabulate(table_data, headers=headers, tablefmt="github"))

    print("\nNote: A file named deepval-cache.json is created to cache evaluation results and reduce API calls.")
