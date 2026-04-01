# 贡献指南

感谢您考虑为 PDF Proofreading Tool 做出贡献！🎉

## 行为准则

请遵守以下行为准则：
- 尊重所有贡献者
- 建设性的讨论和反馈
- 包容和友好的环境

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议：
1. 在 Issues 页面搜索是否已有类似问题
2. 如果没有，创建新的 Issue
3. 清晰描述问题，包括：
   - 重现步骤
   - 预期行为
   - 实际行为
   - 相关截图或日志

### 提交代码

#### 1. Fork 项目
- 点击右上角的 Fork 按钮
- 克隆您的 fork 到本地

#### 2. 创建分支
```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

#### 3. 开发代码
- 遵循项目的代码风格
- 添加必要的测试
- 更新相关文档

#### 4. 提交更改
```bash
git add .
git commit -m "描述您的更改"
```

#### 5. 推送到您的 fork
```bash
git push origin feature/your-feature-name
```

#### 6. 创建 Pull Request
- 在 GitHub 上创建 Pull Request
- 清晰描述您的更改
- 链接相关的 Issue

## 开发环境设置

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/pdf-proofreading-tool.git
cd pdf-proofreading-tool
```

### 2. 安装依赖
```bash
# 使用安装脚本
./scripts/install.sh

# 或手动安装
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

### 3. 运行测试
```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_basic.py

# 生成测试覆盖率报告
pytest --cov=src tests/
```

## 代码规范

### Python 代码风格
- 遵循 PEP 8 规范
- 使用 Black 格式化代码
- 使用 Flake8 进行代码检查

```bash
# 格式化代码
black src/ tests/

# 检查代码风格
flake8 src/ tests/
```

### 文档规范
- 所有公共函数和类都需要文档字符串
- 使用 Google 风格的文档字符串
- 更新相关的 README 和文档

### 提交信息规范
使用约定式提交：
- `feat:` 新功能
- `fix:` bug 修复
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例：
```
feat: 添加中文成语检查功能
fix: 修复PDF标注位置不准确的问题
docs: 更新使用指南
```

## 项目结构

```
pdf-proofreading-tool/
├── src/                    # 源代码
│   ├── __init__.py
│   ├── proofreader.py     # 主校对程序
│   ├── grammar_checker.py # 语法检查器
│   ├── pdf_annotator.py   # PDF标注器
│   ├── report_generator.py # 报告生成器
│   └── utils.py           # 工具函数
├── tests/                  # 测试文件
├── docs/                   # 文档
├── examples/              # 示例文件
├── scripts/               # 辅助脚本
└── config.example.yaml    # 示例配置
```

## 添加新功能

### 1. 添加新的检查规则
1. 在 `src/grammar_checker.py` 中添加规则
2. 更新相关测试
3. 更新文档说明

### 2. 添加新的标注样式
1. 在 `src/pdf_annotator.py` 中添加样式
2. 更新配置说明
3. 添加示例

### 3. 添加新的报告格式
1. 在 `src/report_generator.py` 中添加格式
2. 更新配置选项
3. 添加测试

## 测试要求

### 单元测试
- 所有新功能都需要单元测试
- 测试覆盖率不应降低
- 测试应该独立且可重复

### 集成测试
- 测试整个工作流程
- 使用示例文件进行测试
- 验证输出结果

### 性能测试
- 对于性能敏感的功能，添加性能测试
- 确保不会显著降低性能

## 文档要求

### 代码文档
- 所有公共 API 都需要文档字符串
- 文档应该清晰、准确
- 包含使用示例

### 用户文档
- 更新 README.md
- 更新使用指南
- 添加变更日志

### API 文档
- 保持 API 文档的同步更新
- 提供详细的参数说明
- 包含返回值说明

## 审查流程

### Pull Request 审查
1. **自动化检查**：CI/CD 流水线运行测试和代码检查
2. **代码审查**：至少需要一名维护者审查
3. **功能测试**：验证功能按预期工作
4. **文档审查**：确保文档已更新

### 审查要点
- 代码质量和可读性
- 测试覆盖率和质量
- 文档完整性和准确性
- 性能影响
- 向后兼容性

## 发布流程

### 版本号
使用语义化版本：
- `MAJOR`：不兼容的 API 修改
- `MINOR`：向下兼容的功能性新增
- `PATCH`：向下兼容的问题修正

### 发布步骤
1. 更新版本号
2. 更新变更日志
3. 创建发布标签
4. 构建发布包
5. 发布到 PyPI（如果适用）

## 获取帮助

如果您在贡献过程中遇到问题：
1. 查看现有文档
2. 搜索 Issues 和 Pull Requests
3. 在 Discussions 中提问
4. 联系维护者

## 致谢

所有贡献者都将被列在项目的贡献者列表中。感谢您的贡献！🙏

---

Happy Contributing! 🚀