#!/usr/bin/env python3
"""
工具函数模块
提供各种辅助功能
"""

import os
import sys
import logging
import pdfplumber
import hashlib
import pickle
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime


def setup_logging(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    设置日志记录
    
    Args:
        name: 日志器名称
        level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        
    Returns:
        logging.Logger: 配置好的日志器
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # 设置日志级别
        log_level = getattr(logging, level or "INFO", logging.INFO)
        logger.setLevel(log_level)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(console_handler)
    
    return logger


def extract_text_from_pdf(pdf_path: str, use_cache: bool = True) -> str:
    """
    从PDF中提取文本内容
    
    Args:
        pdf_path: PDF文件路径
        use_cache: 是否使用缓存
        
    Returns:
        str: 提取的文本内容
    """
    logger = logging.getLogger(__name__)
    
    # 检查缓存
    if use_cache:
        cached_text = _get_cached_text(pdf_path)
        if cached_text is not None:
            logger.debug(f"使用缓存文本: {pdf_path}")
            return cached_text
    
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"=== 第{page_num}页 ===\n{page_text}\n\n"
                else:
                    text += f"=== 第{page_num}页 ===\n[无法提取文本]\n\n"
        
        logger.info(f"从PDF提取文本: {pdf_path} ({len(text)} 字符)")
        
        # 缓存结果
        if use_cache:
            _cache_text(pdf_path, text)
        
        return text
        
    except Exception as e:
        logger.error(f"提取PDF文本时出错: {e}")
        raise


def _get_cached_text(pdf_path: str) -> Optional[str]:
    """从缓存获取文本"""
    cache_dir = Path(".pdf_cache")
    if not cache_dir.exists():
        return None
    
    # 生成缓存文件名
    try:
        with open(pdf_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
    except:
        return None
    
    cache_file = cache_dir / f"{file_hash}.pkl"
    
    if cache_file.exists():
        try:
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                
            # 检查缓存是否过期（24小时）
            cache_time = cached_data.get("timestamp", 0)
            if datetime.now().timestamp() - cache_time < 24 * 3600:
                return cached_data.get("text", "")
        except:
            pass
    
    return None


def _cache_text(pdf_path: str, text: str):
    """缓存文本"""
    cache_dir = Path(".pdf_cache")
    cache_dir.mkdir(exist_ok=True)
    
    try:
        with open(pdf_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
    except:
        return
    
    cache_file = cache_dir / f"{file_hash}.pkl"
    
    cache_data = {
        "timestamp": datetime.now().timestamp(),
        "text": text,
        "source": pdf_path,
    }
    
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
    except:
        pass


def validate_pdf_file(pdf_path: str, max_size_mb: int = 100) -> Dict[str, Any]:
    """
    验证PDF文件
    
    Args:
        pdf_path: PDF文件路径
        max_size_mb: 最大文件大小（MB）
        
    Returns:
        Dict: 验证结果
    """
    result = {
        "valid": False,
        "message": "",
        "size_mb": 0,
        "exists": False,
        "is_file": False,
        "is_pdf": False,
    }
    
    path = Path(pdf_path)
    
    # 检查文件是否存在
    if not path.exists():
        result["message"] = f"文件不存在: {pdf_path}"
        return result
    result["exists"] = True
    
    # 检查是否是文件
    if not path.is_file():
        result["message"] = f"不是文件: {pdf_path}"
        return result
    result["is_file"] = True
    
    # 检查文件扩展名
    if path.suffix.lower() != ".pdf":
        result["message"] = f"不是PDF文件: {pdf_path}"
        return result
    result["is_pdf"] = True
    
    # 检查文件大小
    try:
        file_size = path.stat().st_size
        result["size_mb"] = file_size / (1024 * 1024)
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            result["message"] = f"文件过大: {result['size_mb']:.1f}MB > {max_size_mb}MB"
            return result
    except:
        result["message"] = f"无法获取文件大小: {pdf_path}"
        return result
    
    result["valid"] = True
    result["message"] = "文件验证通过"
    return result


def format_file_size(bytes_size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


def get_timestamp() -> str:
    """获取当前时间戳"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def create_output_filename(input_path: str, suffix: str = "annotated") -> str:
    """
    创建输出文件名
    
    Args:
        input_path: 输入文件路径
        suffix: 文件名后缀
        
    Returns:
        str: 输出文件名
    """
    path = Path(input_path)
    return f"{path.stem}_{suffix}{path.suffix}"


def ensure_directory(directory: str) -> bool:
    """
    确保目录存在
    
    Args:
        directory: 目录路径
        
    Returns:
        bool: 是否成功
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"创建目录失败: {e}")
        return False


def load_config(config_path: str) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        Dict: 配置字典
    """
    import yaml
    import json
    
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    try:
        if path.suffix.lower() == ".yaml" or path.suffix.lower() == ".yml":
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        elif path.suffix.lower() == ".json":
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise ValueError(f"不支持的配置文件格式: {path.suffix}")
    except Exception as e:
        raise ValueError(f"加载配置文件失败: {e}")


def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """
    保存配置文件
    
    Args:
        config: 配置字典
        config_path: 配置文件路径
        
    Returns:
        bool: 是否成功
    """
    import yaml
    import json
    
    path = Path(config_path)
    
    try:
        if path.suffix.lower() == ".yaml" or path.suffix.lower() == ".yml":
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        elif path.suffix.lower() == ".json":
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        else:
            return False
        
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"保存配置文件失败: {e}")
        return False


def progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', 
                 length: int = 50, fill: str = '█') -> str:
    """
    生成进度条字符串
    
    Args:
        iteration: 当前迭代
        total: 总迭代数
        prefix: 前缀
        suffix: 后缀
        length: 进度条长度
        fill: 填充字符
        
    Returns:
        str: 进度条字符串
    """
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    return f'\r{prefix} |{bar}| {percent}% {suffix}'


def cleanup_temp_files(temp_dir: str = ".temp", max_age_hours: int = 24) -> int:
    """
    清理临时文件
    
    Args:
        temp_dir: 临时目录
        max_age_hours: 最大保留时间（小时）
        
    Returns:
        int: 清理的文件数量
    """
    import time
    import shutil
    
    path = Path(temp_dir)
    if not path.exists():
        return 0
    
    cleaned = 0
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for item in path.iterdir():
        try:
            # 检查文件/目录年龄
            item_age = current_time - item.stat().st_mtime
            
            if item_age > max_age_seconds:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                cleaned += 1
        except:
            pass
    
    return cleaned


if __name__ == "__main__":
    # 测试代码
    logger = setup_logging(__name__, "DEBUG")
    logger.info("工具函数测试")
    
    # 测试文件大小格式化
    test_sizes = [1024, 1024*1024, 1024*1024*1024]
    for size in test_sizes:
        print(f"{size} bytes = {format_file_size(size)}")
    
    # 测试时间戳
    print(f"当前时间戳: {get_timestamp()}")