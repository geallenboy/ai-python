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

def get_all_json_files(directory, query="", tag_filter=None, has_translation=None):
    """获取目录及其子目录下的所有JSON文件路径"""
    all_files = []
    all_info = []
    
    if not directory.exists():
        st.error(f"目录不存在: {directory}")
        return all_files, all_info
    
    # 遍历目录及子目录
    for path in directory.glob('**/*.json'):
        if path.is_file():
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
                
                # 翻译状态过滤
                if has_translation is not None:
                    if has_translation and not file_info.get("has_workflow_json_zh", False):
                        continue
                    elif not has_translation and file_info.get("has_workflow_json_zh", False):
                        continue
                
                all_files.append(path)
                all_info.append(file_info)
    
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
        
        # 提取预览信息
        title = data.get("title", "") or data.get("title_zh", "") or json_path.name
        publish_date = format_datetime(data.get("publish_date", ""))
        tags = data.get("tags", [])
        tag_display = " ".join([f"<span class='tag'>{tag}</span>" for tag in tags]) if tags else ""
        
        # 创建可折叠区域
        with st.expander(f"#{index} - {title} {publish_date}", expanded=False):
            # 顶部信息栏
            if tag_display:
                st.markdown(f"<div class='tags-container'>{tag_display}</div>", unsafe_allow_html=True)
            
            # 显示文件路径
            st.caption(f"文件路径: {json_path}")
            
            # 创建选项卡
            tab1, tab2, tab3 = st.tabs(["基本信息", "工作流数据", "原始JSON"])
            
            with tab1:
                # 创建基本信息子选项卡，分为英文和中文
                info_tab_en, info_tab_zh = st.tabs(["英文信息", "中文信息"])
                
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
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("**中文工作流数据:**")
                    with col2:
                        filename = f"{os.path.splitext(json_path.name)[0]}_workflow_json_zh.json"
                        download_link = get_download_link(data["workflow_json_zh"], filename, "📥 下载中文工作流")
                        st.markdown(download_link, unsafe_allow_html=True)
                    
                    # 显示中文工作流预览信息
                    try:
                        workflow_zh = json.loads(data["workflow_json_zh"]) if isinstance(data["workflow_json_zh"], str) else data["workflow_json_zh"]
                        st.write(f"中文工作流名称: {workflow_zh.get('name', '未命名')}")
                    except:
                        st.write("无法解析中文工作流数据")
            
            with tab3:
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
    </style>
    """, unsafe_allow_html=True)
    
    # 侧边栏过滤和搜索选项
    with st.sidebar:
        st.header("搜索和过滤")
        
        # 搜索框
        search_query = st.text_input("搜索文件名或标题", "")
        
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
            translation_filter = "全部"
            has_translation = None
            items_per_page = 10
            st.session_state.page_number = 1
            st.experimental_rerun()
    
    # 应用过滤并获取文件
    all_json_files, file_infos = get_all_json_files(data_dir, search_query, selected_tags, has_translation)
    
    # 显示结果统计
    st.write(f"共找到 {len(all_json_files)} 个工作流文件")
    
    # 如果没有文件，显示提示并退出
    if not all_json_files:
        st.warning("没有找到符合条件的文件，请尝试调整搜索或过滤条件。")
        return
    
    # 分页参数
    total_pages = math.ceil(len(all_json_files) / items_per_page)
    
    # 确保页码在有效范围内
    if st.session_state.page_number < 1:
        st.session_state.page_number = 1
    elif st.session_state.page_number > total_pages:
        st.session_state.page_number = total_pages
    
    # 添加分页导航
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    with col1:
        if st.button("« 首页"):
            st.session_state.page_number = 1
            st.experimental_rerun()
    with col2:
        if st.button("‹ 上一页", disabled=(st.session_state.page_number <= 1)):
            st.session_state.page_number -= 1
            st.experimental_rerun()
    with col3:
        page_number = st.number_input(
            "页码", 
            min_value=1, 
            max_value=total_pages if total_pages > 0 else 1, 
            value=st.session_state.page_number,
            step=1,
            key="page_input"
        )
        # 当页码输入框值变化时更新session state
        if page_number != st.session_state.page_number:
            st.session_state.page_number = page_number
            st.experimental_rerun()
    with col4:
        if st.button("下一页 ›", disabled=(st.session_state.page_number >= total_pages)):
            st.session_state.page_number += 1
            st.experimental_rerun()
    
    # 计算当前页的文件索引范围
    start_idx = (st.session_state.page_number - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(all_json_files))
    
    # 显示当前页信息
    st.write(f"当前显示: {start_idx + 1} - {end_idx} / {len(all_json_files)}")
    
    # 显示当前页的文件内容
    for i, json_file in enumerate(all_json_files[start_idx:end_idx], start=start_idx + 1):
        display_json_content(json_file, i)
    
    # 底部分页导航(重复顶部的分页导航)
    if len(all_json_files) > 5:
        st.write("---")
        col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
        with col1:
            if st.button("« 首页", key="bottom_first"):
                st.session_state.page_number = 1
                st.experimental_rerun()
        with col2:
            if st.button("‹ 上一页", key="bottom_prev", disabled=(st.session_state.page_number <= 1)):
                st.session_state.page_number -= 1
                st.experimental_rerun()
        with col3:
            st.write(f"第 {st.session_state.page_number} 页，共 {total_pages} 页")
        with col4:
            if st.button("下一页 ›", key="bottom_next", disabled=(st.session_state.page_number >= total_pages)):
                st.session_state.page_number += 1
                st.experimental_rerun()

if __name__ == "__main__":
    main()