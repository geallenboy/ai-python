import os
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import logging
import html2text
import traceback

# 创建日志目录
os.makedirs("logs", exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/hosting.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class N8nDocumentationScraper:
    def __init__(self):
        self.base_url = "https://docs.n8n.io/hosting/"
        self.output_dir = "data/hosting"
        self.visited_urls = set()
        self.menu_structure = {}
        
        # 配置Selenium - 增强配置
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # 使用新的无头模式
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")  # 设置窗口大小
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
        
        # 使用webdriver_manager自动管理ChromeDriver
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            self.driver.set_page_load_timeout(30)  # 设置页面加载超时
        except Exception as e:
            logger.error(f"初始化ChromeDriver时出错: {str(e)}")
            # 尝试直接初始化
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                logger.error(f"备选初始化ChromeDriver失败: {str(e)}")
                raise
                
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.body_width = 0  # 不自动换行
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
    def clean_filename(self, name):
        """将菜单名转换为合法的文件名或文件夹名"""
        # 移除非法字符并替换空格
        clean_name = re.sub(r'[\\/*?:"<>|]', '', name)
        clean_name = clean_name.replace(' ', '-').lower()
        # 确保文件名不为空
        if not clean_name:
            clean_name = "unnamed"
        return clean_name
    
    def extract_menu_items(self):
        """提取左侧菜单结构"""
        logger.info("开始提取左侧菜单结构...")
        
        try:
            self.driver.get(self.base_url)
            logger.info("已加载页面，等待菜单元素...")
            
            # 等待菜单加载完成 - 增加等待时间和错误处理
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".sidebar-nav, .sidebar, nav.sidebar"))
                )
                logger.info("菜单元素已找到")
            except Exception as e:
                logger.warning(f"等待菜单元素超时: {str(e)}")
                logger.info("尝试继续执行...")
            
            # 给页面足够的时间加载
            time.sleep(5)
            
            # 记录当前页面源码以便调试
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.info("已保存页面源码用于调试")
            
            # 尝试采用不同的菜单选择器
            selectors = [".sidebar-nav", ".sidebar", "nav.sidebar", ".menu", "nav", "#sidebar"]
            sidebar = None
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            for selector in selectors:
                sidebar_element = soup.select_one(selector)
                if sidebar_element:
                    logger.info(f"找到菜单元素使用选择器: {selector}")
                    sidebar = sidebar_element
                    break
            
            if not sidebar:
                # 如果没找到明确的菜单，尝试分析页面上所有链接
                logger.warning("无法找到明确的菜单结构，尝试分析页面链接...")
                menu_items = self._extract_links_as_menu(soup)
                return menu_items
            
            # 展开所有菜单项
            self._expand_all_menus()
            
            # 重新获取页面源码
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 使用找到的选择器重新获取菜单
            for selector in selectors:
                sidebar = soup.select_one(selector)
                if sidebar:
                    break
            
            # 提取菜单结构
            menu_items = []
            self._extract_menu_recursive(sidebar, menu_items, 0)
            
            logger.info(f"成功提取 {len(menu_items)} 个菜单项")
            return menu_items
            
        except Exception as e:
            logger.error(f"提取菜单时出错: {str(e)}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            # 尝试返回一个空列表而不是抛出异常
            return []
    
    def _extract_links_as_menu(self, soup):
        """从页面中提取所有链接作为菜单项的备选方案"""
        menu_items = []
        base_links = []
        processed_urls = set()  # 防止重复处理相同的URL
        
        # 寻找所有链接，但排除外部链接和锚点链接
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            title = link.get_text(strip=True)
            
            # 只考虑内部链接且有文本内容的链接
            if href and title and not href.startswith(('http', 'www', 'mailto:', 'tel:', '#')):
                # 构建完整URL
                full_url = urljoin(self.base_url, href)
                
                # 跳过已处理的URL
                if full_url in processed_urls:
                    continue
                
                processed_urls.add(full_url)
                
                item = {
                    'title': title,
                    'url': full_url,
                    'level': 0,
                    'children': []
                }
                
                base_links.append(item)
    
        # 简化版：不尝试构建复杂的层级关系，只按URL路径长度排序
        base_links.sort(key=lambda x: len(x['url']))
        
        # 只返回链接，不构建层级关系
        menu_items = base_links
        logger.info(f"通过链接分析提取了 {len(menu_items)} 个菜单项")
        return menu_items
    
    def _build_menu_hierarchy(self, url_segments, parent_items, depth=0):
        """根据URL路径构建菜单层级关系"""
        # 添加递归深度限制
        if depth > 3:  # 最多允许3层嵌套
            return
            
        for parent in parent_items:
            url_path = parent['url'].replace(self.base_url, "").strip("/")
            # 查找此路径下的子项
            children = url_segments.get(url_path, [])
            if children:
                parent['children'] = children
                # 递归处理子项
                self._build_menu_hierarchy(url_segments, children, depth + 1)
    
    def _expand_all_menus(self):
        """尝试展开所有折叠的菜单项"""
        try:
            # 尝试多种可能的菜单项选择器
            selectors = [
                ".sidebar-nav .section-link", 
                ".sidebar-nav .sidebar-heading",
                ".sidebar .collapsible",
                "nav.sidebar .submenu-button",
                ".sidebar button",
                ".sidebar .dropdown",
                ".sidebar details summary",  # 新增: details/summary折叠元素
                ".sidebar .arrow",          # 常见的展开/折叠箭头
                ".sidebar [aria-expanded]"   # 具有aria-expanded属性的元素
            ]
            
            for selector in selectors:
                try:
                    collapsible_items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    logger.info(f"找到 {len(collapsible_items)} 个可能的折叠菜单项 (选择器: {selector})")
                    
                    for item in collapsible_items:
                        try:
                            # 检查是否可点击且可见
                            if item.is_displayed() and item.is_enabled():
                                self.driver.execute_script("arguments[0].click();", item)  # 使用JS点击，更可靠
                                time.sleep(0.3)  # 给予更多时间展开
                        except Exception as e:
                            # 忽略单个点击错误
                            pass
                except Exception as e:
                    logger.debug(f"使用选择器 {selector} 查找菜单项时出错: {str(e)}")
                    
            # 等待更长时间确保展开完成
            time.sleep(2)
            
            # 第二次尝试点击，确保所有折叠菜单都被展开
            for selector in selectors:
                try:
                    collapsible_items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for item in collapsible_items:
                        try:
                            if item.is_displayed() and item.is_enabled():
                                self.driver.execute_script("arguments[0].click();", item)
                        except:
                            pass
                except:
                    pass
            
        except Exception as e:
            logger.warning(f"展开菜单时出错: {str(e)}")
    
    def _extract_menu_recursive(self, element, menu_items, level):
        """递归提取菜单结构"""
        if not element:
            return
        
        # 尝试多种可能的链接选择器
        link_selectors = ['a.sidebar-link', 'a', 'a.nav-link']
        links = []
        
        for selector in link_selectors:
            links = element.select(selector)
            if links:
                logger.debug(f"使用选择器 {selector} 找到 {len(links)} 个链接")
                break
        
        for link in links:
            href = link.get('href', '')
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
                
            title = link.get_text(strip=True)
            if not title:
                continue
                
            # 构建完整URL
            full_url = urljoin(self.base_url, href)
            
            menu_item = {
                'title': title,
                'url': full_url,
                'level': level,
                'children': []
            }
            
            menu_items.append(menu_item)
            
            # 查找此菜单项的子菜单
            # 尝试多种可能的子菜单选择器
            child_found = False
            parent = link.parent
            
            if parent:
                # 尝试多种可能的子菜单容器选择器
                child_selectors = ['ul', 'div.children', '.submenu']
                for selector in child_selectors:
                    next_sibling = parent.find_next_sibling(selector)
                    if next_sibling:
                        self._extract_menu_recursive(next_sibling, menu_item['children'], level + 1)
                        child_found = True
                        break
                
                if not child_found:
                    # 尝试查找子元素中的子菜单
                    for selector in child_selectors:
                        child = parent.select_one(selector)
                        if child:
                            self._extract_menu_recursive(child, menu_item['children'], level + 1)
                            break
    
    def scrape_page_content(self, url):
        """抓取页面的右侧内容"""
        if url in self.visited_urls:
            return None
            
        self.visited_urls.add(url)
        logger.info(f"抓取页面: {url}")
        
        try:
            self.driver.get(url)
            logger.info(f"已加载页面: {url}")
            
            # 等待页面加载 - 使用更基本的方法
            time.sleep(5)  # 直接等待5秒确保页面加载
            
            # 解析页面
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 尝试多个内容选择器，优先级从高到低
            content_selectors = [
                "main", 
                ".content", 
                "article", 
                ".theme-default-content", 
                ".article", 
                ".doc-content", 
                "#content"
            ]
            
            # 提取右侧内容区域 - 尝试多个选择器
            content_div = None
            for selector in content_selectors:
                content_div = soup.select_one(selector)
                if content_div:
                    logger.info(f"使用选择器 {selector} 找到内容")
                    break
            
            # 如果都没找到，使用body作为内容，但移除header和footer
            if not content_div:
                logger.warning(f"在页面 {url} 中找不到明确的内容区域，使用整个页面体")
                content_div = soup.select_one('body')
                
                # 移除header和footer
                if content_div:
                    for header in content_div.select('header'):
                        header.decompose()
                    for footer in content_div.select('footer'):
                        footer.decompose()
                    
            if not content_div:
                logger.error(f"无法提取页面 {url} 的内容")
                return None
                
            # 移除不需要的元素
            for selector in ['.page-nav', '.edit-link', 'script', '.ads', 'nav', 'footer', '.footer', '.sidebar', 'header']:
                for element in content_div.select(selector):
                    element.decompose()
                
            # 将HTML转换为Markdown
            markdown_content = self.html_converter.handle(str(content_div))
            
            return markdown_content
            
        except Exception as e:
            logger.error(f"抓取页面 {url} 时出错: {str(e)}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            return None
    
    def save_to_markdown(self, title, content, path=""):
        """将内容保存为Markdown文件，按照层级创建目录"""
        if not content:
            return
    
        # 创建保存目录
        dir_path = os.path.join(self.output_dir, path)
        os.makedirs(dir_path, exist_ok=True)
    
        filename = self.clean_filename(title)
        filepath = os.path.join(dir_path, f"{filename}.md")
    
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # 添加标题
                f.write(f"# {title}\n\n")
                f.write(content)
                
            relative_path = os.path.relpath(filepath, self.output_dir)
            logger.info(f"已保存: {filepath} (相对路径: {relative_path})")
            return filepath
            
        except Exception as e:
            logger.error(f"保存文件 {filepath} 时出错: {str(e)}")
            return None
    
    def create_index_file(self, menu_items, path=""):
        """在每个目录中创建索引文件，列出所有子项"""
        if not menu_items:
            return
        
        dir_path = os.path.join(self.output_dir, path)
        os.makedirs(dir_path, exist_ok=True)
        
        index_path = os.path.join(dir_path, "README.md")
        dir_title = os.path.basename(path) if path else "n8n 文档索引"
        dir_title = dir_title.replace("-", " ").title()
        
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(f"# {dir_title}\n\n")
                f.write("## 目录\n\n")
                
                for item in menu_items:
                    item_filename = self.clean_filename(item['title'])
                    if item['children']:
                        # 对于有子项的条目，链接到子目录
                        rel_path = f"{item_filename}/"
                    else:
                        # 对于没有子项的条目，链接到Markdown文件
                        rel_path = f"{item_filename}.md"
                    
                    f.write(f"- [{item['title']}]({rel_path})\n")
                
            logger.info(f"已创建索引文件: {index_path}")
            
        except Exception as e:
            logger.error(f"创建索引文件 {index_path} 时出错: {str(e)}")
    
    def process_menu_items(self, menu_items, path=""):
        """处理菜单项列表，抓取内容并保存，同时创建目录结构"""
        # 为当前级别创建索引文件
        self.create_index_file(menu_items, path)
        
        level_info = f"路径: '{path}'" if path else "根级别"
        logger.info(f"处理 {len(menu_items)} 个菜单项（{level_info}）")
        
        for item in menu_items:
            title = item['title']
            url = item['url']
            clean_title = self.clean_filename(title)
            
            # 有子菜单时，创建子目录
            if item['children']:
                # 创建子目录
                sub_dir = os.path.join(path, clean_title)
                logger.info(f"创建子目录: {sub_dir} (标题: {title})")
                
                # 抓取当前项内容作为子目录的首页
                content = self.scrape_page_content(url)
                if content:
                    # 保存到子目录的index.md或README.md
                    self.save_to_markdown("首页", content, sub_dir)
            
                # 递归处理子菜单
                self.process_menu_items(item['children'], sub_dir)
            else:
                # 没有子菜单时，直接保存内容
                content = self.scrape_page_content(url)
                if content:
                    logger.info(f"保存内容: {title} 到路径: {path}")
                    self.save_to_markdown(title, content, path)
    
    def run(self):
        """运行爬虫"""
        try:
            logger.info("开始爬取 n8n 文档...")
            
            # 尝试多种方法获取菜单项
            menu_items = []
            
            # 方法1: 提取菜单结构
            try:
                logger.info("尝试方法1: 提取菜单结构...")
                menu_items = self.extract_menu_items()
            except Exception as e:
                logger.error(f"方法1失败: {str(e)}")
            
            # 方法2: 如果方法1失败，尝试分析页面链接
            if not menu_items:
                try:
                    logger.info("尝试方法2: 分析页面链接...")
                    self.driver.get(self.base_url)
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    menu_items = self._extract_links_as_menu(soup)
                except Exception as e:
                    logger.error(f"方法2失败: {str(e)}")
                    logger.error(f"错误详情: {traceback.format_exc()}")
            
            # 方法3: 如果前两种方法都失败，使用预定义的基本URL列表
            if not menu_items:
                logger.info("尝试方法3: 使用预定义URL列表...")
                basic_urls = [
                    {"title": "首页", "url": self.base_url, "level": 0, "children": []},
                    {"title": "入门指南", "url": urljoin(self.base_url, "try-it-out/"), "level": 0, "children": []},
                    {"title": "工作流", "url": urljoin(self.base_url, "workflows/"), "level": 0, "children": []},
                    {"title": "节点", "url": urljoin(self.base_url, "integrations/"), "level": 0, "children": []},
                    {"title": "API", "url": urljoin(self.base_url, "api/"), "level": 0, "children": []},
                    {"title": "高级AI", "url": urljoin(self.base_url, "advanced-ai/"), "level": 0, "children": []}
                ]
                menu_items = basic_urls
                logger.info(f"使用预定义的 {len(menu_items)} 个基本URL")
        
            # 处理每个菜单项
            if menu_items:
                flat_menu = self._flatten_menu_items(menu_items)
                logger.info(f"将处理 {len(flat_menu)} 个页面")
                
                # 尝试构建层级结构并保存内容
                try:
                    logger.info("正在构建层级结构并保存内容...")
                    self.process_menu_items(menu_items)
                    logger.info("内容处理完成")
                except Exception as e:
                    logger.error(f"构建层级结构时出错: {str(e)}")
                    logger.error(f"错误详情: {traceback.format_exc()}")
                    
                    # 备选方案：如果层级处理失败，使用平级保存
                    logger.info("尝试使用备选的平级保存方案...")
                    for item in flat_menu:
                        try:
                            content = self.scrape_page_content(item['url'])
                            if content:
                                self.save_to_markdown(item['title'], content)  # 平级保存
                        except Exception as inner_e:
                            logger.error(f"处理页面 {item['url']} 时出错: {str(inner_e)}")
            else:
                logger.error("未能提取到任何菜单项，爬虫终止")
        
            logger.info("文档爬取完成")
            
        except Exception as e:
            logger.error(f"爬虫运行时出错: {str(e)}")
            logger.error(f"错误详情: {traceback.format_exc()}")
            
        finally:
            # 关闭浏览器
            try:
                self.driver.quit()
                logger.info("浏览器已关闭")
            except:
                logger.warning("关闭浏览器时发生错误")

    def _flatten_menu_items(self, menu_items, result=None):
        """将嵌套的菜单项列表展平为一维列表"""
        if result is None:
            result = []
            
        for item in menu_items:
            result.append(item)
            if item.get('children'):
                self._flatten_menu_items(item['children'], result)
                
        return result


if __name__ == "__main__":
    try:
        scraper = N8nDocumentationScraper()
        scraper.run()
    except Exception as e:
        logger.critical(f"程序执行失败: {str(e)}")
        logger.critical(f"错误详情: {traceback.format_exc()}")