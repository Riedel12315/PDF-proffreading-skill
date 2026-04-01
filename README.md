# PDF Proofreading Tool 📚✏️

一个智能的PDF文档校对工具，自动检查中文文档中的拼写错误、语法问题和表达不通顺之处，并提供可视化标注和修改建议。

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![GitHub Stars](https://img.shields.io/github/stars/yourusername/pdf-proofreading-tool?style=social)

## ✨ 功能特性

### 🔍 智能检查
- **拼写检查**：自动检测常见中文错别字（的/得/地、在/再、做/作等）
- **语法检查**：识别重复用词、冗长表达、被动语态过度等问题
- **表达检查**：分析句子结构、逻辑连接、修饰语位置等表达问题

### 🎨 可视化标注
- **红色矩形框**：拼写错误
- **红色下划线**：语法错误  
- **红色波浪线**：表达不通顺问题
- **黄色注释框**：详细的修改建议

### 📊 详细报告
- 错误类型统计
- 分页错误列表
- 具体位置信息
- 修改建议说明

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/pdf-proofreading-tool.git
cd pdf-proofreading-tool

# 安装依赖
pip install -r requirements.txt
```

### 基本使用

```bash
# 校对单个PDF文件
python -m src.proofreader your_document.pdf

# 会自动生成：
#   - your_document_annotated.pdf（带标注的PDF）
#   - your_document_report.md（详细报告）
```

### 高级选项

```bash
# 指定输出文件
python -m src.proofreader input.pdf output.pdf report.md

# 批量处理目录下所有PDF
python scripts/batch_process.py ./documents
```

## 📖 使用示例

### 1. 检查拼写错误
```python
from src.proofreader import Proofreader

proofreader = Proofreader()
result = proofreader.check("book.pdf")
print(f"发现 {len(result.errors)} 处错误")
```

### 2. 自定义检查规则
```python
from src.grammar_checker import GrammarChecker

# 添加自定义规则
checker = GrammarChecker()
checker.add_rule(r"(\S+)\s+\1", "重复用词")
```

### 3. 生成标注PDF
```python
from src.pdf_annotator import PDFAnnotator

annotator = PDFAnnotator()
annotator.annotate("input.pdf", "output.pdf", errors)
```

## 🛠️ 技术架构

```
pdf-proofreading-tool/
├── src/                         # 源代码
│   ├── proofreader.py          # 主校对程序
│   ├── grammar_checker.py      # 语法检查模块
│   ├── pdf_annotator.py        # PDF标注模块
│   └── utils.py                # 工具函数
├── examples/                    # 示例文件
├── tests/                       # 测试文件
├── docs/                        # 文档
└── scripts/                     # 辅助脚本
```

### 核心模块

1. **Proofreader**：协调整个校对流程
2. **GrammarChecker**：语法和表达检查引擎
3. **PDFAnnotator**：PDF标注和注释生成
4. **ReportGenerator**：报告生成器

## 📋 支持的错误类型

### 拼写错误
- 的/得/地混用
- 在/再混用
- 做/作混用
- 象/像混用
- 那/哪混用
- 即/既混用
- 须/需混用
- 至/致混用

### 语法错误
- 重复用词
- 冗长表达（"进行...的工作"）
- 被动语态过度（"被...所"）
- "的"字过多
- 句子过长（>50字无标点）
- 搭配不当

### 表达问题
- 句子结构不完整
- 逻辑连接不当
- 修饰语位置错误
- 语序问题

## 🔧 配置选项

创建 `config.yaml` 文件：

```yaml
proofreading:
  # 检查选项
  check_spelling: true
  check_grammar: true
  check_expression: true
  
  # 标注样式
  annotations:
    spelling:
      color: "#FF0000"
      style: "rectangle"
    grammar:
      color: "#FF0000"
      style: "underline"
    expression:
      color: "#FF0000"
      style: "wavy"
  
  # 性能设置
  performance:
    max_file_size_mb: 50
    timeout_seconds: 300
```

## 📈 性能优化

- **增量处理**：大文件分页处理
- **缓存机制**：文本提取结果缓存
- **并行处理**：多文件批量处理
- **内存优化**：流式处理大文件

## 🧪 测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_proofreader.py

# 生成测试覆盖率报告
pytest --cov=src tests/
```

## 📚 文档

- [详细使用指南](docs/usage.md)
- [API参考](docs/api.md)
- [开发指南](docs/development.md)
- [常见问题](docs/faq.md)

## 🤝 贡献指南

欢迎贡献代码！请阅读[贡献指南](CONTRIBUTING.md)。

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF文本提取
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF标注和注释
- [reportlab](https://www.reportlab.com/) - PDF生成

## 📞 联系方式

如有问题或建议，请：
- 提交 [Issue](https://github.com/yourusername/pdf-proofreading-tool/issues)
- 发送邮件至：your.email@example.com

---

⭐ 如果这个项目对你有帮助，请给个 Star！