openai tools fine_tunes.prepare_data -f training-data.jsonl
openai api fine_tunes.create -t training-data_prepared.jsonl -m gpt-3.5-turbo
openai api fine_tunes.create -t training-data_prepared.jsonl -m gpt-3.5-turbo -s "k8s-troubleshooter-v1"

# list all the fine-tunes:
openai api fine_tunes.list
