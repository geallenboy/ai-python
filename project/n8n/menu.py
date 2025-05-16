import os
import json
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("menu_extractor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class N8nMenuExtractor:
    def __init__(self, base_url, output_path):
        """
        初始化菜单提取器
        
        Args:
            base_url (str): 起始URL
            output_path (str): 输出文件路径
        """
        self.base_url = base_url
        self.output_path = output_path
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    def fetch_page(self, url):
        """
        获取页面内容
        
        Args:
            url (str): 页面URL
            
        Returns:
            str: 页面HTML内容，如果获取失败则返回None
        """
        try:
            logger.info(f"正在获取页面: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"获取页面失败: {url}, 错误: {e}")
            return None
    
    def extract_menu_structure(self, html_content):
        """
        从HTML内容中提取菜单结构，转换为树形JSON结构
        
        Args:
            html_content (str): 包含导航菜单的HTML内容
            
        Returns:
            dict: 包含菜单树形结构的字典
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 找到包含"Hosting n8n"的导航项
        hosting_nav = None
        for nav_item in soup.find_all('li', class_='md-nav__item'):
            if nav_item.find(string=lambda text: text and "Hosting n8n" in text):
                hosting_nav = nav_item
                break
        
        if not hosting_nav:
            logger.error("未找到Hosting n8n导航菜单")
            return {}
        
        # 提取菜单结构
        return self.extract_menu_item(hosting_nav)
    
    def extract_menu_item(self, menu_item):
        """
        递归提取菜单项及其子菜单
        
        Args:
            menu_item (BeautifulSoup): 菜单项的BeautifulSoup对象
            
        Returns:
            dict: 菜单项的结构信息
        """
        result = {}
        
        # 获取当前菜单项的名称和URL
        link = menu_item.find('a', class_='md-nav__link')
        if link:
            # 提取菜单名称，移除多余空白
            name_elem = link.find('span', class_='md-ellipsis')
            if name_elem:
                result['name'] = name_elem.get_text(strip=True)
            else:
                # 尝试直接从链接中获取文本
                result['name'] = link.get_text(strip=True)
            
            # 提取URL
            href = link.get('href', '')
            result['url'] = urljoin(self.base_url, href) if href else ''
        else:
            # 如果没有链接，可能是一个分组标题
            title_span = menu_item.find('span', class_='md-ellipsis')
            if title_span:
                result['name'] = title_span.get_text(strip=True)
                result['url'] = ''
            else:
                # 尝试从任何可用的文本内容中提取名称
                text = menu_item.get_text(strip=True)
                if text:
                    result['name'] = text
                    result['url'] = ''
                else:
                    # 如果无法提取名称，则返回空字典
                    return {}
        
        # 查找子菜单
        sub_nav = menu_item.find('nav', class_='md-nav')
        if sub_nav:
            sub_items = sub_nav.find_all('li', class_='md-nav__item', recursive=False)
            if sub_items:
                result['children'] = []
                for sub_item in sub_items:
                    sub_structure = self.extract_menu_item(sub_item)
                    if sub_structure:  # 只添加非空结构
                        result['children'].append(sub_structure)
        
        return result
    
    def save_menu_structure(self, menu_structure):
        """
        保存菜单结构到JSON文件
        
        Args:
            menu_structure (dict): 菜单结构字典
        """
        # 确保输出目录存在
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # 保存到JSON文件
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(menu_structure, f, ensure_ascii=False, indent=2)
        
        logger.info(f"菜单结构已保存到: {self.output_path}")
    
    def run(self):
        """
        运行菜单提取器
        """
        # 获取页面内容
        html_content = self.fetch_page(self.base_url)
        if not html_content:
            logger.error("无法获取页面内容")
            return
        
        # 提取菜单结构
        menu_structure = self.extract_menu_structure(html_content)
        if not menu_structure:
            logger.error("无法提取菜单结构")
            return
        
        # 保存菜单结构
        self.save_menu_structure(menu_structure)
        logger.info("菜单提取完成")


def main():
    # 创建输出目录
    os.makedirs("./data/hosting", exist_ok=True)
    
    # 初始化菜单提取器
    base_url = "https://docs.n8n.io/hosting/"
    output_path = "./data/hosting/menu_structure.json"
    
    extractor = N8nMenuExtractor(base_url, output_path)
    extractor.run()


if __name__ == "__main__":
    main()