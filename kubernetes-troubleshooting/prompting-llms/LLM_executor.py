from typing import Literal
import openai
import anthropic 
from huggingface_hub import InferenceClient

import transformers

import os
import requests
import torch

from dotenv import load_dotenv
load_dotenv()

class LLMExecutor:
    def __init__(self, model: Literal["gpt-4", "gpt-3.5-turbo", "claude-3", "mistral"]):
        self.model = model
        self.api_keys = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "huggingface": os.getenv("HF_TOKEN"),
        }

    def run(self, prompt: str) -> str:
        if self.model in ["gpt-4", "gpt-3.5-turbo"]:
            return self._query_openai(prompt)
        elif self.model == "claude-3":
            return self._query_claude(prompt)
        elif self.model == "mistral":
            return self._query_mistral(prompt)
        elif self.model == "llama":
            return self._query_llama(prompt)
        else:
            raise ValueError(f"Unsupported model: {self.model}")

    def _query_openai(self, prompt: str) -> str:
        client = openai.OpenAI(api_key=self.api_keys["openai"])

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        return response.choices[0].message.content

    def _query_claude(self, prompt: str) -> str: 
        client = anthropic.Anthropic(api_key=self.api_keys["anthropic"])
        response = client.messages.create(
            model="claude-3-opus-20240229",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024
        )
        return response.content[0].text
    
    
    
    def _query_llama(self, prompt: str) -> str:
        # model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

        # # Create a pipeline for text generation
        # pipeline = transformers.pipeline(
        #     "text-generation",
        #     model=model_id,
        #     model_kwargs={"torch_dtype": torch.bfloat16},
        #     device_map="auto",  # or "cuda" if you want to force GPU
        #     return_full_text=False,
        # )

        # # Prepare your chat messages
        # messages = [
        #     {"role": "system", "content": "You are a helpful assistant."},
        #     {"role": "user", "content": "What is the capital of France?"},
        # ]

        # # Apply the chat template to format the prompt
        # prompt = pipeline.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        # # Generate a response
        # outputs = pipeline(prompt, max_new_tokens=256)
        # print(outputs[0]["generated_text"])
        pass

    def _query_mistral(self, prompt: str) -> str:
        raise NotImplementedError("Add mistral client if needed.")
