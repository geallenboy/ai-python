#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
该脚本用于爬取 https://blog.n8n.io/sitemap-posts.xml 中的博客文章，
并保存到 data/posts 目录下的 JSON 文件中。
# 爬取所有博客文章
python posts.py

# 爬取指定数量的文章
python posts.py --count 10

# 使用无头模式
python posts.py --headless

# 强制重新爬取
python posts.py --force
"""

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

class BlogPostsCrawler:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.setup_logging()
        self.ensure_data_dir()
        self.crawled_urls = self.load_crawled_urls()
    
    def setup_logging(self):
        """设置日志系统"""
        # 确保日志目录存在
        logs_dir = Path("data/posts/logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置日志
        log_file = logs_dir / "posts_crawler.log"
        
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
        data_dir = Path("data/posts")
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
                                # 过滤博客文章URL（通常包含日期格式）
                                if url and ('blog.n8n.io' in url and url not in urls):
                                    urls.append(url)
                        
                        self.logger.info(f"从 sitemap 中找到 {len(urls)} 个博客文章 URL")
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
    
    async def get_post_detail(self, url: str) -> Dict[str, Any]:
        """获取博客文章详情页信息"""
        self.logger.info(f"访问博客文章: {url}")
        
        try:
            page = await self.context.new_page()
            
            # 访问页面
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(3)
            
            # 初始化详情信息
            details = {
                'url': url,
                'title': '',
                'excerpt': '',
                'thumbnail': '',
                'tags': [],
                'html': '',
                'readme': '',
                'crawled_at': datetime.now().isoformat()
            }
            
            # 获取标题
            try:
                title_selectors = [
                    '.item-content .item-title',
                    'h1.item-title',
                    'h1',
                    '.post-title'
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
            
            # 获取简介
            try:
                excerpt_selectors = [
                    '.item-content .item-excerpt',
                    '.post-excerpt',
                    '.excerpt'
                ]
                for selector in excerpt_selectors:
                    excerpt_element = await page.query_selector(selector)
                    if excerpt_element:
                        excerpt = await excerpt_element.text_content()
                        if excerpt and excerpt.strip():
                            details['excerpt'] = excerpt.strip()
                            self.logger.info(f"提取到简介: {details['excerpt'][:100]}...")
                            break
            except Exception as e:
                self.logger.warning(f"提取简介时出错: {e}")
            
            # 获取缩略图
            try:
                thumbnail_selectors = [
                    '.item-container .item-image img',
                    '.post-image img',
                    '.featured-image img'
                ]
                for selector in thumbnail_selectors:
                    img_element = await page.query_selector(selector)
                    if img_element:
                        src = await img_element.get_attribute('src')
                        if src:
                            # 处理相对路径，添加前缀
                            if src.startswith('/'):
                                details['thumbnail'] = f"https://blog.n8n.io{src}"
                            elif src.startswith('http'):
                                details['thumbnail'] = src
                            else:
                                details['thumbnail'] = f"https://blog.n8n.io/{src}"
                            self.logger.info(f"提取到缩略图: {details['thumbnail']}")
                            break
            except Exception as e:
                self.logger.warning(f"提取缩略图时出错: {e}")
            
            # 获取标签
            try:
                tag_selectors = [
                    '.item-content .item-tags a',
                    '.post-tags a',
                    '.tags a'
                ]
                
                tags = []
                for selector in tag_selectors:
                    tag_elements = await page.query_selector_all(selector)
                    if tag_elements:
                        for tag_elem in tag_elements:
                            tag_text = await tag_elem.text_content()
                            if tag_text and tag_text.strip():
                                tags.append(tag_text.strip())
                        
                        if tags:
                            break
                
                details['tags'] = tags
                if tags:
                    self.logger.info(f"提取到标签: {tags}")
                    
            except Exception as e:
                self.logger.warning(f"提取标签时出错: {e}")
                details['tags'] = []
            
            # 获取文章HTML内容
            try:
                html_selectors = [
                    '.post-content',
                    '.content',
                    '.article-content',
                    'article'
                ]
                
                for selector in html_selectors:
                    content_element = await page.query_selector(selector)
                    if content_element:
                        html_content = await page.evaluate("""(element) => {
                            return element.innerHTML;
                        }""", content_element)
                        
                        if html_content and html_content.strip():
                            details['html'] = html_content.strip()
                            self.logger.info(f"成功获取 HTML 内容: {len(details['html'])} 字符")
                            break
            except Exception as e:
                self.logger.warning(f"提取 HTML 内容时出错: {e}")
            
            # 将HTML转换为Markdown格式
            try:
                if details['html']:
                    try:
                        import html2text
                        h2t = html2text.HTML2Text()
                        h2t.ignore_links = False
                        h2t.body_width = 0
                        h2t.ignore_images = False
                        details['readme'] = h2t.handle(details['html'])
                        self.logger.info(f"成功转换为 Markdown: {len(details['readme'])} 字符")
                    except ImportError:
                        self.logger.warning("html2text 模块未安装，跳过 Markdown 转换")
                        # 简单的HTML标签清理作为备选方案
                        import re
                        text = re.sub(r'<[^>]+>', '', details['html'])
                        details['readme'] = text.strip()
            except Exception as e:
                self.logger.warning(f"转换 Markdown 时出错: {e}")
            
            await page.close()
            return details
            
        except Exception as e:
            self.logger.error(f"获取博客文章详情时出错: {e}")
            try:
                await page.close()
            except:
                pass
            return {'url': url, 'error': str(e)}
    
    def save_post(self, post_data: Dict[str, Any]) -> bool:
        """保存博客文章到文件"""
        try:
            title = post_data.get('title', '').strip()
            url = post_data.get('url', '')
            
            # 从 URL 提取文章标识符
            post_id = ''
            # 尝试从URL中提取日期和标题作为ID
            url_parts = url.split('/')
            if len(url_parts) > 0:
                post_id = url_parts[-1] if url_parts[-1] else url_parts[-2]
            
            # 创建安全的文件名
            if not title:
                title = f"post_{int(time.time())}"
            
            safe_title = "".join([c if c.isalnum() or c == ' ' else '_' for c in title])
            safe_title = safe_title.replace(' ', '_')[:100]
            
            # 构造文件名
            if post_id:
                filename = f"{post_id}_{safe_title}.json"
            else:
                filename = f"{safe_title}_{int(time.time())}.json"
            
            # 清理文件名中的特殊字符
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(post_data, f, ensure_ascii=False, indent=2)
            
            # 保存URL到缓存
            self.save_crawled_url(url)
            
            self.logger.info(f"已保存博客文章: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存博客文章时出错: {e}")
            return False
    
    async def crawl_posts(self, sitemap_url: str, max_count: int = None, force_recrawl: bool = False):
        """爬取博客文章"""
        if max_count is None:
            self.logger.info("开始爬取所有博客文章")
        else:
            self.logger.info(f"开始爬取博客文章，最多 {max_count} 篇")
        
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
                
            self.logger.info(f"将爬取以下 {len(urls)} 篇博客文章:")
            for i, url in enumerate(urls, 1):
                self.logger.info(f"{i}. {url}")
            
            # 设置浏览器
            await self.setup_browser()
            
            # 爬取每篇文章
            successful_count = 0
            for i, url in enumerate(urls, 1):
                self.logger.info(f"\n[{i}/{len(urls)}] 开始爬取: {url}")
                
                try:
                    # 获取详情
                    post_data = await self.get_post_detail(url)
                    
                    if post_data and 'error' not in post_data:
                        # 保存到文件
                        if self.save_post(post_data):
                            successful_count += 1
                            self.logger.info(f"成功处理博客文章: {post_data.get('title', 'Unknown')}")
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
                    self.logger.error(f"处理博客文章 {url} 时出错: {e}")
            
            self.logger.info(f"\n爬取完成! 成功处理 {successful_count}/{len(urls)} 篇博客文章")
            
        finally:
            await self.close_browser()

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='N8N 博客文章爬虫')
    parser.add_argument('--sitemap', 
                       default='https://blog.n8n.io/sitemap-posts.xml',
                       help='Sitemap URL')
    parser.add_argument('--count', type=int, default=None,
                       help='爬取的文章数量 (默认: 爬取所有)')
    parser.add_argument('--headless', action='store_true',
                       help='使用无头模式')
    parser.add_argument('--force', action='store_true',
                       help='强制重新爬取已存在的文章')
    
    args = parser.parse_args()
    
    # 创建爬虫实例
    crawler = BlogPostsCrawler(headless=args.headless)
    
    # 开始爬取
    await crawler.crawl_posts(args.sitemap, args.count, args.force)

if __name__ == "__main__":
    asyncio.run(main())