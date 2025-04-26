
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
    
    async def scrape_category_workflows(self, categories: List[Dict[str, str]], max_workflows_per_category: int = None) -> List[Dict[str, Any]]:
        """
        爬取每个分类URL中的工作流程，支持"加载更多"功能
        
        Args:
            categories: 包含分类信息的列表
            max_workflows_per_category: 每个分类最多爬取的工作流程数量，None 表示不限制
            
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
            
            # 修改日志输出
            if max_workflows_per_category is not None:
                logger.info(f"限制：每个分类最多爬取 {max_workflows_per_category} 条数据")
            else:
                logger.info(f"不限制爬取数量，将爬取所有工作流程")
            
            try:
                # 创建新页面
                page = await self.context.new_page()
                
                # 初始化分类工作流程列表
                category_workflows = []
                already_loaded = 0
                has_more = True  # 初始设为True，假设有更多内容可以加载
                
                # 访问分类URL
                await page.goto(category_url, wait_until="domcontentloaded")
                await asyncio.sleep(3)  # 给JavaScript额外的时间加载内容
                
                # 验证当前URL，确保我们在正确的页面上
                current_url = page.url
                logger.info(f"当前页面URL: {current_url}")
                
                # 获取总结果数量信息（仅供参考）
                try:
                    total_element = await page.wait_for_selector('h2.title--white-violet', timeout=5000)
                    result_text = await total_element.text_content()
                    match = re.search(r'\((\d+)\)', result_text)
                    total_count = int(match.group(1)) if match else 0
                    if max_workflows_per_category is not None:
                        logger.info(f"该分类下共有 {total_count} 个工作流程（仅获取前 {max_workflows_per_category} 条）")
                    else:
                        logger.info(f"该分类下共有 {total_count} 个工作流程（将获取全部）")
                except Exception as e:
                    logger.warning(f"无法获取总结果数量: {e}")
                    total_count = 0
                
                # 等待工作流项目加载
                await page.wait_for_selector('.workflow-search-result, a.workflow-search-result')
                
                # 循环"加载更多"，直到没有更多内容或达到最大数量限制
                while has_more:
                    # 获取当前页面上的所有工作流项目
                    workflow_items = await page.query_selector_all('.workflow-search-result, a.workflow-search-result')
                    current_count = len(workflow_items)
                    
                    logger.info(f"当前已加载 {current_count} 个工作流程（之前已加载 {already_loaded} 个）")
                    
                    # 检查是否有新内容加载
                    if current_count <= already_loaded:
                        logger.info("没有新内容加载，停止加载更多")
                        break
                    
                    # 检查是否已达到最大爬取数量
                    if max_workflows_per_category is not None and current_count >= max_workflows_per_category:
                        logger.info(f"已达到限制数量 {max_workflows_per_category}，停止加载更多")
                        break
                    
                    # 查找"加载更多"按钮
                    load_more_button = None
                    load_more_selectors = [
                        'button:has-text("Load more")', 
                        'button:has-text("加载更多")',
                        '.load-more-button',
                        'button.btn.btn--main',
                    ]
                    
                    for selector in load_more_selectors:
                        try:
                            load_more_button = await page.query_selector(selector)
                            if load_more_button:
                                logger.info(f"找到加载更多按钮，使用选择器: {selector}")
                                break
                        except Exception:
                            continue
                    
                    # 处理当前页面的工作流程
                    items_to_process = workflow_items[already_loaded:]
                    logger.info(f"处理新加载的 {len(items_to_process)} 个工作流程")
                    
                    # 更新已加载数量
                    already_loaded = current_count
                    
                    # 处理每个工作流程项
                    for j, item in enumerate(items_to_process):
                        try:
                            # 获取详情页URL
                            href = await item.get_attribute('href')
                            if not href:
                                continue
                            
                            # 构造完整URL
                            workflow_url = f"https://n8n.io{href}" if href.startswith('/') else href
                            logger.info(f"工作流程详情页URL: {workflow_url}")
                            
                            # 提取工作流程标题
                            try:
                                # 使用更精确的选择器，包括类名
                                title_element = await item.query_selector('h4.font-geomanist.text-lg.text-shades-hazy-white, .title')
                                
                                # 如果找不到特定类名的h4，回退到更通用的选择器
                                if not title_element:
                                    title_element = await item.query_selector('h4, .title')
                                
                                # 提取文本内容
                                if title_element:
                                    title = await title_element.text_content()
                                    # 清理文本（去除多余空格、换行符等）
                                    title = title.strip()
                                    logger.info(f"    提取到标题: {title}")
                                else:
                                    title = "未知标题"
                                    logger.warning("    未能找到标题元素，使用默认值")
                            except Exception as e:
                                title = "未知标题"
                                logger.warning(f"    提取标题时出错: {e}")
                            
                            logger.info(f"  [{len(category_workflows) + 1}] 发现工作流程: {title}")
                            logger.info(f"      URL: {workflow_url}")
                            
                            # 检查文件是否已经存在
                            if hasattr(self, 'workflow_file_exists') and self.workflow_file_exists(category_name, workflow_url, title):
                                logger.info(f"  已存在该工作流，跳过详情页爬取: {title}")
                                
                                # 创建一个简化版的工作流数据
                                workflow_data = {
                                    'title': title,
                                    'url': workflow_url,
                                    'category': category_name,
                                    'category_url': category_url,
                                    'skipped_details': True,  # 标记为跳过详情页
                                    'note': '文件已存在，跳过详情页爬取'
                                }
                                
                                category_workflows.append(workflow_data)
                                continue  # 跳过详情页爬取
                            
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
                                'category': category_name,
                                'category_url': category_url,
                                **detailed_info  # 合并详情页中获取的信息
                            }

                            # 立即保存此工作流到文件
                            try:
                                save_success = self.save_workflow_to_file(workflow_data)
                                if save_success:
                                    logger.info(f"  已实时保存工作流: {title}")
                                else:
                                    logger.warning(f"  实时保存工作流失败: {title}")
                            except Exception as save_error:
                                logger.error(f"  实时保存工作流时出错: {save_error}")
                            
                            # 仍然添加到列表，用于后续的批量统计
                            category_workflows.append(workflow_data)
                            logger.info(f"  已添加详细信息: {title}")
                            
                            # 检查是否已达到最大爬取数量
                            if max_workflows_per_category is not None and len(category_workflows) >= max_workflows_per_category:
                                logger.info(f"已达到限制数量 {max_workflows_per_category}，停止处理更多工作流程")
                                has_more = False
                                break
                        
                        except Exception as e:
                            logger.error(f"  处理工作流程时出错: {e}")
                    
                    # 如果没有找到"加载更多"按钮或已经达到最大数量，则结束循环
                    if not load_more_button or not has_more:
                        logger.info("未找到加载更多按钮或已达到最大数量限制，停止加载更多")
                        break
                    
                    # 点击"加载更多"按钮
                    try:
                        logger.info("点击加载更多按钮...")
                        await load_more_button.click()
                        
                        # 等待加载动画
                        try:
                            await page.wait_for_selector('.loading, .spinner', timeout=2000)
                            logger.info("检测到加载动画，等待其消失...")
                            await page.wait_for_selector('.loading, .spinner', state='detached', timeout=20000)
                        except Exception:
                            # 如果没有加载动画或它消失得太快，我们仍然需要等待
                            pass
                        
                        # 等待更多内容加载
                        await asyncio.sleep(3)
                        
                        logger.info("内容加载完成，继续处理")
                    except Exception as e:
                        logger.error(f"点击加载更多按钮时出错: {e}")
                        has_more = False  # 出错时停止加载更多
            
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
            
            # 访问详情页并使用重试机制
            success = await self.goto_with_retry(page, url)
            if not success:
                logger.error(f"无法访问详情页: {url}")
                await page.close()
                return {}
           
            
            # 初始化详情信息字典
            details = {
                'author': '',
                'publish_date': '',
                'content': '',
                'workflow_json': '',
                'readme': ''
            }
            
            
            # 提取作者信息 - 根据您提供的DOM信息更新
            try:
                # 尝试多种选择器获取作者信息
                author_selectors = [
                    'a[href^="/creators/"] p.font-geomanist.text-caption-large-medium.text-shades-soft-gray',  # 作者链接内的段落
                    'a[href^="/creators/"] div p',  # 嵌套在div中的作者名称
                ]
                
                for selector in author_selectors:
                    try:
                        author_element = await page.query_selector(selector)
                        if author_element:
                            # 从元素中提取作者名称文本
                            author_name = await author_element.text_content()
                            logger.info(f" author_name: {author_name}")
                            if author_name and author_name.strip():
                                details['author'] = author_name.strip()
                                logger.info(f"    提取到作者: {details['author']}")
                                break
                    except Exception as e:  # 正确地捕获异常到变量 e
                        logger.debug(f"    提取作者链接失败: {e}")
                        continue
                
                
            except Exception as e:
                logger.warning(f"    提取作者信息时出错: {e}")
            
            # 提取发布/更新日期 - 根据您提供的DOM信息更新
            try:
                # 尝试多种选择器获取更新日期
                date_selectors = [
                    'div.group-info p.font-geomanist.text-md',           # 新提供的选择器
                ]
                
                for selector in date_selectors:
                    try:
                        date_element = await page.query_selector(selector)
                        if date_element:
                            date_text = await date_element.text_content()
                            if date_text and 'update' in date_text.lower():
                                details['publish_date'] = date_text.strip()
                                logger.info(f"    提取到更新日期: {details['publish_date']}")
                                break
                    except Exception:
                        continue
                        
                if not details['publish_date']:
                    logger.warning("    未能找到更新日期元素")
            except Exception as e:
                logger.warning(f"    提取更新日期时出错: {e}")
            
        
            
            # 提取工作流程JSON数据
            try:
                # 方法: 等待n8n-demo元素并获取workflow属性
                try:
                    await page.wait_for_selector('n8n-demo', timeout=10000)
                    
                    # 使用evaluate直接获取元素属性
                    workflow_json = await page.evaluate('''() => {
                        const element = document.querySelector('n8n-demo');
                        return element ? element.getAttribute('workflow') : '';
                    }''')
                    
                    if workflow_json:
                        logger.info(f"    成功获取workflow JSON数据: {len(workflow_json)} 字符")
                        details['workflow_json'] = workflow_json

                except Exception as e:
                    logger.warning(f"    通过n8n-demo元素获取workflow JSON失败: {e}")
            except Exception as e:
                logger.warning(f"    提取工作流程JSON数据时出错: {e}")
            
            # 提取README内容 - 保存为Markdown格式
            try:
                # 添加必要的依赖
                import html2text
                
                # 尝试多种选择器获取README内容
                readme_selectors = [
                    'div.content-base.text-md',             # 新提供的选择器
                   
                ]
                
                readme_content = ""
                readme_html = ""
                
                for i, selector in enumerate(readme_selectors):
                    try:
                        readme_element = await page.query_selector(selector)
                        if readme_element:
                            # 获取元素的HTML内容
                            readme_html = await page.evaluate("""(element) => {
                                return element.innerHTML;
                            }""", readme_element)
                            
                            if readme_html and readme_html.strip():
                                # 转换HTML为Markdown
                                h2t = html2text.HTML2Text()
                                h2t.ignore_links = False
                                h2t.ignore_images = False
                                h2t.ignore_tables = False
                                h2t.ignore_emphasis = False
                                h2t.body_width = 0  # 不自动换行
                                
                                readme_content = h2t.handle(readme_html)
                                logger.info(f"    方法{i+1}：选择器获取README内容并转换为Markdown: {len(readme_content)} 字符")
                                break
                    except Exception as e:
                        logger.debug(f"    选择器 {selector} 获取HTML失败: {str(e)}")
                        continue
                
               
                
                # 保存转换后的Markdown内容
                details['readme'] = readme_content
                
                # 同时保存原始HTML (可选)
                details['readme_html'] = readme_html
            except Exception as e:
                logger.warning(f"    提取README内容时出错: {e}")
                # 如果html2text模块不可用，提示安装
                if "html2text" in str(e):
                    logger.error("请安装html2text模块: pip install html2text")
            
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
        
        # 检查是否是跳过详情的工作流
        if workflow_data.get('skipped_details'):
            logger.info(f"  跳过保存已存在的工作流: {workflow_data.get('title', '')}")
            return True  # 视为成功处理
        
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
    
    async def run(self, max_workflows_per_category: int = None, use_hardcoded_categories: bool = False):
        """
        运行爬虫
        
        Args:
            max_workflows_per_category: 每个分类最多爬取的工作流程数量，None 表示不限制
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
            self.save_workflows_to_file(categories, filename="workflow/n8n_categories.json")
            
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
    
    def workflow_file_exists(self, category_name: str, workflow_url: str, title: str) -> bool:
        """
        检查工作流文件是否已经存在
        
        Args:
            category_name: 分类名称
            workflow_url: 工作流URL（用于提取ID）
            title: 工作流标题
            
        Returns:
            文件是否已存在
        """
        # 从URL中提取工作流ID
        workflow_id = ''
        id_match = re.search(r'/workflows/(\d+)-', workflow_url)
        if id_match:
            workflow_id = id_match.group(1)
        
        # 获取分类目录
        safe_category_name = self.get_safe_dirname(category_name)
        category_dir = os.path.join("data", "workflow", safe_category_name)
        
        # 如果目录不存在，则文件肯定不存在
        if not os.path.exists(category_dir):
            return False
        
        # 1. 首先通过ID检查（最精确的方式）
        if workflow_id:
            for filename in os.listdir(category_dir):
                if filename.startswith(f"{workflow_id}_"):
                    logger.info(f"  通过ID找到已存在的文件: {os.path.join(category_dir, filename)}")
                    return True
        
        # 2. 通过标题进行模糊匹配（备用方式）
        safe_title = self.get_safe_dirname(title)
        if len(safe_title) > 100:
            safe_title = safe_title[:100]
        
        for filename in os.listdir(category_dir):
            if safe_title in filename:
                logger.info(f"  通过标题模糊匹配找到已存在的文件: {os.path.join(category_dir, filename)}")
                return True
                
        return False


async def main():
    """
    主函数
    """
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='n8n 工作流爬虫')
    parser.add_argument('--headless', action='store_true', help='使用无头模式')
    # 将默认值改为 None 表示不限制数量
    parser.add_argument('--max-workflows', type=int, default=None, help='每个分类最多爬取的工作流程数量 (默认: 不限制)')
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