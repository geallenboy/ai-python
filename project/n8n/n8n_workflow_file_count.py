import os
import json
from collections import defaultdict
from pathlib import Path

def count_json_files_by_category():
    # 指定工作流目录路径
    workflow_dir = Path("data/workflow")
    
    # 检查目录是否存在
    if not workflow_dir.exists():
        print(f"错误: 目录 {workflow_dir} 不存在")
        return
    
    # 初始化计数器
    counts = defaultdict(int)
    total_count = 0
    
    # 遍历所有分类目录
    for category_dir in workflow_dir.iterdir():
        if category_dir.is_dir():
            category_name = category_dir.name
            json_count = 0
            
            # 统计此分类下的JSON文件
            for file_path in category_dir.glob("**/*.json"):
                if file_path.is_file():
                    json_count += 1
            
            counts[category_name] = json_count
            total_count += json_count
    
    # 输出统计结果
    print("=== JSON 文件统计 ===")
    print(f"{'分类目录':<20} {'文件数量':<10}")
    print("-" * 30)
    
    # 按照文件数量降序排列
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    
    for category, count in sorted_counts:
        print(f"{category:<20} {count:<10}")
    
    print("-" * 30)
    print(f"{'总计':<20} {total_count:<10}")

if __name__ == "__main__":
    count_json_files_by_category()