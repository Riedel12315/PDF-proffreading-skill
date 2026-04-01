#!/usr/bin/env python3
"""
创建示例PDF文件
用于演示和测试
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os


def create_example_pdf(output_path="examples/sample.pdf"):
    """创建示例PDF文件"""
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 创建PDF画布
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # 设置字体
    c.setFont("Helvetica", 12)
    
    # 第一页：介绍
    text_lines = [
        "PDF校对工具示例文档",
        "=" * 40,
        "",
        "这是一个用于演示PDF校对工具功能的示例文档。",
        "文档中包含了一些常见的中文写作错误。",
        "",
        "一、拼写错误示例",
        "",
        "1. 的/得/地混用：",
        "   - 他高兴的跳了起来。（错误）",
        "   - 正确的写法：他高兴得跳了起来。",
        "",
        "2. 在/再混用：",
        "   - 我在说一遍。（错误）",
        "   - 正确的写法：我再说一遍。",
        "",
        "3. 做/作混用：",
        "   - 我要去作饭。（错误）",
        "   - 正确的写法：我要去做饭。",
    ]
    
    y_position = height - inch
    for line in text_lines:
        c.drawString(inch, y_position, line)
        y_position -= 20
    
    # 第二页：语法错误示例
    c.showPage()
    c.setFont("Helvetica", 12)
    y_position = height - inch
    
    text_lines2 = [
        "二、语法错误示例",
        "",
        "1. 重复用词：",
        "   - 这个问题非常重要非常重要。",
        "   - 建议：删除重复的'非常重要'",
        "",
        "2. 冗长表达：",
        "   - 我们需要进行市场调研的工作。",
        "   - 建议：简化为'我们需要市场调研'",
        "",
        "3. 被动语态过度：",
        "   - 这个问题被大家所关注。",
        "   - 建议：改为'大家关注这个问题'",
        "",
        "4. 句子过长：",
        "   今天早上我起床后先刷牙洗脸然后吃早餐接着去上班路上遇到堵车迟到了十分钟。",
        "   - 建议：添加标点，拆分为多个句子",
    ]
    
    for line in text_lines2:
        c.drawString(inch, y_position, line)
        y_position -= 20
    
    # 第三页：表达问题示例
    c.showPage()
    c.setFont("Helvetica", 12)
    y_position = height - inch
    
    text_lines3 = [
        "三、表达问题示例",
        "",
        "1. 缺少主语：",
        "   - 看完电影后，觉得很感动。",
        "   - 建议：添加主语，如'我看完电影后，觉得很感动'",
        "",
        "2. 逻辑连接不当：",
        "   - 因为下雨，比赛取消了。",
        "   - 建议：添加'所以'或调整句式",
        "",
        "3. 修饰语位置：",
        "   - 他慢慢地地走路。",
        "   - 建议：'他慢慢地走路'",
        "",
        "四、综合示例",
        "",
        "在进行项目管理的工作时，我们需要进行团队协作的工作，",
        "并且需要做出项目规划的决定。这个问题被领导所重视，",
        "我们需要提高我们的项目管理水平。",
    ]
    
    for line in text_lines3:
        c.drawString(inch, y_position, line)
        y_position -= 20
    
    # 保存PDF
    c.save()
    
    print(f"示例PDF已创建: {output_path}")
    print(f"文件大小: {os.path.getsize(output_path)} 字节")
    
    return output_path


def create_perfect_pdf(output_path="examples/perfect_sample.pdf"):
    """创建完美版本的PDF（无错误）"""
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 创建PDF画布
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # 设置字体
    c.setFont("Helvetica", 12)
    
    # 第一页：正确示例
    text_lines = [
        "PDF校对工具示例文档（正确版本）",
        "=" * 40,
        "",
        "这是一个没有错误的示例文档，用于对比。",
        "",
        "一、正确用法示例",
        "",
        "1. 的/得/地正确使用：",
        "   - 他高兴得跳了起来。",
        "   - 她慢慢地走路。",
        "",
        "2. 在/再正确使用：",
        "   - 我再说一遍。",
        "   - 我们明天再见面。",
        "",
        "3. 做/作正确使用：",
        "   - 我要去做饭。",
        "   - 这是他的作品。",
    ]
    
    y_position = height - inch
    for line in text_lines:
        c.drawString(inch, y_position, line)
        y_position -= 20
    
    # 第二页：良好写作习惯
    c.showPage()
    c.setFont("Helvetica", 12)
    y_position = height - inch
    
    text_lines2 = [
        "二、良好写作习惯",
        "",
        "1. 简洁表达：",
        "   - 我们需要市场调研。",
        "   - 大家关注这个问题。",
        "",
        "2. 句子结构完整：",
        "   - 我看完电影后，觉得很感动。",
        "   - 因为下雨，所以比赛取消了。",
        "",
        "3. 逻辑清晰：",
        "   - 首先，我们需要明确目标。",
        "   - 然后，制定详细的计划。",
        "   - 最后，执行并评估结果。",
        "",
        "三、写作建议",
        "",
        "1. 写完后再读一遍",
        "2. 检查常见错误",
        "3. 保持简洁明了",
        "4. 注意逻辑连贯",
    ]
    
    for line in text_lines2:
        c.drawString(inch, y_position, line)
        y_position -= 20
    
    # 保存PDF
    c.save()
    
    print(f"完美示例PDF已创建: {output_path}")
    
    return output_path


def main():
    """主函数"""
    print("创建示例PDF文件...")
    print("-" * 40)
    
    # 创建包含错误的示例
    error_pdf = create_example_pdf()
    
    # 创建完美版本
    perfect_pdf = create_perfect_pdf()
    
    print("-" * 40)
    print("示例文件创建完成！")
    print(f"1. 包含错误的PDF: {error_pdf}")
    print(f"2. 正确版本的PDF: {perfect_pdf}")
    
    # 创建使用说明
    readme_content = f"""
# 示例文件说明

## 文件列表

1. `{os.path.basename(error_pdf)}` - 包含常见错误的示例文档
   - 拼写错误（的/得/地、在/再、做/作混用）
   - 语法错误（重复用词、冗长表达、被动语态过度）
   - 表达问题（缺少主语、逻辑连接不当）

2. `{os.path.basename(perfect_pdf)}` - 正确版本的示例文档
   - 所有错误都已修正
   - 展示良好的写作习惯

## 使用方法

```bash
# 校对包含错误的文档
proofread {error_pdf}

# 校对正确版本的文档（应该没有错误）
proofread {perfect_pdf}
```

## 预期结果

校对 `{os.path.basename(error_pdf)}` 应该发现：
- 多个拼写错误
- 多个语法错误  
- 多个表达问题

校对 `{os.path.basename(perfect_pdf)}` 应该：
- 未发现明显错误
- 生成"文档质量良好"的报告
"""
    
    readme_path = "examples/README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"\n使用说明已保存: {readme_path}")


if __name__ == "__main__":
    main()