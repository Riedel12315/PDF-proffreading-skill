# 使用指南

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/pdf-proofreading-tool.git
cd pdf-proofreading-tool

# 运行安装脚本
./scripts/install.sh

# 激活环境
source activate.sh
```

### 基本使用

```bash
# 校对单个PDF文件
proofread document.pdf

# 会自动生成：
#   - document_annotated.pdf（带标注的PDF）
#   - document_report.md（详细报告）
```

## 命令行选项

### 主程序

```bash
proofread [选项] <输入PDF> [输出PDF] [报告文件]
```

**选项：**
- `-c, --config <文件>`：配置文件路径
- `-o, --output-dir <目录>`：输出目录
- `-f, --overwrite`：覆盖已存在文件
- `-v, --verbose`：详细输出
- `--version`：显示版本信息
- `-h, --help`：显示帮助信息

**示例：**
```bash
# 使用默认配置
proofread book.pdf

# 指定输出文件
proofread input.pdf output.pdf report.md

# 使用自定义配置
proofread --config my_config.yaml document.pdf

# 输出到指定目录
proofread --output-dir ./results document.pdf
```

### 批量处理

```bash
python scripts/batch_process.py [选项] <输入目录>
```

**选项：**
- `-o, --output <目录>`：输出目录（默认：./batch_output）
- `-p, --pattern <模式>`：文件匹配模式（默认：*.pdf）
- `-w, --workers <数量>`：工作线程数（默认：4）
- `-c, --config <文件>`：配置文件路径
- `-f, --overwrite`：覆盖已存在文件
- `-v, --verbose`：详细输出
- `-s, --summary <文件>`：摘要报告文件路径
- `-h, --help`：显示帮助信息

**示例：**
```bash
# 处理目录下所有PDF
python scripts/batch_process.py ./documents

# 使用4个线程处理
python scripts/batch_process.py ./documents --workers 4

# 生成摘要报告
python scripts/batch_process.py ./documents --summary summary.md
```

## 配置文件

### 配置文件格式

支持YAML和JSON格式的配置文件：

```yaml
# config.yaml
check_options:
  check_spelling: true
  check_grammar: true
  check_expression: true

annotations:
  spelling:
    color: [1.0, 0.0, 0.0]
    style: "rectangle"
```

### 配置选项说明

#### 检查选项
- `check_spelling`：是否检查拼写错误
- `check_grammar`：是否检查语法错误  
- `check_expression`：是否检查表达问题
- `max_file_size_mb`：最大文件大小（MB）
- `timeout_seconds`：超时时间（秒）
- `use_cache`：是否使用缓存
- `cache_expiry_hours`：缓存过期时间（小时）

#### 标注样式
- `spelling`：拼写错误标注样式
- `grammar`：语法错误标注样式
- `expression`：表达问题标注样式

每个标注样式包含：
- `color`：RGB颜色数组，如 `[1.0, 0.0, 0.0]` 表示红色
- `style`：标注样式，可选：`rectangle`（矩形）、`underline`（下划线）、`wavy`（波浪线）
- `border_width`：边框宽度
- `opacity`：透明度（0.0-1.0）

#### 注释设置
- `color`：注释边框颜色
- `fill_color`：注释填充颜色
- `opacity`：注释透明度
- `font_size`：字体大小
- `offset`：距离文本的偏移（像素）

#### 报告设置
- `format`：报告格式，可选：`markdown`、`html`、`text`
- `include_summary`：是否包含摘要
- `include_details`：是否包含详细错误列表
- `include_statistics`：是否包含统计信息
- `include_recommendations`：是否包含修改建议
- `max_errors_per_page`：每页最大错误显示数量
- `output_encoding`：输出编码

#### 自定义规则
```yaml
custom_rules:
  - name: "避免使用特定词汇"
    pattern: "非常非常"
    suggestion: "避免重复使用'非常'，建议使用其他表达"
    error_type: "grammar"
```

## 作为Python模块使用

### 基本使用

```python
from src import Proofreader

# 创建校对器
proofreader = Proofreader()

# 校对PDF
result = proofreader.check("document.pdf")

if result.success:
    print(f"校对完成: {result.message}")
    print(f"输出文件: {result.output_path}")
    print(f"报告文件: {result.report_path}")
else:
    print(f"校对失败: {result.message}")
```

### 自定义配置

```python
from src import Proofreader

config = {
    "check_spelling": True,
    "check_grammar": True,
    "check_expression": True,
    "output_dir": "./results",
    "overwrite": False,
}

proofreader = Proofreader(config)
result = proofreader.check("document.pdf")
```

### 使用各个模块

```python
from src.grammar_checker import GrammarChecker
from src.pdf_annotator import PDFAnnotator
from src.report_generator import ReportGenerator

# 语法检查
checker = GrammarChecker()
errors = checker.check_spelling(text)

# PDF标注
annotator = PDFAnnotator()
annotator.annotate("input.pdf", "output.pdf", errors)

# 生成报告
generator = ReportGenerator()
generator.generate("report.md", errors, stats)
```

## 标注样式说明

### 错误类型与标注样式

| 错误类型 | 标注样式 | 说明 |
|---------|---------|------|
| 拼写错误 | 红色矩形框 | 的/得/地、在/再、做/作等错别字 |
| 语法错误 | 红色下划线 | 重复用词、冗长表达、被动语态过度等 |
| 表达问题 | 红色波浪线 | 句子结构不完整、逻辑连接不当等 |

### 修改建议注释

每个错误旁边会显示黄色注释框，包含：
- 错误类型
- 具体修改建议
- 其他相关信息

## 报告格式

### Markdown报告

默认生成Markdown格式报告，包含：
1. **基本信息**：生成时间、文档字数、总页数
2. **错误统计**：错误类型分布、分页统计
3. **详细错误列表**：按页码列出所有错误
4. **修改建议**：针对发现的错误给出建议
5. **报告摘要**：总结文档质量

### HTML报告

生成HTML格式报告，适合在浏览器中查看：
```bash
# 在配置中设置报告格式
report:
  format: "html"
```

### 纯文本报告

生成纯文本格式报告，适合命令行查看：
```bash
# 在配置中设置报告格式
report:
  format: "text"
```

## 高级功能

### 缓存机制

工具会自动缓存PDF文本提取结果，提高重复处理的效率：
- 缓存文件保存在 `.pdf_cache` 目录
- 默认缓存过期时间为24小时
- 可通过配置调整缓存设置

### 性能优化

对于大文件或批量处理，建议：
1. **调整工作线程数**：根据CPU核心数设置合适的线程数
2. **启用缓存**：减少重复的文本提取操作
3. **分页处理**：大文件自动分页处理，避免内存不足
4. **设置超时**：防止单个文件处理时间过长

### 自定义规则

可以通过配置文件添加自定义检查规则：

```yaml
custom_rules:
  - name: "检查特定术语"
    pattern: "旧术语"
    suggestion: "建议使用'新术语'"
    error_type: "spelling"
  
  - name: "避免口语化"
    pattern: "搞定|贼好|巨难"
    suggestion: "建议使用正式书面语"
    error_type: "grammar"
```

## 故障排除

### 常见问题

#### 1. 无法提取文本
**症状**：报告显示"未提取到文本内容"
**原因**：PDF可能是扫描图像或加密文档
**解决方案**：
- 使用OCR工具预处理扫描版PDF
- 确保PDF不是加密的

#### 2. 标注位置不准确
**症状**：标注位置与错误文本不对齐
**原因**：PDF文本层与显示层不一致
**解决方案**：
- 调整标注偏移量
- 使用更精确的文本搜索算法

#### 3. 处理速度慢
**症状**：大文件处理时间过长
**原因**：文件过大或配置不当
**解决方案**：
- 增加工作线程数
- 启用缓存
- 设置合理的超时时间

#### 4. 内存不足
**症状**：处理大文件时内存溢出
**原因**：文件过大，内存不足
**解决方案**：
- 增加内存限制
- 使用分页处理
- 优化代码内存使用

### 调试模式

启用详细日志输出：
```bash
# 命令行选项
proofread --verbose document.pdf

# 或在配置中设置
logging:
  level: "DEBUG"
```

### 获取帮助

```bash
# 查看命令行帮助
proofread --help
python scripts/batch_process.py --help

# 查看版本信息
proofread --version
```

## 最佳实践

### 1. 预处理PDF
- 确保PDF包含可提取的文本层
- 对于扫描版PDF，先进行OCR处理
- 移除不必要的加密或保护

### 2. 配置优化
- 根据文档类型调整检查规则
- 设置合适的性能参数
- 定期清理缓存文件

### 3. 工作流程
1. 先进行快速检查，了解文档大致问题
2. 根据报告优先级处理错误
3. 修改后重新校对，确保问题已解决
4. 保存配置和报告，便于后续参考

### 4. 版本控制
- 将配置文件纳入版本控制
- 保存重要的校对报告
- 记录自定义规则的变更

## 扩展开发

### 添加新的检查规则

1. 在配置文件中添加自定义规则
2. 或直接修改 `src/grammar_checker.py`
3. 测试新规则的效果
4. 更新文档说明

### 集成其他工具

工具可以与其他文本处理工具集成：
- OCR工具（如Tesseract）
- 翻译工具
- 格式转换工具

### 开发API

工具提供了清晰的API接口，可以：
- 集成到其他Python项目中
- 开发Web服务
- 构建桌面应用程序

---

更多详细信息，请参考：
- [API参考](api.md)
- [开发指南](development.md)
- [常见问题](faq.md)