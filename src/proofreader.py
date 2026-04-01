#!/usr/bin/env python3
"""
PDF校对主程序
协调整个校对流程：文本提取 → 错误检查 → 标注生成 → 报告输出
"""

import os
import sys
import logging
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from .grammar_checker import GrammarChecker
from .pdf_annotator import PDFAnnotator
from .report_generator import ReportGenerator
from .utils import extract_text_from_pdf, setup_logging

# 配置日志
logger = setup_logging(__name__)


@dataclass
class ProofreadingResult:
    """校对结果数据类"""
    input_path: str
    output_path: str
    report_path: str
    errors: List[Tuple[str, str, int, int, int, str]]
    stats: Dict[str, Any]
    success: bool
    message: str


class Proofreader:
    """PDF校对器主类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化校对器
        
        Args:
            config: 配置字典
        """
        self.config = config or self._default_config()
        self.grammar_checker = GrammarChecker(config)
        self.pdf_annotator = PDFAnnotator(config)
        self.report_generator = ReportGenerator(config)
        
        logger.info("PDF校对器初始化完成")
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "check_spelling": True,
            "check_grammar": True,
            "check_expression": True,
            "output_dir": None,
            "overwrite": False,
            "verbose": False,
        }
    
    def check(self, input_path: str, output_path: Optional[str] = None, 
              report_path: Optional[str] = None) -> ProofreadingResult:
        """
        校对PDF文档
        
        Args:
            input_path: 输入PDF路径
            output_path: 输出PDF路径（可选）
            report_path: 报告文件路径（可选）
            
        Returns:
            ProofreadingResult: 校对结果
        """
        logger.info(f"开始校对: {input_path}")
        
        # 验证输入文件
        if not self._validate_input(input_path):
            return ProofreadingResult(
                input_path=input_path,
                output_path="",
                report_path="",
                errors=[],
                stats={},
                success=False,
                message=f"输入文件无效: {input_path}"
            )
        
        # 设置输出路径
        output_path, report_path = self._setup_output_paths(
            input_path, output_path, report_path
        )
        
        try:
            # 1. 提取文本
            logger.info("提取PDF文本...")
            text = extract_text_from_pdf(input_path)
            
            if not text.strip():
                return ProofreadingResult(
                    input_path=input_path,
                    output_path=output_path,
                    report_path=report_path,
                    errors=[],
                    stats={"text_length": 0},
                    success=False,
                    message="未提取到文本内容，可能是扫描版PDF"
                )
            
            # 2. 检查错误
            logger.info("检查文档错误...")
            errors = self._check_all_errors(text)
            
            # 3. 生成统计信息
            stats = self._generate_stats(text, errors)
            
            if not errors:
                logger.info("未发现明显错误")
                # 仍然生成报告
                self.report_generator.generate(report_path, errors, stats)
                return ProofreadingResult(
                    input_path=input_path,
                    output_path=output_path,
                    report_path=report_path,
                    errors=errors,
                    stats=stats,
                    success=True,
                    message="未发现明显错误"
                )
            
            # 4. 添加PDF标注
            logger.info("添加PDF标注...")
            self.pdf_annotator.annotate(input_path, output_path, errors)
            
            # 5. 生成报告
            logger.info("生成校对报告...")
            self.report_generator.generate(report_path, errors, stats)
            
            # 6. 返回结果
            message = self._generate_summary_message(stats)
            logger.info(f"校对完成: {message}")
            
            return ProofreadingResult(
                input_path=input_path,
                output_path=output_path,
                report_path=report_path,
                errors=errors,
                stats=stats,
                success=True,
                message=message
            )
            
        except Exception as e:
            logger.error(f"校对过程中出错: {e}", exc_info=True)
            return ProofreadingResult(
                input_path=input_path,
                output_path=output_path,
                report_path=report_path,
                errors=[],
                stats={},
                success=False,
                message=f"校对失败: {str(e)}"
            )
    
    def _validate_input(self, input_path: str) -> bool:
        """验证输入文件"""
        path = Path(input_path)
        
        if not path.exists():
            logger.error(f"文件不存在: {input_path}")
            return False
        
        if not path.is_file():
            logger.error(f"不是文件: {input_path}")
            return False
        
        if path.suffix.lower() != ".pdf":
            logger.error(f"不是PDF文件: {input_path}")
            return False
        
        # 检查文件大小
        file_size = path.stat().st_size
        max_size = self.config.get("max_file_size_mb", 100) * 1024 * 1024
        
        if file_size > max_size:
            logger.error(f"文件过大: {file_size / (1024*1024):.1f}MB > {max_size / (1024*1024):.1f}MB")
            return False
        
        return True
    
    def _setup_output_paths(self, input_path: str, output_path: Optional[str], 
                           report_path: Optional[str]) -> Tuple[str, str]:
        """设置输出路径"""
        input_dir = Path(input_path).parent
        input_name = Path(input_path).stem
        
        # 输出目录
        output_dir = self.config.get("output_dir")
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = input_dir
        
        # 输出PDF路径
        if not output_path:
            output_path = str(output_dir / f"{input_name}_annotated.pdf")
        
        # 报告文件路径
        if not report_path:
            report_path = str(output_dir / f"{input_name}_report.md")
        
        # 检查是否覆盖
        if not self.config.get("overwrite", False):
            for path in [output_path, report_path]:
                if Path(path).exists():
                    raise FileExistsError(f"文件已存在: {path}")
        
        return output_path, report_path
    
    def _check_all_errors(self, text: str) -> List[Tuple[str, str, int, int, int, str]]:
        """检查所有类型的错误"""
        errors = []
        
        # 检查拼写错误
        if self.config.get("check_spelling", True):
            spelling_errors = self.grammar_checker.check_spelling(text)
            errors.extend(spelling_errors)
        
        # 检查语法错误
        if self.config.get("check_grammar", True):
            grammar_errors = self.grammar_checker.check_grammar(text)
            errors.extend(grammar_errors)
        
        # 检查表达问题
        if self.config.get("check_expression", True):
            expression_errors = self.grammar_checker.check_expression(text)
            errors.extend(expression_errors)
        
        return errors
    
    def _generate_stats(self, text: str, errors: List) -> Dict[str, Any]:
        """生成统计信息"""
        # 基础统计
        stats = {
            "text_length": len(text),
            "total_errors": len(errors),
            "error_types": {},
        }
        
        # 错误类型统计
        for error in errors:
            if len(error) == 6:
                error_type = error[5]
            else:
                error_type = "spelling"
            stats["error_types"][error_type] = stats["error_types"].get(error_type, 0) + 1
        
        # 分页统计
        pages = {}
        for error in errors:
            if len(error) >= 3:
                page_num = error[2]
                pages[page_num] = pages.get(page_num, 0) + 1
        
        stats["errors_by_page"] = pages
        stats["total_pages"] = len(pages)
        
        return stats
    
    def _generate_summary_message(self, stats: Dict[str, Any]) -> str:
        """生成摘要消息"""
        total_errors = stats.get("total_errors", 0)
        
        if total_errors == 0:
            return "未发现明显错误"
        
        error_types = stats.get("error_types", {})
        type_messages = []
        
        for error_type, count in error_types.items():
            type_name = {
                "spelling": "拼写错误",
                "grammar": "语法错误",
                "expression": "表达问题"
            }.get(error_type, error_type)
            type_messages.append(f"{type_name} {count}处")
        
        type_summary = "，".join(type_messages)
        return f"发现 {total_errors} 处错误（{type_summary}）"


def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="PDF文档校对工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s document.pdf
  %(prog)s input.pdf output.pdf report.md
  %(prog)s --config config.yaml document.pdf
        """
    )
    
    parser.add_argument("input", help="输入PDF文件")
    parser.add_argument("output", nargs="?", help="输出PDF文件（可选）")
    parser.add_argument("report", nargs="?", help="报告文件（可选）")
    
    parser.add_argument("--config", "-c", help="配置文件路径")
    parser.add_argument("--output-dir", "-o", help="输出目录")
    parser.add_argument("--overwrite", "-f", action="store_true", help="覆盖已存在文件")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    
    args = parser.parse_args()
    
    # 配置
    config = {
        "output_dir": args.output_dir,
        "overwrite": args.overwrite,
        "verbose": args.verbose,
    }
    
    # 加载配置文件
    if args.config:
        import yaml
        with open(args.config, 'r', encoding='utf-8') as f:
            config.update(yaml.safe_load(f))
    
    # 运行校对
    proofreader = Proofreader(config)
    result = proofreader.check(args.input, args.output, args.report)
    
    # 输出结果
    if result.success:
        print("✓ 校对完成！")
        print(f"   输入文件: {result.input_path}")
        print(f"   输出文件: {result.output_path}")
        print(f"   报告文件: {result.report_path}")
        print(f"   结果: {result.message}")
        
        if result.stats.get("total_errors", 0) > 0:
            print("\n错误统计:")
            for error_type, count in result.stats.get("error_types", {}).items():
                type_name = {
                    "spelling": "拼写错误",
                    "grammar": "语法错误",
                    "expression": "表达问题"
                }.get(error_type, error_type)
                print(f"   {type_name}: {count}处")
    else:
        print(f"✗ 校对失败: {result.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()