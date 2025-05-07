from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Upload file
file = client.files.create(
    file=open("training-data_prepared.jsonl", "rb"),
    purpose="fine-tune"
)

# Start fine-tune
fine_tune_job = client.fine_tuning.jobs.create(
    training_file=file.id,
    model="gpt-3.5-turbo"
)

print(fine_tune_job.id)



# import jsonlines



# data = [
#     {
#         "prompt": "**Diagnostic Evidence**:\n- Critical Logs: Connection refused to DB_HOST=10.0.0.5\nDatabase unreachable - exiting\n- Cluster Events: Connection refused to DB_HOST=10.0.0.5\n- Environment Variables: {\"DB_HOST\": \"10.0.0.5\", \"DB_PORT\": \"5432\"}\n- Probe Warning: Probe timeout might be too short",
#         "completion": " 1. Service Discovery & DNS\n\"Pods should reference Services by their DNS name (<service>.<namespace>.svc.cluster.local), not static IPs.\"\n\n2. CrashLoopBackOff Definition\n\"A pod enters CrashLoopBackOff when it crashes repeatedly. Check with kubectl logs --previous.\"\n\n3. Readiness Probe Best Practices\n\"Set initialDelaySeconds longer than max init time. timeoutSeconds should exceed processing time.\""
#     },
#     {
#         "prompt": "**Diagnostic Evidence**:\n- Critical Logs: Unable to bind to port 8080\n- Events: Address already in use\n- Environment Variables: {\"PORT\": \"8080\"}",
#         "completion": " 1. Port Conflict\n\"Two containers should not bind to the same hostPort.\"\n\n2. Pod Port Exposure\n\"A pod should expose ports via containerPort.\"\n\n3. Debugging Tips\n\"Use netstat or lsof inside the container to debug port issues.\""
#     }
# ]

# # Write correctly to JSONL file
# with jsonlines.open("training-data.jsonl", mode="w") as writer:
#     for example in data:
#         writer.write(example)