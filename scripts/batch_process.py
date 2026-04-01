#!/usr/bin/env python3
"""
批量处理PDF文件
"""

import os
import sys
import argparse
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.proofreader import Proofreader
from src.utils import setup_logging, validate_pdf_file, format_file_size

logger = setup_logging(__name__)


class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化批量处理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.proofreader = Proofreader(config)
        self.results = []
        
        # 设置默认配置
        self.config.setdefault("max_workers", 4)
        self.config.setdefault("output_dir", "./batch_output")
        self.config.setdefault("overwrite", False)
        self.config.setdefault("verbose", False)
    
    def process_directory(self, input_dir: str, pattern: str = "*.pdf") -> List[Dict[str, Any]]:
        """
        处理目录下的所有PDF文件
        
        Args:
            input_dir: 输入目录
            pattern: 文件匹配模式
            
        Returns:
            处理结果列表
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            logger.error(f"输入目录不存在: {input_dir}")
            return []
        
        if not input_path.is_dir():
            logger.error(f"不是目录: {input_dir}")
            return []
        
        # 查找PDF文件
        pdf_files = list(input_path.glob(pattern))
        if not pdf_files:
            logger.warning(f"在 {input_dir} 中未找到 {pattern} 文件")
            return []
        
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        
        # 创建输出目录
        output_dir = Path(self.config.get("output_dir", "./batch_output"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 处理文件
        if self.config.get("max_workers", 1) > 1:
            return self._process_parallel(pdf_files, output_dir)
        else:
            return self._process_sequential(pdf_files, output_dir)
    
    def _process_sequential(self, pdf_files: List[Path], output_dir: Path) -> List[Dict[str, Any]]:
        """顺序处理文件"""
        results = []
        
        for i, pdf_file in enumerate(pdf_files, 1):
            logger.info(f"处理文件 {i}/{len(pdf_files)}: {pdf_file.name}")
            
            result = self._process_single_file(pdf_file, output_dir)
            results.append(result)
            
            # 显示进度
            self._print_progress(i, len(pdf_files), result)
        
        return results
    
    def _process_parallel(self, pdf_files: List[Path], output_dir: Path) -> List[Dict[str, Any]]:
        """并行处理文件"""
        results = []
        max_workers = self.config.get("max_workers", 4)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            future_to_file = {
                executor.submit(self._process_single_file, pdf_file, output_dir): pdf_file
                for pdf_file in pdf_files
            }
            
            # 收集结果
            completed = 0
            for future in concurrent.futures.as_completed(future_to_file):
                pdf_file = future_to_file[future]
                completed += 1
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    # 显示进度
                    self._print_progress(completed, len(pdf_files), result)
                    
                except Exception as e:
                    logger.error(f"处理文件失败 {pdf_file.name}: {e}")
                    results.append({
                        "file": str(pdf_file),
                        "success": False,
                        "error": str(e)
                    })
        
        return results
    
    def _process_single_file(self, pdf_file: Path, output_dir: Path) -> Dict[str, Any]:
        """处理单个文件"""
        start_time = datetime.now()
        
        try:
            # 验证文件
            validation = validate_pdf_file(str(pdf_file))
            if not validation["valid"]:
                return {
                    "file": str(pdf_file),
                    "success": False,
                    "error": validation["message"],
                    "duration": 0
                }
            
            # 设置输出路径
            output_file = output_dir / f"{pdf_file.stem}_annotated.pdf"
            report_file = output_dir / f"{pdf_file.stem}_report.md"
            
            # 检查是否覆盖
            if not self.config.get("overwrite", False):
                if output_file.exists() or report_file.exists():
                    return {
                        "file": str(pdf_file),
                        "success": False,
                        "error": "输出文件已存在（使用 --overwrite 覆盖）",
                        "duration": 0
                    }
            
            # 运行校对
            result = self.proofreader.check(
                input_path=str(pdf_file),
                output_path=str(output_file),
                report_path=str(report_file)
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "file": str(pdf_file),
                "success": result.success,
                "output_pdf": str(output_file) if result.success else None,
                "report": str(report_file) if result.success else None,
                "message": result.message,
                "stats": result.stats if result.success else {},
                "duration": duration,
                "size_mb": validation["size_mb"]
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"处理文件时出错 {pdf_file.name}: {e}", exc_info=True)
            
            return {
                "file": str(pdf_file),
                "success": False,
                "error": str(e),
                "duration": duration
            }
    
    def _print_progress(self, current: int, total: int, result: Dict[str, Any]):
        """显示进度"""
        if self.config.get("verbose", False):
            status = "✓" if result.get("success", False) else "✗"
            message = result.get("message", result.get("error", ""))
            print(f"  [{current}/{total}] {status} {Path(result['file']).name}: {message}")
        else:
            percent = int(current / total * 100)
            print(f"\r处理进度: {current}/{total} ({percent}%)", end="")
            if current == total:
                print()  # 换行
    
    def generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成处理摘要"""
        total_files = len(results)
        successful = sum(1 for r in results if r.get("success", False))
        failed = total_files - successful
        
        # 统计错误类型
        error_types = {}
        total_errors = 0
        
        for result in results:
            if result.get("success", False):
                stats = result.get("stats", {})
                total_errors += stats.get("total_errors", 0)
                
                for error_type, count in stats.get("error_types", {}).items():
                    error_types[error_type] = error_types.get(error_type, 0) + count
        
        # 计算平均处理时间
        durations = [r.get("duration", 0) for r in results if r.get("duration", 0) > 0]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # 计算总文件大小
        total_size_mb = sum(r.get("size_mb", 0) for r in results)
        
        return {
            "total_files": total_files,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total_files if total_files > 0 else 0,
            "total_errors": total_errors,
            "error_types": error_types,
            "avg_duration_seconds": avg_duration,
            "total_size_mb": total_size_mb,
            "start_time": min(r.get("_start_time", datetime.now()) for r in results) if results else datetime.now(),
            "end_time": datetime.now(),
        }
    
    def save_summary_report(self, results: List[Dict[str, Any]], output_path: str):
        """保存摘要报告"""
        summary = self.generate_summary(results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 批量处理摘要报告\n\n")
            
            f.write("## 处理统计\n")
            f.write(f"- **总文件数**: {summary['total_files']}\n")
            f.write(f"- **成功处理**: {summary['successful']}\n")
            f.write(f"- **处理失败**: {summary['failed']}\n")
            f.write(f"- **成功率**: {summary['success_rate']:.1%}\n")
            f.write(f"- **总错误数**: {summary['total_errors']}\n")
            f.write(f"- **平均处理时间**: {summary['avg_duration_seconds']:.1f}秒\n")
            f.write(f"- **总文件大小**: {summary['total_size_mb']:.1f}MB\n\n")
            
            if summary['error_types']:
                f.write("## 错误类型统计\n")
                for error_type, count in summary['error_types'].items():
                    type_name = {
                        "spelling": "拼写错误",
                        "grammar": "语法错误",
                        "expression": "表达问题"
                    }.get(error_type, error_type)
                    f.write(f"- **{type_name}**: {count}处\n")
                f.write("\n")
            
            f.write("## 详细结果\n")
            f.write("| 文件 | 状态 | 错误数 | 处理时间 | 备注 |\n")
            f.write("|------|------|--------|----------|------|\n")
            
            for result in results:
                filename = Path(result['file']).name
                status = "成功" if result.get('success', False) else "失败"
                error_count = result.get('stats', {}).get('total_errors', 0) if result.get('success', False) else "-"
                duration = f"{result.get('duration', 0):.1f}秒"
                note = result.get('message', result.get('error', ''))
                
                f.write(f"| {filename} | {status} | {error_count} | {duration} | {note} |\n")
            
            f.write("\n")
            f.write(f"报告生成时间: {summary['end_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(
        description="批量处理PDF文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s ./documents
  %(prog)s ./documents --output ./results --workers 4
  %(prog)s ./documents --pattern "*.pdf" --config config.yaml
        """
    )
    
    parser.add_argument("input_dir", help="输入目录")
    parser.add_argument("--output", "-o", default="./batch_output", help="输出目录")
    parser.add_argument("--pattern", "-p", default="*.pdf", help="文件匹配模式")
    parser.add_argument("--workers", "-w", type=int, default=4, help="工作线程数")
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--overwrite", "-f", action="store_true", help="覆盖已存在文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--summary", "-s", help="摘要报告文件路径")
    
    args = parser.parse_args()
    
    # 加载配置
    config = {
        "output_dir": args.output,
        "max_workers": args.workers,
        "overwrite": args.overwrite,
        "verbose": args.verbose,
    }
    
    if args.config:
        from src.utils import load_config
        try:
            config.update(load_config(args.config))
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            sys.exit(1)
    
    # 创建处理器
    processor = BatchProcessor(config)
    
    print(f"开始批量处理: {args.input_dir}")
    print(f"文件模式: {args.pattern}")
    print(f"输出目录: {args.output}")
    print(f"工作线程: {args.workers}")
    print("-" * 50)
    
    # 处理文件
    results = processor.process_directory(args.input_dir, args.pattern)
    
    print("\n" + "=" * 50)
    print("批量处理完成！")
    print("=" * 50)
    
    # 生成摘要
    summary = processor.generate_summary(results)
    
    print(f"\n处理统计:")
    print(f"  总文件数: {summary['total_files']}")
    print(f"  成功处理: {summary['successful']}")
    print(f"  处理失败: {summary['failed']}")
    print(f"  成功率: {summary['success_rate']:.1%}")
    print(f"  总错误数: {summary['total_errors']}")
    print(f"  平均处理时间: {summary['avg_duration_seconds']:.1f}秒")
    
    if summary['error_types']:
        print(f"\n错误类型统计:")
        for error_type, count in summary['error_types'].items():
            type_name = {
                "spelling": "拼写错误",
                "grammar": "语法错误",
                "expression": "表达问题"
            }.get(error_type, error_type)
            print(f"  {type_name}: {count}处")
    
    # 保存摘要报告
    if args.summary:
        processor.save_summary_report(results, args.summary)
        print(f"\n摘要报告已保存: {args.summary}")
    
    # 显示失败文件
    failed_files = [r for r in results if not r.get('success', False)]
    if failed_files:
        print(f"\n失败文件 ({len(failed_files)}):")
        for result in failed_files:
            print(f"  {Path(result['file']).name}: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    main()