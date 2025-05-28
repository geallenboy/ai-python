#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
该脚本用于扫描data/newworkflow目录下的所有JSON文件，
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
import datetime
import re
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

# 文件处理器 - 输出到日志文件 (修改日志名称为newworkflow)
file_handler = logging.FileHandler(logs_dir / 'newworkflow.log')
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
        time.sleep(0.2)
        return translated_text
    
    except Exception as e:
        logger.error(f"翻译失败: {e}")
        return text

def parse_relative_date(relative_date_str):
    """
    从相对日期描述（如'Last update 4 days ago'）推算出绝对日期
    
    Args:
        relative_date_str (str): 相对日期描述字符串
    
    Returns:
        str: YYYY-MM-DD格式的绝对日期，如果无法解析则返回空字符串
    """
    today = datetime.datetime.now()
    
    # 处理"days ago"格式
    days_pattern = re.compile(r"(\d+)\s*days?\s*ago", re.IGNORECASE)
    days_match = days_pattern.search(relative_date_str)
    if days_match:
        days = int(days_match.group(1))
        result_date = today - datetime.timedelta(days=days)
        return result_date.strftime("%Y-%m-%d")
    
    # 处理"weeks ago"格式
    weeks_pattern = re.compile(r"(\d+)\s*weeks?\s*ago", re.IGNORECASE)
    weeks_match = weeks_pattern.search(relative_date_str)
    if weeks_match:
        weeks = int(weeks_match.group(1))
        result_date = today - datetime.timedelta(weeks=weeks)
        return result_date.strftime("%Y-%m-%d")
    
    # 处理"months ago"格式
    months_pattern = re.compile(r"(\d+)\s*months?\s*ago", re.IGNORECASE)
    months_match = months_pattern.search(relative_date_str)
    if months_match:
        months = int(months_match.group(1))
        # 简单处理月份减法（不考虑不同月份天数）
        year = today.year
        month = today.month - months
        while month <= 0:
            year -= 1
            month += 12
        result_date = today.replace(year=year, month=month)
        return result_date.strftime("%Y-%m-%d")
    
    # 处理"years ago"格式
    years_pattern = re.compile(r"(\d+)\s*years?\s*ago", re.IGNORECASE)
    years_match = years_pattern.search(relative_date_str)
    if years_match:
        years = int(years_match.group(1))
        result_date = today.replace(year=today.year - years)
        return result_date.strftime("%Y-%m-%d")
    
    # 处理"yesterday"
    if re.search(r"yesterday", relative_date_str, re.IGNORECASE):
        result_date = today - datetime.timedelta(days=1)
        return result_date.strftime("%Y-%m-%d")
    
    # 处理"last week"
    if re.search(r"last\s*week", relative_date_str, re.IGNORECASE):
        result_date = today - datetime.timedelta(weeks=1)
        return result_date.strftime("%Y-%m-%d")
    
    # 处理"last month"
    if re.search(r"last\s*month", relative_date_str, re.IGNORECASE):
        year = today.year
        month = today.month - 1
        if month <= 0:
            year -= 1
            month += 12
        result_date = today.replace(year=year, month=month)
        return result_date.strftime("%Y-%m-%d")
    
    # 处理"today"
    if re.search(r"today", relative_date_str, re.IGNORECASE):
        return today.strftime("%Y-%m-%d")
    
    # 尝试解析已有的日期格式（如果相对日期中已经包含确切日期）
    date_patterns = [
        # 美式日期: Month DD, YYYY
        (r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})", "%b %d %Y"),
        # 欧式日期: DD Month YYYY
        (r"(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})", "%d %b %Y"),
        # ISO格式: YYYY-MM-DD
        (r"(\d{4})-(\d{2})-(\d{2})", "%Y-%m-%d"),
        # 其他常见格式: DD/MM/YYYY
        (r"(\d{1,2})/(\d{1,2})/(\d{4})", "%d/%m/%Y"),
        # 其他常见格式: MM/DD/YYYY
        (r"(\d{1,2})/(\d{1,2})/(\d{4})", "%m/%d/%Y")
    ]
    
    for pattern, date_format in date_patterns:
        match = re.search(pattern, relative_date_str)
        if match:
            try:
                if date_format == "%b %d %Y":
                    date_str = f"{match.group(1)} {match.group(2)} {match.group(3)}"
                elif date_format == "%d %b %Y":
                    date_str = f"{match.group(1)} {match.group(2)} {match.group(3)}"
                else:
                    date_str = match.group(0)
                
                parsed_date = datetime.datetime.strptime(date_str, date_format)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
    
    # 如果无法解析，返回空字符串
    return ""

def translate_workflow_json(workflow_json_str):
    """
    智能翻译workflow_json，只翻译节点名称和Sticky Note内容，
    保留所有技术结构不变，确保符合n8n格式要求
    
    Args:
        workflow_json_str (str): 原始的workflow_json字符串
        
    Returns:
        str: 翻译后的workflow_json字符串，保持原始的JSON结构和技术元素
    """
    try:
        # 解析JSON字符串为Python对象
        workflow_obj = json.loads(workflow_json_str)
        original_obj = json.loads(workflow_json_str)  # 保留原始结构副本用于比较和验证
        
        # 创建节点名称映射字典 (英文名 -> 中文名)
        node_name_map = {}
        
        # 翻译节点内容 - 只翻译节点名称和Sticky Note内容
        if "nodes" in workflow_obj and isinstance(workflow_obj["nodes"], list):
            for node_index, node in enumerate(workflow_obj["nodes"]):
                # # 翻译节点名称
                # if "name" in node and isinstance(node["name"], str):
                #     english_name = node["name"]
                #     # 保存原始节点名称，用于连接引用
                #     node_name_map[english_name] = translate_text(english_name)
                #     node["name"] = node_name_map[english_name]
                #     logger.info(f"已翻译节点名称: {english_name} -> {node['name']}")
                
                # 翻译Sticky Note内容
                if "type" in node and node["type"] == "n8n-nodes-base.stickyNote":
                    if "parameters" in node and isinstance(node["parameters"], dict):
                        if "content" in node["parameters"] and isinstance(node["parameters"]["content"], str) and node["parameters"]["content"]:
                            # 翻译便利贴内容
                            original_content = node["parameters"]["content"]
                            node["parameters"]["content"] = translate_text(original_content)
                            logger.info(f"已翻译Sticky Note内容: {original_content[:30]}...")
        
       
            # 创建新的连接对象
            new_connections = {}
            
            # 遍历原始连接
            for source_node, targets in workflow_obj["connections"].items():
                # 使用翻译后的名称作为源节点
                if source_node in node_name_map:
                    new_source_node = node_name_map[source_node]
                    new_connections[new_source_node] = targets
                    
                    # 处理目标节点引用
                    if isinstance(targets, dict) and "main" in targets and isinstance(targets["main"], list):
                        for target_list_index, target_list in enumerate(targets["main"]):
                            if isinstance(target_list, list):
                                for target_index, target in enumerate(target_list):
                                    if isinstance(target, dict) and "node" in target:
                                        # 更新节点引用到翻译后的名称
                                        english_node_name = target["node"]
                                        if english_node_name in node_name_map:
                                            target["node"] = node_name_map[english_node_name]
                else:
                    # 如果在映射中找不到源节点，保留原始名称
                    new_connections[source_node] = targets
            
            # 替换原有连接对象
            workflow_obj["connections"] = new_connections
        
        # 将Python对象转换回JSON字符串
        # 检查原始字符串是否是压缩格式
        is_compact = not ("\n" in workflow_json_str or "  " in workflow_json_str)
        
        if is_compact:
            # 如果原始JSON是压缩的，返回压缩格式
            return json.dumps(workflow_obj, ensure_ascii=False, separators=(',', ':'))
        else:
            # 如果原始JSON是美化的，返回美化格式
            return json.dumps(workflow_obj, ensure_ascii=False, indent=2)
    
    except Exception as e:
        logger.error(f"翻译workflow_json失败: {e}")
        return workflow_json_str  # 如果失败则返回原始字符串

def check_translation_status(data):
    """
    检查JSON数据的翻译状态
    
    Args:
        data (dict): JSON数据
        
    Returns:
        dict: 翻译状态信息
    """
    status = {
        'has_translatable_fields': False,
        'fully_translated': True,
        'translated_fields': [],
        'untranslated_fields': [],
        'translatable_fields': []
    }
    
    # 检查可翻译的字段
    translatable_fields = [
        ('readme', 'readme_zh'),
        ('title', 'title_zh'),
        ('publish_date', 'publish_date_zh'),
        ('workflow_json', 'workflow_json_zh')
    ]
    
    for original_field, translated_field in translatable_fields:
        if original_field in data and data[original_field]:
            status['has_translatable_fields'] = True
            status['translatable_fields'].append(original_field)
            
            if translated_field in data and data[translated_field]:
                status['translated_fields'].append(original_field)
            else:
                status['untranslated_fields'].append(original_field)
                status['fully_translated'] = False
    
    # 检查publish_date_absolute字段
    if 'publish_date' in data and data['publish_date']:
        if 'publish_date_absolute' not in data or not data['publish_date_absolute']:
            status['untranslated_fields'].append('publish_date_absolute')
            status['fully_translated'] = False
        else:
            status['translated_fields'].append('publish_date_absolute')
    
    return status

def process_json_file(file_path):
    """
    处理单个JSON文件，检查是否包含readme、workflow_json、title和publish_date字段，如有则翻译并添加对应的中文字段
    
    Args:
        file_path (Path): JSON文件路径
    
    Returns:
        dict: 处理结果 {'updated': bool, 'status': str, 'fields': list}
    """
    try:
        logger.info(f"开始处理文件: {file_path}")
        
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查翻译状态
        translation_status = check_translation_status(data)
        
        if not translation_status['has_translatable_fields']:
            logger.info(f"文件不包含可翻译字段，跳过: {file_path}")
            return {'updated': False, 'status': 'no_translatable_fields', 'fields': []}
        
        if translation_status['fully_translated']:
            logger.info(f"文件已完全翻译，跳过: {file_path}")
            return {'updated': False, 'status': 'already_translated', 'fields': translation_status['translated_fields']}
        
        file_updated = False
        processed_fields = []
        
        # 检查是否包含readme字段
        if isinstance(data, dict) and "readme" in data and data["readme"]:
            # 检查是否已经翻译过readme
            if "readme_zh" not in data or not data["readme_zh"]:
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
            if "title_zh" not in data or not data["title_zh"]:
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
            # 处理publish_date_absolute字段
            if "publish_date_absolute" not in data or not data["publish_date_absolute"]:
                logger.info(f"处理publish_date_absolute字段: {file_path}")
                
                # 从相对日期推算绝对日期
                relative_date = data["publish_date"]
                absolute_date = parse_relative_date(relative_date)
                
                # 添加publish_date_absolute字段
                data["publish_date_absolute"] = absolute_date
                logger.info(f"已成功推算publish_date_absolute字段: {relative_date} -> {absolute_date}")
                file_updated = True
                processed_fields.append("publish_date_absolute")
            
            # 检查是否已经翻译过publish_date
            if "publish_date_zh" not in data or not data["publish_date_zh"]:
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
            if "workflow_json_zh" not in data or not data["workflow_json_zh"]:
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
            return {'updated': True, 'status': 'translated', 'fields': processed_fields}
        else:
            logger.info(f"文件无需更新: {file_path}")
            return {'updated': False, 'status': 'no_updates_needed', 'fields': []}
    
    except Exception as e:
        logger.error(f"处理文件 {file_path} 时出错: {e}")
        return {'updated': False, 'status': 'error', 'fields': []}

def scan_directory(base_dir):
    """
    扫描data/newworkflow目录下的所有JSON文件并进行翻译处理
    
    Args:
        base_dir (Path): 基础目录路径
    
    Returns:
        dict: 详细的统计信息
    """
    newworkflow_dir = base_dir / 'newworkflow'
    if not newworkflow_dir.exists() or not newworkflow_dir.is_dir():
        logger.error(f"newworkflow目录不存在: {newworkflow_dir}")
        return {
            'total_files': 0,
            'translated_files': 0,
            'already_translated_files': 0,
            'no_translatable_fields_files': 0,
            'error_files': 0,
            'processed_files': [],
            'already_translated_list': [],
            'no_translatable_list': [],
            'error_list': []
        }
    
    logger.info(f"开始扫描目录: {newworkflow_dir}")
    
    # 获取所有JSON文件（递归搜索）
    json_files = list(newworkflow_dir.glob('**/*.json'))
    
    # 过滤掉日志目录中的文件
    json_files = [f for f in json_files if 'logs' not in f.parts]
    
    logger.info(f"在 {newworkflow_dir} 中找到 {len(json_files)} 个JSON文件")
    
    # 统计信息
    stats = {
        'total_files': len(json_files),
        'translated_files': 0,
        'already_translated_files': 0,
        'no_translatable_fields_files': 0,
        'error_files': 0,
        'processed_files': [],
        'already_translated_list': [],
        'no_translatable_list': [],
        'error_list': []
    }
    
    # 处理每个JSON文件
    for i, file_path in enumerate(json_files):
        relative_path = file_path.relative_to(base_dir)
        
        # 显示处理进度
        logger.info(f"正在处理 [{i+1}/{len(json_files)}]: {relative_path}")
        
        result = process_json_file(file_path)
        
        if result['status'] == 'translated':
            stats['translated_files'] += 1
            stats['processed_files'].append({
                'file': str(relative_path),
                'fields': result['fields']
            })
        elif result['status'] == 'already_translated':
            stats['already_translated_files'] += 1
            stats['already_translated_list'].append({
                'file': str(relative_path),
                'fields': result['fields']
            })
        elif result['status'] == 'no_translatable_fields':
            stats['no_translatable_fields_files'] += 1
            stats['no_translatable_list'].append(str(relative_path))
        elif result['status'] == 'error':
            stats['error_files'] += 1
            stats['error_list'].append(str(relative_path))
        
        # 打印当前进度
        if (i+1) % 10 == 0 or i+1 == len(json_files):
            logger.info(f"进度: {i+1}/{len(json_files)} ({(i+1)/max(1, len(json_files))*100:.1f}%), "
                       f"新翻译: {stats['translated_files']}, "
                       f"已翻译: {stats['already_translated_files']}, "
                       f"无可翻译字段: {stats['no_translatable_fields_files']}, "
                       f"错误: {stats['error_files']}")
    
    return stats

def main():
    """主函数"""
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="将data/newworkflow目录下的JSON文件翻译为中文")
    parser.add_argument("--count", "-c", type=int, help="限制处理的文件数量")
    args = parser.parse_args()
    
    start_time = time.time()
    try:
        logger.info("=== 开始JSON文件翻译任务 ===")
        logger.info("目标目录: data/newworkflow")
        
        # 获取当前脚本所在目录
        current_dir = Path(__file__).parent
        data_dir = current_dir / 'data'
        
        # 检查data目录是否存在
        if not data_dir.exists():
            logger.error(f"data目录不存在: {data_dir}")
            print(f"错误: data目录不存在: {data_dir}")
            return
        
        # 检查newworkflow目录是否存在
        newworkflow_dir = data_dir / 'newworkflow'
        if not newworkflow_dir.exists():
            logger.error(f"newworkflow目录不存在: {newworkflow_dir}")
            print(f"错误: newworkflow目录不存在: {newworkflow_dir}")
            return
        
        # 处理data/newworkflow目录下的所有JSON文件
        logger.info("开始处理data/newworkflow目录下的所有JSON文件")
        stats = scan_directory(data_dir)
        
        # 计算运行时间
        end_time = time.time()
        duration = end_time - start_time
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        logger.info("=== 处理完成 ===")
        logger.info(f"总运行时间: {int(hours)}小时 {int(minutes)}分钟 {seconds:.2f}秒")
        logger.info("=== 统计信息 ===")
        logger.info(f"总文件数: {stats['total_files']}")
        logger.info(f"新翻译文件数: {stats['translated_files']}")
        logger.info(f"已翻译文件数: {stats['already_translated_files']}")
        logger.info(f"无可翻译字段文件数: {stats['no_translatable_fields_files']}")
        logger.info(f"错误文件数: {stats['error_files']}")
        
        # 记录新翻译的文件
        if stats['processed_files']:
            logger.info("--- 新翻译的文件 ---")
            for item in stats['processed_files'][:10]:  # 只显示前10个
                logger.info(f"√ {item['file']} (字段: {', '.join(item['fields'])})")
            if len(stats['processed_files']) > 10:
                logger.info(f"... 还有 {len(stats['processed_files']) - 10} 个文件")
        
        # 记录已翻译的文件
        if stats['already_translated_list']:
            logger.info("--- 已翻译的文件（跳过） ---")
            for item in stats['already_translated_list'][:5]:  # 只显示前5个
                logger.info(f"○ {item['file']} (已有字段: {', '.join(item['fields'])})")
            if len(stats['already_translated_list']) > 5:
                logger.info(f"... 还有 {len(stats['already_translated_list']) - 5} 个文件")
        
        # 记录无可翻译字段的文件
        if stats['no_translatable_list']:
            logger.info("--- 无可翻译字段的文件 ---")
            for file in stats['no_translatable_list'][:5]:  # 只显示前5个
                logger.info(f"- {file}")
            if len(stats['no_translatable_list']) > 5:
                logger.info(f"... 还有 {len(stats['no_translatable_list']) - 5} 个文件")
        
        # 记录错误文件
        if stats['error_list']:
            logger.info("--- 处理失败的文件 ---")
            for file in stats['error_list']:
                logger.info(f"× {file}")
        
        print(f"处理完成。")
        print(f"总文件数: {stats['total_files']}")
        print(f"新翻译: {stats['translated_files']} 个文件")
        print(f"已翻译: {stats['already_translated_files']} 个文件")
        print(f"无可翻译字段: {stats['no_translatable_fields_files']} 个文件")
        print(f"错误: {stats['error_files']} 个文件")
        print(f"详细信息请查看日志文件: {logs_dir / 'newworkflow.log'}")
    
    except Exception as e:
        logger.error(f"执行过程中出错: {e}")
        print(f"执行过程中出错: {e}")

if __name__ == "__main__":
    main()