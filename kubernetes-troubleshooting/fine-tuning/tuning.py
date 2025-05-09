from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

status = client.fine_tuning.jobs.retrieve("ftjob-JWV29PZ5S6EyEeGCIyJvxEo3")
print(status.status)  # Should become 'succeeded' if successful
print(status.fine_tuned_model)  # This is the actual model ID you will use
