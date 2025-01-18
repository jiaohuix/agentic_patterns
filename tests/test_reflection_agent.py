import os

from openai import OpenAI
from dotenv import load_dotenv

from agentic_patterns import ReflectionAgent

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE')


client = OpenAI(
api_key=OPENAI_API_KEY,
base_url=OPENAI_API_BASE
)
model_name = "Qwen/Qwen2.5-Coder-7B-Instruct"

agent = ReflectionAgent(client=client,
        model=model_name)

generation_system_prompt = "You are a Python programmer tasked with generating high quality Python code"

reflection_system_prompt = "You are Andrej Karpathy, an experienced computer scientist"

user_msg = "Generate a Python implementation of the Merge Sort algorithm"

final_response = agent.run(
    user_msg=user_msg,
    generation_system_prompt=generation_system_prompt,
    reflection_system_prompt=reflection_system_prompt,
    n_steps=10,
    verbose=1,
)