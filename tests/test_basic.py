#!/usr/bin/env python3
"""
基本功能测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from src.proofreader import Proofreader
from src.grammar_checker import GrammarChecker
from src.pdf_annotator import PDFAnnotator
from src.report_generator import ReportGenerator
from src.utils import extract_text_from_pdf, validate_pdf_file


class TestGrammarChecker:
    """语法检查器测试"""
    
    def setup_method(self):
        self.checker = GrammarChecker()
    
    def test_check_spelling(self):
        """测试拼写检查"""
        text = "这是一个测试文本。他高兴的跳了起来。"
        errors = self.checker.check_spelling(text)
        
        # 应该检测到"的"误用
        assert len(errors) > 0
        assert any("的" in error[0] for error in errors)
    
    def test_check_grammar(self):
        """测试语法检查"""
        text = "这个问题非常重要非常重要。"
        errors = self.checker.check_grammar(text)
        
        # 应该检测到重复用词
        assert len(errors) > 0
        assert any("重复用词" in error[1] for error in errors)
    
    def test_check_expression(self):
        """测试表达检查"""
        text = "看完电影后，觉得很感动。"
        errors = self.checker.check_expression(text)
        
        # 应该检测到缺少主语
        assert len(errors) > 0
        assert any("缺少明确主语" in error[1] for error in errors)
    
    def test_add_custom_rule(self):
        """测试添加自定义规则"""
        initial_count = len(self.checker.rules)
        
        self.checker.add_rule(
            name="测试规则",
            pattern="测试模式",
            suggestion="测试建议",
            error_type="grammar"
        )
        
        assert len(self.checker.rules) == initial_count + 1


class TestPDFAnnotator:
    """PDF标注器测试"""
    
    def setup_method(self):
        self.annotator = PDFAnnotator()
    
    def test_default_config(self):
        """测试默认配置"""
        config = self.annotator.config
        
        assert "annotations" in config
        assert "spelling" in config["annotations"]
        assert "grammar" in config["annotations"]
        assert "expression" in config["annotations"]
        
        assert "comments" in config
        assert "color" in config["comments"]
    
    def test_group_errors(self):
        """测试错误分组"""
        errors = [
            ("错误1", "建议1", 1, 0, 5, "spelling"),
            ("错误2", "建议2", 2, 0, 5, "grammar"),
            ("错误3", "建议3", 1, 10, 15, "expression"),
        ]
        
        grouped = self.annotator._group_errors_by_page(errors, 3)
        
        assert 1 in grouped
        assert 2 in grouped
        assert len(grouped[1]) == 2
        assert len(grouped[2]) == 1


class TestReportGenerator:
    """报告生成器测试"""
    
    def setup_method(self):
        self.generator = ReportGenerator()
    
    def test_generate_markdown_report(self):
        """测试生成Markdown报告"""
        errors = [
            ("的", "可能应为'得'", 1, 10, 11, "spelling"),
        ]
        
        stats = {
            "text_length": 1000,
            "total_errors": 1,
            "total_pages": 1,
            "error_types": {"spelling": 1},
            "errors_by_page": {1: 1}
        }
        
        report = self.generator._generate_markdown_report(errors, stats)
        
        assert "# PDF校对报告" in report
        assert "错误统计" in report
        assert "的" in report
        assert "可能应为'得'" in report
    
    def test_get_error_type_name(self):
        """测试错误类型名称"""
        assert self.generator._get_error_type_name("spelling") == "拼写错误"
        assert self.generator._get_error_type_name("grammar") == "语法错误"
        assert self.generator._get_error_type_name("expression") == "表达问题"
        assert self.generator._get_error_type_name("unknown") == "unknown"


class TestUtils:
    """工具函数测试"""
    
    def test_validate_pdf_file(self):
        """测试PDF文件验证"""
        # 测试不存在的文件
        result = validate_pdf_file("nonexistent.pdf")
        assert not result["valid"]
        assert "不存在" in result["message"]
    
    def test_format_file_size(self):
        """测试文件大小格式化"""
        from src.utils import format_file_size
        
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
    
    def test_create_output_filename(self):
        """测试创建输出文件名"""
        from src.utils import create_output_filename
        
        filename = create_output_filename("document.pdf", "annotated")
        assert filename == "document_annotated.pdf"
        
        filename = create_output_filename("/path/to/document.pdf", "checked")
        assert filename == "document_checked.pdf"


class TestIntegration:
    """集成测试"""
    
    def test_proofreader_initialization(self):
        """测试校对器初始化"""
        proofreader = Proofreader()
        assert proofreader is not None
        assert proofreader.config is not None
        assert proofreader.grammar_checker is not None
        assert proofreader.pdf_annotator is not None
        assert proofreader.report_generator is not None
    
    def test_empty_config(self):
        """测试空配置"""
        proofreader = Proofreader({})
        assert proofreader.config is not None


if __name__ == "__main__":
    # 运行所有测试
    print("运行PDF校对工具测试...")
    print("=" * 50)
    
    # 创建测试实例
    test_classes = [
        TestGrammarChecker(),
        TestPDFAnnotator(),
        TestReportGenerator(),
        TestUtils(),
        TestIntegration(),
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n测试类: {class_name}")
        
        # 获取测试方法
        test_methods = [m for m in dir(test_class) if m.startswith('test_')]
        
        for method_name in test_methods:
            test_method = getattr(test_class, method_name)
            
            try:
                # 执行setup_method（如果存在）
                if hasattr(test_class, 'setup_method'):
                    test_class.setup_method()
                
                # 运行测试
                test_method()
                print(f"  ✓ {method_name}")
                passed += 1
                
            except AssertionError as e:
                print(f"  ✗ {method_name}: {e}")
                failed += 1
            except Exception as e:
                print(f"  ✗ {method_name}: 异常 {e}")
                failed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("所有测试通过！🎉")
    else:
        print(f"有 {failed} 个测试失败")
        sys.exit(1)