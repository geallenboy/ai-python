import json
import time
import random
import os
import re
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('n8n_scraper.log', 'a', 'utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 代理服务器配置 - 替换为您的代理服务器列表
PROXY_SERVERS = [
    # 格式: "http://username:password@ip:port"
    # 如果不需要验证: "http://ip:port"
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    # 添加更多代理...
]

# 如果无代理可用，设置为空列表
# PROXY_SERVERS = []

class N8nWorkflowScraper:
    def __init__(self, headless: bool = False, use_proxies: bool = False, max_retries: int = 3):
        """
        初始化 n8n 工作流爬虫
        
        Args:
            headless: 是否使用无头模式
            use_proxies: 是否使用代理轮换 (由于没有可用代理，此选项将被忽略)
            max_retries: 最大重试次数
        """
        self.headless = headless
        # 不管传入什么，都将 use_proxies 设置为 False
        self.use_proxies = False  # 由于没有代理，强制设为 False
        self.max_retries = max_retries
        self.current_proxy_index = 0
        self.browser = None
        self.context = None
    
    async def setup_browser(self) -> None:
        """
        设置 Playwright 浏览器环境，不使用代理
        """
        logger.info("初始化 Playwright...")
        playwright = await async_playwright().start()
        
        # 浏览器选项
        browser_options = {
            "headless": self.headless,
            "args": [
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-extensions",
                "--disable-notifications",
                "--disable-infobars",
                "--blink-settings=imagesEnabled=false"  # 禁用图像加载
            ]
        }
        
        # 创建浏览器实例
        self.browser = await playwright.chromium.launch(**browser_options)
        
        # 创建浏览器上下文，不使用代理
        context_options = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
            
        self.context = await self.browser.new_context(**context_options)

        # 设置超时
        self.context.set_default_timeout(60000)  # 增加到 60 秒
        self.context.set_default_navigation_timeout(60000)  # 专门设置导航超时
        
        # 设置拦截器 (可选，用于优化加载速度)
        await self.context.route("**/*.{png,jpg,jpeg,gif,svg,pdf,woff,woff2}", lambda route: route.abort())
    
    async def close_browser(self) -> None:
        """
        关闭浏览器
        """
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("浏览器已关闭")
    
    async def rotate_proxy(self) -> None:
        """
        空实现的代理轮换函数，因为没有可用代理
        """
        # 由于没有代理，此函数不执行任何操作
        logger.info("未配置代理服务器，跳过代理轮换")
        pass
    
    async def retry_with_proxies(self, func, *args, **kwargs):
        """
        重试函数（无代理版本）
        
        Args:
            func: 要重试的异步函数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数返回值
        """
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                retries += 1
                logger.warning(f"操作失败 ({retries}/{self.max_retries}): {str(e)}")
                
                # 随机等待时间，递增延迟
                wait_time = random.uniform(2, 5) * retries
                logger.info(f"等待 {wait_time:.2f} 秒后重试...")
                await asyncio.sleep(wait_time)
        
        logger.error(f"达到最大重试次数 {self.max_retries}，操作失败: {last_error}")
        raise last_error
    
    async def scrape_categories(self) -> List[Dict[str, str]]:
        """
        从n8n.io/workflows抓取工作流程分类信息
        
        Returns:
            分类信息列表
        """
        base_url = "https://n8n.io/workflows/"
        categories = []
        
        logger.info(f"开始从 {base_url} 抓取工作流程分类")
        
        try:
            # 创建新页面
            page = await self.context.new_page()
            
            # 修改加载策略，使用 domcontentloaded 替代 networkidle
            logger.info("访问网站并等待页面加载...")
            await page.goto(base_url, wait_until="domcontentloaded")
            logger.info("页面基本内容已加载，等待分类元素...")
            
            # 增加页面加载后的额外等待时间
            await asyncio.sleep(5)  # 等待5秒钟让JavaScript完成渲染
            
            logger.info(f"页面标题: {await page.title()}")
            
            # 使用更长的超时时间等待分类容器
            try:
                logger.info("等待分类容器元素...")
                category_container = await page.wait_for_selector(
                    '.flex.flex-wrap.gap-2.justify-center', 
                    timeout=60000  # 增加到60秒
                )
                logger.info("分类容器元素已找到")
            except Exception as e:
                logger.warning(f"未能找到分类容器，尝试截图记录当前页面状态")
                # 截图记录页面状态
                await page.screenshot(path="error_categories_page.png")
                logger.info("错误页面截图已保存到 error_categories_page.png")
                
                # 尝试使用备选选择器
                logger.info("尝试使用备选选择器...")
                category_container = await page.query_selector('div.container')
                if not category_container:
                    raise Exception("无法找到分类容器，即使使用备选选择器")
            
            # 获取所有分类链接
            category_links = await category_container.query_selector_all('a')
            
            logger.info(f"\n===== 获取的分类信息 =====")
            logger.info(f"共找到 {len(category_links)} 个分类")
            logger.info("--------------------------")
            
            for link in category_links:
                href = await link.get_attribute('href')
                category_name = await link.text_content()
                category_name = category_name.strip()
                
                # 打印每个分类的详细信息
                logger.info(f"分类名称: {category_name}")
                logger.info(f"分类链接: {href}")
                logger.info("--------------------------")
                
                # 将分类信息添加到categories列表
                categories.append({
                    'category_url': href if href.startswith("http") else f"https://n8n.io{href}",
                    'category_name': category_name
                })
            
            logger.info(f"\n成功获取 {len(categories)} 个分类")
            
            # 关闭页面
            await page.close()
            
        except Exception as e:
            logger.error(f"获取分类信息时出错: {e}")
            # 确保页面关闭
            try:
                await page.close()
            except:
                pass
        
        return categories
    
    async def scrape_category_workflows(self, categories: List[Dict[str, str]], max_workflows_per_category: int = 10) -> List[Dict[str, Any]]:
        """
        爬取每个分类URL中的工作流程，支持分页加载，并进入详情页获取更多信息
        
        Args:
            categories: 包含分类信息的列表
            max_workflows_per_category: 每个分类最多爬取的工作流程数量
            
        Returns:
            所有爬取到的工作流程列表
        """
        all_workflows = []
        
        # 添加调试输出以确认正在爬取的分类
        logger.info("\n===== 开始爬取以下分类 =====")
        for cat in categories:
            logger.info(f"- {cat.get('category_name')} ({cat.get('category_url')})")
        logger.info("===========================\n")
        
        # 遍历每个分类
        for i, category in enumerate(categories):
            category_url = category.get('category_url')
            category_name = category.get('category_name')
            
            logger.info(f"\n[{i+1}/{len(categories)}] 开始爬取分类: {category_name}")
            logger.info(f"URL: {category_url}")
            logger.info(f"限制：每个分类最多爬取 {max_workflows_per_category} 条数据")
            
            try:
                # 创建新页面
                page = await self.context.new_page()
                
                # 初始化分类工作流程列表
                category_workflows = []
                already_loaded = 0
                has_more = False
                
                # 访问分类URL
                await page.goto(category_url, wait_until="domcontentloaded")
                await asyncio.sleep(3)  # 给JavaScript额外的时间加载内容
                
                # 验证当前URL，确保我们在正确的页面上
                current_url = page.url
                logger.info(f"当前页面URL: {current_url}")
                
                # 获取总结果数量
                try:
                    total_element = await page.wait_for_selector('h2.title--white-violet', timeout=5000)
                    result_text = await total_element.text_content()
                    match = re.search(r'\((\d+)\)', result_text)
                    total_count = int(match.group(1)) if match else 0
                    logger.info(f"该分类下共有 {total_count} 个工作流程（仅获取前 {max_workflows_per_category} 条）")
                except Exception as e:
                    logger.warning(f"无法获取总结果数量: {e}")
                    total_count = 0
                
                while has_more:
                    # 等待工作流项目加载
                    await page.wait_for_selector('.workflow-search-result, a[href^="/workflows/"]')
                    
                    # 获取当前页面上的所有工作流项目
                    workflow_items = await page.query_selector_all('.workflow-search-result, a[href^="/workflows/"]')
                    logger.info(f"本次找到 {len(workflow_items)} 个工作流程")
                    
                    if not workflow_items:
                        logger.warning("未找到工作流程项，可能需要调整选择器")
                        break
                    
                    # 处理每个工作流程项，但限制数量
                    items_to_process = workflow_items
                    remaining_count = max_workflows_per_category - len(category_workflows)
                    if remaining_count < len(items_to_process):
                        items_to_process = items_to_process[:remaining_count]
                        logger.info(f"限制处理数量，本次仅处理 {len(items_to_process)} 个工作流程")
                    
                    for j, item in enumerate(items_to_process):
                        try:
                            # 获取详情页URL
                            href = await item.get_attribute('href')
                            if not href:
                                continue
                                
                            # 构造完整URL
                            workflow_url = f"https://n8n.io{href}" if href.startswith('/') else href
                            
                            # 提取工作流程标题
                            try:
                                title_element = await item.query_selector('h4, .title')
                                title = await title_element.text_content() if title_element else "未知标题"
                            except Exception:
                                title = "未知标题"
                            
                            # 提取工作流程描述
                            try:
                                desc_element = await item.query_selector('p')
                                description = await desc_element.text_content() if desc_element else ""
                            except Exception:
                                description = ""
                            
                            logger.info(f"  [{len(category_workflows) + 1}] 发现工作流程: {title}")
                            logger.info(f"      URL: {workflow_url}")
                            
                            # 随机延迟，模拟人类行为
                            await asyncio.sleep(random.uniform(0.5, 1.5))
                            
                            # 获取详情页内容
                            detailed_info = await self.retry_with_proxies(
                                self.get_workflow_detail, workflow_url
                            )
                            
                            # 将工作流程信息添加到列表
                            workflow_data = {
                                'title': title,
                                'url': workflow_url,
                                'description': description,
                                'category': category_name,
                                'category_url': category_url,
                                **detailed_info  # 合并详情页中获取的信息
                            }
                            
                            category_workflows.append(workflow_data)
                            logger.info(f"  已添加详细信息: {title}")
                            
                            # 检查是否已达到每个分类的最大爬取数量
                            if len(category_workflows) >= max_workflows_per_category:
                                logger.info(f"已达到每个分类的最大爬取数量: {max_workflows_per_category}")
                                has_more = False
                                break
                        
                        except Exception as e:
                            logger.error(f"  处理工作流程时出错: {e}")
                    
                    # 如果已经达到限制，不再加载更多
                    if len(category_workflows) >= max_workflows_per_category:
                        has_more = False
                        logger.info(f"已达到测试限制数量: {max_workflows_per_category}，停止加载更多")
                        break
                    
                    # 更新已加载数量
                    already_loaded += len(workflow_items)
                    
                    # 检查是否有"加载更多"按钮，且未达到最大爬取数量
                    try:
                        load_more_btn = await page.query_selector("button:has-text('Load more templates')")
                        
                        if load_more_btn:
                            is_disabled = await load_more_btn.get_attribute('disabled')
                            
                            if not is_disabled and total_count > already_loaded and len(category_workflows) < max_workflows_per_category:
                                # 滚动到按钮位置
                                await load_more_btn.scroll_into_view_if_needed()
                                await asyncio.sleep(1)  # 等待页面滚动
                                
                                # 点击加载更多按钮
                                await load_more_btn.click()
                                logger.info(f"加载更多，已加载 {already_loaded}/{total_count}")
                                
                                # 等待新内容加载
                                await asyncio.sleep(3)
                            else:
                                has_more = False
                                logger.info(f"已加载足够内容: {len(category_workflows)} 项")
                        else:
                            has_more = False
                            logger.info("没有找到加载更多按钮")
                    
                    except Exception as e:
                        has_more = False
                        logger.warning(f"处理加载更多按钮时出错: {e}")
                
                # 将当前分类的工作流程添加到总列表
                all_workflows.extend(category_workflows)
                
                # 保存每个分类的工作流程到单独的文件
                self.save_category_workflows_to_file(category_workflows, category_name)
                
                logger.info(f"分类 '{category_name}' 爬取完成，共 {len(category_workflows)} 个工作流程")
                
                # 关闭页面
                await page.close()
                
                # 添加延迟以尊重服务器，没有代理时增加随机等待时间
                if i < len(categories) - 1:
                    # 没有代理的情况下，增加随机等待时间降低被封风险
                    delay = random.uniform(5.0, 10.0)  # 增加等待时间
                    logger.info(f"等待 {delay:.2f} 秒后爬取下一个分类...")
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                logger.error(f"爬取分类 '{category_name}' 时出错: {e}")
                # 确保页面关闭
                try:
                    await page.close()
                except:
                    pass
        
        logger.info(f"\n所有分类爬取完成，共获取 {len(all_workflows)} 个工作流程")
        return all_workflows
    
    async def get_workflow_detail(self, url: str) -> Dict[str, Any]:
        """
        访问工作流程详情页，获取更多信息
        
        Args:
            url: 工作流程详情页URL
            
        Returns:
            包含详情页信息的字典
        """
        logger.info(f"访问详情页: {url}")
        
        try:
            # 创建新页面
            page = await self.context.new_page()
            
            # 访问详情页
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(3)  # 给JavaScript额外的时间加载内容
            
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
                title_element = await page.wait_for_selector('h1.title, h1.title--violet', timeout=5000)
                
                # 检查是否有子div
                title_div = await title_element.query_selector('div')
                if title_div:
                    details['title_full'] = await title_div.text_content()
                else:
                    details['title_full'] = await title_element.text_content()
                
                details['title_full'] = details['title_full'].strip()
            except Exception:
                logger.warning("    未找到标题元素")
            
            # 提取作者信息
            try:
                author_element = await page.query_selector('.group-info a[href^="/creators/"]')
                if author_element:
                    details['author'] = await author_element.text_content()
                    details['author_url'] = await author_element.get_attribute('href')
            except Exception:
                logger.warning("    未找到作者信息")
            
            # 提取发布/更新日期
            try:
                date_element = await page.query_selector('.group-info p.font-geomanist')
                if date_element:
                    details['publish_date'] = await date_element.text_content()
            except Exception:
                logger.warning("    未找到发布日期")
            
            # 提取是否是高级内容
            try:
                premium_elements = await page.query_selector_all("span:has-text('Free'), span:has-text('Premium')")
                if premium_elements:
                    premium_text = await premium_elements[0].text_content()
                    details['is_premium'] = 'Premium' in premium_text
            except Exception:
                logger.warning("    未找到Premium/Free信息")
            
            # 提取工作流程JSON数据 - 多种方法尝试
            try:
                # 方法1: 等待n8n-demo元素并获取workflow属性
                await page.wait_for_selector('n8n-demo', timeout=10000)
                
                # 使用evaluate直接获取元素属性
                workflow_json = await page.evaluate('''() => {
                    const element = document.querySelector('n8n-demo');
                    return element ? element.getAttribute('workflow') : '';
                }''')
                
                if workflow_json:
                    logger.info(f"    成功获取workflow JSON数据: {len(workflow_json)} 字符")
                    details['workflow_json'] = workflow_json
                    
                    # 尝试提取节点数量
                    try:
                        nodes_match = re.search(r'"nodes":\s*\[(.*?)\]', workflow_json, re.DOTALL)
                        if nodes_match:
                            nodes_text = nodes_match.group(1)
                            # 计算节点数量 (通过计算 "id": 出现的次数)
                            node_count = nodes_text.count('"id":')
                            details['node_count'] = node_count
                            logger.info(f"    工作流程包含约 {node_count} 个节点")
                    except Exception as e:
                        logger.warning(f"    解析工作流程JSON时出错: {e}")
                else:
                    # 方法2: 通过脚本选择器获取
                    html_content = await page.content()
                    workflow_match = re.search(r'<n8n-demo[^>]*\sworkflow="([^"]*)"', html_content)
                    if workflow_match:
                        workflow_json = workflow_match.group(1)
                        # HTML实体解码 (使用Playwright的evaluate方法)
                        workflow_json = await page.evaluate('''(html) => {
                            const div = document.createElement('div');
                            div.innerHTML = html;
                            return div.textContent;
                        }''', workflow_json)
                        logger.info(f"    通过正则表达式获取workflow JSON数据: {len(workflow_json)} 字符")
                        details['workflow_json'] = workflow_json
                    else:
                        logger.warning("    无法提取workflow JSON数据")
            except Exception as e:
                logger.error(f"    获取workflow JSON数据时出错: {e}")
            
            # 提取README内容 - 多种选择器尝试
            readme_selectors = [
                'div.flex.flex-col.gap-12.lg\\:w-8\\/12.lg\\:gap-16 > div.content-base.text-md',
                'div[data-v-006f9244] > div.content-base.text-md',
                'div.content-base.text-md'
            ]
            
            readme_content = ""
            
            for i, selector in enumerate(readme_selectors):
                try:
                    readme_element = await page.query_selector(selector)
                    if readme_element:
                        content = await readme_element.text_content()
                        if content and content.strip():
                            readme_content = content.strip()
                            logger.info(f"    方法{i+1}：选择器获取README内容: {len(readme_content)} 字符")
                            break
                except Exception:
                    continue
            
            if not readme_content:
                # 如果所有选择器都失败，尝试使用JavaScript获取
                try:
                    readme_js = """
                    () => {
                        const elements = document.querySelectorAll('.content-base.text-md');
                        for (const el of elements) {
                            if (el.textContent && el.textContent.trim().length > 0) {
                                return el.textContent.trim();
                            }
                        }
                        return '';
                    }
                    """
                    readme_content = await page.evaluate(readme_js)
                    if readme_content:
                        logger.info(f"    通过JavaScript获取README内容: {len(readme_content)} 字符")
                    else:
                        logger.warning("    未找到README内容")
                except Exception as e:
                    logger.warning(f"    通过JavaScript获取README内容时出错: {e}")
            
            details['readme'] = readme_content
            
            logger.info(f"    详情页信息获取成功，作者: {details['author']}, 发布于: {details['publish_date']}")
            
            # 关闭页面
            await page.close()
            
            return details
            
        except Exception as e:
            logger.error(f"    获取详情页时出错: {e}")
            import traceback
            logger.error(traceback.format_exc())  # 打印完整的错误堆栈
            
            # 确保页面关闭
            try:
                await page.close()
            except:
                pass
                
            return {}
    
    def ensure_data_dir(self) -> str:
        """
        确保数据目录结构存在
        
        Returns:
            主数据目录路径
        """
        # 创建主数据目录
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"创建了主数据目录: {data_dir}/")
        
        # 创建工作流程目录
        workflow_dir = os.path.join(data_dir, "workflow")
        if not os.path.exists(workflow_dir):
            os.makedirs(workflow_dir)
            logger.info(f"创建了工作流程目录: {workflow_dir}/")
        
        return data_dir
    
    def get_safe_dirname(self, name: str) -> str:
        """
        将名称转换为安全的目录名
        
        Args:
            name: 原始名称
            
        Returns:
            安全的目录名
        """
        # 替换空格为下划线，并移除其他不安全的字符
        safe_name = "".join([c if c.isalnum() or c == ' ' else '_' for c in name])
        safe_name = safe_name.replace(' ', '_')
        return safe_name
    
    def ensure_category_dir(self, category_name: str) -> str:
        """
        确保分类目录存在
        
        Args:
            category_name: 分类名称
            
        Returns:
            分类目录路径
        """
        data_dir = self.ensure_data_dir()
        safe_category_name = self.get_safe_dirname(category_name)
        category_dir = os.path.join(data_dir, "workflow", safe_category_name)
        
        if not os.path.exists(category_dir):
            os.makedirs(category_dir)
            logger.info(f"创建了分类目录: {category_dir}/")
        
        return category_dir
    
    def save_workflow_to_file(self, workflow_data: Dict[str, Any]) -> bool:
        """
        将单个工作流程保存到文件
        
        Args:
            workflow_data: 工作流程数据
            
        Returns:
            是否成功保存
        """
        if not workflow_data:
            return False
        
        category_name = workflow_data.get('category', 'Other')
        title = workflow_data.get('title', '').strip() or workflow_data.get('title_full', '').strip()
        
        if not title:
            title = f"workflow_{int(time.time())}"
        
        # 创建分类目录
        category_dir = self.ensure_category_dir(category_name)
        
        # 为文件名创建安全的标题
        safe_title = self.get_safe_dirname(title)
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
        
        logger.info(f"  已将工作流程 '{title}' 保存到 {filepath}")
        return True
    
    def save_category_workflows_to_file(self, workflows: List[Dict[str, Any]], category_name: str) -> int:
        """
        将特定分类的所有工作流程保存到各自的文件
        
        Args:
            workflows: 工作流程数据列表
            category_name: 分类名称
            
        Returns:
            成功保存的工作流程数量
        """
        if not workflows:
            return 0
        
        successful_saves = 0
        logger.info(f"\n开始保存 {len(workflows)} 个工作流程到分类 '{category_name}' 目录")
        
        for i, workflow in enumerate(workflows):
            try:
                if self.save_workflow_to_file(workflow):
                    successful_saves += 1
            except Exception as e:
                logger.error(f"  保存工作流程 {i+1} 时出错: {e}")
        
        logger.info(f"成功保存了 {successful_saves}/{len(workflows)} 个工作流程到分类 '{category_name}' 目录")
        return successful_saves
    
    def save_workflows_to_file(self, workflows: List[Dict[str, Any]], filename: str = "n8n_workflows.json") -> None:
        """
        将工作流程保存到data目录下的JSON文件
        
        Args:
            workflows: 工作流程数据列表
            filename: 文件名
        """
        data_dir = self.ensure_data_dir()
        filepath = os.path.join(data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(workflows, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已将 {len(workflows)} 个工作流程保存到 {filepath}")
    
    async def run(self, max_workflows_per_category: int = 10, use_hardcoded_categories: bool = False):
        """
        运行爬虫
        
        Args:
            max_workflows_per_category: 每个分类最多爬取的工作流程数量
            use_hardcoded_categories: 是否使用硬编码的分类，而不是从网站抓取
        """
        # 确保数据目录结构存在
        self.ensure_data_dir()
        
        try:
            # 设置浏览器
            await self.setup_browser()
            
            # 抓取所有工作流程分类
            if use_hardcoded_categories:
                categories = [{
                    "category_url": "https://n8n.io/workflows/categories/ai/",
                    "category_name": "AI"
                }]
                logger.info("使用硬编码的分类列表")
            else:
                categories = await self.retry_with_proxies(self.scrape_categories)
            
            # 保存分类信息到文件
            self.save_workflows_to_file(categories, filename="n8n_categories.json")
            
            # 打印所有获取的分类信息的JSON格式
            logger.info("\n===== 工作流程分类数据(JSON格式) =====")
            logger.info(json.dumps(categories, ensure_ascii=False, indent=2))
            
            if categories:
                logger.info(f"\n===== 开始爬取全部 {len(categories)} 个分类 =====")
                logger.info(f"每个分类最多爬取 {max_workflows_per_category} 条工作流程")
                
                # 爬取所有分类中的工作流程
                all_workflows = await self.retry_with_proxies(
                    self.scrape_category_workflows, 
                    categories, 
                    max_workflows_per_category
                )
                
                # 保存所有工作流程
                if all_workflows:
                    # 保存所有分类的汇总数据
                    self.save_workflows_to_file(all_workflows, filename="n8n_all_workflows.json")
                    
                    # 打印爬取到的工作流程数据
                    logger.info("\n===== 工作流程数据汇总 =====")
                    logger.info(f"共爬取 {len(categories)} 个分类，总计 {len(all_workflows)} 个工作流程")
                    
                    # 按分类统计
                    category_counts = {}
                    for workflow in all_workflows:
                        cat = workflow.get('category', 'Unknown')
                        if cat in category_counts:
                            category_counts[cat] += 1
                        else:
                            category_counts[cat] = 1
                    
                    logger.info("\n===== 按分类统计工作流程数量 =====")
                    for cat, count in category_counts.items():
                        logger.info(f"{cat}: {count} 个工作流程")
                else:
                    logger.warning("未获取到任何工作流程")
            else:
                logger.warning("未获取到任何分类数据，无法进行爬取")
            
            logger.info("\n爬取任务完成!")
            logger.info(f"所有数据均已保存到 'data/workflow/' 目录下，按分类整理")
        
        finally:
            # 确保关闭浏览器
            await self.close_browser()
            logger.info("爬取任务结束")
    
    async def goto_with_retry(self, page, url, max_attempts=3):
        """
        带重试的页面导航
        """
        attempt = 0
        while attempt < max_attempts:
            try:
                attempt += 1
                logger.info(f"尝试访问 {url} (尝试 {attempt}/{max_attempts})")
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(3)  # 等待额外时间
                return True
            except Exception as e:
                logger.warning(f"页面访问失败: {e}")
                if attempt < max_attempts:
                    wait_time = random.uniform(5, 10) * attempt
                    logger.info(f"等待 {wait_time:.2f} 秒后重试...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"已达最大重试次数，无法访问 {url}")
                    return False


async def main():
    """
    主函数
    """
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='n8n 工作流爬虫')
    parser.add_argument('--headless', action='store_true', help='使用无头模式')
    # 注释或删除代理相关参数
    # parser.add_argument('--use-proxies', action='store_true', help='使用代理轮换')
    parser.add_argument('--max-workflows', type=int, default=5, help='每个分类最多爬取的工作流程数量 (默认: 5)')
    parser.add_argument('--test-mode', action='store_true', help='测试模式 (只爬取AI分类)')
    args = parser.parse_args()
    
    # 创建爬虫实例，不使用代理
    scraper = N8nWorkflowScraper(
        headless=args.headless,
        use_proxies=False,  # 强制设置为 False
        max_retries=3
    )
    
    # 运行爬虫
    await scraper.run(
        max_workflows_per_category=args.max_workflows,
        use_hardcoded_categories=args.test_mode
    )

if __name__ == "__main__":
    asyncio.run(main())