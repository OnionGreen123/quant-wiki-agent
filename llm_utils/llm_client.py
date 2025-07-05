import os
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    """
    一个用于调用大语言模型的通用客户端类。
    统一使用 OpenAI 兼容的 API 接口调用各种模型。

    使用示例:
        # --- 使用 OpenAI 模型 ---
        # client_openai = LLMClient(model_name="gpt-4o", api_key="YOUR_OPENAI_API_KEY")
        # client_openai.set_system_prompt("你是一个专业的翻译家，将所有内容翻译成法语。")
        # response_openai = client_openai.call("Hello, how are you?")
        # print(f"OpenAI Response: {response_openai}")

        # --- 使用 Gemini 模型（通过 OpenAI 兼容接口）---
        # client_gemini = LLMClient(
        #     model_name="gemini-1.5-pro-latest", 
        #     api_key="YOUR_GEMINI_API_KEY",
        #     base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        # )
        # client_gemini.set_system_prompt("你是一个快乐的助手，总是在回答的结尾加上一个笑脸。")
        # response_gemini = client_gemini.call("地球到月球的距离是多少？")
        # print(f"Gemini Response: {response_gemini}")
    """
    def __init__(
        self,
        model_name: str = None,
        api_key: str = None,
        base_url: str = None,
        system_prompt: str = None
    ):
        """
        初始化 LLM 客户端。
        参数:
            model_name (str): 模型的名称, e.g., "gpt-4o", "gemini-1.5-pro-latest".
            api_key (str, optional): 对应服务商的 API Key. 若未传入则自动从环境变量读取。
            base_url (str, optional): OpenAI 兼容 API 的 Base URL. 若未传入则自动从环境变量读取。
            system_prompt (str, optional): 系统提示词。未传入时自动从环境变量读取或用默认。
        """
        self.model_name = model_name or os.environ.get("MODEL_NAME")
        self.api_key = api_key or os.environ.get("API_KEY")
        self.base_url = base_url or os.environ.get("BASE_URL")

        if not self.model_name:
            raise ValueError("model_name 必须显式指定，或在 .env 文件中设置 MODEL_NAME")
        
        # 优先使用传入的 system_prompt，否则用环境变量，否则用默认
        self.system_prompt = (
            system_prompt
            or os.environ.get("DEFAULT_SYSTEM_PROMPT")
            or "You are a helpful assistant."
        )

        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """初始化 OpenAI 客户端"""
        if not self.api_key:
            raise ValueError(f"未找到 API Key，请检查环境变量或传入参数")
        
        # 统一使用 OpenAI 客户端
        self.client = OpenAI(
            api_key=self.api_key, 
            base_url=self.base_url
        )

    def set_system_prompt(self, prompt: str):
        """
        设置一个系统级的提示词(System Prompt)。

        参数:
            prompt (str): 你希望模型扮演的角色或遵循的规则。
        """
        self.system_prompt = prompt
        print(f"System prompt 已设置为: '{prompt}'")

    def call(self, user_prompt: str, max_retries: int = 3, retry_delay: float = 1.0, **kwargs) -> str:
        """
        调用大模型并获取返回结果，支持出错自动重试。

        参数:
            user_prompt (str): 用户输入的问题或指令。
            max_retries (int): 最大重试次数，默认3次。
            retry_delay (float): 每次重试间隔秒数，默认2秒。
            **kwargs: 传递给底层 API 的其他参数 (e.g., temperature, max_tokens)。

        返回:
            str: 模型生成的文本结果。
        """
        if not self.client:
            raise ConnectionError("客户端未初始化，请检查初始化参数。")
        
        last_exception = None
        for attempt in range(1, max_retries + 1):
            try:
                # 构建消息列表
                messages = []
                if self.system_prompt:
                    messages.append({"role": "system", "content": self.system_prompt})
                messages.append({"role": "user", "content": user_prompt})
                
                # 统一使用 OpenAI chat completions API
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"调用 API 时出错（第{attempt}次）: {e}")
                last_exception = e
                if attempt < max_retries:
                    import time
                    time.sleep(retry_delay)
        return f"Error after {max_retries} retries: {last_exception}"

    def get_available_models(self):
        """
        获取可用的模型列表（如果API支持）
        
        返回:
            list: 可用模型列表，如果API不支持则返回空列表
        """
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            print(f"获取模型列表时出错: {e}")
            return []

    def __str__(self):
        return f"LLMClient(model={self.model_name}, base_url={self.base_url})"

    def __repr__(self):
        return self.__str__()
    
# test 
# test_client = LLMClient()
# print(test_client.api_key)
# print(test_client.base_url)
# print(test_client.model_name)

# test_output = test_client.call("Hello, how are you?", max_retries=1, retry_delay=0.5)
# print(test_output)