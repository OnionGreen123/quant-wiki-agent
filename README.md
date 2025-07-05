# 量化百科智能代理 / Quant Wiki Agent

[English](#english) | [中文](#中文)

---

## 中文

一个基于大语言模型的量化百科文档处理工具，专门用于批量处理和翻译markdown文档。

## 项目特点

- 🚀 **高效批处理**：支持多线程并行处理，最大化处理效率
- 🔧 **模型兼容**：支持OpenAI兼容的API接口，可接入多种大语言模型
- 📝 **智能编辑**：基于YAML配置的提示词模板，可灵活定制处理逻辑
- 🌐 **文档翻译**：专门优化的中文翻译和格式化功能
- 📁 **保持结构**：自动保持原有文件夹结构，复制非markdown文件

## 项目结构

```
quant-wiki-agent/
├── llm_utils/          # LLM工具模块
│   └── llm_client.py   # 大语言模型客户端
├── prompts/            # 提示词模板
│   ├── complete_library.yaml
│   ├── edit_prompt.yaml
│   └── re-translate.yaml
├── test/               # 测试和示例
│   ├── example_usage.py
│   ├── folder_processor.py
│   └── single_file_test.py
└── README.md
```

## 主要功能

### 1. LLM客户端 (`llm_utils/llm_client.py`)

提供统一的大语言模型调用接口，支持：
- OpenAI API
- Gemini API（通过OpenAI兼容接口）
- 其他兼容OpenAI API的模型服务

**功能特色：**
- 自动重试机制
- 环境变量配置
- 系统提示词设置
- 错误处理和日志记录

### 2. 批量文档处理 (`test/folder_processor.py`)

核心功能模块，支持：
- 多线程并行处理markdown文件
- 自动复制非markdown文件
- 保持原有文件夹结构
- 进度监控和状态报告

**处理流程：**
1. 扫描输入文件夹，识别markdown文件
2. 复制所有非markdown文件到输出目录
3. 多线程并行处理markdown文件
4. 生成处理报告

### 3. 提示词模板 (`prompts/`)

提供专业的文档处理提示词：
- `re-translate.yaml`: 专门用于重新翻译和格式化中文文档
- `edit_prompt.yaml`: 通用文档编辑提示词
- `complete_library.yaml`: 完整的文档库处理模板

## 安装和配置

### 1. 环境要求

- Python 3.7+
- 依赖包：
  ```bash
  pip install openai python-dotenv
  ```

### 2. 环境配置

创建 `.env` 文件并配置以下变量：

```env
# 模型配置
MODEL_NAME=gpt-4o
API_KEY=your_api_key_here
BASE_URL=https://api.openai.com/v1/

# 系统提示词（可选）
DEFAULT_SYSTEM_PROMPT=你是一个专业的文档处理助手。
```

### 3. 支持的模型配置

#### OpenAI 模型
```env
MODEL_NAME=gpt-4o
API_KEY=your_openai_api_key
BASE_URL=https://api.openai.com/v1/
```

#### Gemini 模型
```env
MODEL_NAME=gemini-1.5-pro-latest
API_KEY=your_gemini_api_key
BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

## 使用方法

### 1. 基本使用

```python
from test.folder_processor import process_folder

# 处理文件夹
result = process_folder(
    input_folder_path="/path/to/input",
    output_folder_path="/path/to/output",
    prompt_file_path="/path/to/prompts/re-translate.yaml",
    max_workers=30,
    rate_limit_delay=0.5
)

print(f"处理完成！成功：{result['successful_count']}，失败：{result['failed_count']}")
```

### 2. 单独使用LLM客户端

```python
from llm_utils.llm_client import LLMClient

# 初始化客户端
client = LLMClient(
    model_name="gpt-4o",
    api_key="your_api_key",
    system_prompt="你是一个专业的翻译助手。"
)

# 调用模型
response = client.call("请翻译这段文本")
print(response)
```

### 3. 运行示例

```bash
cd test
python example_usage.py
```

## 配置参数

### 文件夹处理器参数

- `input_folder_path`: 输入文件夹路径
- `output_folder_path`: 输出文件夹路径
- `prompt_file_path`: 提示词文件路径（可选，默认使用edit_prompt.yaml）
- `max_workers`: 最大并发线程数（默认30）
- `rate_limit_delay`: API调用间隔秒数（默认0.5秒）

### LLM客户端参数

- `model_name`: 模型名称
- `api_key`: API密钥
- `base_url`: API基础URL
- `system_prompt`: 系统提示词
- `max_retries`: 最大重试次数（默认3）
- `retry_delay`: 重试间隔（默认1秒）

## 特色功能

### 文档格式化和翻译

专门针对量化金融文档的处理，支持：
- 删除多余的元数据字段
- 清理超链接格式
- 统一markdown格式
- 中英文翻译
- 保持代码块和数学公式格式

### 智能错误处理

- 自动重试机制
- 详细错误日志
- 处理进度监控
- 失败文件统计

### 性能优化

- 多线程并行处理
- 可配置的API调用频率限制
- 内存友好的流式处理
- 自动复制非处理文件

## 注意事项

1. **API配额管理**：注意控制并发数量和调用频率，避免超出API限制
2. **文件备份**：处理前请备份原始文件
3. **模型选择**：根据文档复杂度选择合适的模型
4. **网络稳定性**：确保网络连接稳定，避免处理中断

## 许可证

此项目使用 MIT 许可证。详情请参阅 LICENSE 文件。

## 贡献

欢迎提交问题和拉取请求。在贡献之前，请先阅读贡献指南。

## 联系方式

如有问题或建议，请创建 GitHub Issue 或联系维护者。

---

## English

An LLM-based quantitative encyclopedia document processing tool, specifically designed for batch processing and translation of markdown documents.

## Features

- 🚀 **Efficient Batch Processing**: Supports multi-threaded parallel processing for maximum efficiency
- 🔧 **Model Compatibility**: Supports OpenAI-compatible API interfaces, can integrate with various large language models
- 📝 **Smart Editing**: YAML-based prompt templates for flexible processing logic customization
- 🌐 **Document Translation**: Optimized Chinese translation and formatting functionality
- 📁 **Structure Preservation**: Automatically maintains original folder structure, copies non-markdown files

## Project Structure

```
quant-wiki-agent/
├── llm_utils/          # LLM utility modules
│   └── llm_client.py   # Large language model client
├── prompts/            # Prompt templates
│   ├── complete_library.yaml
│   ├── edit_prompt.yaml
│   └── re-translate.yaml
├── test/               # Tests and examples
│   ├── example_usage.py
│   ├── folder_processor.py
│   └── single_file_test.py
└── README.md
```

## Main Features

### 1. LLM Client (`llm_utils/llm_client.py`)

Provides unified large language model calling interface, supporting:
- OpenAI API
- Gemini API (via OpenAI-compatible interface)
- Other OpenAI API-compatible model services

**Key Features:**
- Automatic retry mechanism
- Environment variable configuration
- System prompt settings
- Error handling and logging

### 2. Batch Document Processing (`test/folder_processor.py`)

Core functionality module supporting:
- Multi-threaded parallel processing of markdown files
- Automatic copying of non-markdown files
- Maintains original folder structure
- Progress monitoring and status reporting

**Processing Flow:**
1. Scan input folder, identify markdown files
2. Copy all non-markdown files to output directory
3. Multi-threaded parallel processing of markdown files
4. Generate processing report

### 3. Prompt Templates (`prompts/`)

Provides professional document processing prompts:
- `re-translate.yaml`: Specialized for re-translating and formatting Chinese documents
- `edit_prompt.yaml`: General document editing prompts
- `complete_library.yaml`: Complete document library processing template

## Installation and Configuration

### 1. Requirements

- Python 3.7+
- Dependencies:
  ```bash
  pip install openai python-dotenv
  ```

### 2. Environment Configuration

Create `.env` file and configure the following variables:

```env
# Model configuration
MODEL_NAME=gpt-4o
API_KEY=your_api_key_here
BASE_URL=https://api.openai.com/v1/

# System prompt (optional)
DEFAULT_SYSTEM_PROMPT=You are a professional document processing assistant.
```

### 3. Supported Model Configurations

#### OpenAI Models
```env
MODEL_NAME=gpt-4o
API_KEY=your_openai_api_key
BASE_URL=https://api.openai.com/v1/
```

#### Gemini Models
```env
MODEL_NAME=gemini-1.5-pro-latest
API_KEY=your_gemini_api_key
BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

## Usage

### 1. Basic Usage

```python
from test.folder_processor import process_folder

# Process folder
result = process_folder(
    input_folder_path="/path/to/input",
    output_folder_path="/path/to/output",
    prompt_file_path="/path/to/prompts/re-translate.yaml",
    max_workers=30,
    rate_limit_delay=0.5
)

print(f"Processing complete! Success: {result['successful_count']}, Failed: {result['failed_count']}")
```

### 2. Using LLM Client Separately

```python
from llm_utils.llm_client import LLMClient

# Initialize client
client = LLMClient(
    model_name="gpt-4o",
    api_key="your_api_key",
    system_prompt="You are a professional translation assistant."
)

# Call model
response = client.call("Please translate this text")
print(response)
```

### 3. Running Examples

```bash
cd test
python example_usage.py
```

## Configuration Parameters

### Folder Processor Parameters

- `input_folder_path`: Input folder path
- `output_folder_path`: Output folder path
- `prompt_file_path`: Prompt file path (optional, defaults to edit_prompt.yaml)
- `max_workers`: Maximum concurrent threads (default 30)
- `rate_limit_delay`: API call interval in seconds (default 0.5 seconds)

### LLM Client Parameters

- `model_name`: Model name
- `api_key`: API key
- `base_url`: API base URL
- `system_prompt`: System prompt
- `max_retries`: Maximum retry attempts (default 3)
- `retry_delay`: Retry interval (default 1 second)

## Special Features

### Document Formatting and Translation

Specialized for quantitative finance document processing, supporting:
- Remove redundant metadata fields
- Clean hyperlink formats
- Unify markdown formatting
- Chinese-English translation
- Preserve code blocks and mathematical formulas

### Smart Error Handling

- Automatic retry mechanism
- Detailed error logging
- Processing progress monitoring
- Failed file statistics

### Performance Optimization

- Multi-threaded parallel processing
- Configurable API call frequency limits
- Memory-friendly streaming processing
- Automatic copying of non-processed files

## Notes

1. **API Quota Management**: Control concurrency and call frequency to avoid exceeding API limits
2. **File Backup**: Backup original files before processing
3. **Model Selection**: Choose appropriate models based on document complexity
4. **Network Stability**: Ensure stable network connection to avoid processing interruptions

## License

This project uses the MIT License. See the LICENSE file for details.

## Contributing

Issues and pull requests are welcome. Please read the contribution guidelines before contributing.

## Contact

For questions or suggestions, please create a GitHub Issue or contact the maintainer.