#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
该脚本用于清理 data/workflow/ 目录下所有 JSON 文件中的翻译字段
移除 readme_zh, title_zh, publish_date_zh, workflow_json_zh 等字段
"""

import os
import json
import logging
import sys
from pathlib import Path

# 当前脚本所在目录
current_dir = Path(__file__).parent
logs_dir = current_dir / 'logs'
if not logs_dir.exists():
    logs_dir.mkdir(parents=True, exist_ok=True)

# 配置日志 - 同时输出到文件和控制台
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 文件处理器 - 输出到日志文件
file_handler = logging.FileHandler(logs_dir / 'remove_translation_fields.log')
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

def remove_translation_fields(file_path):
    """
    从JSON文件中移除翻译字段
    
    Args:
        file_path (Path): JSON文件路径
        
    Returns:
        bool: 是否修改了文件
    """
    try:
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 要移除的翻译字段
        translation_fields = []
        #['readme_zh', 'title_zh', 'publish_date_zh', 'workflow_json_zh']
        
        # 检查并移除翻译字段
        modified = False
        removed_fields = []
        
        for field in translation_fields:
            if field in data:
                del data[field]
                removed_fields.append(field)
                modified = True
        
        # 如果有修改，保存文件
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"已从文件移除字段 {', '.join(removed_fields)}: {file_path}")
            return True
        else:
            logger.info(f"文件无需修改: {file_path}")
            return False
            
    except Exception as e:
        logger.error(f"处理文件 {file_path} 时出错: {e}")
        return False

def scan_workflow_directory(base_dir):
    """
    扫描工作流目录，处理所有JSON文件
    
    Args:
        base_dir (Path): 基础目录路径
    
    Returns:
        tuple: (处理的文件数, 修改的文件数)
    """
    workflow_dir = base_dir / 'data' / 'workflow'
    if not workflow_dir.exists() or not workflow_dir.is_dir():
        logger.error(f"工作流目录不存在: {workflow_dir}")
        return 0, 0
    
    total_files = 0
    modified_files = 0
    
    # 获取所有JSON文件
    json_files = list(workflow_dir.glob('**/*.json'))
    logger.info(f"找到 {len(json_files)} 个JSON文件")
    
    # 处理每个JSON文件
    for i, file_path in enumerate(json_files):
        total_files += 1
        relative_path = file_path.relative_to(base_dir)
        
        # 显示处理进度
        logger.info(f"正在处理 [{i+1}/{len(json_files)}]: {relative_path}")
        
        # 移除翻译字段
        if remove_translation_fields(file_path):
            modified_files += 1
        
        # 打印当前进度
        if (i+1) % 10 == 0 or i+1 == len(json_files):
            logger.info(f"进度: {i+1}/{len(json_files)} ({(i+1)/len(json_files)*100:.1f}%), 已修改: {modified_files}")
    
    return total_files, modified_files

def main():
    """主函数"""
    logger.info("=== 开始清理JSON文件翻译字段 ===")
    
    try:
        # 获取当前脚本所在目录
        base_dir = Path(__file__).parent
        
        # 处理工作流目录
        total_files, modified_files = scan_workflow_directory(base_dir)
        
        logger.info("=== 处理完成 ===")
        logger.info(f"共处理 {total_files} 个JSON文件，修改了 {modified_files} 个文件")
        
        print(f"处理完成。共处理 {total_files} 个JSON文件，修改了 {modified_files} 个文件")
        print(f"详细信息请查看日志文件: {logs_dir / 'remove_translation_fields.log'}")
    
    except Exception as e:
        logger.error(f"执行过程中出错: {e}")
        print(f"执行过程中出错: {e}")

if __name__ == "__main__":
    main()