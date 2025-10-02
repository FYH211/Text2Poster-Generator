# 📖 Text2Poster Generator - 用户手册

> 快速将文本内容转换为精美的小红书风格海报

---

## 🎯 项目简介

自动将长文本转换为多张小红书风格海报的工具。

**核心功能**：
- ✅ 智能分页 - 自动分割长文本，默认3:4 比例
- ✅ AI 增强 - 关键词高亮 + 智能 Emoji
- ✅ 精美排版 - 小红书渐变风格
- ✅ 一键生成 - 无需设计技能


**模块化设计**

```
main.py                  # 主流程
├── read_input_article   # 读取和预处理
├── JS_PAGINATE_ONE_PAGE # 分页逻辑（JS）
└── main                 # 主函数

kimi_highlighter.py      # AI 功能模块
├── extract_keywords     # 关键词提取
├── auto_add_emoji       # 智能 Emoji
└── highlight_keywords   # 高亮标记

style.css                # 样式模块
├── 基础样式
├── 主题样式
└── 响应式样式
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 检查 Python 版本（需要 3.8+）
python --version

# 安装依赖
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. 配置kimi API（https://www.volcengine.com/experience/ark?model=kimi-k2-250905，可选，大模型主要用于智能识别关键词句突显和emoji，可以直接查看output文件夹示例图片）

创建 `.env` 文件：
```env
KIMI_API_KEY=your_api_key_here
KIMI_API_URL=https://ark.cn-beijing.volces.com/api/v3/chat/completions
KIMI_MODEL=kimi-k2-250905
```

### 3. 准备输入文件

编辑 `input.txt`（默认第一行为标题，第二行开始为正文内容：
```txt
标题文字（第一行）
正文第一段内容...

第二段内容...

1. 列表项标题: 详细说明...
2. 第二项: 内容...
```

### 4. 运行生成

```bash
python main.py
```
---

## ⚙️ 功能配置

编辑 `main.py` 中的配置：
```python
ENABLE_HIGHLIGHT = True      # 关键词高亮（需 API）
ENABLE_AUTO_EMOJI = True     # AI 添加 Emoji（需 API）
```
---




## 📤 输出说明

**输出目录**：`output/`

**文件命名**：
```
cover.png       # 封面页
content_01.png  # 内容页 1
content_02.png  # 内容页 2
```

**图片规格**：1080x1440 像素（3:4），PNG 格式

---

## ❓ 常见问题

### Q1: 安装失败
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install playwright -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: 运行报错
```bash
# 重新安装依赖
pip uninstall playwright
pip install playwright
python -m playwright install chromium
```

### Q3: API 调用失败
关闭 AI 功能继续使用：
```python
ENABLE_HIGHLIGHT = False
ENABLE_AUTO_EMOJI = False
```

### Q4: 修改样式
编辑 `style.css`：
```css
.title-container { font-size: 76px; }    /* 标题字号 */
#text-container { font-size: 38px; }     /* 正文字号 */
#poster { background: linear-gradient(...); }  /* 背景色 */
```

### Q5: 自定义封面图像
1. 将图像文件命名为 `img.png`，放在 `Reference-style/` 目录
2. 修改 `style.css` 中的 `.image-placeholder` 类：
```css
.image-placeholder {
    background: linear-gradient(to top, #e06a80, transparent 35%), 
                url('Reference-style/img.png');
    background-size: cover;
    background-position: center;
}
```

---

## 💡 使用技巧

- **内容准备**：双换行分段，列表用 `数字. 标题: 内容` 格式
- **Emoji 使用**：自动模式（AI）或手动模式（自己输入）
- **样式定制**：编辑 `style.css` 调整字号、配色、间距
- **封面图像**：使用 `img.png` 自定义封面页背景相框图像

---


## 📚 更多文档

- [项目设计文档](design.md)
- [开发日志](dev_log.md)
- [实施计划](implementation_plan.md)
- [项目经验](experience.md)

---


**感谢使用！如有问题欢迎反馈** 🎉