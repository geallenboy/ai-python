import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

class TranslationSyncer:
    def __init__(self):
        self.setup_logging()
        self.source_dir = Path("data/workflow")
        self.target_dir = Path("data/newworkflow")
        
        # 需要同步的翻译字段
        self.translation_fields = [
            'readme_zh',
            'title_zh', 
            'publish_date_zh',
            'workflow_json_zh'
        ]
    
    def setup_logging(self):
        """设置日志系统"""
        # 确保日志目录存在
        log_dir = Path("data/newworkflow/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('data/newworkflow/logs/translation_sync.log', 'a', 'utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def ensure_directories(self):
        """确保目录存在"""
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.target_dir.mkdir(parents=True, exist_ok=True)
        (self.target_dir / "logs").mkdir(parents=True, exist_ok=True)
    
    def get_json_files(self, directory: Path) -> Dict[str, Path]:
        """获取目录中所有JSON文件，返回文件名到路径的映射"""
        json_files = {}
        
        if not directory.exists():
            return json_files
        
        # 处理data/workflow目录 - 需要遍历子目录
        if directory.name == "workflow":
            self.logger.info(f"扫描 {directory} 目录的子文件夹...")
            for subfolder in directory.iterdir():
                if subfolder.is_dir():
                    self.logger.info(f"  检查子文件夹: {subfolder.name}")
                    for json_file in subfolder.glob("*.json"):
                        json_files[json_file.name] = json_file
                        self.logger.debug(f"    找到文件: {json_file.name}")
        else:
            # 处理data/newworkflow目录 - 直接扫描JSON文件
            self.logger.info(f"扫描 {directory} 目录...")
            for json_file in directory.glob("*.json"):
                json_files[json_file.name] = json_file
                self.logger.debug(f"  找到文件: {json_file.name}")
        
        return json_files
    
    def load_json_file(self, file_path: Path) -> Dict:
        """加载JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载文件 {file_path} 时出错: {e}")
            return {}
    
    def save_json_file(self, file_path: Path, data: Dict) -> bool:
        """保存JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"保存文件 {file_path} 时出错: {e}")
            return False
    
    def check_missing_fields(self, target_data: Dict) -> List[str]:
        """检查目标文件中缺失的翻译字段"""
        missing_fields = []
        for field in self.translation_fields:
            if field not in target_data or not target_data[field]:
                missing_fields.append(field)
        return missing_fields
    
    def get_available_fields(self, source_data: Dict) -> List[str]:
        """获取源文件中可用的翻译字段"""
        available_fields = []
        for field in self.translation_fields:
            if field in source_data and source_data[field]:
                available_fields.append(field)
        return available_fields
    
    def sync_translation_fields(self, source_file: Path, target_file: Path) -> Tuple[bool, List[str]]:
        """同步翻译字段从源文件到目标文件"""
        # 加载源文件和目标文件
        source_data = self.load_json_file(source_file)
        target_data = self.load_json_file(target_file)
        
        if not source_data or not target_data:
            return False, []
        
        # 检查目标文件缺失的字段
        missing_fields = self.check_missing_fields(target_data)
        if not missing_fields:
            self.logger.debug(f"目标文件 {target_file.name} 已包含所有翻译字段，跳过")
            return True, []
        
        # 检查源文件中可用的字段
        available_fields = self.get_available_fields(source_data)
        if not available_fields:
            self.logger.debug(f"源文件 {source_file.name} 不包含任何翻译字段，跳过")
            return True, []
        
        # 找出需要同步的字段（既缺失又可用的字段）
        fields_to_sync = [field for field in missing_fields if field in available_fields]
        
        if not fields_to_sync:
            self.logger.debug(f"文件 {target_file.name} 与 {source_file.name} 无可同步字段")
            return True, []
        
        # 同步字段
        updated = False
        synced_fields = []
        
        for field in fields_to_sync:
            target_data[field] = source_data[field]
            synced_fields.append(field)
            updated = True
            self.logger.info(f"   📋 同步字段 '{field}' 到目标文件")
        
        # 保存更新后的目标文件
        if updated:
            if self.save_json_file(target_file, target_data):
                self.logger.info(f"   💾 成功保存到 {target_file.name}，更新了 {len(synced_fields)} 个字段")
                return True, synced_fields
            else:
                self.logger.error(f"   ❌ 保存目标文件 {target_file.name} 失败")
                return False, []
        
        return True, []
    
    def sync_all_files(self):
        """同步所有匹配的文件"""
        self.ensure_directories()
        
        # 获取两个目录中的所有JSON文件
        self.logger.info("开始扫描文件...")
        source_files = self.get_json_files(self.source_dir)
        target_files = self.get_json_files(self.target_dir)
        
        self.logger.info(f"源目录 (data/workflow) 包含 {len(source_files)} 个JSON文件")
        self.logger.info(f"目标目录 (data/newworkflow) 包含 {len(target_files)} 个JSON文件")
        
        # 找出同名的文件
        common_files = set(source_files.keys()) & set(target_files.keys())
        
        if not common_files:
            self.logger.info("没有找到同名的JSON文件")
            return
        
        self.logger.info(f"找到 {len(common_files)} 个同名文件需要处理")
        
        # 统计信息
        total_processed = 0
        total_updated = 0
        total_fields_synced = 0
        
        # 处理每个同名文件
        for filename in sorted(common_files):
            source_file = source_files[filename]  # data/workflow/子目录/文件.json
            target_file = target_files[filename]  # data/newworkflow/文件.json
            
            self.logger.info(f"\n[{total_processed + 1}/{len(common_files)}] 处理文件: {filename}")
            
            # 修复路径显示问题 - 明确显示不同目录
            try:
                source_path_str = str(source_file.relative_to(Path.cwd()))
            except ValueError:
                source_path_str = str(source_file)
            
            try:
                target_path_str = str(target_file.relative_to(Path.cwd()))
            except ValueError:
                target_path_str = str(target_file)
            
            # 验证文件确实来自不同目录
            if source_file.parent.name == target_file.parent.name:
                self.logger.warning(f"⚠️  源文件和目标文件在同一目录! 跳过处理")
                self.logger.warning(f"   源: {source_path_str}")
                self.logger.warning(f"   目标: {target_path_str}")
                continue
            
            self.logger.info(f"  📂 源文件 (有翻译): {source_path_str}")
            self.logger.info(f"  📝 目标文件 (待补充): {target_path_str}")
            
            success, synced_fields = self.sync_translation_fields(source_file, target_file)
            total_processed += 1
            
            if success and synced_fields:
                total_updated += 1
                total_fields_synced += len(synced_fields)
                self.logger.info(f"✅ 成功同步 {len(synced_fields)} 个字段: {', '.join(synced_fields)}")
                self.logger.info(f"   更新的文件: {target_path_str}")
            elif success:
                self.logger.info("ℹ️  无需更新 (目标文件已有所有翻译或源文件无翻译)")
            else:
                self.logger.error("❌ 处理失败")
        
        # 输出统计信息
        self.logger.info(f"\n=== 同步完成 ===")
        self.logger.info(f"总共处理: {total_processed} 个文件")
        self.logger.info(f"成功更新: {total_updated} 个文件")
        self.logger.info(f"同步字段: {total_fields_synced} 个")
        self.logger.info(f"所有更新都保存在: data/newworkflow/ 目录中")
        
        # 处理目标目录中独有的文件
        target_only_files = set(target_files.keys()) - set(source_files.keys())
        if target_only_files:
            self.logger.info(f"\n📋 data/newworkflow 独有文件 ({len(target_only_files)} 个):")
            self.logger.info("   这些文件在 data/workflow 中没有对应的翻译源文件")
            for filename in sorted(list(target_only_files)[:10]):
                self.logger.info(f"     - {filename}")
            if len(target_only_files) > 10:
                self.logger.info(f"     ... 还有 {len(target_only_files) - 10} 个文件")
        
        # 处理源目录中独有的文件
        source_only_files = set(source_files.keys()) - set(target_files.keys())
        if source_only_files:
            self.logger.info(f"\n📚 data/workflow 独有文件 ({len(source_only_files)} 个):")
            self.logger.info("   这些翻译文件在 data/newworkflow 中没有对应的目标文件")
            for filename in sorted(list(source_only_files)[:10]):
                self.logger.info(f"     - {filename}")
            if len(source_only_files) > 10:
                self.logger.info(f"     ... 还有 {len(source_only_files) - 10} 个文件")
    
    def check_file_status(self, filename: str = None):
        """检查文件状态（用于调试）"""
        source_files = self.get_json_files(self.source_dir)
        target_files = self.get_json_files(self.target_dir)
        
        if filename:
            # 检查特定文件
            if filename in source_files and filename in target_files:
                source_data = self.load_json_file(source_files[filename])
                target_data = self.load_json_file(target_files[filename])
                
                print(f"\n📄 文件分析: {filename}")
                
                # 修复路径显示问题
                try:
                    source_path_str = str(source_files[filename].relative_to(Path.cwd()))
                except ValueError:
                    source_path_str = str(source_files[filename])
                
                try:
                    target_path_str = str(target_files[filename].relative_to(Path.cwd()))
                except ValueError:
                    target_path_str = str(target_files[filename])
                
                print(f"📚 源文件路径 (有翻译): {source_path_str}")
                print(f"📝 目标文件路径 (待补充): {target_path_str}")
                
                # 验证是否来自不同目录
                if source_files[filename].parent.name == target_files[filename].parent.name:
                    print("⚠️  警告: 源文件和目标文件在同一目录!")
                
                print("\n📚 源文件翻译字段 (data/workflow):")
                for field in self.translation_fields:
                    status = "✅ 有内容" if field in source_data and source_data[field] else "❌ 无内容"
                    value_preview = ""
                    if field in source_data and source_data[field]:
                        preview = str(source_data[field])[:50]
                        if len(str(source_data[field])) > 50:
                            preview += "..."
                        value_preview = f" ({preview})"
                    print(f"  {status} {field}{value_preview}")
                
                print("\n📝 目标文件翻译字段 (data/newworkflow):")
                for field in self.translation_fields:
                    status = "✅ 已有" if field in target_data and target_data[field] else "❌ 缺失"
                    value_preview = ""
                    if field in target_data and target_data[field]:
                        preview = str(target_data[field])[:50]
                        if len(str(target_data[field])) > 50:
                            preview += "..."
                        value_preview = f" ({preview})"
                    print(f"  {status} {field}{value_preview}")
                
                # 分析可同步的字段
                missing_fields = self.check_missing_fields(target_data)
                available_fields = self.get_available_fields(source_data)
                syncable_fields = [field for field in missing_fields if field in available_fields]
                
                print(f"\n🔄 可同步字段: {', '.join(syncable_fields) if syncable_fields else '无'}")
                if syncable_fields:
                    print(f"   这些字段将从源文件复制到目标文件")
                
            else:
                if filename not in source_files and filename not in target_files:
                    print(f"❌ 文件 {filename} 在两个目录中都不存在")
                elif filename not in source_files:
                    print(f"❌ 文件 {filename} 在源目录 (data/workflow) 中不存在")
                else:
                    print(f"❌ 文件 {filename} 在目标目录 (data/newworkflow) 中不存在")
        else:
            # 检查所有同名文件的状态
            common_files = set(source_files.keys()) & set(target_files.keys())
            
            print(f"\n📁 目录结构说明:")
            print(f"  📚 源目录: {self.source_dir} (嵌套子目录，包含翻译内容)")
            print(f"  📝 目标目录: {self.target_dir} (直接文件，需要补充翻译)")
            
            print(f"\n📊 同名文件状态汇总 (共 {len(common_files)} 个):")
            
            # 统计信息
            files_needing_sync = 0
            total_syncable_fields = 0
            
            display_count = min(15, len(common_files))
            for filename in sorted(list(common_files)[:display_count]):
                source_data = self.load_json_file(source_files[filename])
                target_data = self.load_json_file(target_files[filename])
                
                missing_count = len(self.check_missing_fields(target_data))
                available_count = len(self.get_available_fields(source_data))
                syncable_count = len([field for field in self.check_missing_fields(target_data) 
                                    if field in self.get_available_fields(source_data)])
                
                if syncable_count > 0:
                    files_needing_sync += 1
                    total_syncable_fields += syncable_count
                
                status_icon = "🔄 需同步" if syncable_count > 0 else "✅ 完整" if missing_count == 0 else "ℹ️  无源"
                print(f"  {status_icon} {filename}: 目标缺失 {missing_count}/4, 源可用 {available_count}/4, 可同步 {syncable_count}")
            
            if len(common_files) > display_count:
                print(f"  ... 还有 {len(common_files) - display_count} 个文件")
            
            print(f"\n📈 统计汇总:")
            print(f"  🔄 需要同步的文件: {files_needing_sync} 个")
            print(f"  📋 可同步的字段: {total_syncable_fields} 个")
            print(f"  💾 所有更新将保存在 data/newworkflow 目录中")
def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='翻译字段同步工具')
    parser.add_argument('--check', type=str, nargs='?', const='all',
                       help='检查文件状态，可指定文件名或使用 "all" 检查所有')
    parser.add_argument('--sync', action='store_true',
                       help='执行同步操作')
    
    args = parser.parse_args()
    
    syncer = TranslationSyncer()
    
    if args.check is not None:
        if args.check == 'all':
            syncer.check_file_status()
        else:
            syncer.check_file_status(args.check)
    elif args.sync:
        syncer.sync_all_files()
    else:
        print("请指定操作:")
        print("  --sync     执行同步操作")
        print("  --check    检查所有文件状态")
        print("  --check filename.json  检查特定文件状态")

if __name__ == "__main__":
    main()