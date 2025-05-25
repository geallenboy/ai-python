#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件夹内容批量翻译工具

该脚本用于将指定文件夹中的所有文件翻译成中文
- 使用DeepSeek模型进行翻译
- 在logs目录中生成日志记录
- 跟踪已翻译的文件，避免重复翻译
"""

import os
import sys
import json
import logging
import hashlib
import time
import argparse
from pathlib import Path
from datetime import datetime
import requests
from tqdm import tqdm
try:
    from dotenv import load_dotenv
except ImportError:
    print("正在安装 python-dotenv...")
    os.system(f"{sys.executable} -m pip install python-dotenv")
    from dotenv import load_dotenv

# 当前脚本所在目录
current_dir = Path(__file__).parent
logs_dir = current_dir / 'logs'
if not logs_dir.exists():
    logs_dir.mkdir(parents=True, exist_ok=True)

# 加载.env文件
env_path = current_dir / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logger_setup = logging.getLogger("setup")
    logger_setup.info(f"已从 {env_path} 加载环境变量")
else:
    print(f"警告: 没有找到 .env 文件: {env_path}")

# 配置日志 - 同时输出到文件和控制台
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建日志文件名，包含当前日期
log_filename = f"file_translation_{datetime.now().strftime('%Y%m%d')}.log"
file_handler = logging.FileHandler(logs_dir / log_filename, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# 控制台处理器 - 输出到控制台
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# 添加处理器到logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 避免输出重复的日志
logger.propagate = False

class DeepSeekTranslator:
    """DeepSeek模型翻译接口封装"""
    
    def __init__(self, api_key=None, api_base="https://api.deepseek.com/v1"):
        """
        初始化翻译器
        
        Args:
            api_key (str, optional): DeepSeek API密钥，如不提供则从环境变量获取
            api_base (str, optional): API基础URL
        """
        # 优先从参数获取API密钥，然后尝试从环境变量获取
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        
        # 如果还是没有获取到密钥，提出明确的错误
        if not self.api_key:
            raise ValueError("未找到DeepSeek API密钥。请通过以下方法提供:\n"
                             "1. 命令行参数: --api-key 或 -k\n"
                             "2. 环境变量: DEEPSEEK_API_KEY\n"
                             "3. .env文件中设置: DEEPSEEK_API_KEY=你的密钥")
        
        if self.api_key:
            logger.info("已成功获取DeepSeek API密钥")
            
        self.api_base = api_base
        self.model = "deepseek-chat"  # 默认使用deepseek-chat模型
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
    def translate(self, text, retries=3, delay=2):
        """
        将文本翻译为中文
        
        Args:
            text (str): 要翻译的文本
            retries (int, optional): 重试次数
            delay (int, optional): 重试间隔（秒）
            
        Returns:
            str: 翻译后的中文文本
        """
        if not text or not text.strip():
            return ""
        
        # 如果文本过长，可能需要分段翻译
        if len(text) > 8000:  # DeepSeek 可能对过长的文本处理较慢
            logger.info(f"文本长度为 {len(text)} 字符，尝试分段翻译")
            chunks = self._split_text(text)
            translated_chunks = []
            for i, chunk in enumerate(chunks):
                logger.info(f"翻译第 {i+1}/{len(chunks)} 段")
                translated_chunk = self.translate(chunk, retries, delay)
                translated_chunks.append(translated_chunk)
            return "\n\n".join(translated_chunks)
        
        prompt = f"""请将以下关于n8n AI编码功能的文档翻译成中文。要求：

1. 保持所有原文的结构和格式，包括标题层级、列表、代码块和图片链接
2. 保留所有技术术语、产品名称和功能名的原文，如"Code node"、"ChatGPT"、"JavaScript"、"n8n"等
3. 代码块内容保持原样不翻译
4. 保留所有URL链接和图片引用不变
5. 对于示例提示词和提示词建议，应当翻译为中文，以便中文用户理解如何编写有效的提示词
6. 对于引用的代码注释，如果代码块中出现，需要翻译成中文
7. 精确翻译功能说明、限制条件和使用说明，确保技术准确性
8. 对于特定的AI概念（如"prompt"），首次出现时可提供中文翻译（如"提示词"），但后续仍使用原文
9. 保持文档的专业性和技术准确性，特别是在描述数据结构和代码功能时
10. 将示例workflow文件名和路径保持不变
11. 对于格式混乱的代码块，请重新组织为正确的代码块格式。例如，当看到类似"This is the JavaScript you need: 1 2 3 4 | const xxx"这样的内容时，应将其重新格式化为标准Markdown代码块：
    ```javascript
    const xxx = ...
    ```

12. 如果表格格式异常或被破坏，请将其重新组织为清晰的表格或适当的文本格式
13. 如果发现明显的排版错误，如标题格式错误、列表缩进不一致等，请在翻译时予以修正
14. 对于不合理的分行或段落划分，请在保持原意的基础上调整为更合理的格式
请翻译整篇文档，保持原文的信息完整性和专业度。

请开始翻译：

{text}"""

        endpoint = f"{self.api_base}/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,  # 较低的温度以确保翻译准确性
            "max_tokens": 4000
        }
        
        for attempt in range(retries):
            try:
                # 增加超时时间到60秒
                response = requests.post(endpoint, headers=self.headers, json=payload, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                translated_text = result["choices"][0]["message"]["content"].strip()
                return translated_text
                
            except Exception as e:
                logger.warning(f"翻译请求失败 (尝试 {attempt+1}/{retries}): {str(e)}")
                if attempt < retries - 1:
                    # 增加延迟，每次重试等待更长时间
                    retry_delay = delay * (attempt + 1)
                    logger.info(f"等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"翻译失败，已达到最大重试次数: {str(e)}")
                    raise
                
    def _split_text(self, text, max_length=4000):
        """
        将长文本分割成较小的块
        
        Args:
            text (str): 要分割的文本
            max_length (int): 每块的最大长度
            
        Returns:
            list: 文本块列表
        """
        # 尝试在段落边界分割
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= max_length:
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += paragraph
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # 如果段落本身超过最大长度，需要进一步分割
                if len(paragraph) > max_length:
                    # 尝试按句子分割
                    sentences = paragraph.replace(". ", ".\n").split("\n")
                    current_chunk = ""
                    
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 <= max_length:
                            if current_chunk:
                                current_chunk += " "
                            current_chunk += sentence
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            
                            # 如果单个句子超过最大长度，直接按长度截断
                            if len(sentence) > max_length:
                                for i in range(0, len(sentence), max_length):
                                    chunks.append(sentence[i:i+max_length])
                                current_chunk = ""
                            else:
                                current_chunk = sentence
                else:
                    current_chunk = paragraph
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
                    

    def translate_markdown(self, markdown_text):
        """
        翻译Markdown文本，保持格式和代码块不变
        
        Args:
            markdown_text (str): Markdown格式文本
            
        Returns:
            str: 翻译后的Markdown文本
        """
        return self.translate(markdown_text)
                    
    def translate_file(self, file_path):
        """
        翻译文件内容
        
        Args:
            file_path (Path): 文件路径
            
        Returns:
            str: 翻译后的内容
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 根据文件类型选择不同的翻译方法
            if file_path.suffix.lower() in ['.md', '.txt']:
                return self.translate_markdown(content)
            else:
                return self.translate(content)
                
        except Exception as e:
            logger.error(f"读取或翻译文件 {file_path} 时出错: {str(e)}")
            raise

class TranslationManager:
    """翻译管理器，负责文件翻译和状态跟踪"""
    
    def __init__(self, source_dir, translator, db_path=None):
        """
        初始化翻译管理器
        
        Args:
            source_dir (Path): 源文件目录
            translator: 翻译器对象
            db_path (Path, optional): 状态数据库路径
        """
        self.source_dir = Path(source_dir)
        self.translator = translator
        
        # 状态数据库，用于跟踪文件翻译状态
        self.db_path = db_path or (current_dir / "translation_state.json")
        self.state_db = self._load_state_db()
        
    def _load_state_db(self):
        """加载状态数据库，如不存在则创建空数据库"""
        if not self.db_path.exists():
            return {}
            
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"加载状态数据库失败，将创建新数据库: {str(e)}")
            return {}
            
    def _save_state_db(self):
        """保存状态数据库"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.state_db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存状态数据库失败: {str(e)}")
            
    def _get_file_hash(self, file_path):
        """计算文件内容的哈希值，用于检测文件是否变化"""
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            return hashlib.md5(file_content).hexdigest()
        except Exception as e:
            logger.error(f"计算文件 {file_path} 哈希值时出错: {str(e)}")
            return None
            
    def _is_file_translated(self, file_path, file_hash):
        """检查文件是否已翻译"""
        rel_path = str(file_path.relative_to(self.source_dir))
        
        # 如果文件记录存在且哈希值匹配，表示已翻译
        if rel_path in self.state_db and self.state_db[rel_path]["hash"] == file_hash:
            return True
        return False
        
    def _update_file_state(self, file_path, file_hash):
        """更新文件翻译状态"""
        rel_path = str(file_path.relative_to(self.source_dir))
        self.state_db[rel_path] = {
            "hash": file_hash,
            "translated_at": datetime.now().isoformat()
        }
        self._save_state_db()
        
    def _should_translate_file(self, file_path):
        """判断文件是否需要翻译"""
        # 只处理特定类型的文件
        valid_extensions = ['.md', '.txt', '.html']
        if file_path.suffix.lower() not in valid_extensions:
            return False
            
        # 计算文件哈希值
        file_hash = self._get_file_hash(file_path)
        if not file_hash:  # 无法计算哈希值，可能是文件读取问题
            return False
            
        # 检查文件是否已翻译
        return not self._is_file_translated(file_path, file_hash)
        
    def _save_translated_file(self, file_path, translated_content):
        """直接在原文件中更新翻译内容，而不是创建新文件"""
        try:
            # 备份原文件
            backup_path = file_path.with_name(f"{file_path.stem}_backup{file_path.suffix}")
            import shutil
            shutil.copy2(file_path, backup_path)
            
            # 直接更新原文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            logger.info(f"已将翻译内容更新到原文件: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"保存翻译内容到原文件 {file_path} 时出错: {str(e)}")
            return None
        
    def _is_content_already_translated(self, content):
        """检查内容是否已经被翻译（包含中文）"""
        # 简单检测：如果内容中包含足够多的中文字符，认为已翻译
        chinese_char_count = sum(1 for char in content if '\u4e00' <= char <= '\u9fff')
        total_chars = len(content)
        
        # 计算中文字符比例
        if total_chars > 0:
            chinese_ratio = chinese_char_count / total_chars
            # 如果中文字符比例超过15%，认为已翻译
            if chinese_ratio > 0.15:
                logger.info(f"检测到文件已翻译（中文比例: {chinese_ratio:.2f}）")
                return True
        
        return False

    def translate_file(self, file_path):
        """
        翻译单个文件
        
        Args:
            file_path (Path): 文件路径
            
        Returns:
            bool: 是否成功翻译
        """
        try:
            file_hash = self._get_file_hash(file_path)
            if not file_hash:
                return False
                
            # 读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 尝试使用其他编码
                with open(file_path, 'r', encoding='latin1') as f:
                    content = f.read()
        
            # 检查内容是否已翻译
            if self._is_content_already_translated(content):
                logger.info(f"文件已包含中文内容，跳过: {file_path}")
                
                # 仍然更新状态数据库，以便下次跳过
                self._update_file_state(file_path, file_hash)
                return True
            
            # 状态数据库检查
            if not self._should_translate_file(file_path):
                logger.info(f"文件已翻译过（基于状态记录），跳过: {file_path}")
                return True
                
            # 翻译文件
            logger.info(f"正在翻译文件: {file_path}")
            translated_content = self.translator.translate_file(file_path)
            
            # 保存翻译结果到原文件
            target_path = self._save_translated_file(file_path, translated_content)
            if not target_path:
                return False
                
            # 更新状态
            self._update_file_state(file_path, file_hash)
            return True
            
        except Exception as e:
            logger.error(f"翻译文件 {file_path} 时出错: {str(e)}")
            return False
            
    def scan_and_translate(self):
        """
        扫描并翻译目录中的文件
        
        Returns:
            tuple: (总文件数, 成功翻译数, 跳过数, 失败数)
        """
        if not self.source_dir.exists():
            logger.error(f"源目录不存在: {self.source_dir}")
            return 0, 0, 0, 0
            
        # 统计数据
        total_files = 0
        translated_files = 0
        skipped_files = 0
        failed_files = 0
        
        # 获取所有要处理的文件
        valid_extensions = ['.md', '.txt', '.html']
        files_to_process = []
        for ext in valid_extensions:
            files_to_process.extend(self.source_dir.glob(f"**/*{ext}"))
            
        total_files = len(files_to_process)
        logger.info(f"找到 {total_files} 个文件需要处理")
        
        # 使用进度条显示处理进度
        with tqdm(total=total_files, desc="翻译进度") as pbar:
            for file_path in files_to_process:
                try:
                    # 检查文件是否需要翻译
                    file_hash = self._get_file_hash(file_path)
                    if not file_hash:
                        failed_files += 1
                        pbar.update(1)
                        continue
                        
                    if not self._should_translate_file(file_path):
                        logger.info(f"文件已翻译，跳过: {file_path}")
                        skipped_files += 1
                        pbar.update(1)
                        continue
                    
                    # 翻译文件
                    logger.info(f"正在翻译文件: {file_path}")
                    translated_content = self.translator.translate_file(file_path)
                    
                    # 保存翻译结果
                    target_path = self._save_translated_file(file_path, translated_content)
                    if not target_path:
                        failed_files += 1
                        pbar.update(1)
                        continue
                    
                    # 更新状态
                    self._update_file_state(file_path, file_hash)
                    translated_files += 1
                    
                except Exception as e:
                    logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
                    failed_files += 1
                
                finally:
                    pbar.update(1)
                    time.sleep(0.1)  # 防止API请求过于频繁
                    
        return total_files, translated_files, skipped_files, failed_files

def main():
    """主函数"""
    # 在解析命令行参数前，确认环境变量是否已加载
    env_from_file = os.environ.get("DEEPSEEK_API_KEY", "").startswith("sk-")
    env_source = "从.env文件中" if env_from_file else "从系统环境变量中"
    
    parser = argparse.ArgumentParser(description="文件夹内容批量翻译工具")
    parser.add_argument('source_dir', nargs='?', default=None, 
                        help="要翻译的源文件目录 (默认: ./data)")
    parser.add_argument('--api-key', '-k', default=None,
                        help="DeepSeek API密钥 (也可通过DEEPSEEK_API_KEY环境变量设置)")
    parser.add_argument('--reset', action='store_true', 
                        help="重置翻译状态，重新翻译所有文件")
    
    args = parser.parse_args()
    
    # 默认源目录为当前目录下的data文件夹
    source_dir = args.source_dir or (current_dir / "data")
    source_dir = Path(source_dir)
    
    logger.info("=== 开始文件夹内容批量翻译 ===")
    logger.info(f"源目录: {source_dir}")
    logger.info(f"翻译模式: 直接在原文件中更新翻译内容，保留备份")
    
    if not args.api_key and env_from_file:
        logger.info(f"{env_source}读取到API密钥")
    
    try:
        # 初始化翻译器
        translator = DeepSeekTranslator(api_key=args.api_key)
        
        # 如果需要重置状态，删除状态文件
        db_path = current_dir / "translation_state.json"
        if args.reset and db_path.exists():
            db_path.unlink()
            logger.info("已重置翻译状态")
        
        # 初始化翻译管理器
        manager = TranslationManager(source_dir, translator, db_path)
        
        # 扫描并翻译文件
        total, translated, skipped, failed = manager.scan_and_translate()
        
        logger.info("=== 翻译完成 ===")
        logger.info(f"总文件数: {total}")
        logger.info(f"成功翻译: {translated}")
        logger.info(f"已翻译跳过: {skipped}")
        logger.info(f"翻译失败: {failed}")
        
        print(f"\n翻译完成。总文件数: {total}, 成功翻译: {translated}, 已翻译跳过: {skipped}, 翻译失败: {failed}")
        print(f"详细信息请查看日志文件: {logs_dir / log_filename}")
    
    except Exception as e:
        logger.error(f"执行过程中出错: {str(e)}")
        logger.error(f"错误详情: ", exc_info=True)
        print(f"执行过程中出错: {str(e)}")

if __name__ == "__main__":
    main()