"""
文件夹批量处理使用示例
"""

from folder_processor import process_folder

def main():
    # 示例1: 基本使用
    print("=== 示例1: 基本使用 ===")
    input_folder = "/Users/fengwenjun/Local/Data/wiki-main"
    output_folder = "/Users/fengwenjun/Local/Data/wiki-output"
    
    result = process_folder(input_folder, output_folder, prompt_file_path="/Users/fengwenjun/Local/CODE/LLMQuant_Tool/quant-wiki-folder/quant-wiki-agent/prompts/re-translate.yaml")
    
    if "error" in result:
        print(f"处理失败: {result['error']}")
    else:
        print(f"处理完成！总共 {result['total_files']} 个文件，成功 {result['successful_count']} 个，失败 {result['failed_count']} 个")


if __name__ == "__main__":
    main() 