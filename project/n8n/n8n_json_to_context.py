#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
该脚本用于将n8n工作流JSON数据转换为人类可理解的上下文描述
使用OpenRouter API调用大型语言模型进行分析
"""

import os
import json
import logging
import requests
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 确保logs目录存在
logs_dir = Path("logs")
if not logs_dir.exists():
    logs_dir.mkdir(parents=True, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(logs_dir / "n8n_json_to_context.log", encoding='utf-8')
    ]
)
logger = logging.getLogger("n8n_json_to_context")

# 获取OpenRouter API密钥
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY未设置，请在.env文件中添加OPENROUTER_API_KEY")

def get_workflow_analysis(workflow_json, model="anthropic/claude-3-haiku"):
    """
    使用OpenRouter API分析n8n工作流JSON数据
    
    Args:
        workflow_json: n8n工作流JSON数据
        model: 使用的AI模型
    
    Returns:
        str: 分析结果文本
    """
    if not OPENROUTER_API_KEY:
        return "API密钥未设置，无法分析工作流。请设置OPENROUTER_API_KEY环境变量。"
    
    # 准备提示词
    prompt = """你是一位专业的 n8n 工作流解释器，你的任务是将复杂的 n8n 工作流 JSON 数据转换成清晰、简洁、面向非技术用户的白话文说明。请按照以下结构组织你的输出：

    **1. 工作流概述：**
    - 简要描述工作流的整体目标和功能。
    - 这个工作流是做什么的？它能解决什么问题？
    - 为用户带来什么价值？
    - 使用通俗易懂的语言，避免技术术语。
    - 强调工作流解决的问题和带来的价值。

    **2. 工作流执行流程：**
    - 说明工作流如何被触发启动（例如：表单提交、定时触发、Webhook等）
    - 按顺序描述工作流执行的主要步骤和处理流程
    - 解释数据如何在各节点间流动和转换
    - 描述工作流的最终产出和结果交付方式
    - 使用简单的语言描述每个节点的功能和作用

    **3. 主要节点功能解析：**
    - 识别并解释工作流中的关键节点或节点组
    - 对每个重要节点解释它做什么、处理什么数据
    - 重点说明节点的实际业务功能，而非技术实现
    - 对复杂节点使用简单比喻或类比帮助理解

    **4. 所需集成和服务：**
    - 列出工作流依赖的外部服务和集成（如Google服务、API等）
    - 简要解释每个服务在工作流中的作用
    - 提及可能需要的凭证或权限

    **5. 设置和配置指南：**
    - 提供清晰的初始设置步骤
    - 列出用户需要配置的关键参数和字段
    - 解释参数设置对工作流行为的影响
    - 提供任何必要的前置条件

    **6. 使用场景与示例：**
    - 提供3-5个实际使用场景描述
    - 通过具体例子说明工作流如何在实际业务中发挥作用
    - 展示最终用户如何从中受益

    **7. 注意事项和最佳实践：**
    - 提醒用户使用过程中需要注意的事项
    - 提供提高工作流效果的建议
    - 说明任何潜在的局限性或风险

    **7. 故障排除与常见问题：**
    - 预测可能遇到的常见问题
    - 提供简单的故障诊断和解决方案
    - 建议何时需要寻求技术支持

    **请参考以下 JSON 数据：**

    ```json
    {workflow_json}
    ````
    请确保你的输出满足以下要求：
    面向受众：假设读者是非技术人员，但对自己的业务领域有专业知识
    语言风格：简洁、清晰、友好，避免使用技术术语和行话。
    解释深度：找到适当平衡，既不过于简化也不陷入技术细节
    实用导向：侧重于"如何使用"和"解决什么问题"，而非"如何构建"
    本地化：使用自然、流畅的表达，适合目标语言读者（中文）
    详细程度：提供足够的细节，使读者能够理解工作流的功能和执行流程，但避免过度解释。
    逻辑清晰：使用标题、列表和短段落增强可读性
    实用性：强调工作流的实际应用和价值，以及如何使用它来解决实际问题。
    输出为中文。 
    开头不要有任何开场白、问候语或介绍性文字，如"好的"、"我会为您提供"等。
    结束时，不要添加任何总结、额外服务提议或询问，如"希望这份解释有所帮助"、"如有其他问题"等"""

    #将工作流JSON数据插入提示词
    if isinstance(workflow_json, dict): 
        workflow_json_str = json.dumps(workflow_json, ensure_ascii=False) 
    else: workflow_json_str = workflow_json 

    prompt = prompt.replace("{workflow_json}", workflow_json_str)

    # 调用OpenRouter API
    url = "https://openrouter.ai/api/v1/chat/completions" 
    headers = { "Content-Type": "application/json", "Authorization": f"Bearer {OPENROUTER_API_KEY}", "HTTP-Referer": "https://github.com/geallenboy/ai-python" }

    payload = { "model": model, "messages": [ {"role": "system", "content": "You are a professional n8n workflow analyst. Your task is to analyze complex n8n workflow JSON data and convert it into clear, concise, and user-friendly explanations in Chinese."}, {"role": "user", "content": prompt} ], "max_tokens": 4000, "temperature": 0.7 }

    try: 
        response = requests.post(url, headers=headers, json=payload) 
        response.raise_for_status() 
        result = response.json() 
        analysis = result["choices"][0]["message"]["content"] 
        return analysis 
    except Exception as e: 
        logger.error(f"调用API时出错: {e}") 
        return f"分析工作流时出错: {str(e)}"

def save_workflow_file(file_path: str, analysis: str) -> bool: 
    """ 将分析结果保存到指定的JSON文件中 Args: file_path: 文件路径 analysis: 分析结果
    Returns:
    bool: 是否保存成功
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 添加分析结果
        data["workflow_analysis"] = analysis
        
        # 保存更新后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"保存到文件时出错: {e}")
        return False

def analyze_workflow_file(file_path: str, force: bool = False) -> str: 
    """ 分析工作流文件，生成可理解的上下文描述
    Args:
    file_path: 工作流JSON文件路径
    force: 是否强制重新分析已有结果

    Returns:
        str: 分析结果或错误信息
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"
        
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 如果已经有分析结果且不强制重新分析，则直接返回
        if "workflow_analysis" in data and not force:
            return data["workflow_analysis"]
        
        # 检查是否有工作流数据
        if "workflow_json" not in data or not data["workflow_json"]:
            if "workflow_json_zh" not in data or not data["workflow_json_zh"]:
                return "此文件不包含工作流数据"
            else:
                workflow_json = data["workflow_json_zh"]
        else:
            workflow_json = data["workflow_json"]
        
        # 分析工作流
        analysis = get_workflow_analysis(workflow_json)
        
        # 保存分析结果
        if save_workflow_file(file_path, analysis):
            logger.info(f"成功分析并保存: {file_path}")
        else:
            logger.error(f"保存分析结果失败: {file_path}")
        
        return analysis
    except Exception as e:
        logger.error(f"分析工作流时出错: {e}")
        return f"分析工作流时出错: {str(e)}"
    
def get_available_models():
    """
    获取OpenRouter上可用的所有模型列表
    
    Returns:
        list: 可用模型列表，每个模型为一个字典，包含id、name等信息
    """
    try:
        if not OPENROUTER_API_KEY:
            logger.warning("未设置OPENROUTER_API_KEY，无法获取模型列表")
            return get_default_models()
        
        url = "https://openrouter.ai/api/v1/models"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/geallenboy/ai-python"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # 获取所有模型数据
        models = data.get("data", [])
        
        # 过滤和排序模型
        # 1. 只保留Anthropic和OpenAI的模型
        # 2. 按提供商和名称排序
        filtered_models = [
            model for model in models 
            if "anthropic" in model.get("id", "") or "openai" in model.get("id", "")
        ]
        
        # 按提供商和模型名称排序
        sorted_models = sorted(
            filtered_models, 
            key=lambda x: (
                0 if "anthropic/claude-3" in x.get("id", "") else 1 if "anthropic" in x.get("id", "") else 2,
                x.get("id", "")
            )
        )
        
        return sorted_models
    except Exception as e:
        logger.error(f"获取模型列表时出错: {e}")
        return get_default_models()

def get_default_models():
    """
    返回默认的模型列表，当API调用失败时使用
    
    Returns:
        list: 默认模型列表
    """
    return [
        {
            "id": "anthropic/claude-3-7-sonnet",
            "name": "Claude 3.7 Sonnet (推荐)",
            "context_length": 200000,
        },
        {
            "id": "anthropic/claude-3-5-sonnet",
            "name": "Claude 3.5 Sonnet",
            "context_length": 200000,
        },
        {
            "id": "anthropic/claude-3-haiku",
            "name": "Claude 3 Haiku (快速)",
            "context_length": 200000,
        },
        {
            "id": "anthropic/claude-3-opus",
            "name": "Claude 3 Opus (高质量)",
            "context_length": 200000,
        },
        {
            "id": "openai/gpt-4o",
            "name": "GPT-4o",
            "context_length": 128000,
        },
        {
            "id": "openai/gpt-4-turbo",
            "name": "GPT-4 Turbo",
            "context_length": 128000,
        },
    ]
# 只有在直接运行此文件时才执行以下代码
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='分析n8n工作流JSON数据') 
    parser.add_argument('--file', help='需要分析的JSON文件路径') 
    parser.add_argument('--force', action='store_true', help='强制重新分析已有结果')
    args = parser.parse_args()

    if args.file:
        result = analyze_workflow_file(args.file, args.force)
        print(result)
    else:
        print("请使用--file参数指定要分析的JSON文件")