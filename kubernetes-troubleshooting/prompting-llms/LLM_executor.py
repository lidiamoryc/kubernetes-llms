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

# HF_TOKEN = os.getenv("HF_TOKEN"),

# from huggingface_hub import model_info
# try:
#     info = model_info("meta-llama/Meta-Llama-3.1-8B-Instruct", token=HF_TOKEN)
#     print("Access granted")
# except Exception as e:
#     print(f"Access denied: {e}")

class LLMExecutor:
    def __init__(self, model: Literal["gpt-4", "gpt-3.5-turbo", "claude-3", "llama", "mistral"]):
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
        client = InferenceClient(
            token=self.api_keys["huggingface"],
            model="meta-llama/Llama-3.1-8B-Instruct")
        
        response = client.text_generation(
            prompt, 
            max_new_tokens=256,
            temperature=0.6
        )
        return response
        

    def _query_mistral(self, prompt: str) -> str:
        raise NotImplementedError("Add mistral client if needed.")
