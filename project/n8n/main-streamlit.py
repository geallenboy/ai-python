#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
n8n工作流爬取工具的Streamlit可视化界面
用于管理和执行爬取操作，查看分类状态和进度
"""

import streamlit as st
import json
import os
import asyncio
import time
import subprocess
from pathlib import Path
import sys
from typing import Dict, List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import FontProperties
import n8n_workflow_main as scraper_module
from n8n_workflow_main import N8nWorkflowScraper

# 设置页面配置
st.set_page_config(
    page_title="n8n工作流爬取工具",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加CSS样式
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1E88E5;
    }
    .category-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1E88E5;
    }
    .category-name {
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    .status-complete {
        color: #4CAF50;
        font-weight: bold;
    }
    .status-incomplete {
        color: #FFC107;
        font-weight: bold;
    }
    .status-not-crawled {
        color: #F44336;
        font-weight: bold;
    }
    .progress-container {
        margin-top: 0.5rem;
    }
    .progress-bar {
        color: #000; 
        background-color: #4CAF50;
        text-align: center;
        line-height: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 全局变量
DATA_DIR = Path("data/workflow")
LOGS_DIR = Path("logs")

# 确保必要的目录存在
def ensure_directories():
    """确保数据和日志目录存在"""
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not LOGS_DIR.exists():
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

# 加载分类数据
def load_categories() -> List[Dict]:
    """
    从n8n_categories.json文件加载分类信息
    
    Returns:
        分类信息列表
    """
    categories_file = DATA_DIR / "n8n_categories.json"
    
    if not categories_file.exists():
        st.warning("未找到分类数据文件。请先运行爬虫获取分类信息。")
        return []
    
    try:
        with open(categories_file, "r", encoding="utf-8") as f:
            categories = json.load(f)
        return categories
    except Exception as e:
        st.error(f"加载分类数据时出错: {e}")
        return []

# 加载已爬取的分类记录
def load_crawled_categories() -> Dict:
    """
    加载已爬取的分类记录
    
    Returns:
        已爬取的分类记录，格式为 {category_name: {'last_crawled': timestamp, 'count': count}}
    """
    crawled_file = LOGS_DIR / "crawled_categories.json"
    
    if not crawled_file.exists():
        return {}
    
    try:
        with open(crawled_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.warning(f"读取已爬取分类记录出错: {e}")
        return {}

# 获取分类目录中的文件数量
def get_category_file_count(category_name: str) -> int:
    """
    获取指定分类目录中的JSON文件数量
    
    Args:
        category_name: 分类名称
        
    Returns:
        目录中的JSON文件数量
    """
    # 创建安全的目录名
    safe_name = "".join([c if c.isalnum() or c == ' ' else '_' for c in category_name])
    safe_name = safe_name.replace(' ', '_')
    
    category_dir = DATA_DIR / safe_name
    
    if not category_dir.exists():
        return 0
    
    # 计算目录中的JSON文件数量
    return sum(1 for f in category_dir.glob("*.json") if f.is_file())

# 运行爬虫任务
async def run_crawler(category_name: str, max_workflows: int = None, headless: bool = True):
    """
    运行爬虫任务爬取指定分类
    
    Args:
        category_name: 要爬取的分类名称
        max_workflows: 最多爬取的工作流数量
        headless: 是否使用无头模式
    """
    try:
        # 创建爬虫实例
        scraper = N8nWorkflowScraper(
            headless=headless,
            use_proxies=False,
            max_retries=3
        )
        
        # 运行爬虫
        await scraper.run(
            max_workflows_per_category=max_workflows,
            categories_to_crawl=[category_name],
            force_update=True
        )
        
        return True
    except Exception as e:
        st.error(f"爬虫运行出错: {e}")
        return False

# 使用subprocess运行爬虫（用于不阻塞Streamlit界面）
def run_crawler_subprocess(category_name: str, max_workflows: int = None, headless: bool = True):
    """
    使用子进程运行爬虫
    
    Args:
        category_name: 要爬取的分类名称
        max_workflows: 最多爬取的工作流数量
        headless: 是否使用无头模式
    """
    cmd = [
        sys.executable, 
        'n8n_workflow_main.py',
        '--categories', category_name,
        '--force-update'
    ]
    
    if max_workflows is not None:
        cmd.extend(['--max-workflows', str(max_workflows)])
    
    if headless:
        cmd.append('--headless')
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=os.environ.copy(),  # 传递当前环境变量
        cwd=os.path.dirname(os.path.abspath(__file__))  # 确保在正确的工作目录
    )
    
    return process

# 获取分类数据分析
def get_category_analysis() -> pd.DataFrame:
    """
    分析所有分类数据并返回DataFrame
    
    Returns:
        包含分类分析的DataFrame
    """
    categories = load_categories()
    crawled_info = load_crawled_categories()
    
    analysis_data = []
    
    for cat in categories:
        name = cat.get('category_name', '')
        if not name:
            continue
            
        # 从爬虫记录中获取信息
        crawled_data = crawled_info.get(name, {})
        last_crawled = crawled_data.get('last_crawled_date', '未爬取')
        expected_count = crawled_data.get('count', 0)
        
        # 获取实际文件数量
        actual_count = get_category_file_count(name)
        
        # 计算一致性
        if expected_count == 0:
            consistency = "未爬取"
        else:
            consistency = f"{(actual_count / expected_count * 100):.1f}%" if expected_count > 0 else "N/A"
        
        # 确定状态
        if expected_count == 0:
            status = "未爬取"
        elif actual_count >= expected_count:
            status = "完整"
        else:
            status = "不完整"
            
        analysis_data.append({
            "分类名称": name,
            "最后爬取时间": last_crawled,
            "预期数量": expected_count,
            "实际数量": actual_count,
            "一致性": consistency,
            "状态": status
        })
    
    return pd.DataFrame(analysis_data)

# 主界面
def main():
    # 确保目录存在
    ensure_directories()
    
    # 显示标题
    st.markdown("<div class='main-title'>n8n工作流爬取工具</div>", unsafe_allow_html=True)
    
    # 侧边栏 - 操作控制
    with st.sidebar:
        st.header("操作控制")
        
        # 功能选择
        function = st.radio(
            "选择功能",
            ["分类状态概览", "爬取管理", "数据分析"]
        )
        
        # 爬取设置
        st.subheader("爬取设置")
        headless = st.checkbox("无头模式", value=True, help="开启无头模式后浏览器将在后台运行，不会显示界面")
        max_workflows = st.number_input("每个分类最多爬取数量", 
                                      min_value=1, 
                                      value=100, 
                                      help="设置为较大的数以爬取全部工作流")
        
        # 获取分类信息的按钮
        if st.button("获取/更新分类列表"):
            with st.spinner("正在获取分类信息..."):
                # 使用子进程运行爬虫，只获取分类信息
                process = subprocess.Popen(
                    [sys.executable, 'n8n_workflow_main.py', '--list-categories', '--headless'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    st.success("分类信息获取成功！")
                    st.text_area("输出日志", stdout, height=200)
                else:
                    st.error("分类信息获取失败！")
                    st.text_area("错误信息", stderr, height=200)
    
    # 主内容区域
    if function == "分类状态概览":
        show_categories_overview()
    elif function == "爬取管理":
        show_crawl_management()
    elif function == "数据分析":
        show_data_analysis()

# 分类状态概览页面
def show_categories_overview():
    st.header("分类状态概览")
    
    # 获取分析数据
    df = get_category_analysis()
    
    if df.empty:
        st.warning("没有找到分类数据。请点击侧边栏中的'获取/更新分类列表'按钮。")
        return
    
    # 显示状态统计
    col1, col2, col3 = st.columns(3)
    
    with col1:
        complete_count = len(df[df["状态"] == "完整"])
        st.metric("完整分类", complete_count, f"{complete_count/len(df)*100:.1f}%")
        
    with col2:
        incomplete_count = len(df[df["状态"] == "不完整"])
        st.metric("不完整分类", incomplete_count, f"{incomplete_count/len(df)*100:.1f}%")
        
    with col3:
        not_crawled_count = len(df[df["状态"] == "未爬取"])
        st.metric("未爬取分类", not_crawled_count, f"{not_crawled_count/len(df)*100:.1f}%")
    
    # 数据过滤选项
    status_filter = st.multiselect(
        "按状态筛选", 
        ["完整", "不完整", "未爬取"], 
        default=["完整", "不完整", "未爬取"]
    )
    
    # 应用过滤
    filtered_df = df[df["状态"].isin(status_filter)]
    
    # 显示分类状态表格
    st.subheader("分类状态详情")
    st.dataframe(filtered_df, use_container_width=True)
    
    # 显示柱状图
    st.subheader("分类数据统计")
    
    # 只选择前10个分类，避免图表过于拥挤导致乱码
    display_df = df.head(10) if len(df) > 10 else df
    
    fig, ax = plt.subplots(figsize=(10, 6))
    x = display_df["分类名称"]
    y1 = display_df["预期数量"]
    y2 = display_df["实际数量"]
    
    x_pos = range(len(x))
    width = 0.35
    
    ax.bar([p - width/2 for p in x_pos], y1, width, label='预期数量')
    ax.bar([p + width/2 for p in x_pos], y2, width, label='实际数量')
    
    ax.set_xticks(x_pos)
    # 增加字体大小和旋转角度，提高可读性
    ax.set_xticklabels(x, rotation=45, ha="right", fontsize=9)
    ax.legend(prop={'size': 10})
    
    ax.set_ylabel('数量')
    ax.set_title('各分类预期数量与实际数量对比（前10个）')
    plt.tight_layout()
    
    st.pyplot(fig)
    
    # 如果分类数量超过10个，显示完整数据表格
    if len(df) > 10:
        st.info("由于分类数量较多，图表仅显示前10个分类。完整数据请查看上方表格。")

# 爬取管理页面
def show_crawl_management():
    st.header("爬取管理")
    
    # 获取分类数据
    categories = load_categories()
    
    if not categories:
        st.warning("没有找到分类数据。请点击侧边栏中的'获取/更新分类列表'按钮。")
        return
    
    # 获取爬取记录和分析
    crawled_info = load_crawled_categories()
    df = get_category_analysis()
    
    # 创建两列布局
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 按状态筛选
        status_filter = st.multiselect(
            "按状态筛选", 
            ["完整", "不完整", "未爬取"], 
            default=["不完整", "未爬取"]
        )
        filtered_df = df[df["状态"].isin(status_filter)]
        
        # 按关键词搜索
        search_term = st.text_input("搜索分类名称")
        if search_term:
            filtered_df = filtered_df[filtered_df["分类名称"].str.contains(search_term, case=False)]
    
    with col2:
        # 批量操作
        st.subheader("批量操作")
        
        if st.button("爬取所有不完整分类"):
            incomplete_categories = df[df["状态"] == "不完整"]["分类名称"].tolist()
            if incomplete_categories:
                st.session_state.batch_categories = incomplete_categories
                st.session_state.batch_index = 0
                st.success(f"已添加 {len(incomplete_categories)} 个分类到爬取队列")
            else:
                st.info("没有不完整的分类需要爬取")
                
        if st.button("爬取所有未爬取分类"):
            not_crawled_categories = df[df["状态"] == "未爬取"]["分类名称"].tolist()
            if not_crawled_categories:
                st.session_state.batch_categories = not_crawled_categories
                st.session_state.batch_index = 0
                st.success(f"已添加 {len(not_crawled_categories)} 个分类到爬取队列")
            else:
                st.info("没有未爬取的分类")
    
    # 显示分类列表
    st.subheader("分类列表")
    
    # 初始化批量爬取状态
    if "batch_categories" not in st.session_state:
        st.session_state.batch_categories = []
    if "batch_index" not in st.session_state:
        st.session_state.batch_index = 0
    if "crawling" not in st.session_state:
        st.session_state.crawling = False
    if "current_process" not in st.session_state:
        st.session_state.current_process = None
    
    # 批量爬取进度
    if st.session_state.batch_categories:
        batch_progress = st.progress(0.0)
        batch_status = st.empty()
        
        total = len(st.session_state.batch_categories)
        current = st.session_state.batch_index
        
        if current < total:
            progress_val = current / total
            batch_progress.progress(progress_val)
            current_cat = st.session_state.batch_categories[current]
            batch_status.info(f"正在爬取 ({current}/{total}): {current_cat}")
            
            # 如果没有正在进行的爬取，启动下一个
            if not st.session_state.crawling and st.session_state.current_process is None:
                st.session_state.crawling = True
                max_workflows = int(st.sidebar.number_input("每个分类最多爬取数量", key="batch_max"))
                headless = st.sidebar.checkbox("无头模式", value=True, key="batch_headless")
                
                # 启动爬虫进程
                process = run_crawler_subprocess(current_cat, max_workflows, headless)
                st.session_state.current_process = process
                
                # 创建一个占位符来显示实时输出
                output_placeholder = st.empty()
                
                # 模拟异步检查进程状态
                def check_process():
                    process = st.session_state.current_process
                    if process is not None:
                        output = ""
                        # 使用非阻塞方式读取输出
                        while True:
                            line = process.stdout.readline()
                            if not line and process.poll() is not None:
                                break
                            if line:
                                output += line + "\n"
                                output_placeholder.text_area("爬虫输出", output, height=200)
                                time.sleep(0.1)  # 小的延迟防止过度刷新
                        
                        # 检查进程是否结束
                        if process.poll() is not None:
                            if process.returncode == 0:
                                batch_status.success(f"爬取完成: {current_cat}")
                            else:
                                stderr = process.stderr.read()
                                batch_status.error(f"爬取失败: {current_cat}\n{stderr}")
                            
                            # 更新状态
                            st.session_state.crawling = False
                            st.session_state.current_process = None
                            st.session_state.batch_index += 1
                            
                            # 如果所有分类都爬取完毕，清空队列
                            if st.session_state.batch_index >= total:
                                st.session_state.batch_categories = []
                                st.session_state.batch_index = 0
                                batch_status.success("所有分类爬取完成！")
                            
                            # 强制重新加载页面以更新状态
                            st.rerun()
                
                # 启动检查进程的线程
                import threading
                threading.Thread(target=check_process).start()
        else:
            batch_progress.progress(1.0)
            batch_status.success(f"批量爬取完成！共爬取 {total} 个分类。")
    
    # 显示分类卡片
    if not filtered_df.empty:
        for index, row in filtered_df.iterrows():
            category_name = row["分类名称"]
            expected_count = row["预期数量"]
            actual_count = row["实际数量"]
            last_crawled = row["最后爬取时间"]
            status = row["状态"]
            
            # 确定状态样式
            if status == "完整":
                status_class = "status-complete"
            elif status == "不完整":
                status_class = "status-incomplete"
            else:
                status_class = "status-not-crawled"
            
            # 创建分类卡片
            st.markdown(f"""
            <div class='category-card'>
                <div class='category-name'>{category_name}</div>
                <div>状态: <span class='{status_class}'>{status}</span></div>
                <div>最后爬取: {last_crawled}</div>
                <div>文件数量: {actual_count} / {expected_count}</div>
                <div class='progress-container'>
                    <div class='progress'>
                        <div class='progress-bar' role='progressbar' style='width: {(actual_count/expected_count*100) if expected_count > 0 else 0}%;' 
                            aria-valuenow='{actual_count}' aria-valuemin='0' aria-valuemax='{expected_count}'>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 添加爬取按钮
            col1, col2 = st.columns([3, 1])
            with col1:
                max_to_crawl = expected_count - actual_count if expected_count > actual_count else 1
                max_to_crawl = max(1, max_to_crawl)  # 确保至少为1
                to_crawl = st.number_input(f"爬取数量 ({category_name})", 
                                         min_value=1, 
                                         max_value=1000, 
                                         value=max_to_crawl,
                                         key=f"input_{index}")
            
            with col2:
                if st.button("开始爬取", key=f"crawl_{index}"):
                    # 检查是否有正在进行的爬取
                    if st.session_state.crawling:
                        st.warning("有正在进行的爬取任务，请等待完成后再试")
                    else:
                        st.session_state.crawling = True
                        max_workflows = int(to_crawl)
                        headless = st.sidebar.checkbox("无头模式", value=True)
                        
                        # 显示爬取状态
                        status_placeholder = st.empty()
                        status_placeholder.info(f"正在爬取 {category_name}...")
                        
                        # 启动爬虫进程
                        process = run_crawler_subprocess(category_name, max_workflows, headless)
                        st.session_state.current_process = process
                        
                        # 创建一个占位符来显示实时输出
                        output_placeholder = st.empty()
                        
                        # 检查进程状态
                        def check_single_process():
                            process = st.session_state.current_process
                            if process is not None:
                                output = ""
                                # 读取输出
                                for line in iter(process.stdout.readline, ""):
                                    if not line:
                                        break
                                    output += line + "\n"
                                    output_placeholder.text_area("爬虫输出", output, height=200)
                                
                                # 检查进程是否结束
                                if process.poll() is not None:
                                    if process.returncode == 0:
                                        status_placeholder.success(f"爬取完成: {category_name}")
                                    else:
                                        stderr = process.stderr.read()
                                        status_placeholder.error(f"爬取失败: {category_name}\n{stderr}")
                                    
                                    # 更新状态
                                    st.session_state.crawling = False
                                    st.session_state.current_process = None
                                    
                                    # 强制重新加载页面以更新状态
                                    st.rerun()
                        
                        # 启动检查进程的线程
                        import threading
                        threading.Thread(target=check_single_process).start()

# 数据分析页面
def show_data_analysis():
    st.header("数据分析")
    
    # 获取分析数据
    df = get_category_analysis()
    
    if df.empty:
        st.warning("没有找到分类数据。请点击侧边栏中的'获取/更新分类列表'按钮。")
        return
    
    # 总计统计
    total_categories = len(df)
    total_expected = df["预期数量"].sum()
    total_actual = df["实际数量"].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("总分类数", total_categories)
    with col2:
        st.metric("预期总工作流", int(total_expected))
    with col3:
        st.metric("实际已爬取", int(total_actual), f"{total_actual/total_expected*100:.1f}%" if total_expected > 0 else "N/A")
    
    # 分类状态饼图
    st.subheader("分类状态分布")
    
    status_counts = df["状态"].value_counts()
    
    fig1, ax1 = plt.subplots(figsize=(8, 8))
    # 使用更鲜明的颜色
    colors = ['#4CAF50', '#FFC107', '#F44336']
    ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', 
            startangle=90, colors=colors, textprops={'fontsize': 12})
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    st.pyplot(fig1)
    
    # 最大的分类
    st.subheader("数量最多的分类")
    
    top_df = df.sort_values("实际数量", ascending=False).head(10)
    
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    bars = ax2.barh(top_df["分类名称"], top_df["实际数量"], color='#1E88E5')
    
    # 为每个条形添加数字标签
    for bar in bars:
        width = bar.get_width()
        ax2.text(width + 1, bar.get_y() + bar.get_height()/2, 
                 f'{int(width)}', ha='left', va='center', fontsize=9)
    
    ax2.set_xlabel('工作流数量')
    ax2.set_ylabel('分类名称')
    ax2.set_title('工作流数量最多的10个分类')
    # 增加Y轴标签字体大小
    plt.yticks(fontsize=10)
    plt.tight_layout()
    
    st.pyplot(fig2)
    
    # 最近爬取的分类
    st.subheader("最近爬取的分类")
    
    # 过滤出有爬取记录的分类
    crawled_df = df[df["最后爬取时间"] != "未爬取"].copy()
    
    if not crawled_df.empty:
        # 尝试将日期字符串转换为日期时间对象用于排序
        try:
            crawled_df["爬取日期"] = pd.to_datetime(crawled_df["最后爬取时间"])
            recent_df = crawled_df.sort_values("爬取日期", ascending=False).head(10)
            recent_df = recent_df[["分类名称", "最后爬取时间", "实际数量"]]
            st.dataframe(recent_df, use_container_width=True)
        except:
            st.dataframe(crawled_df[["分类名称", "最后爬取时间", "实际数量"]].head(10), use_container_width=True)
    else:
        st.info("没有找到爬取记录")

# 设置matplotlib中文字体支持
# 尝试使用系统中常见的中文字体
def set_matplotlib_chinese_font():
    try:
        # 尝试系统常见的中文字体
        font_list = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', 'Heiti SC', 'STHeiti', 'WenQuanYi Micro Hei']
        
        # 在macOS上特别常见的字体
        if sys.platform == 'darwin':  # macOS
            font_list = ['PingFang SC', 'Hiragino Sans GB', 'STHeiti', 'Apple LiGothic Medium'] + font_list
            
        # 尝试设置字体，直到找到可用的字体
        for font_name in font_list:
            try:
                matplotlib.rcParams['font.family'] = [font_name]
                matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
                # 测试字体是否可用
                font = FontProperties(family=font_name)
                if font.get_name() != 'DejaVu Sans':  # DejaVu Sans 通常是当找不到字体时的回退选项
                    break
            except:
                continue
                
        # 如果无法设置中文字体，使用通用设置
        if matplotlib.rcParams['font.family'] == ['DejaVu Sans']:
            matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Bitstream Vera Sans', 'sans-serif']
            matplotlib.rcParams['axes.unicode_minus'] = False
    except Exception as e:
        st.warning(f"设置中文字体时出错: {e}")
        # 使用最简单的设置，确保不会出错
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']
        matplotlib.rcParams['axes.unicode_minus'] = False

# 调用函数设置中文字体
set_matplotlib_chinese_font()

if __name__ == "__main__":
    main()