#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
该脚本用于扫描data目录下的所有JSON文件，
查找包含readme、workflow_json、title和publish_date字段的文件，使用DeepSeek API将内容翻译为中文，
并在JSON文件中添加readme_zh、workflow_json_zh、title_zh和publish_date_zh字段保存翻译结果。
"""

import os
import json
import requests
from pathlib import Path
import logging
import time
import sys
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 确保logs目录存在
current_dir = Path(__file__).parent
logs_dir = current_dir / 'logs'
if not logs_dir.exists():
    logs_dir.mkdir(parents=True, exist_ok=True)

# 配置日志 - 同时输出到文件和控制台
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 文件处理器 - 输出到日志文件
file_handler = logging.FileHandler(logs_dir / 'file_translate.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# 控制台处理器 - 输出到控制台
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# 添加处理器到logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# DeepSeek API配置
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_API_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

def translate_text(text, from_lang="English", to_lang="Chinese"):
    """
    使用DeepSeek API将文本从一种语言翻译为另一种语言
    
    Args:
        text (str): 要翻译的文本
        from_lang (str): 源语言，默认为英语
        to_lang (str): 目标语言，默认为中文
    
    Returns:
        str: 翻译后的文本，如果翻译失败则返回原文本
    """
    if not DEEPSEEK_API_KEY:
        logger.error("未设置DEEPSEEK_API_KEY环境变量")
        raise ValueError("请设置DEEPSEEK_API_KEY环境变量或在.env文件中配置")
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system", 
                    "content": f"You are a translation assistant. Translate the following text from {from_lang} to {to_lang}. Only provide the translation, nothing else."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.1
        }
        
        response = requests.post(DEEPSEEK_API_ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        translated_text = result['choices'][0]['message']['content'].strip()
        
        # 添加短暂延迟以避免API限制
        time.sleep(1)
        return translated_text
    
    except Exception as e:
        logger.error(f"翻译失败: {e}")
        return text

def translate_workflow_json(workflow_json_str):
    """
    智能翻译workflow_json，保留JSON结构，只翻译文本内容
    
    Args:
        workflow_json_str (str): 原始的workflow_json字符串
        
    Returns:
        str: 翻译后的workflow_json字符串，保持原始的JSON结构
    """
    try:
        # 解析JSON字符串为Python对象
        workflow_obj = json.loads(workflow_json_str)
        
        # 翻译工作流名称
        if "name" in workflow_obj and isinstance(workflow_obj["name"], str):
            workflow_obj["name"] = translate_text(workflow_obj["name"])
            logger.info(f"已翻译工作流名称: {workflow_obj['name']}")
        
        # 翻译节点名称和内容
        if "nodes" in workflow_obj and isinstance(workflow_obj["nodes"], list):
            for node in workflow_obj["nodes"]:
                # 翻译节点名称
                if "name" in node and isinstance(node["name"], str):
                    node["name"] = translate_text(node["name"])
                
                # 翻译节点参数中的内容
                if "parameters" in node and isinstance(node["parameters"], dict):
                    for param_key, param_value in node["parameters"].items():
                        if isinstance(param_value, str) and len(param_value) > 3:
                            # 避免翻译代码或特殊格式内容
                            if not (param_value.startswith('{{') or 
                                   param_value.startswith('function') or
                                   param_value.startswith('return') or
                                   param_value.startswith('if ') or
                                   param_value.startswith('const ') or
                                   param_value.startswith('let ')):
                                node["parameters"][param_key] = translate_text(param_value)
                
                # 翻译节点描述
                if "description" in node and isinstance(node["description"], str) and len(node["description"]) > 3:
                    node["description"] = translate_text(node["description"])
        
        # 翻译连接标签
        if "connections" in workflow_obj and isinstance(workflow_obj["connections"], dict):
            for source_node, targets in workflow_obj["connections"].items():
                if isinstance(targets, list):
                    for target in targets:
                        if "index" in target and isinstance(target["index"], int) and "label" in target and isinstance(target["label"], str) and len(target["label"]) > 3:
                            target["label"] = translate_text(target["label"])
        
        # 将Python对象转换回JSON字符串
        return json.dumps(workflow_obj, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"智能翻译workflow_json失败: {e}")
        return workflow_json_str  # 如果失败则返回原始字符串

def process_json_file(file_path):
    """
    处理单个JSON文件，检查是否包含readme、workflow_json、title和publish_date字段，如有则翻译并添加对应的中文字段
    
    Args:
        file_path (Path): JSON文件路径
    
    Returns:
        bool: 是否成功处理文件
    """
    try:
        logger.info(f"开始处理文件: {file_path}")
        
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        file_updated = False
        processed_fields = []
        skipped_fields = []
        
        # 检查是否包含readme字段
        if isinstance(data, dict) and "readme" in data and data["readme"]:
            # 检查是否已经翻译过readme
            if "readme_zh" in data and data["readme_zh"]:
                logger.info(f"readme字段已翻译过，跳过: {file_path}")
                skipped_fields.append("readme")
            else:
                logger.info(f"处理readme字段: {file_path}")
                
                # 翻译readme内容
                original_readme = data["readme"]
                translated_readme = translate_text(original_readme)
                
                # 添加readme_zh字段
                data["readme_zh"] = translated_readme
                logger.info(f"已成功翻译readme字段: {file_path}")
                file_updated = True
                processed_fields.append("readme")
        
        # 检查是否包含title字段
        if isinstance(data, dict) and "title" in data and data["title"]:
            # 检查是否已经翻译过title
            if "title_zh" in data and data["title_zh"]:
                logger.info(f"title字段已翻译过，跳过: {file_path}")
                skipped_fields.append("title")
            else:
                logger.info(f"处理title字段: {file_path}")
                
                # 翻译title内容
                original_title = data["title"]
                translated_title = translate_text(original_title)
                
                # 添加title_zh字段
                data["title_zh"] = translated_title
                logger.info(f"已成功翻译title字段: {file_path}")
                file_updated = True
                processed_fields.append("title")
        
        # 检查是否包含publish_date字段
        if isinstance(data, dict) and "publish_date" in data and data["publish_date"]:
            # 检查是否已经翻译过publish_date
            if "publish_date_zh" in data and data["publish_date_zh"]:
                logger.info(f"publish_date字段已翻译过，跳过: {file_path}")
                skipped_fields.append("publish_date")
            else:
                logger.info(f"处理publish_date字段: {file_path}")
                
                # 翻译publish_date内容
                original_date = data["publish_date"]
                translated_date = translate_text(original_date)
                
                # 添加publish_date_zh字段
                data["publish_date_zh"] = translated_date
                logger.info(f"已成功翻译publish_date字段: {file_path}")
                file_updated = True
                processed_fields.append("publish_date")
        
        # 检查是否包含workflow_json字段
        if isinstance(data, dict) and "workflow_json" in data and data["workflow_json"]:
            # 检查是否已经翻译过workflow_json
            if "workflow_json_zh" in data and data["workflow_json_zh"]:
                logger.info(f"workflow_json字段已翻译过，跳过: {file_path}")
                skipped_fields.append("workflow_json")
            else:
                logger.info(f"处理workflow_json字段: {file_path}")
                
                try:
                    # 获取原始的workflow_json字符串
                    workflow_json = data["workflow_json"]
                    
                    # 使用智能翻译方法，保留JSON结构
                    translated_workflow_json = translate_workflow_json(workflow_json)
                    
                    # 添加workflow_json_zh字段存储翻译结果
                    data["workflow_json_zh"] = translated_workflow_json
                    logger.info(f"已成功翻译workflow_json字段: {file_path}")
                    file_updated = True
                    processed_fields.append("workflow_json")
                    
                except Exception as e:
                    logger.error(f"翻译workflow_json字段失败: {e}")
        
        # 如果有更新，保存文件
        if file_updated:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"已更新文件: {file_path}，处理的字段: {', '.join(processed_fields)}")
            return True
        else:
            logger.info(f"文件无需更新: {file_path}，跳过的字段: {', '.join(skipped_fields)}")
            return False
    
    except Exception as e:
        logger.error(f"处理文件 {file_path} 时出错: {e}")
        return False

def scan_directory(directory):
    """
    递归扫描目录，处理所有JSON文件
    
    Args:
        directory (str): 要扫描的目录路径
    
    Returns:
        tuple: (处理的文件数, 成功翻译的文件数, 处理的文件列表, 未处理的文件列表)
    """
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        logger.error(f"目录不存在或不是有效目录: {directory}")
        return 0, 0, [], []
    
    total_files = 0
    translated_files = 0
    processed_files = []
    unprocessed_files = []
    
    # 获取所有JSON文件
    all_json_files = list(dir_path.glob('**/*.json'))
    total_json_count = len(all_json_files)
    
    logger.info(f"在目录 {directory} 中找到 {total_json_count} 个JSON文件")
    
    # 递归遍历目录
    for i, file_path in enumerate(all_json_files):
        total_files += 1
        relative_path = file_path.relative_to(dir_path)
        
        # 显示处理进度
        logger.info(f"正在处理 [{i+1}/{total_json_count}]: {relative_path}")
        
        if process_json_file(file_path):
            translated_files += 1
            processed_files.append(str(relative_path))
        else:
            unprocessed_files.append(str(relative_path))
        
        # 打印当前进度
        if (i+1) % 5 == 0 or i+1 == total_json_count:
            logger.info(f"进度: {i+1}/{total_json_count} ({(i+1)/total_json_count*100:.1f}%), 已翻译: {translated_files}")
    
    return total_files, translated_files, processed_files, unprocessed_files

def main():
    """主函数"""
    start_time = time.time()
    try:
        logger.info("=== 开始JSON文件翻译任务 ===")
        
        # 获取当前脚本所在目录
        current_dir = Path(__file__).parent
        data_dir = current_dir / 'data'
        
        # 检查data目录是否存在
        if not data_dir.exists():
            logger.error(f"data目录不存在: {data_dir}")
            print(f"错误: data目录不存在: {data_dir}")
            return
        
        # 扫描处理data目录下的所有JSON文件
        logger.info(f"开始扫描目录: {data_dir}")
        total, translated, processed_files, unprocessed_files = scan_directory(data_dir)
        
        # 计算运行时间
        end_time = time.time()
        duration = end_time - start_time
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        logger.info("=== 处理完成 ===")
        logger.info(f"总运行时间: {int(hours)}小时 {int(minutes)}分钟 {seconds:.2f}秒")
        logger.info(f"共处理 {total} 个JSON文件，翻译了 {translated} 个文件")
        
        # 记录已处理的文件
        if processed_files:
            logger.info("--- 已翻译的文件 ---")
            for file in processed_files:
                logger.info(f"√ {file}")
        
        # 记录未处理的文件
        if unprocessed_files:
            logger.info("--- 未翻译的文件 ---")
            for file in unprocessed_files:
                logger.info(f"× {file}")
        
        print(f"处理完成。共处理 {total} 个JSON文件，翻译了 {translated} 个文件")
        print(f"详细信息请查看日志文件: {logs_dir / 'file_translate.log'}")
    
    except Exception as e:
        logger.error(f"执行过程中出错: {e}")
        print(f"执行过程中出错: {e}")

if __name__ == "__main__":
    main()