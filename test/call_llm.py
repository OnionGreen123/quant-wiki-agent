
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_utils.llm_client import LLMClient


llm_client = LLMClient(system_prompt="You are a helpful assistant.")

response = llm_client.call("What is the sum of the first 50 prime numbers?")
print(response)

