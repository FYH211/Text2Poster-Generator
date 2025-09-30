# Kimi AI 关键词句智能高亮功能

## 功能说明

本项目已集成 Kimi AI 大模型，可自动识别 `input.txt` 文本中的关键词句，并在生成的海报中以**红色加粗**的方式突出显示。

## 配置说明

### 1. 环境变量配置

在项目根目录的 `.env` 文件中配置以下内容：

```env
KIMI_API_KEY=你的API密钥
KIMI_API_URL=https://ark.cn-beijing.volces.com/api/v3/chat/completions
KIMI_MODEL=kimi-k2-250905
```

### 2. 依赖安装

```bash
pip install -r requirements.txt
```

新增的依赖包：
- `requests` - 用于调用 Kimi API
- `python-dotenv` - 用于加载环境变量

## 使用方法

### 基本使用

直接运行主程序即可自动启用关键词高亮：

```bash
python main.py
```

程序会自动：
1. 读取 `input.txt` 中的文本
2. 调用 Kimi API 智能提取 5-8 个关键词句
3. 在生成的海报中以红色加粗显示这些关键词句

### 关闭关键词高亮

如果不需要关键词高亮功能，可以在 `main.py` 中修改：

```python
# 将这一行：
title_text, body_html, raw_body = read_input_article("input.txt", enable_highlight=True)

# 改为：
title_text, body_html, raw_body = read_input_article("input.txt", enable_highlight=False)
```

## 样式自定义

关键词句的高亮样式在 `style.css` 中定义：

```css
.highlight {
    color: #e06a80;    /* 红色文字 */
    font-weight: 700;  /* 加粗 */
}
```

你可以根据需要修改颜色、字重、背景色等样式。

## 工作原理

1. **文本提取**：从 `input.txt` 读取正文内容
2. **API 调用**：将文本发送给 Kimi API，使用特定的 prompt 提取原文中的关键词句
3. **关键词匹配**：在 HTML 文本中查找这些关键词句
4. **标记高亮**：用 `<span class="highlight">` 标签包裹关键词句
5. **海报生成**：通过 Playwright 渲染并截图生成海报

## API Prompt 说明

系统使用的 prompt 会指导 Kimi：
- 提取**原文中实际存在**的文字片段（不总结、不改写）
- 优先选择核心观点、重要结论、关键动词短语
- 每个关键词句长度在 5-15 个字之间
- 避免提取过于常见的词语

## 文件说明

- `kimi_highlighter.py` - Kimi API 调用和关键词高亮模块
- `.env` - API 配置文件（已在 gitignore 中）
- `style.css` - 包含高亮样式定义
- `main.py` - 主程序（已集成关键词高亮功能）

## 注意事项

1. **API 调用成本**：每次生成海报都会调用一次 Kimi API，请注意 API 使用额度
2. **匹配准确性**：AI 提取的关键词句必须在原文中逐字存在，否则无法高亮
3. **编码问题**：确保 `.env` 文件使用 UTF-8 编码
4. **网络连接**：需要能够访问 Kimi API 服务器

## 调试

如果关键词高亮不生效，可以检查：

1. 查看控制台输出，确认 API 是否调用成功
2. 检查 `.env` 文件配置是否正确
3. 确认提取的关键词句是否在原文中存在
4. 检查网络连接是否正常

## 示例输出

运行成功时，控制台会显示：

```
=== 开始智能识别关键词句 ===
正在调用 Kimi API 提取关键词句...
API 返回内容: ["关键词1", "关键词2", ...]
成功提取 6 个关键词句
识别到的关键词句: ['关键词1', '关键词2', ...]
成功标记 6 个关键词句: ['关键词1', '关键词2', ...]
=== 关键词句识别完成 ===
```

生成的海报中，关键词句会以红色加粗的样式显示。
