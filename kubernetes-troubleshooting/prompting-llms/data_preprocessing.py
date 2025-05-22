import json
import os
import json
import os

from prompts.zero_shot import get_zero_shot_prompt_for_solution, get_zero_shot_prompt_for_documentation
from prompts.one_shot import get_one_shot_prompt_for_solution, get_one_shot_prompt_for_documentation
from prompts.few_shot import get_few_shot_prompt_for_solution, get_few_shot_prompt_for_documentation


class KubernetesPromptBuilder:
    def __init__(self, json_path: str):
        if not os.path.isfile(json_path):
            raise FileNotFoundError(f"File not found: {json_path}")
        
        with open(json_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        
        self._preprocess()


    def _preprocess(self):
        logs = self.data.get("logs", "")
        self.filtered_logs = [
            line.split(" ", 3)[-1]
            for line in logs.split("\n")
            if "ERROR" in line or "FATAL" in line
        ]

        self.critical_events = []
        for event in self.data.get("events") or []:
            if any(k in event for k in ["Failed", "Back-off", "Warning"]):
                parts = event.split(": ", 1)
                self.critical_events.append(parts[1] if len(parts) > 1 else parts[0])

        self.probe_note = ""
        probe_config = self.data.get("probe_config") or {}
        if probe_config.get("timeoutSeconds", 1) < 2:
            self.probe_note = "Probe timeout might be too short for database dependencies"


    def build_prompt_for_documentation(self, mode="zero-shot") -> str:

        if mode == "zero-shot":

            return get_zero_shot_prompt_for_documentation(self.filtered_logs, self.filtered_logs, json.dumps(self.data.get('env', {})), self.probe_note)
        
        if mode == "one-shot":

            return get_one_shot_prompt_for_documentation(self.filtered_logs, self.filtered_logs, json.dumps(self.data.get('env', {})), self.probe_note)

        if mode == "few-shot":
    
            return get_few_shot_prompt_for_documentation(self.filtered_logs, self.filtered_logs, json.dumps(self.data.get('env', {})), self.probe_note)
        
        else:
            raise ValueError("Invalid mode. Choose 'zero-shot', 'one-shot', or 'few-shot'")
                
    def build_prompt_for_error_explanation(self, documentation_excerpts) -> str:
        from prompts.zero_shot import get_zero_shot_prompt_for_error_explanation
        
        return get_zero_shot_prompt_for_error_explanation(
            self.filtered_logs, 
            self.filtered_logs, 
            json.dumps(self.data.get('env', {})), 
            self.probe_note,
            documentation_excerpts
        )
        


    def build_prompt_for_solution(self, documentation_excerpts, mode="zero-shot") -> str:

        if mode == "zero-shot":
            
            return get_zero_shot_prompt_for_solution(self.filtered_logs, self.filtered_logs, json.dumps(self.data.get('env', {})), self.probe_note, documentation_excerpts)
        
            #TODO: think if we should parse it through the Pydantic for structured output?
            #TODO: is the ground truth in the correct format? we can adjust it

        elif mode == "one-shot":

            return get_one_shot_prompt_for_solution(self.filtered_logs, self.filtered_logs, json.dumps(self.data.get('env', {})), self.probe_note, documentation_excerpts)
        
        elif mode == "few-shot":
            
            return get_few_shot_prompt_for_solution(self.filtered_logs, self.filtered_logs, json.dumps(self.data.get('env', {})), self.probe_note, documentation_excerpts)

        else:
            raise ValueError("Invalid mode. Choose 'zero-shot', 'one-shot', or 'few-shot'")