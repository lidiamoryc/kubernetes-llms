import time
import json
import os
from datetime import datetime
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM


model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
print(f"Loading LLaMA model: {model_id}...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
# model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", load_in_4bit=True)
model = AutoModelForCausalLM.from_pretrained(model_id)
generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

LOG_FILE = r"C:\Users\Lidia\Desktop\k8sgpt\logs\k8s_fake_logs.log"
SNAPSHOT_FILE = r"C:\Users\Lidia\Desktop\k8sgpt\snapshots\k8s_fake_snapshots.json"

# reading last N lines from logs
def read_last_logs(n=10):
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        lines = f.readlines()
    return lines[-n:]

# reading last N+1 snapshots
def read_snapshots(n=3):
    if not os.path.exists(SNAPSHOT_FILE):
        return []
    try:
        with open(SNAPSHOT_FILE, "r") as f:
            all_snapshots = json.load(f)
    except json.JSONDecodeError:
        return []
    return all_snapshots[-(n+1):]


def build_prompt(snapshots, logs):
    if not snapshots:
        return None

    latest = snapshots[-1]

    return f"""
            You are a Kubernetes troubleshooting expert.

            Here is the current state of the cluster at {latest['timestamp']}:

            --- Pod data ---
            {json.dumps(latest['pods'], indent=2)}

            --- Logs (last 10 lines) ---
            {"".join(logs)}

            --- Events ---
            {latest['events'][:1000]}

            --- Node Status ---
            {latest['node'][:1000]}

            --- Additional Context ---
            This snapshot is based on simulated cluster state and log data.

            ### Task
            Analyze the cluster and respond with:
            1. Summary of the health of the system
            2. Any issues detected
            3. Recommended actions

            ### Response:
            """


def main_loop(interval=60):

    while True:
        print("Reading logs and snapshots...")
        logs = read_last_logs()
        snapshots = read_snapshots()

        prompt = build_prompt(snapshots, logs)
        if not prompt:
            print("Unable to build prompt. Retrying...")
            time.sleep(interval)
            continue

        print("Sending prompt to LLM...")
        result = generator(prompt, max_new_tokens=500, do_sample=True, temperature=0.7)[0]["generated_text"]

        print("\nLLM Diagnosis:")
        print("=" * 80)
        print(result.strip())
        print("=" * 80)

        ##################
        # static diagnosis
        ##################
        
        ##################
        # # logic of calling the LLM-troubleshooting if needed 
        ##################
        
        time.sleep(interval)

if __name__ == "__main__":
    main_loop()

# import json
# from datetime import datetime, timedelta
# import os

# # Simulate integration with an open-source LLM (e.g., LLaMA, Mistral via transformers)
# # In real use, you'd replace this with actual model inference logic
# def call_fake_llm(prompt: str) -> str:
#     # Simulated response for demonstration
#     return (
#         "✅ Cluster health looks mostly okay.\n"
#         "⚠️ Issue detected: 'api-server-pod' has restarted 3 times in the last 15 minutes.\n"
#         "📌 Suggestion: Check memory usage and investigate recent image changes.\n"
#     )

# def load_latest_snapshots(path="/mnt/data/k8s_fake_snapshots.json", max_age_minutes=10):
#     if not os.path.exists(path):
#         print("❌ Snapshot file not found.")
#         return []

#     try:
#         with open(path, "r") as f:
#             snapshots = json.load(f)
#     except json.JSONDecodeError:
#         print("⚠️ Snapshot file is being written to. Try again shortly.")
#         return []

#     recent_cutoff = datetime.utcnow() - timedelta(minutes=max_age_minutes)
#     recent_snapshots = [
#         s for s in snapshots
#         if datetime.fromisoformat(s["timestamp"].replace("Z", "")) > recent_cutoff
#     ]
#     return recent_snapshots

# def format_prompt(snapshots):
#     if not snapshots:
#         return None

#     latest = snapshots[-1]

#     prompt = f"""
# You are a Kubernetes cluster troubleshooting assistant.

# Below is a snapshot of the system taken at {latest['timestamp']}. Use the information to:
# 1. Summarize the health of the cluster.
# 2. Identify any possible issues.
# 3. Recommend next actions if anything looks wrong.

# --- PODS ---
# {json.dumps(latest['pods'], indent=2)}

# --- LOGS ---
# {latest['logs'][:1000]}  # limit to first 1000 characters

# --- EVENTS ---
# {latest['events'][:1000]}

# --- NODE STATUS ---
# {latest['node'][:1000]}

# Respond with a summary, any detected problems, and recommendations.
# """
#     return prompt

# def main():
#     print("🔍 Loading latest snapshots for diagnosis...")
#     snapshots = load_latest_snapshots()

#     if not snapshots:
#         print("⚠️ No usable snapshot found.")
#         return

#     prompt = format_prompt(snapshots)
#     if not prompt:
#         print("⚠️ Could not generate prompt.")
#         return

#     print("🧠 Sending prompt to LLM...")
#     response = call_fake_llm(prompt)

#     print("\n🩺 LLM Diagnosis:\n")
#     print(response)

# if __name__ == "__main__":
#     main()
