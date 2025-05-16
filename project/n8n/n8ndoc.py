#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
n8ndoc.py - A web scraper for n8n documentation

This script crawls the n8n official documentation site (https://docs.n8n.io/),
extracts content, converts it to markdown, and saves it to the local file system
while maintaining the original URL path structure.

Usage:
    python n8ndoc.py [--start-url URL] [--output-dir DIR]

Example:
    python n8ndoc.py --start-url https://docs.n8n.io/integrations/ --output-dir ./data/integrations/
"""

import os
import re
import argparse
import logging
import time
from typing import Set, Union, List
from urllib.parse import urljoin, urlparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import html2text

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("n8ndoc.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 用户代理设置，让服务器认为我们是真实浏览器
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

# HTML转Markdown配置
html2md = html2text.HTML2Text()
html2md.ignore_links = False
html2md.ignore_images = False
html2md.ignore_emphasis = False
html2md.body_width = 0  # 不自动换行


class N8nDocScraper:
    """
    用于爬取n8n文档网站的爬虫类
    """
    
    def __init__(self, base_url: str, output_dir: str, delay: float = 1.0):
        """
        初始化爬虫
        
        Args:
            base_url: 基础URL (如 https://docs.n8n.io/)
            output_dir: 输出目录路径
            delay: 请求间隔时间（秒）
        """
        self.base_url = base_url.rstrip("/")
        self.output_dir = Path(output_dir)
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.base_domain = urlparse(base_url).netloc
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"初始化爬虫: {base_url} -> {output_dir}")
    
    def is_valid_url(self, url: str) -> bool:
        """
        检查URL是否有效并且属于目标域名
        
        Args:
            url: 要检查的URL
            
        Returns:
            bool: 如果URL有效且属于目标域名则返回True
        """
        parsed = urlparse(url)
        
        # 检查是否是相同域名
        if parsed.netloc and parsed.netloc != self.base_domain:
            return False
        
        # 确保链接是指向文档页面的，不是API、图片等资源
        if any(ext in url for ext in ['.jpg', '.png', '.gif', '.pdf', '.zip', '.js', '.css']):
            return False
            
        # 确保链接是以基础URL开头的
        full_url = urljoin(self.base_url, url)
        if not full_url.startswith(self.base_url):
            return False
            
        return True
    
    def normalize_url(self, url: str) -> str:
        """
        规范化URL
        
        Args:
            url: 输入URL
            
        Returns:
            str: 规范化后的URL
        """
        # 处理相对URL
        full_url = urljoin(self.base_url, url)
        
        # 移除URL中的锚点
        full_url = full_url.split('#')[0]
        
        # 确保URL以/结尾
        if not full_url.endswith('/') and '.' not in os.path.basename(full_url):
            full_url += '/'
            
        return full_url
    
    def url_to_filepath(self, url: str) -> Path:
        """
        将URL转换为本地文件路径
        
        Args:
            url: 网页URL
            
        Returns:
            Path: 对应的本地文件路径
        """
        # 从URL中提取路径部分
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        
        if not path:
            # 如果是根路径，使用index.md
            return self.output_dir / 'index.md'
        
        # 创建目录结构
        dir_path = self.output_dir / path
        
        # 如果URL以/结尾，表示是目录，则文件名为index.md
        if url.endswith('/'):
            return dir_path / 'index.md'
        
        # 如果没有扩展名，添加.md扩展名
        filename = os.path.basename(path)
        if '.' not in filename:
            return dir_path.with_suffix('.md')
        
        # 如果已有扩展名，将其替换为.md
        return Path(str(dir_path).rsplit('.', 1)[0] + '.md')
    
    def save_content(self, url: str, content: str) -> None:
        """
        将内容保存到文件
        
        Args:
            url: 网页URL
            content: 要保存的内容
        """
        filepath = self.url_to_filepath(url)
        
        # 创建必要的目录
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
            logger.info(f"已保存: {url} -> {filepath}")
        except Exception as e:
            logger.error(f"保存文件失败 {filepath}: {e}")
    
    def extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """
        从HTML中提取链接
        
        Args:
            soup: BeautifulSoup对象
            current_url: 当前页面的URL
            
        Returns:
            List[str]: 提取的链接列表
        """
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # 忽略空链接和javascript链接
            if not href or href.startswith('javascript:'):
                continue
                
            # 规范化URL
            full_url = self.normalize_url(href)
            
            # 检查是否是有效URL
            if self.is_valid_url(full_url) and full_url not in self.visited_urls:
                links.append(full_url)
                
        return links
    
    def process_page(self, url: str) -> Union[List[str], None]:
        """
        处理单个页面
        
        Args:
            url: 要处理的页面URL
            
        Returns:
            Union[List[str], None]: 页面中的链接列表，如果处理失败则返回None
        """
        logger.info(f"处理页面: {url}")
        
        # 将URL标记为已访问
        self.visited_urls.add(url)
        
        try:
            # 发送HTTP请求
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取主要内容
            main_content = soup.find('main') or soup.find('div', class_=re.compile(r'content|main|document|article'))
            
            if main_content:
                # 将HTML转换为Markdown
                markdown_content = html2md.handle(str(main_content))
                
                # 提取标题
                title = soup.title.string if soup.title else "无标题"
                
                # 添加页面标题和源URL作为元数据
                full_content = f"""---
title: {title}
source_url: {url}
---

{markdown_content}
"""
                # 保存内容
                self.save_content(url, full_content)
                
                # 提取链接并返回
                return self.extract_links(soup, url)
            else:
                logger.warning(f"未找到主要内容区域: {url}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"请求错误 {url}: {e}")
        except Exception as e:
            logger.error(f"处理页面失败 {url}: {e}")
            
        return None
    
    def crawl(self, start_url: str) -> None:
        """
        从指定的URL开始爬取
        
        Args:
            start_url: 起始URL
        """
        # 规范化起始URL
        start_url = self.normalize_url(start_url)
        
        # 待爬取的URL队列
        queue = [start_url]
        
        while queue:
            # 获取下一个URL
            current_url = queue.pop(0)
            
            # 如果已经访问过，跳过
            if current_url in self.visited_urls:
                continue
                
            # 处理页面并获取新链接
            new_links = self.process_page(current_url)
            
            # 如果成功处理，将新链接添加到队列
            if new_links:
                for link in new_links:
                    if link not in self.visited_urls and link not in queue:
                        queue.append(link)
            
            # 延迟一段时间，避免请求过于频繁
            time.sleep(self.delay)
            
        logger.info(f"爬取完成，共处理 {len(self.visited_urls)} 个页面")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='n8n文档爬虫')
    parser.add_argument('--start-url', default='https://docs.n8n.io/integrations/', 
                        help='起始URL(默认: https://docs.n8n.io/integrations/)')
    parser.add_argument('--output-dir', default='./data/integrations/', 
                        help='输出目录(默认: ./data/integrations/)')
    parser.add_argument('--delay', type=float, default=1.0,
                        help='请求间隔时间，秒(默认: 1.0)')
    
    args = parser.parse_args()
    
    try:
        # 创建并运行爬虫
        scraper = N8nDocScraper(
            base_url='https://docs.n8n.io/',
            output_dir=args.output_dir,
            delay=args.delay
        )
        
        # 开始爬取
        scraper.crawl(args.start_url)
        
        logger.info("爬取完成！")
        
    except KeyboardInterrupt:
        logger.info("用户中断，正在退出...")
    except Exception as e:
        logger.error(f"发生错误: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())