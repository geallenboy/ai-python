#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
该脚本创建一个Streamlit页面，用于展示data/workflow目录下的所有JSON文件内容。
功能包括：文件搜索、分类过滤、预览展示、分页浏览和文件内容下载。
"""

import os
import json
import streamlit as st
import pandas as pd
from pathlib import Path
import math
import base64
import re
from datetime import datetime
import n8n_json_to_context

# 设置页面标题和配置
st.set_page_config(page_title="N8N工作流查看器", page_icon="🔄", layout="wide", initial_sidebar_state="expanded")
st.title("N8N工作流数据查看")

# 定义数据目录路径
current_dir = Path(__file__).parent
data_dir = current_dir / "data" / "workflow"

# 设置会话状态变量
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1

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
            "category": data.get("category", "未分类"),  # 添加分类字段
            "category_url": data.get("category_url", ""),  # 添加分类URL字段
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

def get_all_json_files(directory, query="", tag_filter=None, category_filter="全部", has_translation=None):
    """获取目录及其子目录下的所有JSON文件路径"""
    all_files = []
    all_info = []
    
    if not directory.exists():
        st.error(f"目录不存在: {directory}")
        return all_files, all_info
    
    # 遍历目录及子目录
    for path in directory.glob('**/*.json'):
        if path.is_file() and path.name != "n8n_categories.json":  # 跳过分类文件
            file_info = extract_json_info(path)
            if file_info:
                # 应用搜索和过滤
                if query:
                    # 在文件名或标题中搜索
                    title = file_info["title"] + " " + file_info["title_zh"]
                    if not (query.lower() in path.name.lower() or query.lower() in title.lower()):
                        continue
                
                # 标签过滤
                if tag_filter and not any(tag in file_info.get("tags", []) for tag in tag_filter):
                    continue
                
                # 分类过滤
                if category_filter != "全部" and file_info.get("category", "未分类") != category_filter:
                    continue
                
                # 翻译状态过滤
                if has_translation is not None:
                    if has_translation and not file_info.get("has_workflow_json_zh", False):
                        continue
                    elif not has_translation and file_info.get("has_workflow_json_zh", False):
                        continue
                
                all_files.append(path)
                all_info.append(file_info)
    
    # 对文件按发布日期进行排序
    if all_info:
        # 创建排序键函数
        def get_date_sort_key(info):
            # 首先检查是否有精确日期字段
            date_str = info.get("publish_date_absolute", "")
            if not date_str:
                date_str = info.get("publish_date", "")
            
            # 尝试解析日期
            try:
                # 如果日期字符串包含"hours ago"、"days ago"等相对时间信息
                if "ago" in date_str.lower():
                    # 对于相对时间，我们可以给它一个较新的评分
                    if "hour" in date_str.lower():
                        return datetime.now().timestamp() - 3600  # 小时前，非常新
                    elif "day" in date_str.lower():
                        return datetime.now().timestamp() - 86400  # 天前，较新
                    elif "week" in date_str.lower():
                        return datetime.now().timestamp() - 604800  # 周前
                    elif "month" in date_str.lower():
                        return datetime.now().timestamp() - 2592000  # 月前
                    else:
                        return 0  # 默认很旧
                
                # 尝试解析精确日期
                for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%B %d, %Y"]:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.timestamp()
                    except ValueError:
                        continue
                
                return 0  # 如果无法解析，默认为很旧
            except:
                return 0
        
        # 对文件信息和路径同时进行排序
        sorted_pairs = sorted(zip(all_info, all_files), key=lambda x: get_date_sort_key(x[0]), reverse=True)
        all_info, all_files = zip(*sorted_pairs) if sorted_pairs else ([], [])
        
        # 转换回列表
        all_info = list(all_info)
        all_files = list(all_files)
    
    return all_files, all_info

def get_download_link(content, filename, text):
    """生成下载链接"""
    # 将内容转换为bytes
    if isinstance(content, str):
        content_bytes = content.encode('utf-8')
    else:
        content_bytes = json.dumps(content, ensure_ascii=False, indent=2).encode('utf-8')
    
    b64 = base64.b64encode(content_bytes).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="{filename}" class="download-btn">{text}</a>'
    return href

def format_datetime(date_str):
    """格式化日期时间字符串"""
    if not date_str:
        return ""
    
    try:
        # 尝试不同的日期格式
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO格式
            "%Y-%m-%d %H:%M:%S",       # 标准格式
            "%Y-%m-%d",                # 仅日期
            "%B %d, %Y"                # 英文月份格式
        ]
        
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
        
        # 提取预览信息 - 修改这部分，优先使用中文标题
        title_zh = data.get("title_zh", "")
        title_en = data.get("title", "")
        # 优先显示中文标题，如果没有中文标题则使用英文标题
        display_title = title_zh if title_zh else title_en if title_en else json_path.name
        
        publish_date = format_datetime(data.get("publish_date", ""))
        tags = data.get("tags", [])
        tag_display = " ".join([f"<span class='tag'>{tag}</span>" for tag in tags]) if tags else ""
        
        # 创建可折叠区域 - 使用优先显示的中文标题
        with st.expander(f"#{index} - {display_title} {publish_date}", expanded=False):
            # 顶部信息栏
            if tag_display:
                st.markdown(f"<div class='tags-container'>{tag_display}</div>", unsafe_allow_html=True)
            
            # 显示文件路径
            st.caption(f"文件路径: {json_path}")
            
            # 创建选项卡 - 添加工作流分析选项卡
            tab1, tab2, tab3, tab4 = st.tabs(["基本信息", "工作流数据", "工作流分析", "原始JSON"])
            
            with tab1:
                # 创建基本信息子选项卡，分为中文和英文，注意顺序调整，先显示中文
                info_tab_zh, info_tab_en = st.tabs(["中文信息", "英文信息"])
                
                with info_tab_zh:
                    # 显示中文标题
                    if "title_zh" in data and data["title_zh"]:
                        st.write("**中文标题:** ", data["title_zh"])
                    elif "title" in data and data["title"]:
                        st.write("**中文标题:** ", "(未翻译)")
                        
                    # 显示中文发布日期
                    if "publish_date_zh" in data and data["publish_date_zh"]:
                        st.write("**中文日期:** ", data["publish_date_zh"])
                    elif "publish_date" in data and data["publish_date"]:
                        st.write("**中文日期:** ", "(未翻译)")
                    
                    # 显示标签 (标签通常不翻译)
                    if tags:
                        st.write("**标签:** ", ", ".join(tags))
                    
                    # 显示中文readme
                    if "readme_zh" in data and data["readme_zh"]:
                        st.markdown("### 中文描述")
                        st.markdown(data["readme_zh"])
                    elif "readme" in data and data["readme"]:
                        st.markdown("### 中文描述")
                        st.write("(内容未翻译)")
                
                with info_tab_en:
                    # 显示原始标题
                    if "title" in data and data["title"]:
                        st.write("**标题 (Title):** ", data["title"])
                        
                    # 显示原始发布日期
                    if "publish_date" in data and data["publish_date"]:
                        st.write("**发布日期 (Publish Date):** ", publish_date)
                    
                    # 显示标签
                    if tags:
                        st.write("**标签 (Tags):** ", ", ".join(tags))
                    
                    # 显示英文readme内容
                    if "readme" in data and data["readme"]:
                        st.markdown("### 描述 (Description)")
                        st.markdown(data["readme"])
            
            with tab2:
                # 显示工作流数据
                if "workflow_json" in data and data["workflow_json"]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("**原始工作流数据:**")
                    with col2:
                        filename = f"{os.path.splitext(json_path.name)[0]}_workflow_json.json"
                        download_link = get_download_link(data["workflow_json"], filename, "📥 下载原始工作流")
                        st.markdown(download_link, unsafe_allow_html=True)
                    
                    # 显示工作流预览信息
                    try:
                        workflow = json.loads(data["workflow_json"]) if isinstance(data["workflow_json"], str) else data["workflow_json"]
                        st.write(f"工作流名称: {workflow.get('name', '未命名')}")
                        st.write(f"节点数量: {len(workflow.get('nodes', []))}")
                    except:
                        st.write("无法解析工作流数据")
                
                # 显示中文工作流数据
                if "workflow_json_zh" in data and data["workflow_json_zh"]:
                    col1, col2, col3 = st.columns([2.5, 1, 1])
                    with col1:
                        st.write("**中文工作流数据:**")
                    with col2:
                        filename = f"{os.path.splitext(json_path.name)[0]}_workflow_json_zh.json"
                        download_link = get_download_link(data["workflow_json_zh"], filename, "📥 下载中文工作流")
                        st.markdown(download_link, unsafe_allow_html=True)
                    with col3:
                        # 添加分析按钮，使用侧边栏中选择的模型
                        if st.button("🔍 分析工作流", key=f"analyze_{index}"):
                            # 获取用户在侧边栏选择的模型
                            selected_model = st.session_state.selected_model
                            model_name = selected_model.split("/")[-1].replace("-", " ").title()
                            
                            with st.spinner(f"使用 {model_name} 分析工作流..."):
                                # 使用新模块分析工作流
                                workflow_json = data["workflow_json_zh"] if "workflow_json_zh" in data else data["workflow_json"]
                                analysis = n8n_json_to_context.get_workflow_analysis(workflow_json, model=selected_model)
                                
                                # 保存分析结果到文件
                                success = n8n_json_to_context.save_workflow_file(json_path, analysis)
                                
                                if success:
                                    st.success("分析完成并已保存")
                                    # 重新加载文件以显示分析结果
                                    with open(json_path, 'r', encoding='utf-8') as f:
                                        data = json.load(f)
                                else:
                                    st.error("保存分析结果失败")
            
            # 新增的工作流分析标签页
            with tab3:
                # 显示工作流分析结果
                if "workflow_analysis" in data and data["workflow_analysis"]:
                    st.markdown(data["workflow_analysis"])
                    # 添加重新分析的选项
                    st.write("---")
                    
                    # 添加重新分析按钮，使用侧边栏中选择的模型
                    if st.button("🔄 使用当前选择的模型重新分析", key=f"reanalyze_{index}"):
                        selected_model = st.session_state.selected_model
                        model_name = selected_model.split("/")[-1].replace("-", " ").title()
                        
                        with st.spinner(f"使用 {model_name} 重新分析工作流..."):
                            workflow_json = data["workflow_json_zh"] if "workflow_json_zh" in data else data["workflow_json"]
                            analysis = n8n_json_to_context.get_workflow_analysis(workflow_json, model=selected_model)
                            
                            # 保存分析结果到文件
                            success = n8n_json_to_context.save_workflow_file(json_path, analysis)
                            
                            if success:
                                st.success("分析完成并已保存")
                                # 重新加载文件以显示分析结果
                                with open(json_path, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                # 显示新的分析结果
                                st.markdown(analysis)
                            else:
                                st.error("保存分析结果失败")
                else:
                    st.info("该工作流尚未进行分析。")
                    
                    # 如果有工作流数据，提供直接分析按钮
                    if ("workflow_json" in data and data["workflow_json"]) or ("workflow_json_zh" in data and data["workflow_json_zh"]):
                        # 添加分析按钮，使用侧边栏中选择的模型
                        if st.button("🔍 使用当前选择的模型分析", key=f"analyze_direct_{index}"):
                            selected_model = st.session_state.selected_model
                            model_name = selected_model.split("/")[-1].replace("-", " ").title()
                            
                            with st.spinner(f"使用 {model_name} 分析工作流..."):
                                workflow_json = data["workflow_json_zh"] if "workflow_json_zh" in data else data["workflow_json"]
                                analysis = n8n_json_to_context.get_workflow_analysis(workflow_json, model=selected_model)
                                
                                # 保存分析结果到文件
                                success = n8n_json_to_context.save_workflow_file(json_path, analysis)
                                
                                if success:
                                    st.success("分析完成并已保存")
                                    # 显示分析结果
                                    st.markdown(analysis)
                                else:
                                    st.error("保存分析结果失败")
                    else:
                        st.warning("此文件不包含工作流数据，无法进行分析。")
            
            with tab4:
                # 显示完整JSON内容
                st.json(data)
                
    except Exception as e:
        st.error(f"读取文件 {json_path.name} 时出错: {e}")

def get_unique_tags(file_infos):
    """从文件信息列表中提取所有唯一标签"""
    all_tags = set()
    for info in file_infos:
        tags = info.get("tags", [])
        if tags:
            all_tags.update(tags)
    return sorted(list(all_tags))

def load_categories():
    """从n8n_categories.json加载分类信息"""
    # 修改这一行，将路径从 data/n8n_categories.json 改为 data/workflow/n8n_categories.json
    categories_file = Path(__file__).parent / "data" / "workflow" / "n8n_categories.json"
    
    if not categories_file.exists():
        st.warning("未找到分类数据文件 n8n_categories.json")
        return [{"category_name": "全部", "category_url": ""}]
    
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories_data = json.load(f)
        
        # 确保包含"全部"选项
        categories = [{"category_name": "全部", "category_url": ""}]
        
        # 添加从文件加载的分类
        for item in categories_data:
            if isinstance(item, dict) and "category_name" in item and "category_url" in item:
                categories.append(item)
        
        return categories
    except Exception as e:
        st.error(f"加载分类数据出错: {e}")
        return [{"category_name": "全部", "category_url": ""}]

def main():
    # 添加自定义CSS
    st.markdown("""
    <style>
    .download-btn {
        display: inline-block;
        padding: 0.3rem 0.6rem;
        background-color: #4CAF50;
        color: white !important;
        text-decoration: none;
        border-radius: 4px;
        text-align: center;
        transition: background-color 0.3s;
    }
    .download-btn:hover {
        background-color: #45a049;
        text-decoration: none;
    }
    .tag {
        display: inline-block;
        background-color: #f1f1f1;
        padding: 2px 6px;
        margin: 2px;
        border-radius: 3px;
        font-size: 0.8rem;
    }
    .tags-container {
        margin-bottom: 10px;
    }
    .category-badge {
        background-color: #e8f0fe;
        color: #1967d2;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.85rem;
        display: inline-block;
        margin-right: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 加载分类数据
    categories = load_categories()
    category_names = [cat["category_name"] for cat in categories]
    
    # 侧边栏过滤和搜索选项
    with st.sidebar:
        st.header("搜索和过滤")
        
        # 搜索框
        search_query = st.text_input("搜索文件名或标题", "")
        
        # 分类选择
        selected_category = st.selectbox("按分类过滤", category_names)
        
        # 获取所有JSON文件的基本信息(不过滤)
        _, all_info = get_all_json_files(data_dir)
        
        # 提取所有唯一标签
        unique_tags = get_unique_tags(all_info)
        
        # 标签多选
        selected_tags = st.multiselect("按标签过滤", unique_tags)
        
        # 翻译状态过滤
        translation_options = ["全部", "已翻译", "未翻译"]
        translation_filter = st.radio("翻译状态", translation_options)
        
        has_translation = None
        if translation_filter == "已翻译":
            has_translation = True
        elif translation_filter == "未翻译":
            has_translation = False
        
        # 每页显示数量
        items_per_page = st.slider("每页显示数量", 5, 50, 10, 5)
        
        # 重置按钮
        if st.button("重置过滤器"):
            search_query = ""
            selected_tags = []
            selected_category = "全部"
            translation_filter = "全部"
            has_translation = None
            items_per_page = 10
            st.session_state.page_number = 1
            st.rerun()
            
        # 添加模型选择部分
        st.header("AI 模型选择")
        
        # 获取可用模型列表
        model_list = n8n_json_to_context.get_available_models()
        
        # 转换为易于显示的格式
        model_options = {model["id"]: f"{model['name']} ({model.get('context_length', 0)//1000}K)" for model in model_list}
        
        # 如果列表为空或出错，使用默认模型列表
        if not model_options:
            model_options = {
                "anthropic/claude-3-7-sonnet": "Claude 3.7 Sonnet (推荐)",
                "anthropic/claude-3-5-sonnet": "Claude 3.5 Sonnet",
                "anthropic/claude-3-haiku": "Claude 3 Haiku (快速)",
                "anthropic/claude-3-opus": "Claude 3 Opus (高质量)",
                "openai/gpt-4o": "GPT-4o",
                "openai/gpt-4-turbo": "GPT-4 Turbo",
            }
            
        # 查找默认选择的索引 (Claude 3.7 Sonnet)
        default_model = "anthropic/claude-3-7-sonnet"
        default_index = list(model_options.keys()).index(default_model) if default_model in model_options else 0
        
        # 将选择的模型保存到会话状态，以便在整个应用中使用
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = list(model_options.keys())[default_index]
        
        st.session_state.selected_model = st.selectbox(
            "分析工作流使用的模型", 
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            index=list(model_options.keys()).index(st.session_state.selected_model) if st.session_state.selected_model in model_options else default_index
        )
        
        # 显示当前选择的模型信息
        st.info(f"当前选择: {model_options[st.session_state.selected_model]}")
    
    # 以下是主内容区域的代码，需要添加回来
    
    # 获取过滤后的JSON文件列表
    json_files, file_infos = get_all_json_files(
        data_dir, 
        query=search_query, 
        tag_filter=selected_tags, 
        category_filter=selected_category,
        has_translation=has_translation
    )
    
    # 显示文件总数和过滤结果
    st.write(f"共找到 {len(json_files)} 个文件")
    
    # 如果没有文件，显示提示信息
    if not json_files:
        st.info("没有找到符合过滤条件的文件。请尝试调整过滤器或搜索条件。")
        return
    
    # 分页逻辑
    total_pages = math.ceil(len(json_files) / items_per_page)
    
    # 确保页码在有效范围内
    if st.session_state.page_number < 1:
        st.session_state.page_number = 1
    elif st.session_state.page_number > total_pages:
        st.session_state.page_number = total_pages
    
    # 计算当前页的文件范围
    start_idx = (st.session_state.page_number - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(json_files))
    
    # 显示分页信息
    st.write(f"第 {st.session_state.page_number} 页，共 {total_pages} 页")
    
    # 分页控制
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.session_state.page_number > 1:
            if st.button("上一页"):
                st.session_state.page_number -= 1
                st.rerun()
    
    with col2:
        # 显示页码选择器
        page_options = list(range(1, total_pages + 1))
        selected_page = st.selectbox("跳转到页", page_options, index=st.session_state.page_number - 1)
        if selected_page != st.session_state.page_number:
            st.session_state.page_number = selected_page
            st.rerun()
    
    with col3:
        if st.session_state.page_number < total_pages:
            if st.button("下一页"):
                st.session_state.page_number += 1
                st.rerun()
    
    # 显示当前页的文件
    for i, json_path in enumerate(json_files[start_idx:end_idx], start=start_idx+1):
        display_json_content(json_path, i)

# 调用主函数
if __name__ == "__main__":
    main()