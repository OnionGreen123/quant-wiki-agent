
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_utils.llm_client import LLMClient

# 将prompt.yaml中的内容读取出来
with open("/Users/fengwenjun/Local/CODE/Automatic tools for LLMQuant/quant-wiki-folder/quant-wiki-agent/prompts/complete_library.yaml", "r") as f:
    prompt = f.read()

llm_client = LLMClient(system_prompt=prompt)

with open("/Users/fengwenjun/Local/CODE/Automatic tools for LLMQuant/quant-wiki-folder/quant-wiki/docs/library/book/ Mathematical Techniques in Finance_ An Introduction (2022, Wiley)/index.md", "r") as f:
    article = f.read()
response = llm_client.call(article, temperature=0.1, reasoning_effort="medium")
print("response: ", response)