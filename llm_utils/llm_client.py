import os
from openai import OpenAI
from google import genai

from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    """
    一个用于调用大语言模型的通用客户端类。
    可以根据模型名称自动选择使用 OpenAI 或 Gemini 的 API。

    使用示例:
        # --- 使用 OpenAI 模型 ---
        # client_openai = LLMClient(model_name="gpt-4o", api_key="YOUR_OPENAI_API_KEY")
        # client_openai.set_system_prompt("你是一个专业的翻译家，将所有内容翻译成法语。")
        # response_openai = client_openai.call("Hello, how are you?")
        # print(f"OpenAI Response: {response_openai}")

        # --- 使用 Gemini 模型 ---
        # client_gemini = LLMClient(model_name="gemini-1.5-pro-latest", api_key="YOUR_GEMINI_API_KEY")
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
        self.model_name = (
            model_name 
            or os.environ.get("MODEL_NAME")
        )

        if not self.model_name:
            raise ValueError("model_name 必须显式指定，或在 .env 文件中设置 MODEL_NAME")

        # 根据模型类型自动选择环境变量
        if "gemini" in self.model_name.lower():
            self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
            self.base_url = base_url  # Gemini一般不需要base_url
        else:
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
            self.base_url = base_url or os.environ.get("OPENAI_BASE_URL")


        
        # 优先使用传入的 system_prompt，否则用环境变量，否则用默认
        self.system_prompt = (
            system_prompt
            or os.environ.get("DEFAULT_SYSTEM_PROMPT")
            or "You are a helpful assistant."
        )

        self.client = None
        self.provider = self._determine_provider()
        self._initialize_client()

    def _determine_provider(self) -> str:
        """根据模型名称判断服务提供商"""
        if "gemini" in self.model_name.lower():
            return "gemini"
        elif "gpt" in self.model_name.lower() or self.base_url:
            # 如果提供了 base_url，也默认为是 OpenAI 兼容的 API
            return "openai"
        else:
            raise ValueError(f"无法根据模型名称 '{self.model_name}' 确定服务提供商。请确保名称中包含 'gpt' 或 'gemini'。")

    def _initialize_client(self):
        """根据提供商初始化对应的客户端"""
        if self.provider == "openai":
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        elif self.provider == "gemini":
            # 新版 Gemini API 初始化
            self.client = genai.Client(api_key=self.api_key)
        else:
            # 这个分支理论上不会被触发，因为 _determine_provider 已经做了检查
            raise NotImplementedError(f"不支持的服务提供商: {self.provider}")

    def set_system_prompt(self, prompt: str):
        """
        设置一个系统级的提示词(System Prompt)。

        参数:
            prompt (str): 你希望模型扮演的角色或遵循的规则。
        """
        self.system_prompt = prompt
        print(f"System prompt 已设置为: '{prompt}'")
        
        # 对于 Gemini，更标准的做法是在模型初始化时设置 system_instruction。
        # 为了保持接口统一，我们在 call 方法中将 system prompt 和 user prompt 组合。
        # 如果需要每次都用新的 system_prompt 初始化模型，可以取消下面的注释。
        # if self.provider == "gemini":
        #     self.client = genai.GenerativeModel(
        #         self.model_name,
        #         system_instruction=self.system_prompt
        #     )

    def call(self, user_prompt: str, **kwargs) -> str:
        """
        调用大模型并获取返回结果。

        参数:
            user_prompt (str): 用户输入的问题或指令。
            **kwargs: 传递给底层 API 的其他参数 (e.g., temperature, max_tokens)。

        返回:
            str: 模型生成的文本结果。
        """
        if not self.client:
            raise ConnectionError("客户端未初始化，请检查初始化参数。")

        print(f"\n正在调用模型: {self.model_name}...")
        
        try:
            if self.provider == "openai":
                messages = []
                if self.system_prompt:
                    messages.append({"role": "system", "content": self.system_prompt})
                messages.append({"role": "user", "content": user_prompt})
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content.strip()

            elif self.provider == "gemini":
                from google.genai import types
                # 构建 system_instruction
                config = None
                if self.system_prompt or kwargs:
                    config_kwargs = {}
                    if self.system_prompt:
                        config_kwargs["system_instruction"] = self.system_prompt
                    
                    # 从环境变量读取 thinking 配置
                    thinking_budget = int(os.environ.get("GEMINI_THINKING_BUDGET", "128"))
                    if thinking_budget >= 0:
                        config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=thinking_budget)
                    
                    # 只传递Gemini支持的参数
                    for k in ["temperature", "max_output_tokens", "top_p", "top_k", "stop_sequences"]:
                        if k in kwargs:
                            config_kwargs[k] = kwargs[k]
                    if config_kwargs:
                        config = types.GenerateContentConfig(**config_kwargs)
                
                # 支持多模态输入，文本用list
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[user_prompt],
                    config=config
                )
                print(response)
                return response.text.strip()

        except Exception as e:
            print(f"调用 API 时出错: {e}")
            return f"Error: {e}"