# 🎨 Text2Poster Generator

> 智能文本转海报生成器 - 专为小红书等平台设计的自动化图文创作工具

## ✨ 功能特色

- 🚀 **智能分页**：基于 DOM 渲染高度，确保内容完整不截断
- 🎯 **AI 增强**：自动关键词高亮 + 智能 Emoji 添加
- 🎨 **小红书风格**：3:4 宽高比，渐变背景，现代设计
- ⚡ **一键生成**：从文本到多张海报，全自动化处理
- 🔧 **高度可配置**：支持开关控制各项功能
  - `ENABLE_HIGHLIGHT`：关键词高亮开关
  - `ENABLE_AUTO_EMOJI`：AI 智能 Emoji 添加开关

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
playwright install
```

### 配置环境
配置kimi API，火山引擎免费额度使用https://www.volcengine.com/experience/ark?model=kimi-k2-250905 （大模型主要用于智能识别关键词句突显和emoji，可以直接查看output文件夹示例图片）
```bash
# 创建 .env 文件
KIMI_API_KEY=your_kimi_api_key
KIMI_API_URL=https://ark.cn-beijing.volces.com/api/v3/chat/completions
KIMI_MODEL=kimi-k2-250905
```

### 运行生成
```bash
# 1. 编辑 input.txt 文件，输入标题和正文
# 2. 运行生成脚本
python main.py
# 3. 查看 output/ 文件夹中的生成结果
```

### 功能配置
在 `main.py` 文件中可以控制功能开关：
```python
# 配置选项
ENABLE_HIGHLIGHT = True      # 启用关键词高亮
ENABLE_AUTO_EMOJI = True     # 启用AI智能添加Emoji
```

## 📁 项目结构

```
Text2Poster-Generator/
├── main.py              # 主程序入口
├── kimi_highlighter.py  # AI 功能模块
├── index.html           # 海报模板
├── style.css            # 样式文件
├── input.txt            # 输入文本
├── output/              # 生成结果
└── docs/                # 项目文档
```

## 🎯 使用场景

- 📱 **小红书图文**：长文本自动分页，生成系列海报
- 📊 **内容营销**：批量生成宣传图片，提升效率
- 🎨 **设计自动化**：无需设计技能，AI 智能美化
- 📝 **知识分享**：将文章转换为视觉化内容

## 🔧 技术栈

- **Python 3.8+** - 核心逻辑
- **Playwright** - 浏览器自动化
- **HTML/CSS** - 海报模板
- **Kimi API** - AI 增强功能

## 📚 文档

- [📖 使用手册](docs/manual.md) - 详细使用说明
- [🔧 开发日志](docs/dev_log.md) - 开发过程记录
- [💭 项目总结](docs/experience.md) - 经验分享
- [🎨 设计文档](docs/design.md) - 设计理念

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

**⭐ 如果这个项目对你有帮助，欢迎 Star 支持！**
