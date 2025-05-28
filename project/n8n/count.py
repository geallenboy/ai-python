import os
import glob
from pathlib import Path

def count_json_files(directory_path="data/newworkflow"):
    """
    统计指定目录中JSON文件的数量
    
    Args:
        directory_path (str): 目录路径，默认为 "data/newworkflow"
    
    Returns:
        int: JSON文件的数量
    """
    try:
        # 方法1：使用glob模块
        json_pattern = os.path.join(directory_path, "*.json")
        json_files = glob.glob(json_pattern)
        return len(json_files)
    except Exception as e:
        print(f"统计文件时出错: {e}")
        return 0

def count_json_files_pathlib(directory_path="data/newworkflow"):
    """
    使用pathlib统计指定目录中JSON文件的数量
    
    Args:
        directory_path (str): 目录路径，默认为 "data/newworkflow"
    
    Returns:
        int: JSON文件的数量
    """
    try:
        path = Path(directory_path)
        if path.exists() and path.is_dir():
            json_files = list(path.glob("*.json"))
            return len(json_files)
        else:
            print(f"目录不存在: {directory_path}")
            return 0
    except Exception as e:
        print(f"统计文件时出错: {e}")
        return 0

if __name__ == "__main__":
    # 测试函数
    count1 = count_json_files()
    count2 = count_json_files_pathlib()
    
    print(f"使用glob方法统计: {count1} 个JSON文件")
    print(f"使用pathlib方法统计: {count2} 个JSON文件")