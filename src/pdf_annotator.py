#!/usr/bin/env python3
"""
PDF标注器
在PDF文档上添加各种类型的标注和注释
"""

import fitz  # PyMuPDF
import logging
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
from .utils import setup_logging

logger = setup_logging(__name__)


class PDFAnnotator:
    """PDF标注器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化PDF标注器
        
        Args:
            config: 配置字典
        """
        self.config = config or self._default_config()
        logger.info("PDF标注器初始化完成")
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "annotations": {
                "spelling": {
                    "color": (1, 0, 0),  # 红色
                    "style": "rectangle",
                    "border_width": 1.5,
                    "opacity": 0.3,
                },
                "grammar": {
                    "color": (1, 0, 0),  # 红色
                    "style": "underline",
                    "border_width": 0,
                    "opacity": 0.7,
                },
                "expression": {
                    "color": (1, 0, 0),  # 红色
                    "style": "wavy",
                    "border_width": 0,
                    "opacity": 0.6,
                }
            },
            "comments": {
                "color": (1, 0, 0),  # 红色边框
                "fill_color": (1, 1, 0.8),  # 浅黄色填充
                "opacity": 0.9,
                "font_size": 9,
                "offset": 20,  # 注释距离文本的偏移
            },
            "performance": {
                "max_pages": 1000,
                "timeout_seconds": 300,
            }
        }
    
    def annotate(self, input_path: str, output_path: str, 
                errors: List[Tuple[str, str, int, int, int, str]]) -> bool:
        """
        在PDF上添加标注
        
        Args:
            input_path: 输入PDF路径
            output_path: 输出PDF路径
            errors: 错误列表
            
        Returns:
            bool: 是否成功
        """
        logger.info(f"开始标注: {input_path} -> {output_path}")
        
        try:
            # 打开PDF文档
            doc = fitz.open(input_path)
            total_pages = len(doc)
            
            # 按页码分组错误
            errors_by_page = self._group_errors_by_page(errors, total_pages)
            
            # 为每页添加标注
            for page_num, page_errors in errors_by_page.items():
                if page_num > total_pages:
                    logger.warning(f"页码 {page_num} 超出文档范围（共 {total_pages} 页）")
                    continue
                
                page = doc[page_num - 1]  # 转换为0-based索引
                self._annotate_page(page, page_errors, page_num)
            
            # 保存文档
            doc.save(output_path)
            doc.close()
            
            logger.info(f"标注完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"标注过程中出错: {e}", exc_info=True)
            return False
    
    def _group_errors_by_page(self, errors: List[Tuple], total_pages: int) -> Dict[int, List]:
        """按页码分组错误"""
        errors_by_page = {}
        
        for error in errors:
            if len(error) == 6:
                error_text, correction, page_num, start_pos, end_pos, error_type = error
            else:
                # 兼容旧格式
                error_text, correction, page_num, start_pos, end_pos = error
                error_type = "spelling"
            
            # 验证页码
            if page_num < 1 or page_num > total_pages:
                logger.warning(f"忽略无效页码 {page_num} 的错误")
                continue
            
            if page_num not in errors_by_page:
                errors_by_page[page_num] = []
            
            errors_by_page[page_num].append({
                "text": error_text,
                "correction": correction,
                "start_pos": start_pos,
                "end_pos": end_pos,
                "type": error_type
            })
        
        # 按页码排序
        return dict(sorted(errors_by_page.items()))
    
    def _annotate_page(self, page, page_errors: List[Dict], page_num: int):
        """为单个页面添加标注"""
        logger.debug(f"处理第 {page_num} 页，共 {len(page_errors)} 个错误")
        
        for error in page_errors:
            error_text = error["text"]
            correction = error["correction"]
            error_type = error["type"]
            
            # 搜索错误文本
            text_instances = page.search_for(error_text)
            if not text_instances:
                logger.debug(f"在第 {page_num} 页未找到文本: '{error_text}'")
                continue
            
            # 取第一个匹配项
            rect = text_instances[0]
            
            # 根据错误类型添加标注
            self._add_annotation_by_type(page, rect, error_type)
            
            # 添加注释
            self._add_comment(page, rect, correction, error_type)
    
    def _add_annotation_by_type(self, page, rect, error_type: str):
        """根据错误类型添加标注"""
        config = self.config["annotations"].get(error_type, {})
        
        if error_type == "spelling":
            # 拼写错误：红色矩形框
            self._add_rectangle_annotation(page, rect, config)
            
        elif error_type == "grammar":
            # 语法错误：红色下划线
            self._add_underline_annotation(page, rect, config)
            
        elif error_type == "expression":
            # 表达问题：红色波浪线
            self._add_wavy_annotation(page, rect, config)
            
        else:
            # 默认使用矩形框
            self._add_rectangle_annotation(page, rect, config)
    
    def _add_rectangle_annotation(self, page, rect, config: Dict[str, Any]):
        """添加矩形标注"""
        annot = page.add_rect_annot(rect)
        
        # 设置颜色
        if "color" in config:
            annot.set_colors(stroke=config["color"])
        
        # 设置边框宽度
        border_width = config.get("border_width", 1.5)
        annot.set_border(width=border_width)
        
        # 设置透明度
        opacity = config.get("opacity", 0.3)
        annot.set_opacity(opacity)
        
        annot.update()
    
    def _add_underline_annotation(self, page, rect, config: Dict[str, Any]):
        """添加下划线标注"""
        # 创建下划线（矩形底部的一条线）
        line_height = 2  # 线的高度
        underline_rect = fitz.Rect(
            rect.x0, rect.y1 - line_height,
            rect.x1, rect.y1
        )
        
        annot = page.add_rect_annot(underline_rect)
        
        # 设置颜色
        if "color" in config:
            annot.set_colors(fill=config["color"])
        
        # 设置边框
        border_width = config.get("border_width", 0)
        annot.set_border(width=border_width)
        
        # 设置透明度
        opacity = config.get("opacity", 0.7)
        annot.set_opacity(opacity)
        
        annot.update()
    
    def _add_wavy_annotation(self, page, rect, config: Dict[str, Any]):
        """添加波浪线标注"""
        wave_count = 10  # 波浪线数量
        wave_height = 2  # 波浪线高度
        wave_width = rect.width / wave_count  # 每个波浪的宽度
        
        for i in range(wave_count):
            x_start = rect.x0 + i * wave_width
            x_end = rect.x0 + (i + 1) * wave_width
            
            # 创建波浪线段（交替高度）
            if i % 2 == 0:
                y_start = rect.y1 - wave_height
                y_end = rect.y1
            else:
                y_start = rect.y1 - wave_height * 0.5
                y_end = rect.y1 - wave_height * 1.5
            
            wave_rect = fitz.Rect(x_start, y_start, x_end, y_end)
            annot = page.add_rect_annot(wave_rect)
            
            # 设置颜色
            if "color" in config:
                annot.set_colors(fill=config["color"])
            
            # 设置边框
            border_width = config.get("border_width", 0)
            annot.set_border(width=border_width)
            
            # 设置透明度
            opacity = config.get("opacity", 0.6)
            annot.set_opacity(opacity)
            
            annot.update()
    
    def _add_comment(self, page, rect, correction: str, error_type: str):
        """添加注释"""
        comment_config = self.config["comments"]
        offset = comment_config.get("offset", 20)
        
        # 注释框位置（在文本上方）
        comment_rect = fitz.Rect(
            rect.x0, rect.y0 - offset,
            rect.x1, rect.y0 - 5
        )
        
        # 添加注释
        annot = page.add_text_annot(comment_rect.tl, correction)
        
        # 设置注释样式
        if "color" in comment_config:
            annot.set_colors(stroke=comment_config["color"])
        
        if "fill_color" in comment_config:
            annot.set_colors(fill=comment_config["fill_color"])
        
        if "opacity" in comment_config:
            annot.set_opacity(comment_config["opacity"])
        
        annot.update()
    
    def preview_annotations(self, input_path: str, page_num: int = 1) -> Dict[str, Any]:
        """
        预览标注效果
        
        Args:
            input_path: PDF路径
            page_num: 页码
            
        Returns:
            标注信息
        """
        try:
            doc = fitz.open(input_path)
            
            if page_num < 1 or page_num > len(doc):
                raise ValueError(f"页码 {page_num} 超出范围")
            
            page = doc[page_num - 1]
            annotations = page.annots()
            
            result = {
                "page": page_num,
                "total_annotations": 0,
                "annotations": []
            }
            
            if annotations:
                for annot in annotations:
                    annot_info = {
                        "type": annot.type[1],  # 标注类型
                        "rect": annot.rect,  # 位置
                        "contents": annot.info.get("content", ""),  # 内容
                        "colors": annot.colors,  # 颜色
                    }
                    result["annotations"].append(annot_info)
                    result["total_annotations"] += 1
            
            doc.close()
            return result
            
        except Exception as e:
            logger.error(f"预览标注时出错: {e}")
            return {"error": str(e)}
    
    def remove_annotations(self, input_path: str, output_path: str) -> bool:
        """
        移除PDF中的所有标注
        
        Args:
            input_path: 输入PDF路径
            output_path: 输出PDF路径
            
        Returns:
            bool: 是否成功
        """
        try:
            doc = fitz.open(input_path)
            annotation_count = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                annotations = page.annots()
                
                if annotations:
                    for annot in annotations:
                        page.delete_annot(annot)
                        annotation_count += 1
            
            doc.save(output_path)
            doc.close()
            
            logger.info(f"移除了 {annotation_count} 个标注: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"移除标注时出错: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    annotator = PDFAnnotator()
    
    # 测试配置
    print("标注器配置:")
    for error_type, config in annotator.config["annotations"].items():
        print(f"  {error_type}: {config}")
    
    print("\n注释配置:")
    for key, value in annotator.config["comments"].items():
        print(f"  {key}: {value}")