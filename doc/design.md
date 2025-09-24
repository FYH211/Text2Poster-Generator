# 🎨 Text2Poster Generator 项目设计文档

## 📋 1. 概述

> **项目目标**: 实现一个能够批量生成线上活动宣传图的自动化脚本

本项目旨在实现一个能够批量生成线上活动宣传图的自动化脚本。脚本的核心功能是根据提供的文字列表，自动生成一系列具有统一背景和版式，但内容各异的宣传图片。整个流程将以一个本地或公开的网页模板为核心，利用 Playwright MCP 自动操作浏览器，将文本填充到指定位置，然后进行截图并保存为图片文件。开发过程将全程使用 Gemini CLI 进行编码、执行和迭代优化。

### 🎯 1.1 问题边界定义

#### 📥 输入
- 一个包含多条文本的列表或文件

#### ⚙️ 处理流程
脚本将遍历列表，对每一条文本执行以下操作：

1. 🔄 **加载预设的网页模板**
2. ✏️ **将文本动态填充到网页的特定元素中**
3. 📸 **截取网页中指定区域的图像**
4. 💾 **将截图保存为具有特定尺寸和命名格式的图片文件**

#### 📤 输出
- 一个包含所有生成图片文件的文件夹

#### 🛠️ 工具限制
- **核心开发和执行环境**: Gemini CLI
- **自动化浏览器**: Playwright MCP
- **版本控制**: Git

### 🎨 参考样式

**样式参考**: Reference-style文件夹下的三张图片
- `Reference-style\1.jpg`
- `Reference-style\2.jpg` 
- `Reference-style\3.jpg`

#### 🎨 字体排版参考（可优化）

| 元素 | 规格 |
|------|------|
| **字体** | • 主标题（如果有）和主要文字采用相同的字体，字体风格偏向于圆润、可爱<br>• 字号大小适中，能够清晰阅读<br>• 字色: 主要为黑色或深灰色，与背景形成清晰对比 |
| **间距** | • 文字区域与图片上下边界保持足够的留白<br>• 多行文字之间的行间距能够保持文字不拥挤 |

## 🚀 2. 任务拆解与技术选型

### 📝 2.1 任务拆解

本项目可以分解为以下几个主要步骤，每个步骤都将由 Gemini CLI 辅助完成：

#### 🔧 环境准备
- ✅ 初始化 Git 仓库
- 📦 安装所需的依赖，如 Playwright MCP

#### 🎨 网页模板设计与开发
- 🖼️ 基于参考图片，设计并开发一个 HTML/CSS 网页模板
- 🔗 模板需包含可供脚本动态填充的占位符（如 div 或 span）
- 📐 考虑到后续的截图尺寸，模板应设置为固定的宽高比

#### 💻 脚本核心逻辑开发
- 🐍 使用 Python编写脚本
- 📋 **主函数**: 接收一个文本列表作为参数
- 🔄 **核心循环**: 遍历文本列表

##### 🌐 浏览器操作函数
- 🚀 启动 Playwright MCP 浏览器实例
- 📂 打开网页模板文件
- ✏️ 使用 Playwright 的 `page.fill()` 或 `page.evaluate()` 方法将文本填充到指定元素
- 📸 截取网页区域
- 💾 保存图片
- 🔒 关闭浏览器实例

#### 🔄 自动化流程设计
- 📜 编写一个可由 Gemini CLI 调用的主脚本，该脚本将调用上述功能，实现端到端的自动化
- 📖 设计 `manual.md`，详细说明如何配置和运行脚本
- 🤖 如果需要 Gemini CLI 介入的步骤，编写 `cc-runner.md`

#### 🧪 TDD 与迭代优化
- 🎯 **测试基准**: 使用参考图片作为初始的视觉对比基准
- 🔍 **自动化对比**: 在 Gemini CLI 的帮助下，编写逻辑来比较生成图片与基准图片之间的差异（例如，通过像素对比、颜色直方图对比等方式），并根据差异调整脚本或模板
- 📝 记录 Gemini CLI 在此过程中的所有指令和思考，并整理到 `dev_log.md` 中

#### 📚 文档编写与整理
- 📋 `dev_log.md`: 记录开发过程中的关键决策、遇到的问题和解决方案
- 💭 `experience.md`: 记录整个项目的总结、心得和对 Gemini CLI + Playwright MCP 组合的思考
- 📖 `manual.md`: 编写清晰的脚本使用手册
- 🤖 `cc-runner.md`: （可选）编写 Gemini CLI 执行文档

### 🛠️ 2.2 技术栈

| 类别 | 技术选择 |
|------|----------|
| **编程语言** | 🐍 Python |
| **核心库** | • `playwright`: 用于浏览器自动化，通过 Playwright MCP 进行交互<br>• `os` / `pathlib`: 用于文件系统操作，如创建文件夹、保存文件 |
| **版本控制** | 📝 Git |
| **开发与执行环境** | 🤖 Gemini CLI |

## 💻 3. 核心功能实现细节

### 🎨 3.1 网页模板 (template.html)

#### 📋 结构设计
- 📄 一个简单的 HTML 文件，包含一个 div 容器，内部有用于显示文本的 div

#### 🎨 样式规范
- 🎯 使用 CSS 定义容器的尺寸、背景色、文字的字体、字号、颜色、行间距和对齐方式
- 📍 `div#text-container`: 核心文本区域，使用 `position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);` 实现居中
- 🔧 字体、字号、颜色等参数将根据参考图片进行精确调整

### 🐍 3.2 自动化脚本 (main.py)

```python
import os
from playwright.sync_api import sync_playwright

def generate_image(text, page):
    """
    根据给定的文本在网页上生成一张图片。
    """
    # 找到网页中的文本容器并填充文本
    page.evaluate("document.querySelector('#text-content').textContent = arguments[0]", text)
    
    # 截取指定区域
    screenshot_path = f"output/{text.replace(' ', '_').replace('...', '')[:10]}.png"
    # 获取要截图的元素
    element = page.locator('#main-container') 
    element.screenshot(path=screenshot_path)
    
    return screenshot_path

def main(texts):
    """
    主函数，批量生成图片。
    """
    # 创建输出文件夹
    if not os.path.exists("output"):
        os.makedirs("output")
        
    with sync_playwright() as p:
        # 使用 Chromium 浏览器
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 加载本地的网页模板文件
        # 注意: 路径可能需要根据实际情况调整
        page.goto(f"file://{os.path.abspath('template.html')}")
        
        print("开始生成图片...")
        for text in texts:
            print(f"正在生成: '{text}'...")
            generate_image(text, page)
            
        browser.close()
    
    print("所有图片已生成完毕。")
    print("文件已保存至 'output/' 文件夹。")

if __name__ == "__main__":
    # 示例文本列表
    sample_texts = [
        "今天很开心，明天会更好...",
        "生活不易，但要保持微笑。",
        "星光不问赶路人，时光不负有心人。"
    ]
    main(sample_texts)
```
### 🤖 3.3 Gemini CLI 协作流程

整个开发过程将由 Gemini CLI 驱动，核心指令流如下：

#### 🚀 初始化阶段
```
Gemini CLI, please initialize a new git repository for a project named 'Automated-Poster-Generator' and create a 'dev_log.md' file to document the development process.
```

#### 🎨 模板开发阶段
```
Gemini CLI, let's design the 'template.html' and 'style.css' files. Analyze the provided link (Reference-style文件夹下的三张图片) and summarize the key design elements like font, color, and layout. Then, write the initial HTML and CSS code based on your analysis.
```

#### 💻 脚本开发阶段
```
Gemini CLI, let's start coding the main script 'main.py' using Python. The script should use Playwright MCP to load the 'template.html' and dynamically replace the text. It should then take a screenshot of the main container and save it. Please write the initial code.
```

#### 🔄 迭代优化阶段
```
Gemini CLI, I have generated a sample image. Please compare it with the reference image. Analyze the differences in font size, line spacing, and padding. Provide me with suggestions to adjust the CSS in 'template.html' and explain the reasoning behind your suggestions. I will update the code and ask you to re-evaluate.
```

#### 📚 文档撰写阶段
```
Gemini CLI, please write the 'manual.md' file. The manual should clearly explain the project setup, required dependencies, and how to run the script. It should be easy for a new user to follow.

Gemini CLI, please update the 'dev_log.md' with our recent discussions and code changes. Summarize the key problems we solved and the decisions we made.

Gemini CLI, please write the 'experience.md' document, reflecting on the entire development process. Discuss the advantages and challenges of using Gemini CLI and Playwright MCP for this task.
```

## 📦 4. 交付物

| 类别 | 内容 | 状态 |
|------|------|------|
| **🔗 GitHub 仓库** | GitHub 仓库链接 | ⏳ 待定，开发完成后将在此处填充 |
| **💻 代码文件** | • `main.py`<br>• `template.html`<br>• `style.css` | 📝 待开发 |
| **📚 文档** | • `manual.md`<br>• `dev_log.md`<br>• `experience.md`<br>• `cc-runner.md` (可选) | 📝 待编写 |
| **🖼️ 示例输出** | `output/` 文件夹（在仓库中可以作为示例存在，或在运行脚本后生成） | 📁 待生成 |

## ✅ 5. 验收标准

### 🎯 功能要求
- ✅ 脚本能够无错运行，生成符合尺寸要求的图片
- 🎨 生成的图片在版式、字体、颜色等方面与参考图片高度相似

### 📝 文档要求  
- 📋 Git 提交历史清晰，反映出从模板设计、脚本编写到迭代优化的整个过程
- 📖 所有要求的文档都已完成，内容详实、清晰
- 💭 在 `experience.md` 中能体现出对 Gemini CLI 和 Playwright MCP 的深入理解和运用

---

> 💡 **项目愿景**: 通过自动化技术，让文字内容快速转化为精美的宣传图片，提升内容创作效率