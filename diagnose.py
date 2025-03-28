import json
from datetime import datetime, timedelta
import os

# Simulate integration with an open-source LLM (e.g., LLaMA, Mistral via transformers)
# In real use, you'd replace this with actual model inference logic
def call_fake_llm(prompt: str) -> str:
    # Simulated response for demonstration
    return (
        "✅ Cluster health looks mostly okay.\n"
        "⚠️ Issue detected: 'api-server-pod' has restarted 3 times in the last 15 minutes.\n"
        "📌 Suggestion: Check memory usage and investigate recent image changes.\n"
    )

def load_latest_snapshots(path="/mnt/data/k8s_fake_snapshots.json", max_age_minutes=10):
    if not os.path.exists(path):
        print("❌ Snapshot file not found.")
        return []

    try:
        with open(path, "r") as f:
            snapshots = json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Snapshot file is being written to. Try again shortly.")
        return []

    recent_cutoff = datetime.utcnow() - timedelta(minutes=max_age_minutes)
    recent_snapshots = [
        s for s in snapshots
        if datetime.fromisoformat(s["timestamp"].replace("Z", "")) > recent_cutoff
    ]
    return recent_snapshots

def format_prompt(snapshots):
    if not snapshots:
        return None

    latest = snapshots[-1]

    prompt = f"""
You are a Kubernetes cluster troubleshooting assistant.

Below is a snapshot of the system taken at {latest['timestamp']}. Use the information to:
1. Summarize the health of the cluster.
2. Identify any possible issues.
3. Recommend next actions if anything looks wrong.

--- PODS ---
{json.dumps(latest['pods'], indent=2)}

--- LOGS ---
{latest['logs'][:1000]}  # limit to first 1000 characters

--- EVENTS ---
{latest['events'][:1000]}

--- NODE STATUS ---
{latest['node'][:1000]}

Respond with a summary, any detected problems, and recommendations.
"""
    return prompt

def main():
    print("🔍 Loading latest snapshots for diagnosis...")
    snapshots = load_latest_snapshots()

    if not snapshots:
        print("⚠️ No usable snapshot found.")
        return

    prompt = format_prompt(snapshots)
    if not prompt:
        print("⚠️ Could not generate prompt.")
        return

    print("🧠 Sending prompt to LLM...")
    response = call_fake_llm(prompt)

    print("\n🩺 LLM Diagnosis:\n")
    print(response)

if __name__ == "__main__":
    main()
