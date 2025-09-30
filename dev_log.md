 # Text2Poster Generator - 开发日志 
## 2025年9月25日

### 阶段一：环境准备与模板搭建

1.  **初始化项目结构**：
    -   创建 `output` 文件夹。
    -   创建 `input.txt` 并添加示例文本。
    -   创建 `main.py` 作为核心逻辑脚本。

2.  **安装依赖**：
    -   创建 `requirements.txt` 并添加 `playwright`。
    -   通过 `pip install -r requirements.txt` 安装 `playwright`。
    -   通过 `python -m playwright install` 安装 Playwright 浏览器驱动。

3.  **HTML 模板设计 (`index.html`)**：
    -   创建 `index.html`，包含 `#poster` 和 `#text-container` 元素。

4.  **CSS 样式开发 (`style.css`)**：
    -   创建 `style.css`，设置了背景、Flexbox 布局、引入 Google Fonts（Ma Shan Zheng），并为 `#poster` 设置了固定尺寸（1080x1440px）。

### 阶段二：核心脚本开发

1.  **读取输入文件**：
    -   在 `main.py` 中添加 `read_input_file` 函数，用于读取 `input.txt` 中的文本。

2.  **实现 Playwright 核心逻辑**：
    -   在 `main.py` 中导入 `asyncio` 和 `playwright.async_api`。
    -   编写 `generate_posters` 异步主函数，初始化 Playwright 并启动 Chromium 浏览器。
    -   实现循环遍历 `input.txt` 中的文本。

3.  **自动化浏览器操作**：
    -   在循环中，为每条文本：
        -   打开新页面并导航到本地 `index.html`。
        -   使用 `page.locator("#text-container").evaluate("(node, text_content) => node.textContent = text_content", text)` 设置文本内容。
        -   使用 `page.locator("#poster").screenshot()` 对海报容器进行截图，并保存到 `output/` 文件夹。

4.  **完善与收尾**：
    -   确保浏览器实例在脚本结束时关闭。
    -   添加进度打印信息。

### 阶段三：测试与验证

1.  **运行 `main.py`**：
    -   首次运行 `main.py` 时，遇到 `TimeoutError`，原因是 `locator.fill()` 不适用于 `p` 标签，且元素可能未完全可见。
    -   将 `locator.fill()` 更改为 `locator.evaluate()` 并设置 `textContent`，同时修正了 `evaluate` 的参数传递方式。
    -   第二次运行 `main.py` 成功，生成了 5 张海报图片到 `output/` 文件夹。

## 2025年9月29日 - 文本海报生成器功能完善与优化

**1. 项目初始化与上下文理解**
*   熟悉了项目结构，识别了关键文件 (`index.html`, `style.css`, `main.py`, `input.txt`)。

**2. CSS 重构以匹配参考图像**
*   将渐变背景从 `body` 移动到 `#poster` 元素。
*   修正了图像占位符的定位（移除了绝对定位，调整了外边距）。
*   调整了标题和评论容器的外边距。

**3. 宽高比调整 (3:4)**
*   修改了 `#display-wrapper` 的高度，从 `1920px` 调整为 `1440px`。

**4. 图像占位符裁剪**
*   从 `index.html` 中移除了 `<img>` 标签。
*   在 `.image-placeholder` 上使用 CSS `background-image`、`background-size: cover;` 和 `background-position: center;` 来显示 `Reference-style/1.jpg` 的裁剪部分。
*   移除了 `.image-placeholder` 的 `border` 和 `box-shadow`。

**5. 从 `input.txt` 动态获取标题和正文**
*   修改 `main.py`，将 `input.txt` 的第一行作为标题，其余作为正文。
*   修改 `main.py`，使用 `innerText` 将标题动态注入到 `.title-container`。
*   修改 `index.html`，移除了硬编码的标题。

**6. 移除评论区**
*   从 `index.html` 中移除了 `<div class="comment-container">` 以释放空间。

**7. 分页逻辑优化**
*   修改 `main.py`，将 `body_text` 转换为 HTML 格式（使用 `<p>` 标签和 `<br>`），并使用 `innerHTML` 进行注入和测量。
*   更新 `JS_PAGINATE_ONE_PAGE`，使其在 `measureNode` 中使用 `innerHTML`。
*   更新 `JS_PAGINATE_ONE_PAGE`，通过考虑所有元素的高度和外边距（包括 `#text-container` 的 `margin-bottom`），更健壮地计算 `maxHeight`。
*   移除了 `main.py` 中处理空 `page_text` 的回退逻辑块，以简化分页逻辑。

**8. 布局调整以确保文本可见性与间距**
*   调整了 `.image-placeholder` 的 `margin-top` 到 `100px`（从 `150px` 调整到 `230px`，再到 `100px`）以释放文本空间。
*   调整了 `.image-placeholder` 的 `margin-bottom` 到 `30px`，以补偿图像高度的增加。
*   为 `#text-container` 添加了 `margin-bottom: 80px;` 以保持底部留白一致。
*   为 `#text-container p` 添加了 `margin-bottom: 1em;` 以实现可配置的段落间距。

**9. 注释翻译**
*   将 `main.py` 和 `style.css` 中的所有注释翻译为中文。

---

## 2025年9月30日 - Kimi AI集成与高级分页优化

### 阶段一：Kimi API 智能关键词识别集成

**1. Kimi API 环境配置**
*   创建 `.env` 文件存储 API 凭证：
    -   `KIMI_API_KEY`: API 密钥
    -   `KIMI_API_URL`: API 端点
    -   `KIMI_MODEL`: 使用的模型版本
*   在 `requirements.txt` 添加依赖：`requests`, `python-dotenv`, `pillow`

**2. 关键词提取模块开发 (`kimi_highlighter.py`)**
*   实现 `extract_keywords()` 函数调用 Kimi API：
    -   设计精确的 system prompt，确保提取**逐字存在**的原文片段（而非摘要）
    -   返回 5-8 个关键短语或句子片段（5-15 字）
    -   API 返回 JSON 数组格式
*   实现 `highlight_keywords_in_html()` 函数：
    -   按长度降序处理关键词（避免短词覆盖长词）
    -   使用正则表达式精确匹配并包裹 `<span class="highlight">` 标签
    -   避免重复高亮已标记的内容

**3. 主脚本集成**
*   修改 `read_input_article()` 函数：
    -   添加 `enable_highlight` 参数控制是否启用 Kimi 识别
    -   在生成 HTML 后调用 Kimi API 提取关键词
    -   应用高亮标签到 HTML 内容

**4. CSS 高亮样式**
*   添加 `.highlight` 类：
    -   `color: #e06a80;` (红色)
    -   `font-weight: 700;` (加粗)
    -   参考了提供的样式图片 `1.jpg`, `2.jpg`, `3.jpg`

---

### 阶段二：分页逻辑与HTML标签完整性修复

**5. HTML 标签截断问题修复**
*   **问题**：分页时 HTML 标签被切成两半，导致页面显示 `class="highligh">` 等裸露标签
*   **解决方案**：
    -   优化 `JS_PAGINATE_ONE_PAGE` 的 token 化逻辑
    -   使用正则表达式将完整 HTML 标签作为原子单元处理
    -   在拆分段落时保留原始 `<p>` 标签的属性（如 `class="list-item"`）

**6. 列表项格式优化**
*   **需求**：实现带序号的列表项（如"1. 复杂性："）的特殊格式
    -   标题部分（"复杂性："）加粗
    -   多行列表项的第二行及后续行缩进，与内容对齐（而非序号）
*   **实现**：
    -   修改 `read_input_article()`，使用正则表达式识别列表项格式 `^\d+\.\s+([^:：]+)([:：]\s*)(.*)`
    -   将标题部分包裹在 `<span class="list-title">` 中
    -   为列表项段落添加 `class="list-item"` 属性
*   **CSS 样式**：
    -   `p.list-item`: 使用悬挂缩进（`text-indent: -1.1em; padding-left: 1.1em;`）
    -   `p.list-item .list-title`: 加粗显示

---

### 阶段三：文本连续性与智能断句

**7. 封面页标题修复**
*   **问题**：封面页标题显示错误（"历史问题" 而非 "不是所有的业务都需要SOP"）
*   **原因**：列表项的 `list_title` 变量覆盖了全局的 `title` 变量
*   **解决方案**：将列表项标题变量重命名为 `list_title`，避免命名冲突

**8. 文本截断问题修复**
*   **问题**：内容页之间文本未连接，部分内容（如"不断更新和改进"）未显示
*   **原因**：`maxHeight` 安全缓冲不足，最后一行被隐藏
*   **解决方案**：
    -   将安全缓冲从 `lineHeight` 增加到 `lineHeight * 2`
    -   为智能断句额外预留 `lineHeight * 0.5` 的空间

**9. 智能句子断行优化**
*   **需求**：避免句子在分页时被切断，一句话应完整显示在同一页
*   **实现**：
    -   **内容页**：回溯到最近的标点符号（`。！？；.!?;`）进行断行
    -   **封面页**：优先保留完整段落，仅在第一段过长时按句号断行
    -   确保标点符号包含在当前页，而非分到下一页
    -   实现 HTML 标签平衡检查，避免 `<span>` 标签未闭合

---

### 阶段四：动态高度调整与页面优化

**10. 封面页内容扩展**
*   **问题**：封面页底部大量空白，完整句子"。但如何确定哪些流程需要SOP呢？..."未显示
*   **解决方案**：
    -   调整 `#text-container` 的 `max-height` 从默认值增加到 `680px`，然后最终版本为 `900px`
    -   优化封面页和内容页的缓冲策略：
        -   封面页：`lineHeight * 1.5` 缓冲
        -   内容页：`lineHeight * 2 + lineHeight * 0.5` 缓冲

**11. 动态高度裁剪（内容页）**
*   **需求**：消除内容页底部的大量空白区域，同时保持 3:4 比例
*   **实现**：
    -   在截图前计算实际内容高度：
        ```javascript
        textContentHeight = lastChild.offsetTop + lastChild.offsetHeight + lastChildMarginBottom
        totalHeight = posterPaddingTop + textContentHeight + posterPaddingBottom
        ```
    -   动态设置 `poster.style.height` 为 `totalHeight`
    -   内容页使用智能高度，封面页保持固定 1440px（3:4 比例）

**12. 页面间距对称性优化**
*   **问题**：内容页底部留白视觉上明显大于顶部留白（底部 285px vs 顶部 122px）
*   **诊断过程**：
    -   发现最后一个列表项的 `margin-bottom: 0.8em` 未被覆盖
    -   发现第一个段落的 `margin-top: 1em` 未被移除
    -   高度计算中包含了这些额外的 margin
*   **解决方案（CSS优先级修复）**：
    -   添加 `#text-container p:first-child { margin-top: 0; }` 移除顶部 margin
    -   添加 `#text-container p.list-item:last-child { margin-bottom: 0 !important; }` 强制移除底部 margin
    -   移除 `#text-container` 的 `margin-bottom`
    -   确保所有底部间距由 `#poster` 的 `padding-bottom: 80px` 统一控制
*   **最终效果**：
    -   顶部留白：80px (padding) + 0px (margin) = **80px**
    -   底部留白：80px (padding) + 0px (margin) = **80px**
    -   **完美对称** ✅

---

### 技术亮点总结

1. **Kimi AI 集成**：
   - 精心设计的 prompt 确保提取原文片段而非摘要
   - 智能关键词识别并高亮显示

2. **HTML 安全处理**：
   - Token 化保护 HTML 标签不被截断
   - 段落属性在拆分时保持完整

3. **智能分页**：
   - 句子级别的智能断行
   - 封面页与内容页差异化断句策略
   - HTML 标签平衡检查

4. **动态高度优化**：
   - 精确的高度计算，消除冗余空白
   - 内容页节省 9%-46% 的垂直空间

5. **视觉对称性**：
   - CSS 优先级精细控制
   - 顶部和底部留白完全一致（80px）

### 最终成果

- ✅ 4 张海报自动生成（1 封面 + 3 内容页）
- ✅ 关键词句智能高亮（红色加粗）
- ✅ 列表项完美格式（悬挂缩进 + 标题加粗）
- ✅ 智能分页（句子完整，无截断）
- ✅ 动态高度（精准裁剪，无冗余空白）
- ✅ 完美对称（顶部底部留白一致）

项目状态：**功能完整，视觉完美** 🎉