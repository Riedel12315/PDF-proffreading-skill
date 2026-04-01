#!/usr/bin/env python3
"""
报告生成器
生成详细的PDF校对报告
"""

import os
import re
import logging
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from .utils import setup_logging

logger = setup_logging(__name__)


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化报告生成器
        
        Args:
            config: 配置字典
        """
        self.config = config or self._default_config()
        logger.info("报告生成器初始化完成")
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "format": "markdown",  # markdown, html, text
            "include_summary": True,
            "include_details": True,
            "include_statistics": True,
            "include_recommendations": True,
            "max_errors_per_page": 50,
            "output_encoding": "utf-8",
        }
    
    def generate(self, report_path: str, errors: List[Tuple], stats: Dict[str, Any]) -> bool:
        """
        生成校对报告
        
        Args:
            report_path: 报告文件路径
            errors: 错误列表
            stats: 统计信息
            
        Returns:
            bool: 是否成功
        """
        logger.info(f"生成报告: {report_path}")
        
        try:
            # 确定报告格式
            report_format = self._detect_format(report_path)
            
            # 生成报告内容
            if report_format == "html":
                content = self._generate_html_report(errors, stats)
            elif report_format == "markdown":
                content = self._generate_markdown_report(errors, stats)
            else:
                content = self._generate_text_report(errors, stats)
            
            # 写入文件
            with open(report_path, 'w', encoding=self.config["output_encoding"]) as f:
                f.write(content)
            
            logger.info(f"报告生成完成: {report_path} ({len(content)} 字符)")
            return True
            
        except Exception as e:
            logger.error(f"生成报告时出错: {e}", exc_info=True)
            return False
    
    def _detect_format(self, report_path: str) -> str:
        """检测报告格式"""
        path = Path(report_path)
        suffix = path.suffix.lower()
        
        if suffix == ".html":
            return "html"
        elif suffix == ".md" or suffix == ".markdown":
            return "markdown"
        else:
            return self.config.get("format", "markdown")
    
    def _generate_markdown_report(self, errors: List[Tuple], stats: Dict[str, Any]) -> str:
        """生成Markdown格式报告"""
        lines = []
        
        # 标题
        lines.append("# PDF校对报告")
        lines.append("")
        
        # 基本信息
        lines.append("## 基本信息")
        lines.append("")
        lines.append(f"- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- **文档字数**: {stats.get('text_length', 0)} 字")
        lines.append(f"- **总页数**: {stats.get('total_pages', 0)} 页")
        lines.append("")
        
        # 错误统计
        if self.config.get("include_statistics", True):
            lines.append("## 错误统计")
            lines.append("")
            
            total_errors = stats.get("total_errors", 0)
            lines.append(f"**发现错误总数**: {total_errors}")
            lines.append("")
            
            if total_errors > 0:
                # 错误类型统计
                error_types = stats.get("error_types", {})
                if error_types:
                    lines.append("### 错误类型分布")
                    lines.append("")
                    for error_type, count in error_types.items():
                        type_name = self._get_error_type_name(error_type)
                        lines.append(f"- **{type_name}**: {count} 处")
                    lines.append("")
                
                # 分页统计
                errors_by_page = stats.get("errors_by_page", {})
                if errors_by_page:
                    lines.append("### 分页错误统计")
                    lines.append("")
                    for page_num, error_count in sorted(errors_by_page.items()):
                        lines.append(f"- **第 {page_num} 页**: {error_count} 处")
                    lines.append("")
        
        # 详细错误列表
        if self.config.get("include_details", True) and errors:
            lines.append("## 详细错误列表")
            lines.append("")
            
            # 按页码分组
            errors_by_page = {}
            for error in errors:
                if len(error) >= 3:
                    page_num = error[2]
                    if page_num not in errors_by_page:
                        errors_by_page[page_num] = []
                    errors_by_page[page_num].append(error)
            
            # 按页码排序
            for page_num in sorted(errors_by_page.keys()):
                page_errors = errors_by_page[page_num]
                
                lines.append(f"### 第 {page_num} 页")
                lines.append("")
                
                for i, error in enumerate(page_errors, 1):
                    if len(error) == 6:
                        error_text, correction, _, start_pos, end_pos, error_type = error
                    else:
                        error_text, correction, _, start_pos, end_pos = error
                        error_type = "spelling"
                    
                    type_name = self._get_error_type_name(error_type)
                    
                    lines.append(f"#### 错误 {i}")
                    lines.append(f"- **错误类型**: {type_name}")
                    lines.append(f"- **错误文本**: `{error_text}`")
                    lines.append(f"- **建议修改**: {correction}")
                    lines.append(f"- **位置**: 字符 {start_pos}-{end_pos}")
                    lines.append("")
                
                # 限制每页错误数量
                if len(page_errors) > self.config.get("max_errors_per_page", 50):
                    lines.append(f"*注：本页还有 {len(page_errors) - self.config['max_errors_per_page']} 个错误未显示*")
                    lines.append("")
        
        # 修改建议
        if self.config.get("include_recommendations", True) and errors:
            lines.append("## 修改建议")
            lines.append("")
            
            recommendations = self._generate_recommendations(stats)
            for rec in recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        # 报告摘要
        if self.config.get("include_summary", True):
            lines.append("## 报告摘要")
            lines.append("")
            
            total_errors = stats.get("total_errors", 0)
            if total_errors == 0:
                lines.append("✅ 文档质量良好，未发现明显错误。")
            else:
                lines.append(f"📝 文档共发现 {total_errors} 处需要修改的地方。")
                lines.append("")
                lines.append("**建议修改优先级**:")
                lines.append("1. 拼写错误（红色矩形框）")
                lines.append("2. 语法错误（红色下划线）")
                lines.append("3. 表达问题（红色波浪线）")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_html_report(self, errors: List[Tuple], stats: Dict[str, Any]) -> str:
        """生成HTML格式报告"""
        # 将Markdown转换为HTML（简化版本）
        markdown_content = self._generate_markdown_report(errors, stats)
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF校对报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .error-type {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 10px; }}
        .spelling {{ background: #ffeaea; color: #c0392b; }}
        .grammar {{ background: #fff3cd; color: #856404; }}
        .expression {{ background: #d4edda; color: #155724; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat-box {{ flex: 1; padding: 15px; border-radius: 8px; text-align: center; }}
        .total-errors {{ background: #ffeaea; }}
        .pages {{ background: #e3f2fd; }}
        .words {{ background: #e8f5e9; }}
        code {{ background: #f5f5f5; padding: 2px 4px; border-radius: 3px; font-family: 'Courier New', monospace; }}
        .recommendation {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #3498db; }}
        @media (max-width: 600px) {{
            .stats {{ flex-direction: column; }}
        }}
    </style>
</head>
<body>
    <h1>📄 PDF校对报告</h1>
    
    <div class="stats">
        <div class="stat-box total-errors">
            <h3>总错误数</h3>
            <h2>{stats.get('total_errors', 0)}</h2>
        </div>
        <div class="stat-box pages">
            <h3>总页数</h3>
            <h2>{stats.get('total_pages', 0)}</h2>
        </div>
        <div class="stat-box words">
            <h3>文档字数</h3>
            <h2>{stats.get('text_length', 0)}</h2>
        </div>
    </div>
    
    {self._markdown_to_html(markdown_content)}
    
    <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; color: #7f8c8d; font-size: 14px;">
        <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>生成工具: PDF Proofreading Tool v1.0.0</p>
    </footer>
</body>
</html>"""
        
        return html
    
    def _markdown_to_html(self, markdown: str) -> str:
        """将Markdown转换为HTML（简化版本）"""
        html = markdown
        
        # 转换标题
        html = html.replace("# ", "<h1>").replace("\n# ", "</h1>\n<h1>")
        html = html.replace("## ", "<h2>").replace("\n## ", "</h2>\n<h2>")
        html = html.replace("### ", "<h3>").replace("\n### ", "</h3>\n<h3>")
        html = html.replace("#### ", "<h4>").replace("\n#### ", "</h4>\n<h4>")
        
        # 转换列表
        html = html.replace("- ", "<li>").replace("\n- ", "</li>\n<li>")
        html = re.sub(r"(<li>.*?</li>)", r"<ul>\1</ul>", html, flags=re.DOTALL)
        
        # 转换代码
        html = html.replace("`", "<code>").replace("`", "</code>")
        
        # 转换粗体
        html = html.replace("**", "<strong>").replace("**", "</strong>")
        
        return html
    
    def _generate_text_report(self, errors: List[Tuple], stats: Dict[str, Any]) -> str:
        """生成纯文本格式报告"""
        lines = []
        
        lines.append("=" * 60)
        lines.append("PDF校对报告")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"文档字数: {stats.get('text_length', 0)} 字")
        lines.append(f"总页数: {stats.get('total_pages', 0)} 页")
        lines.append("")
        
        total_errors = stats.get("total_errors", 0)
        lines.append(f"发现错误总数: {total_errors}")
        lines.append("")
        
        if total_errors > 0:
            # 错误类型统计
            error_types = stats.get("error_types", {})
            if error_types:
                lines.append("错误类型分布:")
                for error_type, count in error_types.items():
                    type_name = self._get_error_type_name(error_type)
                    lines.append(f"  {type_name}: {count} 处")
                lines.append("")
            
            # 详细错误
            lines.append("详细错误列表:")
            lines.append("-" * 40)
            
            for i, error in enumerate(errors, 1):
                if len(error) == 6:
                    error_text, correction, page_num, start_pos, end_pos, error_type = error
                else:
                    error_text, correction, page_num, start_pos, end_pos = error
                    error_type = "spelling"
                
                type_name = self._get_error_type_name(error_type)
                
                lines.append(f"错误 {i}:")
                lines.append(f"  页码: 第 {page_num} 页")
                lines.append(f"  类型: {type_name}")
                lines.append(f"  文本: {error_text}")
                lines.append(f"  建议: {correction}")
                lines.append(f"  位置: 字符 {start_pos}-{end_pos}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _get_error_type_name(self, error_type: str) -> str:
        """获取错误类型名称"""
        type_names = {
            "spelling": "拼写错误",
            "grammar": "语法错误",
            "expression": "表达问题"
        }
        return type_names.get(error_type, error_type)
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """生成修改建议"""
        recommendations = []
        error_types = stats.get("error_types", {})
        
        # 拼写错误建议
        if error_types.get("spelling", 0) > 0:
            recommendations.append("仔细检查所有拼写错误，特别是'的/得/地'、'在/再'等常见混用")
        
        # 语法错误建议
        if error_types.get("grammar", 0) > 0:
            recommendations.append("简化冗长表达，避免使用'进行...的工作'、'做出...的决定'等结构")
            recommendations.append("减少被动语态的使用，改为主动语态")
            recommendations.append("避免连续使用多个'的'，简化定语结构")
        
        # 表达问题建议
        if error_types.get("expression", 0) > 0:
            recommendations.append("确保每个句子都有明确的主语和谓语")
            recommendations.append("检查逻辑连接词的使用是否恰当（如'因为...所以'、'虽然...但是'）")
            recommendations.append("注意修饰语的位置，'地'后面应该接动词，'得'前面应该是动词或形容词")
        
        # 通用建议
        total_errors = stats.get("total_errors", 0)
        if total_errors > 0:
            recommendations.append("建议按照错误类型优先级进行修改：先处理拼写错误，再处理语法错误，最后处理表达问题")
            recommendations.append("修改后建议重新校对一次，确保所有问题都已解决")
        
        return recommendations
    
    def generate_summary(self, stats: Dict[str, Any]) -> str:
        """生成摘要报告"""
        total_errors = stats.get("total_errors", 0)
        
        if total_errors == 0:
            return "✅ 文档质量良好，未发现明显错误。"
        
        error_types = stats.get("error_types", {})
        type_details = []
        
        for error_type, count in error_types.items():
            type_name = self._get_error_type_name(error_type)
            type_details.append(f"{type_name} {count}处")
        
        details = "，".join(type_details)
        return f"📝 发现 {total_errors} 处需要修改的地方（{details}）。"


if __name__ == "__main__":
    # 测试代码
    generator = ReportGenerator()
    
    # 测试数据
    test_errors = [
        ("的", "可能应为'得'", 1, 10, 11, "spelling"),
        ("进行市场调研的工作", "表达冗长，建议简化为'市场调研'", 1, 50, 60, "grammar"),
        ("因为下雨", "'因为'缺少对应的'所以'", 2, 30, 34, "expression"),
    ]
    
    test_stats = {
        "text_length": 1500,
        "total_errors": 3,
        "total_pages": 2,
        "error_types": {
            "spelling": 1,
            "grammar": 1,
            "expression": 1
        },
        "errors_by_page": {
            1: 2,
            2: 1
        }
    }
    
    print("测试Markdown报告:")
    report = generator._generate_markdown_report(test_errors, test_stats)
