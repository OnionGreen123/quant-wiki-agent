import sys
import os
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
import shutil

# 添加项目路径到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_utils.llm_client import LLMClient

def copy_non_markdown_files(input_folder, output_folder):
    """
    复制所有非markdown文件到输出文件夹，保持文件夹结构
    
    Args:
        input_folder (Path): 输入文件夹路径
        output_folder (Path): 输出文件夹路径
    
    Returns:
        dict: 复制结果统计
    """
    copied_files = []
    failed_files = []
    
    print("正在复制非markdown文件...")
    
    # 遍历所有文件
    for file_path in input_folder.rglob("*"):
        if file_path.is_file() and not file_path.name.endswith('.md'):
            try:
                # 计算相对路径，保持文件夹结构
                relative_path = file_path.relative_to(input_folder)
                output_file_path = output_folder / relative_path
                
                # 创建输出目录（如果不存在）
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                shutil.copy2(file_path, output_file_path)
                copied_files.append(str(file_path))
                
            except Exception as e:
                error_msg = f"复制文件 {file_path} 时出错: {e}"
                print(error_msg)
                failed_files.append({"file": str(file_path), "error": str(e)})
    
    result = {
        "copied_count": len(copied_files),
        "failed_count": len(failed_files),
        "copied_files": copied_files,
        "failed_files": failed_files
    }
    
    print(f"复制完成：成功复制 {result['copied_count']} 个非markdown文件，失败 {result['failed_count']} 个")
    
    return result

def process_single_file(file_info, llm_client, input_folder, output_folder, progress_queue):
    """
    处理单个文件的函数
    
    Args:
        file_info (tuple): (文件索引, 文件路径, 总文件数)
        llm_client (LLMClient): LLM客户端实例
        input_folder (Path): 输入文件夹路径
        output_folder (Path): 输出文件夹路径
        progress_queue (Queue): 用于进度报告的队列
    
    Returns:
        dict: 处理结果
    """
    i, file_path, total_files = file_info
    thread_id = threading.current_thread().ident
    
    try:
        progress_queue.put(f"[线程{thread_id}] [{i}/{total_files}] 正在处理: {file_path}")
        
        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            article = f.read()
        
        # 使用LLM处理文件
        response = llm_client.call(article, temperature=0.01)
        
        # 计算相对路径，保持文件夹结构
        relative_path = file_path.relative_to(input_folder)
        output_file_path = output_folder / relative_path
        
        # 创建输出目录（如果不存在）
        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入处理后的内容
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(response)
        
        progress_queue.put(f"[线程{thread_id}] 处理完成: {output_file_path}")
        
        return {
            "success": True,
            "file": str(file_path),
            "output": str(output_file_path),
            "thread_id": thread_id
        }
        
    except Exception as e:
        error_msg = f"[线程{thread_id}] 处理文件 {file_path} 时出错: {e}"
        progress_queue.put(error_msg)
        return {
            "success": False,
            "file": str(file_path),
            "error": str(e),
            "thread_id": thread_id
        }

def process_folder(input_folder_path, output_folder_path, prompt_file_path=None, max_workers=30, rate_limit_delay=0.5):
    """
    批量处理文件夹中的所有markdown文件（多线程版本），同时复制所有其他文件
    
    Args:
        input_folder_path (str): 输入文件夹路径
        output_folder_path (str): 输出文件夹路径
        prompt_file_path (str, optional): prompt文件路径，默认使用edit_prompt.yaml
        max_workers (int, optional): 最大并发线程数，默认为4
        rate_limit_delay (float, optional): API调用间隔（秒），默认0.5秒
    
    Returns:
        dict: 包含处理结果的字典
    """
    
    # 设置默认prompt文件路径
    if prompt_file_path is None:
        # 动态计算prompt文件路径
        current_file = Path(__file__)
        project_root = current_file.parent.parent  # 从test文件夹向上两级到quant-wiki-agent
        prompt_file_path = project_root / "prompts" / "edit_prompt.yaml"
    
    input_folder = Path(input_folder_path)
    output_folder = Path(output_folder_path)
    
    # 检查输入文件夹是否存在
    if not input_folder.exists():
        return {"error": f"输入文件夹 {input_folder} 不存在"}
    
    # 创建输出文件夹
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # 首先复制所有非markdown文件
    copy_result = copy_non_markdown_files(input_folder, output_folder)
    
    # 读取prompt文件
    try:
        with open(prompt_file_path, "r", encoding="utf-8") as f:
            prompt = f.read()
    except Exception as e:
        return {"error": f"无法读取prompt文件 {prompt_file_path}: {e}"}
    
    # 初始化LLM客户端
    llm_client = LLMClient(system_prompt=prompt)
    
    # 获取所有markdown文件
    markdown_files = []
    for file_path in input_folder.rglob("*.md"):
        if file_path.is_file():
            markdown_files.append(file_path)
    
    if not markdown_files:
        print(f"在 {input_folder} 中没有找到markdown文件")
        # 即使没有markdown文件，也返回复制结果
        return {
            "total_files": 0,
            "successful_count": 0,
            "failed_count": 0,
            "successful_files": [],
            "failed_files": [],
            "output_folder": str(output_folder),
            "max_workers": max_workers,
            "copy_result": copy_result
        }
    
    print(f"找到 {len(markdown_files)} 个markdown文件")
    print(f"使用 {max_workers} 个线程并行处理")
    
    # 创建进度报告队列
    progress_queue = Queue()
    
    # 准备文件信息
    file_infos = [(i+1, file_path, len(markdown_files)) for i, file_path in enumerate(markdown_files)]
    
    # 处理结果
    successful_files = []
    failed_files = []
    
    # 使用线程池执行器
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_file = {
            executor.submit(process_single_file, file_info, llm_client, input_folder, output_folder, progress_queue): file_info
            for file_info in file_infos
        }
        
        # 监控进度和结果
        completed_count = 0
        for future in as_completed(future_to_file):
            # 处理进度消息
            while not progress_queue.empty():
                try:
                    message = progress_queue.get_nowait()
                    print(message)
                except:
                    break
            
            # 获取结果
            try:
                result = future.result()
                completed_count += 1
                
                if result["success"]:
                    successful_files.append(result["file"])
                else:
                    failed_files.append({"file": result["file"], "error": result["error"]})
                
                # API调用速率限制
                if rate_limit_delay > 0:
                    time.sleep(rate_limit_delay)
                    
            except Exception as e:
                file_info = future_to_file[future]
                error_msg = f"线程执行异常 {file_info[1]}: {e}"
                print(error_msg)
                failed_files.append({"file": str(file_info[1]), "error": str(e)})
                completed_count += 1
    
    # 处理剩余的进度消息
    while not progress_queue.empty():
        try:
            message = progress_queue.get_nowait()
            print(message)
        except:
            break
    
    result = {
        "total_files": len(markdown_files),
        "successful_count": len(successful_files),
        "failed_count": len(failed_files),
        "successful_files": successful_files,
        "failed_files": failed_files,
        "output_folder": str(output_folder),
        "max_workers": max_workers,
        "copy_result": copy_result
    }
    
    print(f"\n处理完成！")
    print(f"成功处理markdown文件: {result['successful_count']} 个")
    print(f"处理失败markdown文件: {result['failed_count']} 个") 
    print(f"成功复制其他文件: {copy_result['copied_count']} 个")
    print(f"复制失败其他文件: {copy_result['failed_count']} 个")
    print(f"输出文件夹: {result['output_folder']}")
    print(f"使用了 {max_workers} 个线程")
    
    return result
