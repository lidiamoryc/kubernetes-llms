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



