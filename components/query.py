
from pydantic import BaseModel, Field
from components.helper import getrisky
from typing import Literal
import json
import logging
import os
import re

logger = logging.getLogger("evaluation")
SYS_INST = (
            "You are a security expert detecting pre-trained model deserialization attacks. "
            "During deserialization, a benign model should ONLY load the structure and weights of a model. "
            "Any other actions are malicious. You are a strict data auditor. Only output verified facts."
        )

# Get the first prompt
def get_input(risky):
    return (f"The provided trace consists of potentially risky globals used during deserializing a Pickle-based Pre-trained model; the safe globals are removed. The potential risky callables are: {risky}\n"
            "First, analyze the usage context of each potentially risky callable and fill in the UsageContext. "
            "Then, infer the expected execution events from the trace. "
            "Finally, justify whether the model is malicious, and populate the JSON schema: AnalysisResult.")

# Sturctured output
class UsageContext(BaseModel):
    model_config = {
        "extra": "forbid"
    }
    target: str = Field(description="The invocation or alteration target.")
    contexts: str = Field(description="Explain how the target is invoked or altered based on its arguments.")
    intention: Literal["Benign", "Malicious", "Uncertain"] = Field(description="The intention of this action.")

class AnalysisResult(BaseModel):
    model_config = {
        "extra": "forbid"
    }
    assessment: Literal["Likely benign", "Likely malicious"] = Field(description="The safety status of the assessed model object.")
    reasoning: str = Field(description="Explain why you believe it is safe/unsafe based on the usage context trace.")
    risky_trace: list[UsageContext] = Field(description="A trace of risky callable/object usage contexts.")

def query_gemini(model, risky, states):
    from google import genai
    client = genai.Client()
    # Retry LLM query until succeed
    while True:
        try:
            response = client.interactions.create(
                model=model,
                system_instruction=SYS_INST,
                input=[
                    {"type": "text", "text": get_input(risky)},
                    {"type": "text", "text": states}
                ],
                response_format={
                        "type": "text",
                        "mime_type": "application/json",
                        "schema": AnalysisResult.model_json_schema()
                },
                generation_config={"temperature": 0}
            )
            
            if response.status == "completed": 
                logger.info("Analysis result generated!")
                structured = AnalysisResult.model_validate_json(response.output_text)
                return structured.model_dump()
            else:
                logger.error(f"Run failed with status: {response.status}, retrying...")
        except Exception as e:
            logger.error(f"Error {e} during processing the response, retrying...")
            
def query_gpt(model, risky, states):
    import openai
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    while True:
        try:
            response = client.responses.parse(
                model=model,
                store=False,
                instructions=SYS_INST,
                input=[
                    {"type": "message", "role": "user", "content": get_input(risky)},
                    {"type": "message", "role": "user", "content": states}
                ],
                text_format=AnalysisResult,
                # This is only for 4.1 nano!!!
                temperature=0
            )
            if response.status == "completed": 
                logger.info("Analysis result generated!")
                return response.output_parsed.model_dump()
            else:
                logger.error(f"Run failed with status: {response.status}, retrying...")
        except Exception as e:
            raise e
            logger.error(f"Error {e} during processing the response, retrying...")
            
def query_deepinfra(model, risky, states):
    import openai
    if model.startswith("DeepSeek"): model = f"deepseek-ai/{model}"
    elif model.startswith("Llama"): model = f"meta-llama/{model}"
    elif model.startswith(("gemini", "gemma")): model = f"google/{model}"
    elif model.startswith("GLM"): model = f"zai-org/{model}"
    elif model.startswith("Qwen"): model = f"Qwen/{model}"
    client = openai.OpenAI(
        base_url="https://api.deepinfra.com/v1/openai",
        api_key=os.environ.get("DEEPINFRA_TOKEN")
        )
    while True:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYS_INST},
                    {"role": "user", "content": get_input(risky)},
                    {"role": "user", "content": states}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "AnalysisResult",
                        "strict": True,
                        "schema": AnalysisResult.model_json_schema()
                    }
                },
                temperature=0
            )
            result = json.loads(response.choices[0].message.content)
            logger.info("Analysis result generated!")
            return result
        except Exception as e:
            raise e
            
def query(model, extract_path, analysis_path):
    risky = getrisky()
    with open(extract_path, "r") as f: states = f.read()
    if model.startswith("gemini"):
        result = query_gemini(model, risky, states)
    elif model.startswith("gpt"):
        result = query_gpt(model, risky, states)
    else:
        result = query_deepinfra(model, risky, states)
    with open(analysis_path, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)