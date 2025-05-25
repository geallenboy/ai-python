#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
该脚本创建一个Streamlit页面，用于展示data/workflow目录下的所有JSON文件内容。
功能包括：文件搜索、分类过滤、预览展示、分页浏览、文件内容下载和翻译。
"""

import os
import json
import streamlit as st
from pathlib import Path
import math
import base64
import re
from datetime import datetime
import time
import requests
import n8n_json_to_context
from dotenv import load_dotenv
import logging
import sys

# 设置页面标题和配置
st.set_page_config(page_title="N8N工作流查看器", page_icon="🔄", layout="wide", initial_sidebar_state="expanded")
st.title("N8N工作流数据查看")

# 定义数据目录路径
current_dir = Path(__file__).parent
data_dir = current_dir / "data" / "workflow"

# 确保logs目录存在
logs_dir = current_dir / 'logs'
if not logs_dir.exists():
    logs_dir.mkdir(parents=True, exist_ok=True)

# 配置日志 - 同时输出到文件和控制台
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 文件处理器 - 输出到日志文件
file_handler = logging.FileHandler(logs_dir / 'workflow_streamlit.log')
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

# 设置会话状态变量
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1

# 加载环境变量
load_dotenv()

def extract_json_info(json_path):
    """从JSON文件中提取关键信息"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        info = {
            "filename": json_path.name,
            "path": json_path,
            "title": data.get("title", ""),
            "title_zh": data.get("title_zh", ""),
            "tags": data.get("tags", []), 
            "category": data.get("category", "未分类"),
            "category_url": data.get("category_url", ""),
            "publish_date": data.get("publish_date", ""),
            "has_workflow_json": "workflow_json" in data and bool(data["workflow_json"]),
            "has_workflow_json_zh": "workflow_json_zh" in data and bool(data["workflow_json_zh"]),
            "has_readme": "readme" in data and bool(data["readme"]),
            "has_readme_zh": "readme_zh" in data and bool(data["readme_zh"])
        }
        return info
    except Exception as e:
        st.error(f"提取文件信息出错 {json_path.name}: {e}")
        return None

def get_all_json_files(directory, query="", category_filter="全部", has_translation=None):
    """获取目录及其子目录下的所有JSON文件路径"""
    all_files = []
    all_info = []
    
    if not directory.exists():
        st.error(f"目录不存在: {directory}")
        return all_files, all_info
    
    for path in directory.glob('**/*.json'):
        if path.is_file() and path.name != "n8n_categories.json":
            file_info = extract_json_info(path)
            if file_info:
                if query:
                    title = file_info["title"] + " " + file_info["title_zh"]
                    if not (query.lower() in path.name.lower() or query.lower() in title.lower()):
                        continue
                
                if category_filter != "全部" and file_info.get("category", "未分类") != category_filter:
                    continue
                
                if has_translation is not None:
                    has_title_zh = file_info.get("title_zh", "") != ""
                    has_readme_zh = file_info.get("has_readme_zh", False)
                    has_workflow_zh = file_info.get("has_workflow_json_zh", False)
                    
                    fully_translated = has_title_zh and has_readme_zh and has_workflow_zh
                    partially_translated = (has_title_zh or has_readme_zh or has_workflow_zh) and not fully_translated
                    not_translated = not (has_title_zh or has_readme_zh or has_workflow_zh)
                    
                    if has_translation == True and not fully_translated:
                        continue
                    elif has_translation == False and not not_translated:
                        continue
                    elif has_translation == "partial" and not partially_translated:
                        continue
                
                all_files.append(path)
                all_info.append(file_info)
    
    if all_info:
        def get_date_sort_key(info):
            date_str = info.get("publish_date_absolute", "")
            if not date_str:
                date_str = info.get("publish_date", "")
            
            try:
                if "ago" in date_str.lower():
                    if "hour" in date_str.lower(): return datetime.now().timestamp() - 3600
                    elif "day" in date_str.lower(): return datetime.now().timestamp() - 86400
                    elif "week" in date_str.lower(): return datetime.now().timestamp() - 604800
                    elif "month" in date_str.lower(): return datetime.now().timestamp() - 2592000
                    else: return 0
                
                for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%B %d, %Y"]:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.timestamp()
                    except ValueError:
                        continue
                return 0
            except:
                return 0
        
        sorted_pairs = sorted(zip(all_info, all_files), key=lambda x: get_date_sort_key(x[0]), reverse=True)
        all_info, all_files = zip(*sorted_pairs) if sorted_pairs else ([], [])
        all_info = list(all_info)
        all_files = list(all_files)
    
    return all_files, all_info

def parse_relative_date(relative_date_str):
    """
    从相对日期描述（如'Last update 4 days ago'）推算出绝对日期
    
    Args:
        relative_date_str (str): 相对日期描述字符串
    
    Returns:
        str: YYYY-MM-DD格式的绝对日期，如果无法解析则返回空字符串
    """
    today = datetime.now()
    
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
                
                parsed_date = datetime.strptime(date_str, date_format)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
    
    # 如果无法解析，返回空字符串
    return ""

def translate_with_openrouter(file_path, data, model_id, force_translate=False):
    """使用OpenRouter API进行翻译"""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        st.error("未设置OPENROUTER_API_KEY环境变量")
        return False
    
    # 设置应用标识信息
    app_name = "N8N Workflow Viewer"
    site_url = "https://github.com/geallenboy/ai-python"
    
    title = data.get("title", "")
    readme = data.get("readme", "")
    workflow_json_str = data.get("workflow_json", "")
    
    fields_to_translate = []
    if title and (not data.get("title_zh") or force_translate): fields_to_translate.append("title")
    if readme and (not data.get("readme_zh") or force_translate): fields_to_translate.append("readme")
    if workflow_json_str and (not data.get("workflow_json_zh") or force_translate): fields_to_translate.append("workflow_json")
    
    # 处理publish_date_absolute字段，无论是否强制翻译
    if "publish_date" in data and data["publish_date"]:
        if "publish_date_absolute" not in data or not data["publish_date_absolute"] or force_translate:
            logger.info(f"处理publish_date_absolute字段: {file_path}")
            
            # 从相对日期推算绝对日期
            relative_date = data["publish_date"]
            absolute_date = parse_relative_date(relative_date)
            
            # 添加publish_date_absolute字段
            data["publish_date_absolute"] = absolute_date
            logger.info(f"已成功推算publish_date_absolute字段: {relative_date} -> {absolute_date}")
    
    if not fields_to_translate:
        if force_translate:
            st.info(f"文件 {file_path.name} 没有可翻译内容")
        else:
            st.info(f"文件 {file_path.name} 所有字段已翻译")
        return True
    
    st.info(f"需要翻译的字段: {', '.join(fields_to_translate)}")
    
    for field in fields_to_translate:
        content = data.get(field, "")
        if not content: continue
            
        if field == "title":
            prompt = f"将以下n8n工作流标题翻译成中文。只返回翻译后的文本，不要包含原文或其他解释：\n\n{content}"
        elif field == "readme":
            prompt = f"将以下n8n工作流描述翻译成中文。保持原文的markdown格式。只返回翻译后的文本，不要包含原文或其他解释：\n\n{content}"
        elif field == "workflow_json":
            try:
                workflow_data = json.loads(content) if isinstance(content, str) else content
                translate_fields = {
                    "name": workflow_data.get("name", ""),
                    "description": workflow_data.get("description", ""),
                    "nodes": [{"name": node.get("name", ""), "description": node.get("description", "")} 
                             for node in workflow_data.get("nodes", [])]
                }
                prompt = f"""将以下n8n工作流的文本字段翻译成中文。只翻译JSON中的文本值，保持原始JSON结构不变。
                返回格式必须是有效的JSON：
                
                {json.dumps(translate_fields, ensure_ascii=False, indent=2)}"""
            except Exception as e:
                st.error(f"解析workflow_json时出错: {str(e)}")
                continue
        
        try:
            st.info(f"正在使用OpenRouter ({model_id}) 翻译 {field}...")
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": site_url,
                "X-Title": app_name
            }
            
            payload = {
                "model": model_id,
                "messages": [
                    {"role": "system", "content": "你是一位专业翻译，请将提供的内容精确翻译成中文。保持原文的格式和信息。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 4000 if field == "workflow_json" else 2000
            }
            
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            
            if response.status_code != 200:
                st.error(f"OpenRouter API请求失败: {response.status_code}, {response.text}")
                
                # 尝试使用DeepSeek作为备选
                if os.environ.get("DEEPSEEK_API_KEY"):
                    st.warning("尝试使用DeepSeek API作为备选翻译引擎...")
                    translated_text = translate_with_deepseek(content, field)
                    if translated_text:
                        if field == "workflow_json":
                            try:
                                # 处理workflow_json的特殊情况
                                workflow_data_orig = json.loads(content) if isinstance(content, str) else content
                                translated_json_data = json.loads(translated_text)
                                
                                if "name" in translated_json_data: workflow_data_orig["name"] = translated_json_data["name"]
                                if "description" in translated_json_data: workflow_data_orig["description"] = translated_json_data["description"]
                                
                                if "nodes" in translated_json_data and "nodes" in workflow_data_orig:
                                    for i, node in enumerate(workflow_data_orig["nodes"]):
                                        if i < len(translated_json_data["nodes"]):
                                            translated_node = translated_json_data["nodes"][i]
                                            if "name" in translated_node: node["name"] = translated_node["name"]
                                            if "description" in translated_node: node["description"] = translated_node["description"]
                                
                                # 处理sticky notes节点
                                for node in workflow_data_orig.get("nodes", []):
                                    if node.get("type") == "n8n-nodes-base.stickyNote" and "parameters" in node and "content" in node["parameters"]:
                                        sticky_content = node["parameters"]["content"]
                                        if sticky_content and len(sticky_content) > 0:
                                            # 翻译便利贴内容
                                            sticky_prompt = f"将以下便利贴内容翻译成中文，保持格式：\n\n{sticky_content}"
                                            try:
                                                sticky_payload = payload.copy()
                                                sticky_payload["messages"][1]["content"] = sticky_prompt
                                                sticky_response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                                                                              headers=headers, json=sticky_payload)
                                                if sticky_response.status_code == 200:
                                                    sticky_result = sticky_response.json()
                                                    node["parameters"]["content"] = sticky_result.get("choices", [{}])[0].get("message", {}).get("content", "")
                                            except Exception as e:
                                                logger.error(f"翻译便利贴内容时出错: {str(e)}")
                            except Exception as e:
                                logger.error(f"处理workflow_json的特殊情况时出错: {str(e)}")
                                continue
                    
                    data[f"{field}_zh"] = json.dumps(workflow_data_orig, ensure_ascii=False)
                    st.success(f"使用DeepSeek成功翻译了 {field}")
                    continue
                else:
                    continue
                
            result = response.json()
            translated_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if field == "workflow_json":
                try:
                    # 处理可能的Markdown代码块包装
                    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', translated_text)
                    if json_match:
                        translated_json_text = json_match.group(1)
                    else:
                        translated_json_text = translated_text
                    
                    translated_json_data = json.loads(translated_json_text)
                    
                    workflow_data_orig = json.loads(content) if isinstance(content, str) else content
                    
                    if "name" in translated_json_data: workflow_data_orig["name"] = translated_json_data["name"]
                    if "description" in translated_json_data: workflow_data_orig["description"] = translated_json_data["description"]
                    
                    if "nodes" in translated_json_data and "nodes" in workflow_data_orig:
                        for i, node in enumerate(workflow_data_orig["nodes"]):
                            if i < len(translated_json_data["nodes"]):
                                translated_node = translated_json_data["nodes"][i]
                                if "name" in translated_node: node["name"] = translated_node["name"]
                                if "description" in translated_node: node["description"] = translated_node["description"]
                    
                    # 处理sticky notes节点
                    for node in workflow_data_orig.get("nodes", []):
                        if node.get("type") == "n8n-nodes-base.stickyNote" and "parameters" in node and "content" in node["parameters"]:
                            sticky_content = node["parameters"]["content"]
                            if sticky_content and len(sticky_content) > 0:
                                # 翻译便利贴内容
                                sticky_prompt = f"将以下便利贴内容翻译成中文，保持格式：\n\n{sticky_content}"
                                try:
                                    sticky_payload = payload.copy()
                                    sticky_payload["messages"][1]["content"] = sticky_prompt
                                    sticky_response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                                                                  headers=headers, json=sticky_payload)
                                    if sticky_response.status_code == 200:
                                        sticky_result = sticky_response.json()
                                        node["parameters"]["content"] = sticky_result.get("choices", [{}])[0].get("message", {}).get("content", "")
                                except Exception as e:
                                    logger.error(f"翻译便利贴内容时出错: {str(e)}")
                    
                    data[f"{field}_zh"] = json.dumps(workflow_data_orig, ensure_ascii=False)
                except Exception as e:
                    st.error(f"处理翻译后的workflow_json时出错: {str(e)}")
                    continue
            else:
                data[f"{field}_zh"] = translated_text
        
        except Exception as e:
            st.error(f"翻译 {field} 时出错: {str(e)}")
            continue
        
        # 如果字段是publish_date，同时处理publish_date_zh
        if field == "title" and "publish_date" in data and data["publish_date"]:
            if not data.get("publish_date_zh") or force_translate:
                try:
                    publish_date = data["publish_date"]
                    prompt = f"将以下n8n工作流发布日期翻译成中文。只返回翻译后的文本，不要包含原文或其他解释：\n\n{publish_date}"
                    
                    st.info(f"正在使用OpenRouter ({model_id}) 翻译 publish_date...")
                    
                    payload["messages"][1]["content"] = prompt
                    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        result = response.json()
                        translated_date = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                        data["publish_date_zh"] = translated_date
                        st.success(f"已成功翻译publish_date: {publish_date} -> {translated_date}")
                    else:
                        st.error(f"翻译publish_date失败: {response.status_code}, {response.text}")
                except Exception as e:
                    st.error(f"翻译publish_date时出错: {str(e)}")
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        st.success(f"文件 {file_path.name} 翻译完成并保存")
        return True
    except Exception as e:
        st.error(f"保存翻译后的文件 {file_path} 时出错: {str(e)}")
        return False

def translate_with_deepseek(content, field_type):
    """使用DeepSeek API进行翻译"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        logger.error("未设置DEEPSEEK_API_KEY环境变量")
        return None
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 根据字段类型构建不同的提示
        if field_type == "title":
            system_prompt = "你是一位专业翻译，请将提供的n8n工作流标题翻译成中文。只返回翻译后的文本，不要包含原文或其他解释。"
        elif field_type == "readme":
            system_prompt = "你是一位专业翻译，请将提供的n8n工作流描述翻译成中文。保持原文的markdown格式。只返回翻译后的文本，不要包含原文或其他解释。"
        elif field_type == "workflow_json":
            system_prompt = "你是一位专业翻译，请将提供的n8n工作流JSON中的文本字段翻译成中文。只翻译JSON中的文本值，保持原始JSON结构不变。返回格式必须是有效的JSON。"
        else:
            system_prompt = "你是一位专业翻译，请将提供的内容翻译成中文。只返回翻译后的文本，不要包含原文或其他解释。"
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            "temperature": 0.1
        }
        
        response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        translated_text = result['choices'][0]['message']['content'].strip()
        
        # 添加短暂延迟以避免API限制
        time.sleep(0.5)
        return translated_text
    
    except Exception as e:
        logger.error(f"DeepSeek翻译失败: {e}")
        return None

def process_json_file(file_path, model="anthropic/claude-3-7-sonnet", force_translate=False):
    """
    处理单个JSON文件，翻译其中的内容
    
    Args:
        file_path: JSON文件路径
        model: 使用的OpenRouter模型ID
        force_translate: 是否强制重新翻译已有内容
        
    Returns:
        bool: 是否成功处理
    """
    try:
        logs_dir = Path(__file__).parent / 'logs'
        logs_dir.mkdir(exist_ok=True)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        title = data.get("title", "")
        readme = data.get("readme", "")
        workflow_json = data.get("workflow_json", "")
        
        # 检查是否已全部翻译，若是，则根据force_translate决定是否继续
        if not force_translate and (title and data.get("title_zh")) and \
           (readme and data.get("readme_zh")) and \
           (workflow_json and data.get("workflow_json_zh")):
            st.info(f"文件 {file_path.name} 已经翻译完成，使用\"重新翻译\"按钮可覆盖现有翻译")
            return True
        
        # 使用OpenRouter进行翻译
        success = translate_with_openrouter(file_path, data, model, force_translate)
        
        return success
        
    except Exception as e:
        st.error(f"处理文件 {file_path} 时出错: {str(e)}")
        with open(Path(__file__).parent / 'logs' / 'translation_errors.log', 'a', encoding='utf-8') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 处理文件 {file_path} 时出错: {str(e)}\n")
        return False

def get_download_link(content, filename, text):
    """生成下载链接"""
    if isinstance(content, str):
        content_bytes = content.encode('utf-8')
    else:
        content_bytes = json.dumps(content, ensure_ascii=False, indent=2).encode('utf-8')
    
    b64 = base64.b64encode(content_bytes).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="{filename}" class="download-btn">{text}</a>'
    return href

def format_datetime(date_str):
    """格式化日期时间字符串"""
    if not date_str: return ""
    try:
        formats = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%B %d, %Y"]
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return date_str
    except Exception:
        return date_str

def display_json_content(json_path, index):
    """展示单个JSON文件的内容"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        title_zh = data.get("title_zh", "")
        title_en = data.get("title", "")
        display_title = title_zh if title_zh else title_en if title_en else json_path.name
        
        publish_date = format_datetime(data.get("publish_date", ""))
        tags = data.get("tags", [])
        tag_display = " ".join([f"<span class='tag'>{tag}</span>" for tag in tags]) if tags else ""
        
        has_zh_title = bool("title_zh" in data and data["title_zh"])
        has_zh_readme = bool("readme_zh" in data and data["readme_zh"])
        has_zh_workflow = bool("workflow_json_zh" in data and data["workflow_json_zh"])
        
        total_items = 3
        translated_items = sum([has_zh_title, has_zh_readme, has_zh_workflow])
        translation_percent = int((translated_items / total_items) * 100)
        
        if translation_percent == 100:
            translation_badge = f"<span class='badge badge-success'>已翻译</span>"
        elif translation_percent > 0:
            translation_badge = f"<span class='badge badge-warning'>部分翻译 {translation_percent}%</span>"
        else:
            translation_badge = f"<span class='badge badge-danger'>未翻译</span>"
        
        with st.expander(f"#{index} - {display_title} {publish_date} {translation_badge}", expanded=False):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.caption(f"翻译状态: 标题 {'✅' if has_zh_title else '❌'} | 描述 {'✅' if has_zh_readme else '❌'} | 工作流 {'✅' if has_zh_workflow else '❌'}")
            with col2:
                # 翻译按钮 - 无论是否已翻译都显示
                if st.button("🌐 翻译此文件", key=f"translate_{index}_{json_path.name}"):
                    success = False
                    with st.spinner("正在翻译..."):
                        selected_model = st.session_state.selected_model
                        model_name = st.session_state.model_options.get(selected_model, selected_model.split("/")[-1])
                        
                        st.info(f"使用 {model_name} 进行翻译...")
                        success = process_json_file(json_path, model=selected_model)
                    
                    # 显示翻译结果
                    if success:
                        st.success("✅ 翻译成功！")
                        # 读取更新后的文件内容
                        with open(json_path, 'r', encoding='utf-8') as f_updated:
                            updated_data = json.load(f_updated)
                        
                        # 更新当前数据，这样基本信息标签页会显示最新翻译内容
                        data = updated_data
                        
                        # 更新翻译状态指标
                        has_zh_title = bool("title_zh" in data and data["title_zh"])
                        has_zh_readme = bool("readme_zh" in data and data["readme_zh"])
                        has_zh_workflow = bool("workflow_json_zh" in data and data["workflow_json_zh"])
                        translated_items = sum([has_zh_title, has_zh_readme, has_zh_workflow])
                        translation_percent = int((translated_items / total_items) * 100)
                        
                        st.info("✨ 翻译已完成，请在「基本信息」标签页查看中文翻译内容")
                        
                        # 添加刷新按钮，用于完全刷新页面（更新expander标题中的翻译状态等）
                        if st.button("🔄 刷新页面更新状态", key=f"refresh_{index}"):
                            st.rerun()
                    else:
                        st.error("❌ 翻译失败，请查看日志或检查API密钥设置")
            
            with col3:
                # 重新翻译按钮 - 只有当至少有一项已翻译时才显示
                if translation_percent > 0:
                    if st.button("🔄 重新翻译", key=f"retranslate_{index}_{json_path.name}"):
                        with st.spinner("正在重新翻译..."):
                            selected_model = st.session_state.selected_model
                            model_name = st.session_state.model_options.get(selected_model, selected_model.split("/")[-1])
                            
                            st.info(f"使用 {model_name} 重新翻译...")
                            # 使用force_translate参数强制重新翻译
                            success = process_json_file(json_path, model=selected_model, force_translate=True)
                        
                        if success:
                            st.success("✅ 重新翻译成功！")
                            # 读取更新后的文件内容
                            with open(json_path, 'r', encoding='utf-8') as f_updated:
                                updated_data = json.load(f_updated)
                            
                            # 更新当前数据
                            data = updated_data
                            
                            st.info("✨ 翻译已更新，请在「基本信息」标签页查看中文翻译内容")
                            
                            # 添加刷新按钮
                            if st.button("🔄 刷新页面查看更新", key=f"refresh_retranslate_{index}"):
                                st.rerun()
                        else:
                            st.error("❌ 重新翻译失败，请查看日志或检查API密钥设置")
            
            if tag_display:
                st.markdown(f"<div class='tags-container'>{tag_display}</div>", unsafe_allow_html=True)
            st.caption(f"文件路径: {json_path}")
            
            # 修改标签页显示，避免嵌套问题
            tabs = st.tabs(["基本信息", "工作流数据", "工作流分析", "原始JSON"])
            
            # Tab 1: 基本信息
            with tabs[0]:
                info_tabs = st.tabs(["中文信息", "英文信息"])
                # 中文信息标签
                with info_tabs[0]:
                    st.write("**中文标题:** ", data.get("title_zh", "(未翻译)" if data.get("title") else ""))
                    st.write("**中文日期:** ", data.get("publish_date_zh", "(未翻译)" if data.get("publish_date") else ""))
                    if tags: st.write("**标签:** ", ", ".join(tags))
                    if "readme_zh" in data and data["readme_zh"]:
                        st.markdown("### 中文描述")
                        st.markdown(data["readme_zh"])
                    elif "readme" in data and data["readme"]:
                        st.markdown("### 中文描述")
                        st.write("(内容未翻译)")
                
                # 英文信息标签
                with info_tabs[1]:
                    if "title" in data and data["title"]: st.write("**标题 (Title):** ", data["title"])
                    if "publish_date" in data and data["publish_date"]: st.write("**发布日期 (Publish Date):** ", publish_date)
                    if tags: st.write("**标签 (Tags):** ", ", ".join(tags))
                    if "readme" in data and data["readme"]:
                        st.markdown("### 描述 (Description)")
                        st.markdown(data["readme"])
            
            # Tab 2: 工作流数据
            with tabs[1]:
                if "workflow_json" in data and data["workflow_json"]:
                    col1, col2 = st.columns([3, 1])
                    with col1: st.write("**原始工作流数据:**")
                    with col2:
                        filename = f"{os.path.splitext(json_path.name)[0]}_workflow_json.json"
                        st.markdown(get_download_link(data["workflow_json"], filename, "📥 下载原始工作流"), unsafe_allow_html=True)
                    try:
                        workflow = json.loads(data["workflow_json"]) if isinstance(data["workflow_json"], str) else data["workflow_json"]
                        st.write(f"工作流名称: {workflow.get('name', '未命名')}")
                        st.write(f"节点数量: {len(workflow.get('nodes', []))}")
                    except: st.write("无法解析工作流数据")
                
                if "workflow_json_zh" in data and data["workflow_json_zh"]:
                    st.markdown("---")
                    col1, col2 = st.columns([3, 1])
                    with col1: st.write("**中文工作流数据:**")
                    with col2:
                        filename = f"{os.path.splitext(json_path.name)[0]}_workflow_json_zh.json"
                        st.markdown(get_download_link(data["workflow_json_zh"], filename, "📥 下载中文工作流"), unsafe_allow_html=True)
            
            # Tab 3: 工作流分析
            with tabs[2]:
                if "workflow_analysis" in data and data["workflow_analysis"]:
                    st.markdown(data["workflow_analysis"])
                    st.write("---")
                    if st.button("🔄 使用当前选择的模型重新分析", key=f"reanalyze_{index}_{json_path.name}"):
                        selected_model = st.session_state.selected_model
                        model_name = st.session_state.model_options.get(selected_model, selected_model.split("/")[-1]).split(" (")[0]
                        with st.spinner(f"使用 {model_name} 重新分析工作流..."):
                            workflow_content = data["workflow_json_zh"] if "workflow_json_zh" in data and data["workflow_json_zh"] else data.get("workflow_json")
                            if workflow_content:
                                analysis = n8n_json_to_context.get_workflow_analysis(workflow_content, model=selected_model)
                                success = n8n_json_to_context.save_workflow_file(json_path, analysis)
                                if success:
                                    st.success("分析完成并已保存")
                                    with open(json_path, 'r', encoding='utf-8') as f_reloaded:
                                        data = json.load(f_reloaded)
                                    st.markdown(analysis)
                                    # 添加刷新按钮
                                    if st.button("🔄 刷新页面查看完整结果", key=f"refresh_analysis_{index}"):
                                        st.rerun()
                                else: 
                                    st.error("保存分析结果失败")
                            else: 
                                st.warning("无工作流数据可供分析。")
                else:
                    st.info("该工作流尚未进行分析。")
                
                workflow_content_for_analysis = data.get("workflow_json_zh") or data.get("workflow_json")
                if workflow_content_for_analysis:
                    analyze_button_text = "🔍 使用当前选择的模型分析" if not ("workflow_analysis" in data and data["workflow_analysis"]) else "🔍 使用当前模型重新分析"
                    if st.button(analyze_button_text, key=f"analyze_direct_{index}_{json_path.name}"):
                        selected_model = st.session_state.selected_model
                        model_name = st.session_state.model_options.get(selected_model, selected_model.split("/")[-1]).split(" (")[0]
                        with st.spinner(f"使用 {model_name} 分析工作流..."):
                            analysis = n8n_json_to_context.get_workflow_analysis(workflow_content_for_analysis, model=selected_model)
                            success = n8n_json_to_context.save_workflow_file(json_path, analysis)
                            if success:
                                st.success("分析完成并已保存")
                                st.markdown(analysis)
                                # 添加刷新按钮
                                if st.button("🔄 刷新页面查看完整结果", key=f"refresh_direct_{index}"):
                                    st.rerun()
                            else: 
                                st.error("保存分析结果失败")
                elif not ("workflow_analysis" in data and data["workflow_analysis"]):
                     st.warning("此文件不包含工作流数据，无法进行分析。")

            # Tab 4: 原始JSON
            with tabs[3]:
                st.json(data)
                
    except Exception as e:
        st.error(f"读取文件 {json_path.name} 时出错: {str(e)}")
        st.exception(e)  # 添加详细错误信息

def load_categories():
    """从n8n_categories.json加载分类信息"""
    categories_file = Path(__file__).parent / "data" / "workflow" / "n8n_categories.json"
    if not categories_file.exists():
        st.warning("未找到分类数据文件 n8n_categories.json")
        return [{"category_name": "全部", "category_url": ""}]
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
        categories = [{"category_name": "全部", "category_url": ""}]
        for item in categories_data:
            if isinstance(item, dict) and "category_name" in item and "category_url" in item:
                categories.append(item)
        return categories
    except Exception as e:
        st.error(f"加载分类数据出错: {e}")
        return [{"category_name": "全部", "category_url": ""}]

def batch_translate_files(file_paths, force_translate=False):
    """批量翻译选定的文件"""
    if not file_paths:
        st.warning("没有选择任何文件")
        return
    
    selected_model = st.session_state.selected_model
    model_name = st.session_state.model_options.get(selected_model, selected_model.split("/")[-1])
    
    st.info(f"使用 {model_name} 批量翻译...")
    progress_bar = st.progress(0)
    status_text = st.empty()
    success_count = 0
    failed_files = []
    
    for i, file_path in enumerate(file_paths):
        progress = (i) / len(file_paths)
        progress_bar.progress(progress)
        status_text.text(f"正在翻译 ({i+1}/{len(file_paths)}): {file_path.name}")
        
        try:
            success = process_json_file(file_path, model=selected_model, force_translate=force_translate)
            if success: success_count += 1
            else: failed_files.append(file_path.name)
        except Exception as e:
            st.error(f"翻译文件 {file_path.name} 时出错: {str(e)}")
            failed_files.append(file_path.name)
        time.sleep(1) # API rate limit avoidance
    
    progress_bar.progress(1.0)
    status_text.text(f"翻译完成! 成功: {success_count}/{len(file_paths)}")
    if success_count > 0: st.success(f"成功翻译 {success_count} 个文件")
    if failed_files: st.warning(f"有 {len(failed_files)} 个文件翻译失败: {', '.join(failed_files)}")
    if success_count > 0:
        st.info("3秒后刷新页面...")
        time.sleep(3)
        st.rerun()

def main():
    st.markdown("""
    <style>
    .download-btn { display: inline-block; padding: 0.3rem 0.6rem; background-color: #4CAF50; color: white !important; text-decoration: none; border-radius: 4px; text-align: center; transition: background-color 0.3s; }
    .download-btn:hover { background-color: #45a049; text-decoration: none; }
    .tag { display: inline-block; background-color: #f1f1f1; padding: 2px 6px; margin: 2px; border-radius: 3px; font-size: 0.8rem; }
    .tags-container { margin-bottom: 10px; }
    .category-badge { background-color: #e8f0fe; color: #1967d2; padding: 3px 8px; border-radius: 12px; font-size: 0.85rem; display: inline-block; margin-right: 5px; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem; font-weight: bold; }
    .badge-success { background-color: #28a745; color: white; }
    .badge-warning { background-color: #ffc107; color: black; }
    .badge-danger { background-color: #dc3545; color: white; }
    </style>
    """, unsafe_allow_html=True)
    
    categories = load_categories()
    category_names = [cat["category_name"] for cat in categories]
    
    with st.sidebar:
        st.header("搜索和过滤")
        search_query = st.text_input("搜索文件名或标题", "")
        selected_category = st.selectbox("按分类过滤", category_names)
        
        translation_options = ["全部", "已翻译", "未翻译", "部分翻译"]
        translation_filter = st.radio("翻译状态", translation_options)
        has_translation = None
        if translation_filter == "已翻译": has_translation = True
        elif translation_filter == "未翻译": has_translation = False
        elif translation_filter == "部分翻译": has_translation = "partial"
        
        items_per_page = st.slider("每页显示数量", 5, 50, 10, 5)
        
        if st.button("重置过滤器"):
            st.session_state.page_number = 1
            st.rerun()
            
        st.header("AI 模型选择")
        model_list = n8n_json_to_context.get_available_models()
        
        # Default model options if API call fails or returns empty
        default_model_options_list = {
            "anthropic/claude-3-7-sonnet": "Claude 3.7 Sonnet (推荐)",
            "anthropic/claude-3-5-sonnet": "Claude 3.5 Sonnet",
            "anthropic/claude-3-haiku": "Claude 3 Haiku (快速)",
            "anthropic/claude-3-opus": "Claude 3 Opus (高质量)",
            "openai/gpt-4o": "GPT-4o",
            "openai/gpt-4-turbo": "GPT-4 Turbo",
            "deepseek/deepseek-chat": "DeepSeek Chat (通用)",
        }

        current_model_options = {model["id"]: f"{model['name']} ({model.get('context_length', 0)//1000}K)" for model in model_list} if model_list else default_model_options_list

        if 'model_options' not in st.session_state or st.session_state.model_options != current_model_options:
             st.session_state.model_options = current_model_options
        
        default_model_id = "anthropic/claude-3-7-sonnet"
        available_model_ids = list(st.session_state.model_options.keys())
        
        default_index = available_model_ids.index(default_model_id) if default_model_id in available_model_ids else 0
        
        if 'selected_model' not in st.session_state or st.session_state.selected_model not in available_model_ids:
            st.session_state.selected_model = available_model_ids[default_index]
        
        # Unified model selection for analysis and translation
        st.session_state.selected_model = st.selectbox(
            "选择AI模型 (用于分析和翻译)", 
            options=available_model_ids,
            format_func=lambda x: st.session_state.model_options[x],
            index=available_model_ids.index(st.session_state.selected_model)
        )
        st.info(f"当前选择: {st.session_state.model_options[st.session_state.selected_model]}")

    json_files, _ = get_all_json_files(
        data_dir, 
        query=search_query, 
        category_filter=selected_category,
        has_translation=has_translation
    )
    
    st.write(f"共找到 {len(json_files)} 个文件")
    if not json_files:
        st.info("没有找到符合过滤条件的文件。请尝试调整过滤器或搜索条件。")
        return
    
    total_pages = math.ceil(len(json_files) / items_per_page)
    if st.session_state.page_number < 1: st.session_state.page_number = 1
    elif st.session_state.page_number > total_pages and total_pages > 0: st.session_state.page_number = total_pages
    elif total_pages == 0 : st.session_state.page_number = 1


    start_idx = (st.session_state.page_number - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(json_files))
    
    if total_pages > 0: # Only show pagination if there are pages
        st.write(f"第 {st.session_state.page_number} 页，共 {total_pages} 页")
        
        page_cols = st.columns([1, 3, 1])
        if st.session_state.page_number > 1:
            if page_cols[0].button("上一页"):
                st.session_state.page_number -= 1
                st.rerun()
        
        page_options = list(range(1, total_pages + 1)) if total_pages > 0 else [1]
        # Ensure selected_page_index is valid
        current_page_index = st.session_state.page_number - 1
        if current_page_index >= len(page_options): current_page_index = len(page_options) -1
        if current_page_index < 0: current_page_index = 0

        selected_page_from_selectbox = page_cols[1].selectbox("跳转到页", page_options, index=current_page_index, label_visibility="collapsed")
        if selected_page_from_selectbox != st.session_state.page_number:
            st.session_state.page_number = selected_page_from_selectbox
            st.rerun()
        
        if st.session_state.page_number < total_pages:
            if page_cols[2].button("下一页"):
                st.session_state.page_number += 1
                st.rerun()
    
    for i, json_path in enumerate(json_files[start_idx:end_idx], start=start_idx+1):
        display_json_content(json_path, i)

    st.header("批量翻译工具")
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
    
    if not openrouter_api_key and not deepseek_api_key:
        st.warning("未设置 OPENROUTER_API_KEY 或 DEEPSEEK_API_KEY 环境变量。批量翻译功能不可用。请在.env文件中配置至少一个API密钥。")
    else:
        api_keys_info = []
        if openrouter_api_key: api_keys_info.append("OpenRouter")
        if deepseek_api_key: api_keys_info.append("DeepSeek (备选)")
        
        st.success(f"已配置API密钥: {', '.join(api_keys_info)}，批量翻译功能可用。")
        
        # 添加"重新翻译"选项
        col1, col2 = st.columns(2)
        with col1:
            if st.button("翻译当前页面显示的文件"):
                current_page_files = json_files[start_idx:end_idx]
                batch_translate_files(current_page_files)
        
        with col2:
            if st.button("翻译当前页面文件 (强制重新翻译)"):
                current_page_files = json_files[start_idx:end_idx]
                batch_translate_files(current_page_files, force_translate=True)
        
        # 全局批量翻译选项
        col3, col4 = st.columns(2)
        with col3:
            if st.button("翻译所有未翻译/部分翻译的文件 (最多20个)"):
                all_files_for_batch, all_info_for_batch = get_all_json_files(data_dir)
                untranslated_files = []
                for file_path, info in zip(all_files_for_batch, all_info_for_batch):
                    fully_translated = (info.get("has_workflow_json_zh", False) and 
                                        info.get("has_readme_zh", False) and 
                                        info.get("title_zh", ""))
                    if not fully_translated:
                        untranslated_files.append(file_path)
                
                if untranslated_files:
                    st.info(f"找到 {len(untranslated_files)} 个未完全翻译的文件。将处理最多20个。")
                    max_batch = min(20, len(untranslated_files))
                    batch_translate_files(untranslated_files[:max_batch])
                else:
                    st.info("所有文件都已完全翻译。")
        
        with col4:
            if st.button("强制重新翻译所有已翻译文件 (最多10个)"):
                all_files_for_batch, all_info_for_batch = get_all_json_files(data_dir)
                translated_files = []
                for file_path, info in zip(all_files_for_batch, all_info_for_batch):
                    has_any_translation = (info.get("has_workflow_json_zh", False) or 
                                        info.get("has_readme_zh", False) or 
                                        info.get("title_zh", ""))
                    if has_any_translation:
                        translated_files.append(file_path)
                
                if translated_files:
                    st.info(f"找到 {len(translated_files)} 个已有翻译的文件。将强制重新翻译最多10个。")
                    max_batch = min(10, len(translated_files))
                    batch_translate_files(translated_files[:max_batch], force_translate=True)
                else:
                    st.info("没有找到已翻译的文件。")

if __name__ == "__main__":
    main()