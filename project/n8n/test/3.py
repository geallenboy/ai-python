#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import time
import random
import os
import re
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# 配置日志 - 输出到logs目录
def setup_logger():
    """
    设置日志记录器
    """
    # 确保logs目录存在
    current_dir = Path(__file__).parent
    logs_dir = current_dir / 'logs'
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger('n8n_scraper')
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 文件处理器 - 输出到logs/workflow_scraper.log
    file_handler = logging.FileHandler(logs_dir / 'workflow_scraper.log')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # 控制台处理器 - 输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # 添加处理器到logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 创建logger
logger = setup_logger()

def setup_driver():
    """
    设置Selenium WebDriver
    """
    logger.info("初始化WebDriver...")
    options = webdriver.ChromeOptions()
    
    # 设置无头模式（可选，取消注释以启用）
    # options.add_argument('--headless')
    
    # 设置其他选项以提高性能
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-notifications')
    options.add_argument('--blink-settings=imagesEnabled=false')  # 禁用图像加载以提高性能
    
    # 添加用户代理
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
    
    # 创建WebDriver实例
    driver = webdriver.Chrome(options=options)
    
    # 设置页面加载超时
    driver.set_page_load_timeout(30)
    
    return driver

def scrape_categorys(driver):
    """
    从n8n.io/workflows抓取工作流程分类信息
    
    Args:
        driver: Selenium WebDriver
    """
    base_url = "https://n8n.io/workflows/"
    categorys = []
    
    print(f"开始从 {base_url} 抓取工作流程")
    
    try:
        # 访问网站
        driver.get(base_url)
        print(f"页面标题: {driver.title}")
        
        # 等待分类容器加载完成
        wait = WebDriverWait(driver, 10)
        category_container = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.flex.flex-wrap.gap-2.justify-center'))
        )
        
        # 获取所有分类链接
        category_links = category_container.find_elements(By.TAG_NAME, 'a')
        
        print("\n===== 获取的分类信息 =====")
        print(f"共找到 {len(category_links)} 个分类")
        print("--------------------------")
        
        for link in category_links:
            href = link.get_attribute('href')
            category_name = link.text.strip()
            
            # 打印每个分类的详细信息
            print(f"分类名称: {category_name}")
            print(f"分类链接: {href}")
            print("--------------------------")
            
            # 将分类信息添加到categorys列表
            categorys.append({
                'category_url': href,
                'category_name': category_name
            })
        
        print(f"\n成功获取 {len(categorys)} 个分类")
    except Exception as e:
        print(f"获取分类信息时出错: {e}")
    
    return categorys

def scrape_category_workflows(driver, categories, max_workflows_per_category=1):
    """
    循环爬取每个分类URL中的工作流程，支持分页加载，并进入详情页获取更多信息
    
    Args:
        driver: Selenium WebDriver
        categories: 包含分类信息的列表，每个元素需包含'category_url'和'category_name'
        max_workflows_per_category: 每个分类最多爬取的工作流程数量，默认为1（用于测试）
    
    Returns:
        所有爬取到的工作流程列表
    """
    all_workflows = []
    
    # 遍历每个分类
    for i, category in enumerate(categories):
        category_url = category.get('category_url')
        category_name = category.get('category_name')
        
        print(f"\n[{i+1}/{len(categories)}] 开始爬取分类: {category_name}")
        print(f"URL: {category_url}")
        print(f"限制：每个分类最多爬取 {max_workflows_per_category} 条数据（测试模式）")
        
        try:
            # 初始化分类工作流程列表
            category_workflows = []
            already_loaded = 0
            has_more = True
            
            # 访问分类URL
            driver.get(category_url)
            
            # 等待页面加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            # 获取总结果数量
            try:
                total_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h2.title--white-violet'))
                )
                result_text = total_element.text.strip()
                match = re.search(r'\((\d+)\)', result_text)
                total_count = int(match.group(1)) if match else 0
                print(f"该分类下共有 {total_count} 个工作流程（仅获取前 {max_workflows_per_category} 条）")
            except (TimeoutException, NoSuchElementException, AttributeError):
                print("无法获取总结果数量")
                total_count = 0
            
            while has_more:
                # 等待工作流项目加载
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.workflow-search-result, a[href^="/workflows/"]'))
                )
                
                # 获取当前页面上的所有工作流项目
                workflow_items = driver.find_elements(By.CSS_SELECTOR, '.workflow-search-result, a[href^="/workflows/"]')
                print(f"本次找到 {len(workflow_items)} 个工作流程")
                
                if not workflow_items:
                    print("未找到工作流程项，可能需要调整选择器")
                    break
                
                # 处理每个工作流程项，但限制数量
                items_to_process = workflow_items
                remaining_count = max_workflows_per_category - len(category_workflows)
                if remaining_count < len(items_to_process):
                    items_to_process = items_to_process[:remaining_count]
                    print(f"限制处理数量，本次仅处理 {len(items_to_process)} 个工作流程")
                
                for j, item in enumerate(items_to_process):
                    try:
                        # 获取详情页URL
                        href = item.get_attribute('href')
                        if not href:
                            continue
                        
                        # 提取工作流程标题
                        try:
                            title_element = item.find_element(By.CSS_SELECTOR, 'h4, .title')
                            title = title_element.text.strip()
                        except NoSuchElementException:
                            title = "未知标题"
                        
                        # 提取工作流程描述
                        try:
                            desc_element = item.find_element(By.TAG_NAME, 'p')
                            description = desc_element.text.strip()
                        except NoSuchElementException:
                            description = ""
                        
                        print(f"  [{len(category_workflows) + 1}] 发现工作流程: {title}")
                        print(f"      URL: {href}")
                        
                        # 获取详情页内容
                        detailed_info = get_workflow_detail(driver, href)
                        
                        # 将工作流程信息添加到列表
                        workflow_data = {
                            'title': title,
                            'url': href,
                            'description': description,
                            'category': category_name,
                            'category_url': category_url,
                            **detailed_info  # 合并详情页中获取的信息
                        }
                        
                        category_workflows.append(workflow_data)
                        print(f"  已添加详细信息: {title}")
                        
                        # 检查是否已达到每个分类的最大爬取数量
                        if len(category_workflows) >= max_workflows_per_category:
                            print(f"已达到每个分类的最大爬取数量: {max_workflows_per_category}")
                            has_more = False
                            break
                    
                    except Exception as e:
                        print(f"  处理工作流程时出错: {e}")
                
                # 如果已经达到限制，不再加载更多
                if len(category_workflows) >= max_workflows_per_category:
                    has_more = False
                    print(f"已达到测试限制数量: {max_workflows_per_category}，停止加载更多")
                    break
                
                # 更新已加载数量
                already_loaded += len(workflow_items)
                
                # 检查是否有"加载更多"按钮，且未达到最大爬取数量
                try:
                    load_more_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Load more templates')]")
                    disabled = load_more_btn.get_attribute('disabled')
                    
                    if not disabled and total_count > already_loaded and len(category_workflows) < max_workflows_per_category:
                        # 点击加载更多按钮
                        driver.execute_script("arguments[0].scrollIntoView();", load_more_btn)
                        time.sleep(1)  # 等待页面滚动
                        driver.execute_script("arguments[0].click();", load_more_btn)
                        print(f"加载更多，已加载 {already_loaded}/{total_count}")
                        
                        # 等待新内容加载
                        time.sleep(3)
                    else:
                        has_more = False
                        print(f"已加载足够内容: {len(category_workflows)} 项")
                except NoSuchElementException:
                    has_more = False
                    print("没有找到加载更多按钮")
            
            # 将当前分类的工作流程添加到总列表
            all_workflows.extend(category_workflows)
            
            # 保存每个分类的工作流程到单独的文件
            save_category_workflows_to_file(category_workflows, category_name)
            
            print(f"分类 '{category_name}' 爬取完成，共 {len(category_workflows)} 个工作流程")
            
            # 添加延迟以尊重服务器
            if i < len(categories) - 1:
                delay = random.uniform(3.0, 6.0)
                print(f"等待 {delay:.2f} 秒后爬取下一个分类...")
                time.sleep(delay)
                
        except Exception as e:
            print(f"爬取分类 '{category_name}' 时出错: {e}")
    
    print(f"\n所有分类爬取完成，共获取 {len(all_workflows)} 个工作流程")
    return all_workflows

def get_workflow_detail(driver, url):
    """
    访问工作流程详情页，获取更多信息
    
    Args:
        driver: Selenium WebDriver
        url: 工作流程详情页URL
        
    Returns:
        包含详情页信息的字典
    """
    print(f"访问详情页: {url}")
    
    try:
        # 访问详情页
        current_window = driver.current_window_handle
        
        # 在新标签页中打开详情页
        driver.execute_script(f"window.open('{url}', '_blank');")
        time.sleep(2)  # 给页面加载一些时间
        
        # 切换到新标签页
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])  # 切换到最新打开的标签页
        
        # 等待页面加载完成
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        # 初始化详情信息字典
        details = {
            'author': '',
            'author_url': '',
            'publish_date': '',
            'is_premium': False,
            'content': '',
            'workflow_json': '',
            'readme': ''
        }
        
        # 提取标题
        try:
            title_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.title, h1.title--violet'))
            )
            title_div = title_element.find_elements(By.TAG_NAME, 'div')
            if title_div:
                details['title_full'] = title_div[0].text.strip()
            else:
                details['title_full'] = title_element.text.strip()
        except (TimeoutException, NoSuchElementException):
            print("    未找到标题元素")
        
        # 提取作者信息
        try:
            author_element = driver.find_element(By.CSS_SELECTOR, '.group-info a[href^="/creators/"]')
            details['author'] = author_element.text.strip()
            details['author_url'] = author_element.get_attribute('href')
        except NoSuchElementException:
            print("    未找到作者信息")
        
        # 提取发布/更新日期
        try:
            date_element = driver.find_element(By.CSS_SELECTOR, '.group-info p.font-geomanist')
            details['publish_date'] = date_element.text.strip()
        except NoSuchElementException:
            print("    未找到发布日期")
        
        # 提取是否是高级内容
        try:
            premium_elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'Free') or contains(text(), 'Premium')]")
            if premium_elements:
                details['is_premium'] = 'Premium' in premium_elements[0].text
        except:
            print("    未找到Premium/Free信息")
        
        # 提取工作流程JSON数据 - 使用Selenium直接获取
        try:
            # 等待n8n-demo元素加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'n8n-demo'))
            )
            
            # 获取n8n-demo元素的workflow属性
            workflow_element = driver.find_element(By.CSS_SELECTOR, 'n8n-demo')
            workflow_json = workflow_element.get_attribute('workflow')
            
            if workflow_json:
                print(f"    成功获取workflow JSON数据: {len(workflow_json)} 字符")
                details['workflow_json'] = workflow_json
                
                # 尝试提取节点数量
                try:
                    nodes_match = re.search(r'"nodes":\s*\[(.*?)\]', workflow_json, re.DOTALL)
                    if nodes_match:
                        nodes_text = nodes_match.group(1)
                        # 计算节点数量 (通过计算 "id": 出现的次数)
                        node_count = nodes_text.count('"id":')
                        details['node_count'] = node_count
                        print(f"    工作流程包含约 {node_count} 个节点")
                except Exception as e:
                    print(f"    解析工作流程JSON时出错: {e}")
            else:
                # 如果直接获取属性失败，尝试使用JavaScript获取
                workflow_json = driver.execute_script(
                    "return document.querySelector('n8n-demo').getAttribute('workflow');"
                )
                if workflow_json:
                    print(f"    通过JavaScript获取到workflow JSON数据: {len(workflow_json)} 字符")
                    details['workflow_json'] = workflow_json
                else:
                    print("    无法提取workflow JSON数据")
        except Exception as e:
            print(f"    获取workflow JSON数据时出错: {e}")
        
        # 提取README内容 - 多种选择器尝试
        readme_selectors = [
            'div.flex.flex-col.gap-12.lg\\:w-8\\/12.lg\\:gap-16 > div.content-base.text-md',
            'div[data-v-006f9244] > div.content-base.text-md',
            'div.content-base.text-md'
        ]
        
        for i, selector in enumerate(readme_selectors):
            try:
                readme_element = driver.find_element(By.CSS_SELECTOR, selector)
                readme_content = readme_element.text.strip()
                if readme_content:
                    print(f"    方法{i+1}：选择器获取README内容: {len(readme_content)} 字符")
                    details['readme'] = readme_content
                    break
            except NoSuchElementException:
                continue
            except Exception as e:
                print(f"    获取README内容时出错: {e}")
        
        if not details.get('readme'):
            # 如果所有选择器都失败，尝试使用JavaScript获取
            try:
                readme_js = """
                const elements = document.querySelectorAll('.content-base.text-md');
                for (const el of elements) {
                    if (el.textContent && el.textContent.trim().length > 0) {
                        return el.textContent.trim();
                    }
                }
                return '';
                """
                readme_content = driver.execute_script(readme_js)
                if readme_content:
                    print(f"    通过JavaScript获取README内容: {len(readme_content)} 字符")
                    details['readme'] = readme_content
                else:
                    print("    未找到README内容")
            except Exception as e:
                print(f"    通过JavaScript获取README内容时出错: {e}")
        
        print(f"    详情页信息获取成功，作者: {details['author']}, 发布于: {details['publish_date']}")
        
        # 关闭当前标签页并切回原始标签页
        driver.close()
        driver.switch_to.window(current_window)
        
        return details
        
    except Exception as e:
        print(f"    获取详情页时出错: {e}")
        import traceback
        print(traceback.format_exc())  # 打印完整的错误堆栈
        
        # 确保切回原始窗口
        try:
            driver.close()
            driver.switch_to.window(current_window)
        except:
            pass  # 忽略切换窗口可能的错误
            
        return {}

def ensure_data_dir():
    """
    确保数据目录结构存在，如果不存在则创建
    """
    # 创建主数据目录
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"创建了主数据目录: {data_dir}/")
    
    # 创建工作流程目录
    workflow_dir = os.path.join(data_dir, "workflow")
    if not os.path.exists(workflow_dir):
        os.makedirs(workflow_dir)
        print(f"创建了工作流程目录: {workflow_dir}/")
    
    return data_dir

def get_safe_dirname(name):
    """
    将分类名称转换为安全的目录名
    
    Args:
        name: 原始名称
        
    Returns:
        安全的目录名
    """
    # 替换空格为下划线，并移除其他不安全的字符
    safe_name = "".join([c if c.isalnum() or c == ' ' else '_' for c in name])
    safe_name = safe_name.replace(' ', '_')
    return safe_name

def ensure_category_dir(category_name):
    """
    确保分类目录存在，如果不存在则创建
    
    Args:
        category_name: 分类名称
        
    Returns:
        分类目录路径
    """
    data_dir = ensure_data_dir()
    safe_category_name = get_safe_dirname(category_name)
    category_dir = os.path.join(data_dir, "workflow", safe_category_name)
    
    if not os.path.exists(category_dir):
        os.makedirs(category_dir)
        print(f"创建了分类目录: {category_dir}/")
    
    return category_dir

def save_workflow_to_file(workflow_data):
    """
    将单个工作流程保存到对应分类目录下的独立JSON文件
    
    Args:
        workflow_data: 工作流程数据
    """
    if not workflow_data:
        return False
    
    category_name = workflow_data.get('category', 'Other')
    title = workflow_data.get('title', '').strip() or workflow_data.get('title_full', '').strip()
    
    if not title:
        title = f"workflow_{int(time.time())}"
    
    # 创建分类目录
    category_dir = ensure_category_dir(category_name)
    
    # 为文件名创建安全的标题
    safe_title = get_safe_dirname(title)
    # 避免文件名过长
    if len(safe_title) > 100:
        safe_title = safe_title[:100]
        
    # 从URL中提取ID以确保文件名的唯一性
    url = workflow_data.get('url', '')
    workflow_id = ''
    if url:
        id_match = re.search(r'/workflows/(\d+)-', url)
        if id_match:
            workflow_id = id_match.group(1)
    
    # 构造文件名
    if workflow_id:
        filename = f"{workflow_id}_{safe_title}.json"
    else:
        filename = f"{safe_title}_{int(time.time())}.json"
    
    # 保存文件
    filepath = os.path.join(category_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(workflow_data, f, ensure_ascii=False, indent=2)
    
    print(f"  已将工作流程 '{title}' 保存到 {filepath}")
    return True

def save_category_workflows_to_file(workflows, category_name):
    """
    将特定分类的所有工作流程保存到各自的文件
    
    Args:
        workflows: 工作流程数据列表
        category_name: 分类名称
    """
    if not workflows:
        return 0
    
    successful_saves = 0
    print(f"\n开始保存 {len(workflows)} 个工作流程到分类 '{category_name}' 目录")
    
    for i, workflow in enumerate(workflows):
        try:
            if save_workflow_to_file(workflow):
                successful_saves += 1
        except Exception as e:
            print(f"  保存工作流程 {i+1} 时出错: {e}")
    
    # 同时保存分类的汇总文件 (可选)
    # category_dir = ensure_category_dir(category_name)
    # summary_filepath = os.path.join(category_dir, f"{get_safe_dirname(category_name)}_summary.json")
    # with open(summary_filepath, 'w', encoding='utf-8') as f:
    #     json.dump(workflows, f, ensure_ascii=False, indent=2)
    
    print(f"成功保存了 {successful_saves}/{len(workflows)} 个工作流程到分类 '{category_name}' 目录")
    return successful_saves

def save_workflows_to_file(workflows, filename="n8n_workflows.json"):
    """
    将工作流程保存到data目录下的JSON文件
    
    Args:
        workflows: 工作流程数据列表
        filename: 文件名
    """
    data_dir = ensure_data_dir()
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(workflows, f, ensure_ascii=False, indent=2)
    
    print(f"已将 {len(workflows)} 个工作流程保存到 {filepath}")

def main():
    # 确保数据目录结构存在
    ensure_data_dir()
    
    logger.info("=== 开始爬取 n8n.io 工作流程 ===")
    
    # 初始化WebDriver
    driver = setup_driver()
    
    try:
        # 抓取所有工作流程分类
        categories = scrape_categorys(driver)
        # categories = [{
        #                 "category_url": "https://n8n.io/workflows/categories/ai/",
        #                 "category_name": "AI"
        #             }]
        
        # 打印所有获取的分类信息的JSON格式
        logger.info("===== 工作流程分类数据(JSON格式) =====")
        logger.info(json.dumps(categories, ensure_ascii=False, indent=2))
        
        if categories:
            logger.info(f"===== 开始爬取全部 {len(categories)} 个分类 =====")
            
            # 每个分类最多爬取的工作流程数量
            max_workflows = 2  # 可以根据需要调整这个数字
            logger.info(f"每个分类最多爬取 {max_workflows} 条工作流程")
            
            # 爬取所有分类中的工作流程
            all_workflows = scrape_category_workflows(driver, categories, max_workflows_per_category=max_workflows)
            
            # 保存所有工作流程
            if all_workflows:
                # 保存所有分类的汇总数据
                save_workflows_to_file(all_workflows, filename="n8n_all_workflows.json")
                
                # 打印爬取到的工作流程数据
                logger.info("===== 工作流程数据汇总 =====")
                logger.info(f"共爬取 {len(categories)} 个分类，总计 {len(all_workflows)} 个工作流程")
                
                # 按分类统计
                category_counts = {}
                for workflow in all_workflows:
                    cat = workflow.get('category', 'Unknown')
                    if cat in category_counts:
                        category_counts[cat] += 1
                    else:
                        category_counts[cat] = 1
                
                logger.info("===== 按分类统计工作流程数量 =====")
                for cat, count in category_counts.items():
                    logger.info(f"{cat}: {count} 个工作流程")
            else:
                logger.warning("未获取到任何工作流程")
        else:
            logger.warning("未获取到任何分类数据，无法进行爬取")
        
        logger.info("爬取任务完成!")
        logger.info(f"所有数据均已保存到 'data/workflow/' 目录下，按分类整理")
    
    finally:
        # 确保关闭WebDriver
        logger.info("关闭WebDriver...")
        driver.quit()
        logger.info("爬取任务结束")

if __name__ == "__main__":
    main()