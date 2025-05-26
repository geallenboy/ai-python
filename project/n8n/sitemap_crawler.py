## # 爬取所有工作流（默认行为）
## python sitemap_crawler.py

# 爬取指定数量的工作流
## python sitemap_crawler.py --count 10

# 使用无头模式爬取所有工作流
## python sitemap_crawler.py --headless

# 强制重新爬取所有工作流
# python sitemap_crawler.py --force

# 强制重新爬取前10个工作流
# python sitemap_crawler.py --count 10 --force

import asyncio
import aiohttp
import json
import time
import random
import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Set
from playwright.async_api import async_playwright
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from datetime import datetime

class SitemapCrawler:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.setup_logging()
        self.ensure_data_dir()
        self.crawled_urls = self.load_crawled_urls()  # 加载已爬取的URL
    
    def setup_logging(self):
        """设置日志系统"""
        # 确保日志目录存在
        logs_dir = Path("data/newworkflow/logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置日志
        log_file = logs_dir / "sitemap_crawler.log"
        
        # 配置日志格式
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 清除已有处理器
        for handler in self.logger.handlers:
            self.logger.removeHandler(handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, 'a', 'utf-8')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def ensure_data_dir(self):
        """确保数据目录存在"""
        data_dir = Path("data/newworkflow")
        data_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = data_dir
    
    def load_crawled_urls(self) -> Set[str]:
        """加载已爬取的URL列表"""
        crawled_urls = set()
        
        # 从现有的JSON文件中提取URL
        for json_file in self.data_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'url' in data:
                        crawled_urls.add(data['url'])
            except Exception as e:
                self.logger.warning(f"读取文件 {json_file} 时出错: {e}")
        
        # 从缓存文件加载
        cache_file = self.data_dir / "crawled_urls.txt"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        url = line.strip()
                        if url:
                            crawled_urls.add(url)
            except Exception as e:
                self.logger.warning(f"读取缓存文件时出错: {e}")
        
        self.logger.info(f"已加载 {len(crawled_urls)} 个已爬取的URL")
        return crawled_urls
    
    def save_crawled_url(self, url: str):
        """保存已爬取的URL到缓存"""
        try:
            self.crawled_urls.add(url)
            cache_file = self.data_dir / "crawled_urls.txt"
            with open(cache_file, 'a', encoding='utf-8') as f:
                f.write(f"{url}\n")
        except Exception as e:
            self.logger.warning(f"保存URL缓存时出错: {e}")
    
    def is_url_crawled(self, url: str) -> bool:
        """检查URL是否已被爬取"""
        return url in self.crawled_urls
    
    def filter_new_urls(self, urls: List[str]) -> List[str]:
        """过滤出未爬取的URL"""
        new_urls = []
        skipped_count = 0
        
        for url in urls:
            if not self.is_url_crawled(url):
                new_urls.append(url)
            else:
                skipped_count += 1
                self.logger.debug(f"跳过已爬取的URL: {url}")
        
        self.logger.info(f"过滤结果: {len(new_urls)} 个新URL，跳过 {skipped_count} 个已爬取的URL")
        return new_urls
    
    async def fetch_sitemap(self, sitemap_url: str) -> List[str]:
        """获取 sitemap 中的 URL 列表"""
        self.logger.info(f"开始获取 sitemap: {sitemap_url}")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(sitemap_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        self.logger.info("成功获取 sitemap 内容")
                        
                        # 解析 XML
                        root = ET.fromstring(content)
                        urls = []
                        
                        # 提取所有 URL
                        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                        for url_elem in root.findall('.//ns:url', namespace):
                            loc_elem = url_elem.find('ns:loc', namespace)
                            if loc_elem is not None:
                                url = loc_elem.text
                                if '/workflows/' in url and url not in urls:
                                    urls.append(url)
                        
                        self.logger.info(f"从 sitemap 中找到 {len(urls)} 个工作流 URL")
                        return urls
                    else:
                        self.logger.error(f"获取 sitemap 失败，状态码: {response.status}")
                        return []
            except Exception as e:
                self.logger.error(f"获取 sitemap 时出错: {e}")
                return []
    
    async def setup_browser(self):
        """设置浏览器"""
        self.logger.info("初始化浏览器...")
        playwright = await async_playwright().start()
        
        browser_options = {
            "headless": self.headless,
            "args": [
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-extensions",
                "--disable-notifications"
            ]
        }
        
        self.browser = await playwright.firefox.launch(**browser_options)
        
        context_options = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        self.context = await self.browser.new_context(**context_options)
        self.context.set_default_timeout(60000)
        
        # 拦截资源以提高速度
        await self.context.route("**/*.{png,jpg,jpeg,gif,svg,pdf,woff,woff2}", 
                                lambda route: route.abort())
    
    async def close_browser(self):
        """关闭浏览器"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            self.logger.info("浏览器已关闭")
        except Exception as e:
            self.logger.warning(f"关闭浏览器时出错: {e}")
    
    def parse_relative_date(self, relative_date_str: str) -> str:
        """解析相对日期为绝对日期"""
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
            year = today.year
            month = today.month - months
            while month <= 0:
                year -= 1
                month += 12
            result_date = today.replace(year=year, month=month)
            return result_date.strftime("%Y-%m-%d")
        
        # 处理"yesterday"
        if re.search(r"yesterday", relative_date_str, re.IGNORECASE):
            result_date = today - datetime.timedelta(days=1)
            return result_date.strftime("%Y-%m-%d")
        
        # 处理"today"
        if re.search(r"today", relative_date_str, re.IGNORECASE):
            return today.strftime("%Y-%m-%d")
        
        return ""
    
    async def get_workflow_detail(self, url: str) -> Dict[str, Any]:
        """获取工作流详情页信息"""
        self.logger.info(f"访问详情页: {url}")
        
        try:
            page = await self.context.new_page()
            
            # 访问页面
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(3)
            
            # 初始化详情信息
            details = {
                'url': url,
                'title': '',
                'author': '',
                'publish_date': '',
                'publish_date_absolute': '',
                'categories': [],
                'workflow_json': '',
                'readme': '',
                'crawled_at': datetime.now().isoformat()  # 添加爬取时间戳
            }
            
            # 获取标题
            try:
                title_selectors = [
                    'h1.title--white-violet',
                    'h1',
                    '.title'
                ]
                for selector in title_selectors:
                    title_element = await page.query_selector(selector)
                    if title_element:
                        title = await title_element.text_content()
                        if title and title.strip():
                            details['title'] = title.strip()
                            self.logger.info(f"提取到标题: {details['title']}")
                            break
            except Exception as e:
                self.logger.warning(f"提取标题时出错: {e}")
            
            # 获取作者信息
            try:
                author_selectors = [
                    'a[href^="/creators/"] p.font-geomanist.text-caption-large-medium.text-shades-soft-gray',
                    'a[href^="/creators/"] div p',
                    '.author-name'
                ]
                for selector in author_selectors:
                    author_element = await page.query_selector(selector)
                    if author_element:
                        author_name = await author_element.text_content()
                        if author_name and author_name.strip():
                            details['author'] = author_name.strip()
                            self.logger.info(f"提取到作者: {details['author']}")
                            break
            except Exception as e:
                self.logger.warning(f"提取作者信息时出错: {e}")
            
            # 获取发布日期
            try:
                date_selectors = [
                    'div.group-info p.font-geomanist.text-md'
                ]
                for selector in date_selectors:
                    date_element = await page.query_selector(selector)
                    if date_element:
                        date_text = await date_element.text_content()
                        if date_text and 'update' in date_text.lower():
                            details['publish_date'] = date_text.strip()
                            details['publish_date_absolute'] = self.parse_relative_date(date_text.strip())
                            self.logger.info(f"提取到日期: {details['publish_date']} -> {details['publish_date_absolute']}")
                            break
            except Exception as e:
                self.logger.warning(f"提取日期时出错: {e}")
            
            # 获取分类信息
            try:
                category_selectors = [
                    'div.group-info ul.flex.flex-row.flex-wrap.gap-2 li a',
                    '.group-info ul li a',
                    '.category a'
                ]
                
                categories = []
                for selector in category_selectors:
                    category_elements = await page.query_selector_all(selector)
                    if category_elements:
                        for category_elem in category_elements:
                            category_text = await category_elem.text_content()
                        
                            if category_text and category_text.strip():
                                category_name = category_text.strip()
                                categories.append({
                                    'name': category_name,
                                })
                        
                        if categories:
                            break
                
                # 保存所有分类
                if categories:
                    details['categories'] = categories
                    category_names = [cat['name'] for cat in categories]
                    self.logger.info(f"提取到分类: {category_names}")
                else:
                    details['categories'] = []
                    
            except Exception as e:
                self.logger.warning(f"提取分类信息时出错: {e}")
                details['categories'] = []
            
            # 获取工作流 JSON
            try:
                await page.wait_for_selector('n8n-demo', timeout=10000)
                workflow_json = await page.evaluate('''() => {
                    const element = document.querySelector('n8n-demo');
                    return element ? element.getAttribute('workflow') : '';
                }''')
                
                if workflow_json:
                    details['workflow_json'] = workflow_json
                    self.logger.info(f"成功获取 workflow JSON: {len(workflow_json)} 字符")
            except Exception as e:
                self.logger.warning(f"提取 workflow JSON 时出错: {e}")
            
            # 获取 README 内容
            try:
                readme_selectors = [
                    'div.content-base.text-md',
                    '.readme-content',
                    '.description'
                ]
                
                for selector in readme_selectors:
                    readme_element = await page.query_selector(selector)
                    if readme_element:
                        readme_html = await page.evaluate("""(element) => {
                            return element.innerHTML;
                        }""", readme_element)
                        
                        if readme_html and readme_html.strip():
                            # 简单的 HTML 到文本转换
                            import html2text
                            h2t = html2text.HTML2Text()
                            h2t.ignore_links = False
                            h2t.body_width = 0
                            details['readme'] = h2t.handle(readme_html)
                            self.logger.info(f"成功获取 README: {len(details['readme'])} 字符")
                            break
            except ImportError:
                self.logger.warning("html2text 模块未安装，跳过 README 转换")
            except Exception as e:
                self.logger.warning(f"提取 README 时出错: {e}")
            
            await page.close()
            return details
            
        except Exception as e:
            self.logger.error(f"获取详情页时出错: {e}")
            try:
                await page.close()
            except:
                pass
            return {'url': url, 'error': str(e)}
    
    def save_workflow(self, workflow_data: Dict[str, Any]) -> bool:
        """保存工作流到文件"""
        try:
            title = workflow_data.get('title', '').strip()
            url = workflow_data.get('url', '')
            
            # 从 URL 提取 ID
            workflow_id = ''
            id_match = re.search(r'/workflows/(\d+)-', url)
            if id_match:
                workflow_id = id_match.group(1)
            
            # 创建安全的文件名
            if not title:
                title = f"workflow_{int(time.time())}"
            
            safe_title = "".join([c if c.isalnum() or c == ' ' else '_' for c in title])
            safe_title = safe_title.replace(' ', '_')[:100]
            
            # 构造文件名
            if workflow_id:
                filename = f"{workflow_id}_{safe_title}.json"
            else:
                filename = f"{safe_title}_{int(time.time())}.json"
            
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(workflow_data, f, ensure_ascii=False, indent=2)
            
            # 保存URL到缓存
            self.save_crawled_url(url)
            
            self.logger.info(f"已保存工作流: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存工作流时出错: {e}")
            return False
    
    async def crawl_workflows(self, sitemap_url: str, max_count: int = None, force_recrawl: bool = False):
        """爬取工作流"""
        if max_count is None:
            self.logger.info("开始爬取所有工作流")
        else:
            self.logger.info(f"开始爬取工作流，最多 {max_count} 个")
        
        try:
            # 获取 sitemap 中的 URL
            urls = await self.fetch_sitemap(sitemap_url)
            
            if not urls:
                self.logger.error("未能获取到任何 URL")
                return
            
            # 过滤已爬取的URL（除非强制重新爬取）
            if not force_recrawl:
                original_count = len(urls)
                urls = self.filter_new_urls(urls)
                if not urls:
                    self.logger.info("所有URL都已被爬取，无需重新获取")
                    return
                self.logger.info(f"从 {original_count} 个URL中过滤出 {len(urls)} 个新URL")
            
            # 限制爬取数量（如果指定了的话）
            if max_count is not None:
                urls = urls[:max_count]
                
            self.logger.info(f"将爬取以下 {len(urls)} 个工作流:")
            for i, url in enumerate(urls, 1):
                self.logger.info(f"{i}. {url}")
            
            # 设置浏览器
            await self.setup_browser()
            
            # 爬取每个工作流
            successful_count = 0
            for i, url in enumerate(urls, 1):
                self.logger.info(f"\n[{i}/{len(urls)}] 开始爬取: {url}")
                
                try:
                    # 获取详情
                    workflow_data = await self.get_workflow_detail(url)
                    
                    if workflow_data and 'error' not in workflow_data:
                        # 保存到文件
                        if self.save_workflow(workflow_data):
                            successful_count += 1
                            self.logger.info(f"成功处理工作流: {workflow_data.get('title', 'Unknown')}")
                        else:
                            self.logger.error(f"保存失败: {url}")
                    else:
                        self.logger.error(f"获取详情失败: {url}")
                    
                    # 随机延迟
                    if i < len(urls):
                        delay = random.uniform(2, 4)
                        self.logger.info(f"等待 {delay:.2f} 秒...")
                        await asyncio.sleep(delay)
                
                except Exception as e:
                    self.logger.error(f"处理工作流 {url} 时出错: {e}")
            
            self.logger.info(f"\n爬取完成! 成功处理 {successful_count}/{len(urls)} 个工作流")
            
        finally:
            await self.close_browser()

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='N8N Sitemap 爬虫')
    parser.add_argument('--sitemap', 
                       default='https://n8n.io/sitemap-workflows.xml',
                       help='Sitemap URL')
    parser.add_argument('--count', type=int, default=None,
                       help='爬取的工作流数量 (默认: 爬取所有)')
    parser.add_argument('--headless', action='store_true',
                       help='使用无头模式')
    parser.add_argument('--force', action='store_true',
                       help='强制重新爬取已存在的工作流')
    
    args = parser.parse_args()
    
    # 创建爬虫实例
    crawler = SitemapCrawler(headless=args.headless)
    
    # 开始爬取
    await crawler.crawl_workflows(args.sitemap, args.count, args.force)

if __name__ == "__main__":
    asyncio.run(main())