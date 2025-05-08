import json
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from metrics.documentation_metrics import DocumentationMetrics


def extract_text_from_chunk(chunk):
    if not isinstance(chunk, str):
        return ""

    if "[SOURCE:" in chunk:
        parts = chunk.split("]", 1)
        if len(parts) > 1:
            return parts[1].strip()

    if chunk.startswith("Chunk ID"):
        parts = chunk.split(":", 1)
        if len(parts) > 1:
            chunk = parts[1].strip()

    return chunk


def preprocess_docs(docs):

    processed_docs = []
    for doc in docs:
        text = doc.replace('\n', ' ').strip()
        text = ' '.join(text.split())
        processed_docs.append(text)
    return processed_docs


def evaluate_retrieval_metrics(results_dir="results", ground_truth_dir="crash-cases/ground-truth-answers", eval_output_dir="eval-results"):
    """Evaluate retrieval metrics for the results of the HyDE model and baseline"""
    metrics = DocumentationMetrics()
    results_summary = {}
    all_metrics = {
        "baseline": {"precision@3": [], "mrr": [], "bertscore": []},
        "hyde": {"precision@3": [], "mrr": [], "bertscore": []}
    }

    os.makedirs(eval_output_dir, exist_ok=True)

    for result_file in glob.glob(os.path.join(results_dir, "*_results.json")):
        case_name = os.path.basename(result_file).split("_results.json")[0]

        with open(result_file, "r", encoding="utf-8") as f:
            retrieval_results = json.load(f)

        ground_truth_file = os.path.join(ground_truth_dir, f"ANS-{case_name}.json")
        if not os.path.exists(ground_truth_file):
            print(f"⚠️ Brak pliku ground truth dla {case_name}")
            continue

        with open(ground_truth_file, "r", encoding="utf-8") as f:
            ground_truth = json.load(f)

        ground_truth_docs = ground_truth.get("documentation", [])
        ground_truth_docs = preprocess_docs(ground_truth_docs)

        baseline_docs_raw = [extract_text_from_chunk(chunk) for chunk in retrieval_results.get("baseline", [])]
        hyde_docs_raw = [extract_text_from_chunk(chunk) for chunk in retrieval_results.get("hyde", [])]

        baseline_docs = preprocess_docs(baseline_docs_raw)
        hyde_docs = preprocess_docs(hyde_docs_raw)

        case_metrics = {
            "baseline": {
                "precision@3": metrics.precision_at_k(ground_truth_docs, baseline_docs, k=3),
                "mrr": metrics.mean_reciprocal_rank(ground_truth_docs, baseline_docs),
                "bertscore": metrics.compute_bertscore(baseline_docs[:3], ground_truth_docs)
            },
            "hyde": {
                "precision@3": metrics.precision_at_k(ground_truth_docs, hyde_docs, k=3),
                "mrr": metrics.mean_reciprocal_rank(ground_truth_docs, hyde_docs),
                "bertscore": metrics.compute_bertscore(hyde_docs[:3], ground_truth_docs)
            }
        }

        results_summary[case_name] = case_metrics

        for method in ["baseline", "hyde"]:
            for metric_name in ["precision@3", "mrr", "bertscore"]:
                all_metrics[method][metric_name].append(case_metrics[method][metric_name])

        print(f"\n📊 Metryki dla {case_name}:")
        print(f"  Baseline - P@3: {case_metrics['baseline']['precision@3']:.3f}, "
              f"MRR: {case_metrics['baseline']['mrr']:.3f}, "
              f"BERTScore: {case_metrics['baseline']['bertscore']:.3f}")
        print(f"  HyDE     - P@3: {case_metrics['hyde']['precision@3']:.3f}, "
              f"MRR: {case_metrics['hyde']['mrr']:.3f}, "
              f"BERTScore: {case_metrics['hyde']['bertscore']:.3f}")

    # calculate averages
    averages = {
        "baseline": {
            metric: np.mean(values) for metric, values in all_metrics["baseline"].items()
        },
        "hyde": {
            metric: np.mean(values) for metric, values in all_metrics["hyde"].items()
        }
    }

    results_summary["_average"] = averages

    print("\n📈 Średnie metryki:")
    print(f"  Baseline - P@3: {averages['baseline']['precision@3']:.3f}, "
          f"MRR: {averages['baseline']['mrr']:.3f}, "
          f"BERTScore: {averages['baseline']['bertscore']:.3f}")
    print(f"  HyDE     - P@3: {averages['hyde']['precision@3']:.3f}, "
          f"MRR: {averages['hyde']['mrr']:.3f}, "
          f"BERTScore: {averages['hyde']['bertscore']:.3f}")

    with open(os.path.join(eval_output_dir, "metrics_summary.json"), "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)

    generate_comparison_charts(results_summary, eval_output_dir)
    generate_radar_chart(averages, eval_output_dir)

    return results_summary


def generate_comparison_charts(results_summary, output_dir="eval-retrival-results"):
    """Generowanie wykresów porównawczych dla metod wyszukiwania"""
    cases = [case for case in results_summary.keys() if not case.startswith("_")]
    metrics = ["precision@3", "mrr", "bertscore"]

    for metric in metrics:
        baseline_values = [results_summary[case]["baseline"][metric] for case in cases]
        hyde_values = [results_summary[case]["hyde"][metric] for case in cases]

        x = np.arange(len(cases))
        width = 0.35

        fig, ax = plt.subplots(figsize=(12, 6))
        baseline_bars = ax.bar(x - width / 2, baseline_values, width, label='Baseline', color='skyblue')
        hyde_bars = ax.bar(x + width / 2, hyde_values, width, label='HyDE', color='orange')

        ax.set_title(f'Porównanie {metric} dla różnych przypadków')
        ax.set_xticks(x)
        ax.set_xticklabels(cases, rotation=45, ha='right')
        ax.set_ylim(0, 1.0)
        ax.legend()

        for i, v in enumerate(baseline_values):
            ax.text(i - width / 2, v + 0.02, f'{v:.2f}', ha='center', fontsize=8)
        for i, v in enumerate(hyde_values):
            ax.text(i + width / 2, v + 0.02, f'{v:.2f}', ha='center', fontsize=8)

        fig.tight_layout()
        plt.savefig(os.path.join(output_dir, f'comparison_{metric}.png'))
        plt.close()

    print(f"✅ Wykresy porównawcze zapisane w {output_dir}")


def generate_radar_chart(averages, output_dir="eval-retrival-results"):
    """Generowanie wykresu radarowego dla porównania średnich metryk"""
    metrics = ["precision@3", "mrr", "bertscore"]
    baseline_values = [averages["baseline"][m] for m in metrics]
    hyde_values = [averages["hyde"][m] for m in metrics]

    # Utwórz wykres radarowy
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()

    # Zamknij okrąg
    baseline_values += [baseline_values[0]]
    hyde_values += [hyde_values[0]]
    angles += [angles[0]]
    metrics += [metrics[0]]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, baseline_values, 'o-', linewidth=2, label='Baseline', color='skyblue')
    ax.fill(angles, baseline_values, alpha=0.25, color='skyblue')
    ax.plot(angles, hyde_values, 'o-', linewidth=2, label='HyDE', color='orange')
    ax.fill(angles, hyde_values, alpha=0.25, color='orange')

    ax.set_thetagrids(np.degrees(angles), metrics)
    ax.set_ylim(0, 1)
    ax.grid(True)
    ax.legend(loc='upper right')
    ax.set_title('Porównanie średnich metryk dla metod wyszukiwania')

    plt.savefig(os.path.join(output_dir, 'radar_comparison.png'))
    plt.close()

    print(f"✅ Wykres radarowy zapisany w {output_dir}")


if __name__ == "__main__":
    evaluate_retrieval_metrics()