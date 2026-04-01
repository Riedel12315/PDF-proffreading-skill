#!/usr/bin/env python3
"""
语法和表达检查器
检查中文文档中的语法错误和表达问题
"""

import re
import logging
from typing import List, Tuple, Dict, Any, Optional, Pattern
from dataclasses import dataclass
from .utils import setup_logging

logger = setup_logging(__name__)


@dataclass
class GrammarRule:
    """语法规则数据类"""
    name: str
    pattern: str
    suggestion: str
    error_type: str
    compiled_pattern: Optional[Pattern] = None
    
    def compile(self):
        """编译正则表达式"""
        if self.compiled_pattern is None:
            self.compiled_pattern = re.compile(self.pattern)
        return self.compiled_pattern


class GrammarChecker:
    """语法检查器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化语法检查器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.rules = self._load_rules()
        logger.info(f"语法检查器初始化完成，加载了 {len(self.rules)} 条规则")
    
    def _load_rules(self) -> List[GrammarRule]:
        """加载语法规则"""
        rules = []
        
        # 拼写错误规则
        spelling_rules = [
            # 的/得/地
            GrammarRule(
                name="的得地混用",
                pattern=r"的(?=[^的地得]{0,10}[得地])|得(?=[^的地得]{0,10}的)|地(?=[^的地得]{0,10}的)",
                suggestion="检查'的/得/地'使用是否正确",
                error_type="spelling"
            ),
            # 在/再
            GrammarRule(
                name="在再混用",
                pattern=r"在(?=次|度|三|说|见)|再(?=家|场|前|后)",
                suggestion="检查'在/再'使用是否正确",
                error_type="spelling"
            ),
            # 做/作
            GrammarRule(
                name="做作混用",
                pattern=r"做(?=品|家|文|曲)|作(?=饭|事|工|业)",
                suggestion="检查'做/作'使用是否正确",
                error_type="spelling"
            ),
            # 象/像
            GrammarRule(
                name="象像混用",
                pattern=r"象(?=是|这样|那样)|像(?=征|棋|牙)",
                suggestion="检查'象/像'使用是否正确",
                error_type="spelling"
            ),
            # 那/哪
            GrammarRule(
                name="那哪混用",
                pattern=r"那(?=里|个|些|么)|哪(?=人|时|样|种)",
                suggestion="检查'那/哪'使用是否正确",
                error_type="spelling"
            ),
        ]
        rules.extend(spelling_rules)
        
        # 语法错误规则
        grammar_rules = [
            # 重复用词
            GrammarRule(
                name="重复用词",
                pattern=r"(\S{2,})\s+\1",
                suggestion="重复用词，建议删除或替换其中一个",
                error_type="grammar"
            ),
            # 冗长表达
            GrammarRule(
                name="进行...的工作",
                pattern=r"进行\s+(\S+)\s+的工作",
                suggestion="表达冗长，建议简化为'$1'",
                error_type="grammar"
            ),
            GrammarRule(
                name="做出...的决定",
                pattern=r"做出\s+(\S+)\s+的决定",
                suggestion="表达冗长，建议简化为'决定$1'",
                error_type="grammar"
            ),
            # 被动语态
            GrammarRule(
                name="被...所",
                pattern=r"被(\S+)所",
                suggestion="被动语态，建议改为主动语态",
                error_type="grammar"
            ),
            # 的字过多
            GrammarRule(
                name="的字过多",
                pattern=r"的.*的.*的",
                suggestion="连续使用多个'的'，建议简化表达",
                error_type="grammar"
            ),
            # 句子过长
            GrammarRule(
                name="句子过长",
                pattern=r"[^。！？]{50,}",
                suggestion="句子过长，建议添加标点或拆分句子",
                error_type="grammar"
            ),
        ]
        rules.extend(grammar_rules)
        
        # 从配置文件加载自定义规则
        custom_rules = self.config.get("custom_rules", [])
        for rule_config in custom_rules:
            rule = GrammarRule(
                name=rule_config.get("name", "自定义规则"),
                pattern=rule_config.get("pattern", ""),
                suggestion=rule_config.get("suggestion", "请检查此处"),
                error_type=rule_config.get("error_type", "grammar")
            )
            rules.append(rule)
        
        return rules
    
    def add_rule(self, name: str, pattern: str, suggestion: str, error_type: str = "grammar"):
        """添加自定义规则"""
        rule = GrammarRule(
            name=name,
            pattern=pattern,
            suggestion=suggestion,
            error_type=error_type
        )
        self.rules.append(rule)
        logger.info(f"添加自定义规则: {name}")
    
    def check_spelling(self, text: str) -> List[Tuple[str, str, int, int, int, str]]:
        """
        检查拼写错误
        
        Args:
            text: 文本内容
            
        Returns:
            错误列表：(错误文本, 建议, 页码, 起始位置, 结束位置, 错误类型)
        """
        return self._check_with_rules(text, ["spelling"])
    
    def check_grammar(self, text: str) -> List[Tuple[str, str, int, int, int, str]]:
        """
        检查语法错误
        
        Args:
            text: 文本内容
            
        Returns:
            错误列表
        """
        return self._check_with_rules(text, ["grammar"])
    
    def check_expression(self, text: str) -> List[Tuple[str, str, int, int, int, str]]:
        """
        检查表达问题
        
        Args:
            text: 文本内容
            
        Returns:
            错误列表
        """
        errors = []
        
        # 分页处理
        pages = text.split("=== 第")
        for page_str in pages[1:]:  # 跳过第一个空元素
            # 提取页码
            page_match = re.match(r"(\d+)页 ===\n", page_str)
            if not page_match:
                continue
            page_num = int(page_match.group(1))
            page_content = page_str[page_match.end():]
            
            # 检查句子结构问题
            sentence_errors = self._check_sentence_structure(page_content, page_num)
            errors.extend(sentence_errors)
        
        return errors
    
    def check_all(self, text: str) -> List[Tuple[str, str, int, int, int, str]]:
        """
        检查所有类型的错误
        
        Args:
            text: 文本内容
            
        Returns:
            所有错误列表
        """
        errors = []
        errors.extend(self.check_spelling(text))
        errors.extend(self.check_grammar(text))
        errors.extend(self.check_expression(text))
        return errors
    
    def _check_with_rules(self, text: str, error_types: List[str]) -> List[Tuple[str, str, int, int, int, str]]:
        """
        使用指定类型的规则检查文本
        
        Args:
            text: 文本内容
            error_types: 要检查的错误类型列表
            
        Returns:
            错误列表
        """
        errors = []
        
        # 筛选规则
        target_rules = [rule for rule in self.rules if rule.error_type in error_types]
        
        # 分页处理
        pages = text.split("=== 第")
        for page_str in pages[1:]:  # 跳过第一个空元素
            # 提取页码
            page_match = re.match(r"(\d+)页 ===\n", page_str)
            if not page_match:
                continue
            page_num = int(page_match.group(1))
            page_content = page_str[page_match.end():]
            
            # 应用规则
            for rule in target_rules:
                pattern = rule.compile()
                for match in pattern.finditer(page_content):
                    error_text = match.group()
                    
                    # 生成建议（处理替换引用）
                    suggestion = rule.suggestion
                    if "$1" in suggestion and match.groups():
                        suggestion = suggestion.replace("$1", match.group(1))
                    
                    errors.append((
                        error_text,
                        suggestion,
                        page_num,
                        match.start(),
                        match.end(),
                        rule.error_type
                    ))
        
        return errors
    
    def _check_sentence_structure(self, page_content: str, page_num: int) -> List[Tuple[str, str, int, int, int, str]]:
        """
        检查句子结构问题
        
        Args:
            page_content: 页面内容
            page_num: 页码
            
        Returns:
            错误列表
        """
        errors = []
        
        # 分割句子
        sentences = re.split(r"[。！？；]", page_content)
        sentence_start = 0
        
        for sentence in sentences:
            if not sentence.strip():
                sentence_start += len(sentence) + 1
                continue
            
            sentence_end = sentence_start + len(sentence)
            sentence_text = sentence.strip()
            
            # 检查主语缺失
            if self._has_subject_issue(sentence_text):
                error_pos = page_content.find(sentence_text, sentence_start)
                if error_pos != -1:
                    errors.append((
                        sentence_text,
                        "句子可能缺少明确主语",
                        page_num,
                        error_pos,
                        error_pos + len(sentence_text),
                        "expression"
                    ))
            
            # 检查谓语缺失
            if self._has_predicate_issue(sentence_text):
                error_pos = page_content.find(sentence_text, sentence_start)
                if error_pos != -1:
                    errors.append((
                        sentence_text,
                        "句子可能缺少明确谓语",
                        page_num,
                        error_pos,
                        error_pos + len(sentence_text),
                        "expression"
                    ))
            
            # 检查逻辑连接
            logic_errors = self._check_logic_connection(sentence_text)
            for error_text, suggestion in logic_errors:
                error_pos = page_content.find(error_text, sentence_start)
                if error_pos != -1:
                    errors.append((
                        error_text,
                        suggestion,
                        page_num,
                        error_pos,
                        error_pos + len(error_text),
                        "expression"
                    ))
            
            # 检查修饰语
            modifier_errors = self._check_modifiers(sentence_text)
            for error_text, suggestion in modifier_errors:
                error_pos = page_content.find(error_text, sentence_start)
                if error_pos != -1:
                    errors.append((
                        error_text,
                        suggestion,
                        page_num,
                        error_pos,
                        error_pos + len(error_text),
                        "expression"
                    ))
            
            sentence_start = sentence_end + 1
        
        return errors
    
    def _has_subject_issue(self, sentence: str) -> bool:
        """检查是否缺少主语"""
        # 长句但没有明显主语
        if len(sentence) > 10:
            subject_words = ["我", "我们", "你", "你们", "他", "她", "它", "他们", "这", "那", "此"]
            if not any(word in sentence for word in subject_words):
                return True
        return False
    
    def _has_predicate_issue(self, sentence: str) -> bool:
        """检查是否缺少谓语"""
        # 有多个词语但无明确谓语
        words = sentence.split()
        if len(words) > 3:
            predicate_words = ["是", "有", "在", "做", "说", "进行", "完成", "开始", "结束"]
            if not any(word in sentence for word in predicate_words):
                return True
        return False
    
    def _check_logic_connection(self, sentence: str) -> List[Tuple[str, str]]:
        """检查逻辑连接问题"""
        errors = []
        
        # 检查配对逻辑词
        if "因为" in sentence and "所以" not in sentence:
            errors.append((sentence, "'因为'缺少对应的'所以'"))
        
        if "虽然" in sentence and "但是" not in sentence:
            errors.append((sentence, "'虽然'缺少对应的'但是'"))
        
        if "不仅" in sentence and "而且" not in sentence:
            errors.append((sentence, "'不仅'缺少对应的'而且'"))
        
        return errors
    
    def _check_modifiers(self, sentence: str) -> List[Tuple[str, str]]:
        """检查修饰语问题"""
        errors = []
        
        # 检查"地"的使用
        if "地" in sentence:
            parts = sentence.split("地")
            if len(parts) > 1 and parts[1].strip():
                next_word = parts[1].strip().split()[0]
                # 简单动词检查
                verbs = ["说", "做", "走", "跑", "看", "听", "写", "读", "想", "笑"]
                if not any(verb in next_word for verb in verbs):
                    errors.append((sentence, "'地'后面可能应该接动词"))
        
        # 检查"得"的使用
        if "得" in sentence:
            parts = sentence.split("得")
            if len(parts) > 1 and parts[0].strip():
                prev_word = parts[0].strip().split()[-1]
                # 前面应该是动词或形容词
                adjectives = ["好", "快", "慢", "高", "低", "大", "小", "多", "少"]
                if not any(adj in prev_word for adj in adjectives):
                    errors.append((sentence, "'得'前面应该是动词或形容词"))
        
        return errors
    
    def get_rule_stats(self) -> Dict[str, Any]:
        """获取规则统计信息"""
        stats = {
            "total_rules": len(self.rules),
            "rules_by_type": {},
            "rule_names": []
        }
        
        for rule in self.rules:
            stats["rules_by_type"][rule.error_type] = stats["rules_by_type"].get(rule.error_type, 0) + 1
            stats["rule_names"].append(rule.name)
        
        return stats


if __name__ == "__main__":
    # 测试代码
    checker = GrammarChecker()
    
    test_text = """
    这是一个测试文本。
    他高兴的跳了起来，这是一个错误。
    我们需要进行市场调研的工作，这也是一个错误。
    因为下雨，比赛取消了，这缺少'所以'。
    """
    
    print("测试拼写检查:")
    errors = checker.check_spelling(test_text)
    for error in errors:
        print(f"  {error}")
    
    print("\n测试语法检查:")
    errors = checker.check_grammar(test_text)
    for error in errors:
        print(f"  {error}")
    
    print("\n规则统计:")
    stats = checker.get_rule_stats()
    print(f"  总规则数: {stats['total_rules']}")
    for error_type, count in stats["rules_by_type"].items():
        print(f"  {error_type}: {count}")